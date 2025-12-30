# Best Practices

Guidelines for effective database version control with DBL.

## Core Principles

### 1. Always Use Sandboxes

✅ **DO:**
```bash
dbl sandbox start
# Make changes...
dbl commit -m "Add feature"
dbl sandbox apply
```

❌ **DON'T:**
```bash
# Directly modify main database
psql -d production -c "ALTER TABLE users ADD COLUMN email TEXT"
```

**Why:** Sandboxes protect your main database and let you preview changes.

### 2. Review Before Commit

✅ **DO:**
```bash
dbl diff                    # Review all changes
# Read the output carefully
dbl commit -m "message"
```

❌ **DON'T:**
```bash
dbl commit -m "changes"     # Blind commit
```

**Why:** Understand what you're committing to avoid mistakes.

### 3. Descriptive Commit Messages

✅ **DO:**
```bash
dbl commit -m "Add email verification column to users table"
dbl commit -m "Create indexes for posts query performance"
dbl commit -m "Add foreign key constraint between orders and products"
```

❌ **DON'T:**
```bash
dbl commit -m "update"
dbl commit -m "fix"
dbl commit -m "changes"
```

**Why:** Clear messages help team understand history.

---

## Migration Patterns

### Expand-Backfill-Contract Pattern

For safe, zero-downtime migrations:

#### Phase 1: Expand (Add)
```bash
dbl sandbox start
```
```sql
-- Add new column (nullable)
ALTER TABLE users ADD COLUMN email VARCHAR(255);
```
```bash
dbl commit -m "expand: Add email column"
dbl sandbox apply
```

#### Phase 2: Backfill (Populate)
```bash
dbl sandbox start
```
```sql
-- Populate existing rows
UPDATE users SET email = username || '@example.com' WHERE email IS NULL;
```
```bash
dbl commit -m "backfill: Populate email column" --with-data
dbl sandbox apply
```

#### Phase 3: Contract (Constrain)
```bash
dbl sandbox start
```
```sql
-- Add constraint
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);
```
```bash
dbl commit -m "contract: Make email required and unique"
dbl sandbox apply
```

**Benefits:**
- ✅ Zero downtime
- ✅ Rollback-safe
- ✅ App can run during migration

### Column Rename Pattern

Don't rename directly - use expand-backfill-contract:

❌ **Don't:**
```sql
ALTER TABLE users RENAME COLUMN name TO full_name;
```

✅ **Do:**
```bash
# Step 1: Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);

# Step 2: Copy data
UPDATE users SET full_name = name;

# Step 3: Update application code to use full_name

# Step 4: Drop old column (after app deployed)
ALTER TABLE users DROP COLUMN name;
```

### Table Rename Pattern

Similar to column rename:

```bash
# Step 1: Create new table
CREATE TABLE customers AS SELECT * FROM users;

# Step 2: Update app to use customers

# Step 3: Drop old table
DROP TABLE users;
```

---

## Branching Strategies

### Feature Branches

Work on features in isolation:

```bash
# Create feature branch
dbl branch feature-comments
dbl checkout feature-comments

# Work on feature
dbl sandbox start
# ... make changes ...
dbl commit -m "Add comments table"
dbl sandbox apply

# Merge when ready
dbl checkout master
dbl merge feature-comments
```

### Hotfix Pattern

Quick fixes on production schema:

```bash
# Create hotfix branch
dbl branch hotfix-index
dbl checkout hotfix-index

# Apply fix
dbl sandbox start
CREATE INDEX idx_users_email ON users(email);
dbl commit -m "Add index for email lookups"
dbl sandbox apply

# Merge to master
dbl checkout master
dbl merge hotfix-index
```

### Development vs Production

```bash
# Development: permissive
validate:
  strict: false
  allow_orphaned: true

# Production: strict
validate:
  strict: true
  require_comments: true
  detect_type_changes: true
```

---

## Team Collaboration

### Commit Conventions

Agree on commit message format:

```bash
# Format: [phase]: Description
dbl commit -m "expand: Add user preferences table"
dbl commit -m "backfill: Populate default preferences"
dbl commit -m "contract: Remove deprecated columns"

# Or: [type]: Description
dbl commit -m "feat: Add comments system"
dbl commit -m "perf: Add indexes for search"
dbl commit -m "fix: Correct foreign key constraint"
```

### Code Review Process

1. **Create feature branch**
2. **Make changes in sandbox**
3. **Commit layers**
4. **Share layer files** (`.dbl/layers/L*.sql`)
5. **Team reviews SQL**
6. **Merge to master**

### Shared Development Database

```yaml
# team-dbl.yaml
engine: postgres
container_name: team_shared_db
user: team_user
password: ${TEAM_DB_PASSWORD}
database: team_dev

policies:
  require_sandbox: true  # Everyone uses sandboxes
```

---

## Performance Considerations

### Index Everything Important

✅ **DO:**
```sql
-- Foreign keys
CREATE INDEX idx_posts_author ON posts(author_id);

-- Frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_status ON posts(status);

-- Composite indexes for complex queries
CREATE INDEX idx_posts_author_status ON posts(author_id, status);
```

### Use Partial Indexes

For large tables:

```sql
-- Index only active records
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- Index only recent data
CREATE INDEX idx_recent_posts ON posts(created_at) 
  WHERE created_at > NOW() - INTERVAL '1 year';
```

### Avoid SELECT * in Data Commits

❌ **Don't:**
```sql
INSERT INTO users SELECT * FROM temp_users;
```

✅ **Do:**
```sql
INSERT INTO users (username, email, created_at)
SELECT username, email, created_at FROM temp_users;
```

---

## Safety Guidelines

### 1. Never Drop Without Backup

```bash
# Before dropping anything important
pg_dump mydb > backup_$(date +%Y%m%d).sql

# Then proceed
dbl sandbox start
DROP TABLE old_table;
dbl commit -m "contract: Remove deprecated old_table"
```

### 2. Test Migrations

```bash
# Test reset (rebuilds from layers)
dbl reset

# Verify app still works
./run-tests.sh
```

### 3. Validate Before Apply

```bash
dbl sandbox start
# Make changes...
dbl diff
dbl validate        # Check for issues
dbl commit -m "msg"
dbl sandbox apply
```

### 4. Use Transactions

In manual SQL:

```sql
BEGIN;

-- Your changes
ALTER TABLE users ADD COLUMN new_col TEXT;
UPDATE users SET new_col = 'default';

-- Verify
SELECT COUNT(*) FROM users WHERE new_col IS NULL;

-- If good:
COMMIT;
-- If bad:
ROLLBACK;
```

---

## Naming Conventions

### Tables

```sql
-- Plural nouns
CREATE TABLE users (...);
CREATE TABLE posts (...);
CREATE TABLE comments (...);

-- Join tables: singular_singular
CREATE TABLE post_tag (...);
CREATE TABLE user_role (...);
```

### Columns

```sql
-- Clear, descriptive names
id              -- Primary key
user_id         -- Foreign key
created_at      -- Timestamp
is_active       -- Boolean
email_verified  -- Boolean
```

### Indexes

```sql
-- Format: idx_table_column(s)
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_author_status ON posts(author_id, status);

-- Unique indexes: uq_table_column(s)
CREATE UNIQUE INDEX uq_users_username ON users(username);
```

### Constraints

```sql
-- Format: fk_table_column_ref
ALTER TABLE posts 
  ADD CONSTRAINT fk_posts_author_users 
  FOREIGN KEY (author_id) REFERENCES users(id);

-- Format: chk_table_condition
ALTER TABLE users 
  ADD CONSTRAINT chk_users_valid_email 
  CHECK (email LIKE '%@%');
```

---

## Configuration Management

### Development

```yaml
# dbl.dev.yaml
engine: postgres
host: localhost
database: myapp_dev

ignore_tables:
  - sessions

validate:
  strict: false
```

### Staging

```yaml
# dbl.staging.yaml
engine: postgres
host: staging.db.internal
database: myapp_staging

validate:
  strict: true
  detect_type_changes: true
```

### Production

```yaml
# dbl.prod.yaml
engine: postgres
host: ${PROD_DB_HOST}
database: myapp_prod

policies:
  require_sandbox: true
  allow_data_loss: false

validate:
  strict: true
  require_comments: true
```

---

## CI/CD Integration

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for uncommitted DB changes
if dbl sandbox status | grep -q "active"; then
    echo "❌ Active sandbox found!"
    echo "Run 'dbl sandbox apply' or 'dbl sandbox rollback'"
    exit 1
fi
```

### CI Pipeline

```yaml
# .github/workflows/db-check.yml
name: Database Check

on: [pull_request]

jobs:
  check-schema:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Database
        run: docker run -d -p 5432:5432 postgres:15
      
      - name: Check Migrations
        run: |
          dbl init
          dbl reset
          # Run app tests
          pytest tests/
```

---

## Common Anti-Patterns

### ❌ Skipping Sandboxes

```bash
# BAD: Directly modifying production
psql -d prod -c "ALTER TABLE users ADD COLUMN email TEXT"
```

### ❌ Mixing Schema and Data

```bash
# BAD: One commit with both
CREATE TABLE posts (...);
INSERT INTO posts VALUES (...);
```

### ❌ Not Testing Reset

```bash
# BAD: Never testing if layers replay correctly
```

### ❌ Vague Commit Messages

```bash
# BAD
dbl commit -m "update"
dbl commit -m "changes"
```

### ❌ Ignoring Validation Warnings

```bash
# BAD: Ignoring warnings
dbl validate
# ⚠️  Warnings found
dbl sandbox apply anyway
```

---

## Checklist

Before each commit:

- [ ] Working in active sandbox
- [ ] Ran `dbl diff` and reviewed output
- [ ] Checked `dbl validate` for warnings
- [ ] Descriptive commit message
- [ ] Tested changes work with app
- [ ] Foreign keys have indexes
- [ ] Using appropriate migration phase

---

## Learn More

- [Migration Patterns](patterns.md)
- [Configuration Guide](configuration.md)
- [Troubleshooting](troubleshooting.md)
- [Commands Reference](../commands/index.md)
