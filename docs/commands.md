# Command Reference

Complete reference for all DBL commands.

---

## Table of Contents

- [Setup Commands](#setup-commands)
- [Sandbox Commands](#sandbox-commands)
- [Layer Commands](#layer-commands)
- [Branch Commands](#branch-commands)
- [Inspection Commands](#inspection-commands)
- [Utility Commands](#utility-commands)

---

## Setup Commands

### `dbl init`

Initialize a new DBL project in the current directory.

**Usage:**
```bash
dbl init
```

**What it does:**
- Creates `dbl.yaml` configuration file
- Creates `.dbl/` directory structure
- Initializes `master` branch
- Creates manifest file

**Example:**
```bash
cd my-project
dbl init
# Edit dbl.yaml with your database credentials
```

**Configuration (dbl.yaml):**
```yaml
engine: postgres
host: localhost
port: 5432
db_name: myapp
user: postgres
password: password
ignore_tables:
  - migrations
  - sessions
policies:
  allow_drop_table: false
  allow_drop_column: false
```

---

### `dbl import <file>`

Import an existing SQL snapshot as the baseline.

**Usage:**
```bash
dbl import snapshot.sql
```

**What it does:**
- Drops and recreates the database
- Imports the SQL file
- Resets branch history
- Sets as master baseline

**Example:**
```bash
# Export your current database
pg_dump myapp > snapshot.sql

# Import into DBL
dbl import snapshot.sql
```

⚠️ **Warning:** This will drop the existing database!

---

## Sandbox Commands

### `dbl sandbox start`

Create a safe sandbox environment for testing changes.

**Usage:**
```bash
dbl sandbox start
```

**What it does:**
- Creates a shadow backup of your database
- Enables sandbox mode
- Allows you to make changes safely

**Example:**
```bash
dbl sandbox start
# Now make schema changes in your database
# Changes won't affect the original until you apply
```

---

### `dbl sandbox status`

Check current sandbox status.

**Usage:**
```bash
dbl sandbox status
```

**Output:**
- Shows if sandbox is active
- Displays shadow database name
- Shows current branch

---

### `dbl sandbox apply`

Confirm and apply sandbox changes.

**Usage:**
```bash
dbl sandbox apply
```

**What it does:**
- Confirms your changes
- Removes the shadow backup
- Exits sandbox mode

**Example:**
```bash
dbl sandbox start
# ... make changes ...
dbl commit -m "Add new columns"
dbl sandbox apply
```

---

### `dbl sandbox rollback`

Discard sandbox changes and restore original state.

**Usage:**
```bash
dbl sandbox rollback
```

**What it does:**
- Restores database from shadow backup
- Discards all uncommitted changes
- Exits sandbox mode

**Example:**
```bash
dbl sandbox start
# ... make changes ...
# Oh no, something went wrong!
dbl sandbox rollback
```

⚠️ **Warning:** All changes in the sandbox will be lost!

---

## Layer Commands

### `dbl commit -m <message>`

Commit current database changes as a new layer.

**Usage:**
```bash
dbl commit -m "Your commit message"
dbl commit -m "Add auth tables" --with-data
```

**Options:**
- `-m, --message` - Commit message (required)
- `--with-data` - Include data changes (opt-in)

**What it does:**
- Compares current DB with sandbox baseline
- Generates migration SQL
- Opens editor for review
- Saves as a layer file

**Example:**
```bash
dbl sandbox start
# Add a column in your database
dbl commit -m "Add user_email column"
```

**Generated SQL Structure:**
```sql
-- DBL Migration Layer: 2025-12-30
-- From: myapp_shadow To: myapp

-- [EXPAND PHASE] --
ALTER TABLE users ADD COLUMN email VARCHAR(255);

-- [CONTRACT PHASE - HARDENING] --
-- ALTER TABLE users ALTER COLUMN email SET NOT NULL;
```

---

### `dbl diff`

Detect changes in the current database.

**Usage:**
```bash
dbl diff
```

**What it does:**
- Compares current schema with baseline
- Checks data hashes for tracked tables
- Shows detected changes

**Exit codes:**
- `0` - No changes detected
- `1` - Changes detected

**Example:**
```bash
dbl diff
# Output:
# 🔴 SCHEMA CHANGE detected
# 🔴 DATA CHANGE: users
```

---

### `dbl reset`

Rebuild database from scratch using all layers.

**Usage:**
```bash
dbl reset
```

**What it does:**
- Drops current database
- Creates fresh database
- Applies snapshot (if exists)
- Replays all layers in order

**Example:**
```bash
dbl reset
# Rebuilding myapp on branch master...
# State restored.
```

⚠️ **Warning:** This will drop and recreate your database!

---

## Branch Commands

### `dbl branch [name]`

List, create, or delete branches.

**Usage:**
```bash
dbl branch                    # List branches
dbl branch feature/new-auth   # Create branch
dbl branch -d old-feature     # Delete branch
```

**Options:**
- `name` - New branch name
- `-d, --delete` - Delete specified branch

**Example:**
```bash
# List all branches
dbl branch
# * master
#   feature/auth <- master

# Create new branch
dbl branch feature/new-table

# Delete old branch
dbl branch -d old-feature
```

---

### `dbl checkout <branch>`

Switch to a different branch.

**Usage:**
```bash
dbl checkout <branch>
```

**What it does:**
- Updates current branch pointer
- Rebuilds database with branch history
- Applies all layers from that branch

**Example:**
```bash
dbl checkout feature/auth
# Switching to branch 'feature/auth'...
# Rebuilding database...
```

⚠️ **Requires:** No active sandbox. Commit or rollback first.

---

### `dbl merge <branch>`

Merge changes from another branch.

**Usage:**
```bash
dbl merge <branch>
```

**What it does:**
- Applies new layers from target branch
- Updates current branch
- Preserves both branches

**Example:**
```bash
dbl checkout master
dbl merge feature/auth
# Applying 3 layers from feature/auth...
# Merge completed.
```

---

### `dbl pull <branch>`

Pull changes from another branch (like merge, but emphasizes fetching).

**Usage:**
```bash
dbl pull <branch>
```

**What it does:**
- Same as merge
- Git-like terminology for familiarity

**Example:**
```bash
dbl pull origin/master
```

---

### `dbl rebase <onto>`

Rebase current branch onto another.

**Usage:**
```bash
dbl rebase <onto>
dbl rebase <onto> --dry-run
dbl rebase <onto> --no-backup
```

**Options:**
- `--dry-run` - Show what would happen
- `--no-backup` - Skip backup branch creation

**What it does:**
- Replays current branch commits on top of target
- Creates backup branch (unless --no-backup)
- Updates branch history

**Example:**
```bash
dbl checkout feature/auth
dbl rebase master
# Rebase completed: 'feature/auth' onto 'master'
# Backup created: feature/auth_backup_20251230
```

---

## Inspection Commands

### `dbl log [branch]`

Show layer history for a branch.

**Usage:**
```bash
dbl log                    # Current branch
dbl log master            # Specific branch
dbl log --oneline         # Compact format
dbl log -n 5              # Last 5 layers
```

**Options:**
- `branch` - Branch to inspect (default: current)
- `--oneline` - Short format
- `-n <number>` - Limit number of layers

**Example:**
```bash
dbl log --oneline
# a1b2c3d Add user authentication
# e4f5g6h Create posts table
# h7i8j9k Initial schema
```

---

### `dbl rev-parse <ref>`

Resolve references (HEAD, branches, etc).

**Usage:**
```bash
dbl rev-parse HEAD
dbl rev-parse master
```

**Example:**
```bash
dbl rev-parse HEAD
# master
```

---

### `dbl validate [branch]`

Validate migration patterns and detect anomalies.

**Usage:**
```bash
dbl validate              # Current branch
dbl validate master       # Specific branch
dbl validate --fix        # (Future) Auto-fix issues
```

**What it checks:**
- Contract without prior backfill
- Uncommented DROP statements
- SET NOT NULL without data population
- Mixed data/schema in same layer
- Type changes without migration
- Orphaned backfill operations

**Example:**
```bash
dbl validate
# ✅ Branch 'master' valid (no anomalies detected)

# Or with issues:
# ⚠️  Validation for branch 'feature/auth': 2 warning(s)
#    ⚠️  Layer master_123.sql: Contract without prior backfill
#    ⚠️  Layer master_124.sql: Column type change detected
```

**Configuration (dbl.yaml):**
```yaml
validate:
  strict: false                # Treat warnings as errors
  allow_orphaned: false        # Allow backfill without expand
  require_comments: false      # Require comments for contract
  detect_type_changes: true    # Warn about type changes
```

---

## Utility Commands

### `dbl version`

Show version information.

**Usage:**
```bash
dbl version
```

**Output:**
```
🚀 DBL (Database Layering) v0.0.1-alpha
ℹ️  Repository: https://github.com/alann-estrada-KSH/dbl-sandbox
```

---

### `dbl help`

Show help information.

**Usage:**
```bash
dbl help
```

**Output:**
- Lists all available commands
- Shows migration phases explanation
- Displays validation configuration options

---

## Exit Codes

DBL uses standard exit codes:

- `0` - Success
- `1` - Error or changes detected (for `diff`)

---

## Environment Variables

- `EDITOR` - Text editor for commit messages (default: `nano`)
- `PGPASSWORD` - PostgreSQL password (if not using docker)

---

## Tips

### 1. Always use sandbox mode
```bash
dbl sandbox start
# ... make changes ...
dbl commit -m "message"
dbl sandbox apply
```

### 2. Review generated SQL
The commit command opens your editor. Always review before saving!

### 3. Use descriptive messages
```bash
# Good ✅
dbl commit -m "Add email column to users table with index"

# Bad ❌
dbl commit -m "changes"
```

### 4. Validate regularly
```bash
dbl validate
```

### 5. Create feature branches
```bash
dbl branch feature/my-feature
dbl checkout feature/my-feature
# ... work on feature ...
dbl checkout master
dbl merge feature/my-feature
```

---

## See Also

- [Getting Started Guide](getting-started.md)
- [Best Practices](best-practices.md)
- [Migration Patterns](patterns.md)
- [Architecture](architecture.md)
