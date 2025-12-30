# dbl commit

Save database changes as a versioned layer.

## Synopsis

```bash
dbl commit -m "message"
dbl commit -m "message" --with-data
```

## Description

Captures the current sandbox changes and saves them as a versioned layer (migration). This creates a SQL file that can be replayed to reproduce the changes.

## Options

| Option | Description |
|--------|-------------|
| `-m, --message` | Commit message (required) |
| `--with-data` | Include INSERT/UPDATE statements for tracked tables |

## What It Does

1. **Captures changes**: Runs `diff` to detect all modifications
2. **Generates SQL**: Creates migration SQL file with proper phases
3. **Creates layer**: Assigns a layer ID (L001, L002, etc.)
4. **Updates manifest**: Records layer metadata in branch history
5. **Saves to disk**: Writes to `.dbl/layers/L###_description.sql`

## Usage Examples

### Basic Schema Commit

```bash
# Make changes in sandbox
psql -d myapp_sandbox -c "
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT
);
"

# Commit changes
dbl commit -m "Add notifications table"
```

**Output:**
```
✓ Changes detected via diff
✓ Generated migration SQL
✓ Created layer L001
✓ Updated manifest
✓ Saved: .dbl/layers/L001_add_notifications_table.sql

Layer Details:
  ID: L001
  Message: Add notifications table
  Branch: master
  Timestamp: 2025-12-30 12:34:56
  Phase: expand (safe additions)
```

### Commit with Data

```bash
# Insert sample data
psql -d myapp_sandbox -c "
INSERT INTO users (username, email) VALUES 
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com');
"

# Commit with data flag
dbl commit -m "Add test users" --with-data
```

**Generated SQL includes:**
```sql
-- Phase: backfill (data changes)
INSERT INTO users (username, email) VALUES 
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com');
```

## Generated Layer File

Example: `.dbl/layers/L001_add_notifications_table.sql`

```sql
-- Layer: L001
-- Message: Add notifications table
-- Author: DBL
-- Branch: master
-- Date: 2025-12-30 12:34:56
-- Parent: (none)

-- =============================================================================
-- Phase: expand (safe additions)
-- =============================================================================

-- New table: notifications
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_notifications_user 
ON notifications(user_id);

-- =============================================================================
-- Migration complete
-- =============================================================================
```

## Migration Phases

DBL automatically categorizes changes into phases:

### Expand Phase (Safe)
```sql
-- Phase: expand (safe additions)
CREATE TABLE ...
ALTER TABLE ... ADD COLUMN ...
CREATE INDEX ...
```

### Backfill Phase (Data)
```sql
-- Phase: backfill (data changes)
INSERT INTO ...
UPDATE ...
```

### Contract Phase (Risky)
```sql
-- Phase: contract (review required)
ALTER TABLE ... DROP COLUMN ...
DROP TABLE ...
ALTER TABLE ... ALTER COLUMN ... SET NOT NULL
```

!!! warning "Contract Phase"
    Contract changes are potentially destructive. Always review carefully!

## Layer Naming

Layers are named automatically:

```
L{number}_{message_slug}.sql
```

**Examples:**
- `L001_add_notifications_table.sql`
- `L002_add_user_email_column.sql`
- `L003_create_indexes_for_performance.sql`

## Complete Workflow Example

```bash
# 1. Start sandbox
$ dbl sandbox start
✓ Sandbox created

# 2. Make changes
$ psql -d myapp_sandbox
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    author_id INTEGER REFERENCES users(id)
);

CREATE INDEX idx_posts_author ON posts(author_id);

# 3. Review changes
$ dbl diff
+ CREATE TABLE posts (...)
+ CREATE INDEX idx_posts_author ...

# 4. Commit
$ dbl commit -m "Add posts table with author relationship"
✓ Layer L005 created

# 5. Apply to main DB
$ dbl sandbox apply
✓ Applied to main database
```

## Commit Message Best Practices

### ✅ Good Messages

```bash
dbl commit -m "Add user_preferences table"
dbl commit -m "Add email_verified column to users"
dbl commit -m "Create indexes for posts query performance"
dbl commit -m "Migrate status column from string to enum"
```

### ❌ Poor Messages

```bash
dbl commit -m "changes"
dbl commit -m "update"
dbl commit -m "fix"
dbl commit -m "wip"
```

### Message Convention

Use imperative mood:
```bash
# Good
"Add notifications table"
"Update user schema"
"Remove deprecated columns"

# Not
"Added notifications table"
"Updates user schema"
"Removed deprecated columns"
```

## Data Commits

### When to Use `--with-data`

✅ **Use for:**
- Reference/seed data
- Lookup tables
- Configuration data
- Test fixtures

❌ **Don't use for:**
- User data
- Production data
- Large datasets
- Sensitive information

### Example: Seed Data

```bash
# Add seed data
psql -d myapp_sandbox -c "
INSERT INTO roles (name, permissions) VALUES 
    ('admin', '{"all": true}'),
    ('user', '{"read": true}'),
    ('guest', '{"read_public": true}');
"

# Commit with data
dbl commit -m "Add default roles" --with-data
```

## Configuration

Control commit behavior in `dbl.yaml`:

```yaml
# Require sandbox for commits
policies:
  require_sandbox: true    # Default: true
  allow_data_loss: false   # Prevent DROP operations

# Validation rules
validate:
  strict: false              # Treat warnings as errors
  require_comments: true     # Require comments for contract phase
  detect_type_changes: true  # Warn about type changes
```

## Metadata

Each layer stores metadata:

```json
{
  "layer_id": "L001",
  "message": "Add notifications table",
  "timestamp": "2025-12-30T12:34:56Z",
  "branch": "master",
  "parent": null,
  "phase": "expand",
  "author": "DBL",
  "sha256": "abc123..."
}
```

## Important Notes

!!! warning "Requires Active Sandbox"
    You must have an active sandbox to commit. This is a safety feature.

!!! tip "Review Before Commit"
    Always run `dbl diff` first to review what you're committing.

!!! danger "Cannot Uncommit"
    Once committed, layers are permanent. You can reset or create new layers, but you cannot delete or modify existing ones.

## Common Issues

### No Active Sandbox

**Error:**
```
Error: No active sandbox found
Run 'dbl sandbox start' first
```

**Solution:**
```bash
dbl sandbox start
```

### No Changes to Commit

**Error:**
```
No changes detected
Nothing to commit
```

**Solution:**
- Ensure you made changes in the sandbox database
- Run `dbl diff` to see if changes are detected
- Check that you're connected to the correct database

### Message Required

**Error:**
```
Error: Commit message required
Usage: dbl commit -m "message"
```

**Solution:**
```bash
dbl commit -m "Your commit message here"
```

### Data Changes Without Flag

If you have data changes but didn't use `--with-data`:

```
⚠️  Data changes detected but not included
Use --with-data flag to include INSERT/UPDATE statements
```

**Solution:**
```bash
dbl commit -m "message" --with-data
```

## After Committing

Once you commit, you typically:

1. **Review the generated SQL**:
   ```bash
   cat .dbl/layers/L001_*.sql
   ```

2. **Test in sandbox** (if needed):
   - Sandbox still exists after commit
   - You can make more changes and commit again

3. **Apply to main database**:
   ```bash
   dbl sandbox apply
   ```

4. **Or discard and try again**:
   ```bash
   dbl sandbox rollback
   ```

## Branching

Commits are associated with your current branch:

```bash
# Create feature branch
dbl branch feature-comments
dbl checkout feature-comments

# Work on feature
dbl sandbox start
# ... make changes ...
dbl commit -m "Add comments feature"

# Commits appear in branch history
dbl log
```

## Version Control

**Should you commit layer files to git?**

It depends:

✅ **Commit to git if:**
- Team collaboration needed
- Want migration history in repo
- Using DBL as migration tool

❌ **Don't commit if:**
- Using other migration tools
- DBL is just for local development
- Sensitive data in migrations

## Next Steps

After committing:

- [Apply changes](../sandbox/apply.md) to main database
- [View history](../history/log.md) of commits
- [Validate patterns](../history/validate.md)
- [Reset database](reset.md) from layers

## See Also

- [`dbl diff`](diff.md) - Review changes before commit
- [`dbl sandbox apply`](../sandbox/apply.md) - Apply committed changes
- [`dbl log`](../history/log.md) - View commit history
- [`dbl validate`](../history/validate.md) - Validate migrations
