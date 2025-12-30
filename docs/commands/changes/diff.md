# dbl diff

Detect and display database changes in your sandbox.

## Synopsis

```bash
dbl diff [--tables TABLE1 TABLE2 ...]
```

## Description

Compares the current sandbox database against the baseline state to detect all schema and data changes. This command is essential for reviewing what will be committed before you save changes as a layer.

## Options

| Option | Description |
|--------|-------------|
| `--tables TABLE1 TABLE2 ...` | Check only specific tables instead of all tracked tables |

## Exit Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| `0` | No changes detected | CI/CD validation |
| `1` | Changes detected | Normal workflow |

!!! tip "CI/CD Integration"
    Use exit codes in scripts to detect uncommitted changes:
    ```bash
    dbl diff
    if [ $? -eq 1 ]; then
      echo "Uncommitted changes detected!"
    fi
    ```

## What It Detects

### Schema Changes

- ✅ New tables
- ✅ Dropped tables
- ✅ New columns
- ✅ Dropped columns
- ✅ Column type changes
- ✅ Constraint changes (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK)
- ✅ Index changes
- ✅ Default value changes

### Data Changes (When Tracking Tables)

- ✅ Inserted rows
- ✅ Updated rows
- ✅ Deleted rows

!!! info "Data Tracking"
    Data changes are only shown for tables listed in `track_tables` configuration.

## Usage Example

```bash
# Make some changes in your sandbox
psql -d myapp_sandbox -c "
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT,
    read BOOLEAN DEFAULT false
);

ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;
"

# Review changes
dbl diff
```

**Output:**
```sql
-- Schema changes detected:

+ CREATE TABLE notifications (
+     id SERIAL PRIMARY KEY,
+     user_id INTEGER NOT NULL,
+     message TEXT,
+     read BOOLEAN DEFAULT false
+ );

+ ALTER TABLE users 
+   ADD COLUMN email_verified BOOLEAN DEFAULT false;

Summary:
  Tables added: 1 (notifications)
  Columns added: 1 (users.email_verified)
  
Changes detected: 2 schema modifications
Exit code: 1
```

### Check Specific Tables Only

```bash
# Only check the 'users' table for changes
dbl diff --tables users

# Check multiple specific tables
dbl diff --tables users posts comments

# Useful for large databases with many tables
dbl diff --tables orders order_items payments
```

**Output with `--tables`:**
```
🔍 Filtering 1 specific tables: users
ℹ️  Analyzing state of: myapp_sandbox...
ℹ️     Schema: 325 tables | Tracking: 1 tables
⏳ [████████████████████████████] 100% (1/1) tables - users
   ✓ Tracked: 1 tables successfully

🔴 DATA CHANGE: users
   Current:  abc123ef...
   Baseline: def456gh...
```

## Detailed Output

For more verbose output:

```bash
dbl diff --verbose  # (if implemented)
```

## Filtering Output

Check specific tables only (via `track_tables` in `dbl.yaml`):

```yaml
track_tables:
  - users
  - posts
  - comments
```

!!! tip "Performance Optimization"
    For databases with hundreds of tables, use `--tables` to check only relevant tables:
    ```bash
    # Much faster than scanning all 500+ tables
    dbl diff --tables critical_table
    ```

## Complete Example

### Scenario: Add User Profiles

```bash
# 1. Start sandbox
$ dbl sandbox start
✓ Sandbox created

# 2. Make changes
$ psql -d myapp_sandbox
myapp_sandbox=# CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    bio TEXT,
    avatar_url VARCHAR(255),
    location VARCHAR(100)
);
CREATE TABLE

myapp_sandbox=# CREATE INDEX idx_profiles_location ON user_profiles(location);
CREATE INDEX

# 3. Review changes
$ dbl diff

+ CREATE TABLE user_profiles (
+     user_id INTEGER PRIMARY KEY REFERENCES users(id),
+     bio TEXT,
+     avatar_url VARCHAR(255),
+     location VARCHAR(100)
+ );

+ CREATE INDEX idx_profiles_location ON user_profiles(location);

Summary:
  Tables added: 1
  Indexes added: 1
  
Exit code: 1

# 4. If satisfied, commit
$ dbl commit -m "Add user profiles table"
```

## Data Changes Example

With `track_tables` configured:

```yaml
# dbl.yaml
track_tables:
  - users
```

```bash
# Insert test data
$ psql -d myapp_sandbox -c "
INSERT INTO users (username, email) VALUES 
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com');
"

# See data changes
$ dbl diff
```

**Output:**
```sql
-- Data changes for tracked tables:

Table: users
+ INSERT INTO users (id, username, email) VALUES 
+   (1, 'alice', 'alice@example.com'),
+   (2, 'bob', 'bob@example.com');

Summary:
  Rows inserted: 2 (users)
  
Exit code: 1
```

## CI/CD Pipeline Example

Detect uncommitted schema changes:

```yaml
# .github/workflows/check-schema.yml
name: Check Schema Changes

on: [pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup database
        run: |
          # Start test database
          docker run -d -p 5432:5432 postgres:15
          
      - name: Check for uncommitted changes
        run: |
          dbl init
          dbl sandbox start
          
          # Run migrations
          psql -f migrations/*.sql
          
          # Check diff
          dbl diff
          if [ $? -eq 1 ]; then
            echo "❌ Schema changes detected but not committed!"
            echo "Run 'dbl commit' to save these changes."
            exit 1
          else
            echo "✅ No uncommitted changes"
          fi
```

## Understanding the Output

### New Table
```sql
+ CREATE TABLE table_name (
+     column1 TYPE,
+     column2 TYPE
+ );
```

### New Column
```sql
+ ALTER TABLE table_name 
+   ADD COLUMN column_name TYPE;
```

### Dropped Column
```sql
- ALTER TABLE table_name 
-   DROP COLUMN column_name;
```

### Type Change
```sql
~ ALTER TABLE table_name 
~   ALTER COLUMN column_name TYPE new_type;
```

### New Index
```sql
+ CREATE INDEX index_name ON table_name(column);
```

### New Constraint
```sql
+ ALTER TABLE table_name 
+   ADD CONSTRAINT constraint_name FOREIGN KEY (col) REFERENCES other(id);
```

## Important Notes

!!! warning "Requires Active Sandbox"
    `dbl diff` only works when a sandbox is active. Run `dbl sandbox start` first.

!!! info "Baseline Comparison"
    Changes are compared against the state captured when the sandbox was created, not the last commit.

!!! tip "Review Before Commit"
    Always run `dbl diff` before `dbl commit` to understand what will be saved.

## Common Issues

### No Sandbox Active

**Error:**
```
Error: No active sandbox found
```

**Solution:**
```bash
dbl sandbox start
```

### No Changes Detected

If you made changes but diff shows nothing:

1. **Check you're in the sandbox:**
   ```bash
   dbl sandbox status
   ```

2. **Verify changes were applied:**
   ```bash
   psql -d your_database_sandbox -c "\dt"  # List tables
   ```

3. **Check table tracking:**
   - Data changes require `track_tables` configuration

### Diff Shows Unexpected Changes

If diff shows changes you didn't make:

- **System tables**: Add them to `ignore_tables` in `dbl.yaml`
- **Auto-generated objects**: Some extensions create objects automatically

```yaml
ignore_tables:
  - pg_stat_statements
  - sessions
  - _prisma_migrations
```

## Performance Considerations

For large databases:

- **Schema diff**: Fast (metadata only)
- **Data diff**: Slower (requires full table comparison)

**Optimize:**
```yaml
# Only track tables you need
track_tables:
  - critical_table1
  - critical_table2

# Ignore large tables
ignore_tables:
  - audit_logs
  - analytics_events
```

## Next Steps

After reviewing diff:

1. **If satisfied** → [`dbl commit`](commit.md)
2. **If not satisfied** → Make more changes and `dbl diff` again
3. **If want to discard** → [`dbl sandbox rollback`](../sandbox/rollback.md)

## See Also

- [`dbl commit`](commit.md) - Save changes as a layer
- [`dbl sandbox start`](../sandbox/start.md) - Create sandbox
- [`dbl sandbox rollback`](../sandbox/rollback.md) - Discard changes
- [Configuration Guide](../../guide/configuration.md) - Configure table tracking
