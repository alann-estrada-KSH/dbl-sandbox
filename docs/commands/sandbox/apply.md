# dbl sandbox apply

Apply sandbox changes to the main database.

## Synopsis

```bash
dbl sandbox apply
```

## Description

Applies all changes from the sandbox to your main database, making them permanent. This also cleans up the sandbox database automatically.

## What It Does

1. **Validates sandbox state** - Ensures sandbox is active and has commits
2. **Applies layers** - Executes committed SQL layers on main database
3. **Updates state** - Marks layers as applied
4. **Drops sandbox** - Removes temporary sandbox database
5. **Cleans metadata** - Removes sandbox tracking files

## Usage Example

```bash
# Complete workflow
dbl sandbox start
# Make changes...
dbl diff
dbl commit -m "Add user preferences"
dbl sandbox apply
```

**Output:**
```
Applying sandbox changes to main database...
✓ Executing layer L005
✓ Changes applied successfully
✓ Sandbox database dropped
✓ Sandbox metadata cleared

Your main database (myapp) now includes all sandbox changes.
```

## Detailed Workflow

### Step-by-Step

```bash
# 1. Create sandbox
$ dbl sandbox start
✓ Sandbox created: myapp_sandbox

# 2. Make changes
$ psql -d myapp_sandbox -c "
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT,
    read BOOLEAN DEFAULT false
);
"

# 3. Review changes
$ dbl diff
+ CREATE TABLE notifications (...)

# 4. Commit
$ dbl commit -m "Add notifications feature"
✓ Layer L008 created

# 5. Apply to main
$ dbl sandbox apply
✓ Applied layer L008 to myapp
✓ Sandbox cleaned up

# 6. Verify
$ psql -d myapp -c "\dt"
         List of relations
 Schema |      Name       | Type  
--------+-----------------+-------
 public | users           | table
 public | posts           | table
 public | notifications   | table  ← New!
```

## Safety Features

### Pre-apply Checks

DBL validates before applying:

- ✅ Sandbox is active
- ✅ Commits exist to apply
- ✅ Main database is accessible
- ✅ No conflicting changes in main DB

### What Gets Applied

Only **committed layers** are applied:

```bash
# Sandbox has uncommitted changes
$ dbl diff
+ ALTER TABLE users ADD COLUMN email TEXT;

$ dbl sandbox apply
Error: Uncommitted changes detected
Commit your changes first with: dbl commit -m "message"

# After committing
$ dbl commit -m "Add email column"
$ dbl sandbox apply
✓ Applied successfully
```

## Complete Example

### Add Comments Feature

```bash
# 1. Start sandbox
$ dbl sandbox start
✓ Sandbox: myapp_sandbox

# 2. Add tables
$ psql -d myapp_sandbox << EOF
-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_comments_post ON comments(post_id);
CREATE INDEX idx_comments_user ON comments(user_id);
EOF

# 3. Review
$ dbl diff
+ CREATE TABLE comments (...)
+ CREATE INDEX idx_comments_post ...
+ CREATE INDEX idx_comments_user ...

# 4. Commit
$ dbl commit -m "Add comments feature with indexes"
✓ Layer L012 created

# 5. Apply to main
$ dbl sandbox apply

Applying sandbox changes to main database (myapp)...
  → Executing L012_add_comments_feature.sql
  → Creating table comments
  → Creating indexes
✓ All changes applied successfully

Cleaning up sandbox...
  → Dropping database myapp_sandbox
  → Removing sandbox metadata
✓ Sandbox cleaned up

Summary:
  Database: myapp
  Layers applied: 1 (L012)
  Tables added: 1 (comments)
  Indexes added: 2
```

## What Happens After Apply

### Database State

```
Before:
  Main DB: myapp          (old schema)
  Sandbox: myapp_sandbox  (new schema)

After:
  Main DB: myapp          (new schema) ✓
  Sandbox: (deleted)
```

### Files Updated

```
.dbl/
├── state.json          ← Updated (no active sandbox)
├── layers/
│   └── L012_*.sql      ← Applied to main
└── sandbox.json        ← Deleted
```

## Important Notes

!!! danger "Permanent Changes"
    After `sandbox apply`, changes are in your main database. **There is no undo** except restoring from backups.

!!! warning "Application Downtime"
    Some operations may briefly lock tables. Plan accordingly for production.

!!! tip "Test First"
    Use `dbl reset` in a test environment to verify layers replay correctly before applying to production.

## Rollback Alternative

If you're not ready to apply:

```bash
# Discard sandbox instead
dbl sandbox rollback

# Sandbox and all changes are deleted
# Main database untouched
```

## Production Deployment

### Safe Production Apply

```bash
# 1. Backup first
pg_dump myapp_prod > backup_$(date +%Y%m%d).sql

# 2. Test in staging
dbl --config staging.yaml sandbox apply

# 3. Verify app works
./run-tests.sh

# 4. Apply to production (during maintenance window)
dbl --config production.yaml sandbox apply

# 5. Verify
./verify-schema.sh
```

### Zero-Downtime Deployment

Use expand-contract pattern:

```bash
# Week 1: Expand (add columns)
dbl sandbox start
ALTER TABLE users ADD COLUMN email TEXT;
dbl commit -m "expand: Add email column"
dbl sandbox apply
# Deploy app v1.1 (reads from both old and new)

# Week 2: Backfill
dbl sandbox start
UPDATE users SET email = username || '@example.com';
dbl commit -m "backfill: Populate email" --with-data
dbl sandbox apply

# Week 3: Contract (enforce constraints)
dbl sandbox start
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
dbl commit -m "contract: Make email required"
dbl sandbox apply
# Deploy app v1.2 (uses only new column)
```

## Error Handling

### Conflicting Changes

**Error:**
```
Error: Main database has conflicting changes
The following tables were modified outside of DBL:
  - users (column added)
```

**Solution:**
1. Review changes in main DB
2. Decide: merge or reset
3. If merging, commit manually
4. If resetting, use `dbl reset`

### Connection Lost

**Error:**
```
Error: Lost connection to main database
```

**Solution:**
- Sandbox remains intact
- Fix connection issue
- Run `dbl sandbox apply` again
- Already-applied changes are skipped (idempotent)

### Insufficient Permissions

**Error:**
```
Error: Permission denied
User 'dbl_user' cannot DROP TABLE
```

**Solution:**
```sql
-- Grant necessary permissions
ALTER USER dbl_user WITH SUPERUSER;
-- Or specific grants
GRANT ALL ON DATABASE myapp TO dbl_user;
```

## Performance Considerations

### Large Databases

For databases > 100GB:

- **Time**: Apply may take several minutes
- **Locks**: Some operations acquire table locks
- **Monitoring**: Watch `pg_stat_activity` for progress

### Optimize Apply

```bash
# For large data migrations
dbl commit -m "Add indexes" --with-data

# Indexes created AFTER data loaded (faster)
```

## CI/CD Integration

### Automated Deployment

```yaml
# .github/workflows/deploy.yml
name: Deploy Database Changes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Apply sandbox
        run: |
          dbl sandbox start
          # Run migrations
          dbl reset
          dbl sandbox apply
          
      - name: Verify
        run: ./verify-schema.sh
```

## Next Steps

After applying:

- **Verify changes**: Check main database has expected schema
- **Test application**: Ensure app works with new schema
- **Monitor logs**: Watch for errors
- **Update documentation**: Document schema changes

## See Also

- [`dbl sandbox start`](start.md) - Create sandbox
- [`dbl sandbox rollback`](rollback.md) - Discard changes
- [`dbl diff`](../changes/diff.md) - Review changes
- [`dbl commit`](../changes/commit.md) - Save changes
- [`dbl reset`](../changes/reset.md) - Rebuild database
