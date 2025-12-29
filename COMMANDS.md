# DBL Commands Guide

A concise reference to DBL's commands, grouped by usage level.

## Basics

### help
Show available commands and validation config.
- **What it does**: Prints a list of all DBL commands with brief descriptions and shows the current validation configuration options.
- **When to use**: When you're learning DBL or need a quick reference.
- **Syntax**: `dbl help`

### init
Initialize a DBL project in the current folder.
- **What it does**: Creates `dbl.yaml` configuration file and `.dbl/` directory structure. Sets up the initial `master` branch in the manifest.
- **Effects**: Writes config files; does NOT touch your database yet.
- **When to use**: First time setting up DBL in a project.
- **Syntax**: `dbl init`
- **Next step**: Edit `dbl.yaml` with your DB credentials and preferences.

### sandbox
Create and manage a safe sandbox for changes.
- **What it does**: 
  - `start`: Clones your main DB to a temporary sandbox DB and tracks it as the active workspace. This isolates your experiments.
  - `apply`: Accepts sandbox changes, makes them permanent in the main DB, and cleans up the sandbox.
  - `rollback`: Discards all sandbox changes and deletes the sandbox DB. Your main DB remains untouched.
  - `status`: Shows if you're in a sandbox and which DB is active.
- **When to use**: Always use sandbox when making DB changes manually or testing migrations. It's your safety net.
- **Syntax**:
  - `dbl sandbox start`
  - `dbl sandbox apply`
  - `dbl sandbox rollback`
  - `dbl sandbox status`
- **Important**: You MUST be in a sandbox to commit changes.

### diff
Detect database changes in the sandbox versus the last known state.
- **What it does**: Compares current sandbox schema and data (for tracked tables) against the baseline snapshot. Reports what changed.
- **Effects**: Read-only operation; shows you what would be captured in a commit.
- **Exit codes**: `0` = no changes detected, `1` = changes detected (useful for scripts/CI).
- **When to use**: After making manual DB changes, before committing, or in CI pipelines to detect drift.
- **Syntax**: `dbl diff`

### commit
Save a migration layer (schema-only by default; data is opt-in).
- **What it does**: 
  - Inspects the sandbox DB vs backup DB.
  - Generates SQL with phase comments (expand/backfill/contract).
  - Opens your editor (nano/vim/etc) for review and editing.
  - Saves the final SQL as a layer file (e.g., `master_1735567890.sql`) under `.dbl/layers/`.
  - Updates branch manifest with commit metadata.
  - Synchronizes the shadow backup DB with your sandbox state.
- **Schema vs Data**:
  - Default (schema-only): captures CREATE/ALTER/DROP statements; ignores data changes.
  - With `--with-data`: includes INSERT/UPDATE statements for tracked tables.
- **When to use**: After verifying `dbl diff` output and you want to persist the changes as a versioned layer.
- **Syntax**:
  - `dbl commit -m "Add users table"` (schema only)
  - `dbl commit -m "Seed initial users" --with-data` (includes data sync)
- **Important**: This does NOT apply changes to production; it just records them.

### log
Show layer history.
- **What it does**: Lists all committed layers (like `git log`) for the current or specified branch. Shows file names, commit messages, timestamps, and type (schema/data/mixed).
- **When to use**: To review what changes have been committed, audit history, or find a specific layer.
- **Syntax**:
  - `dbl log` (current branch)
  - `dbl log feature/auth` (specific branch)
  - `dbl log --oneline` (compact format)
  - `dbl log -n 5` (last 5 layers)

### reset
Rebuild the sandbox DB by replaying snapshot + layers of the current branch.
- **What it does**: 
  - Drops and recreates the sandbox DB.
  - Restores the base snapshot (if exists).
  - Replays all layers from the current branch in order.
  - Brings the DB to a known, reproducible state.
- **When to use**: 
  - After checkout to rebuild for the new branch.
  - After rebase to apply the new layer order.
  - When you want to test that your layers replay correctly (idempotency check).
  - To recover from a broken sandbox state.
- **Syntax**: `dbl reset`
- **Warning**: Destructive to sandbox DB; requires confirmation if not in sandbox.

## Intermediate

### branch
List, create, or delete branches.
- **What it does**: 
  - List: Shows all branches and marks the current one.
  - Create: Creates a new branch starting from the current branch's layer history.
  - Delete: Removes a branch and its layer metadata (files remain in `.dbl/layers/` for safety).
- **When to use**: When working on features in parallel, experimenting with schema changes, or organizing work by team/sprint.
- **Syntax**:
  - `dbl branch` (list all)
  - `dbl branch feature/auth` (create new)
  - `dbl branch -d feature/auth` (delete)
- **Note**: Branches are lightweight pointers; creating many branches is cheap.

### checkout
Switch branch and rebuild DB.
- **What it does**: 
  - Changes the current branch pointer in the manifest.
  - Automatically calls `reset` to rebuild the sandbox DB with the new branch's layer history.
- **Effects**: Destructive to sandbox DB; all uncommitted changes are lost.
- **When to use**: To switch context between features, review another team member's work, or test different schema evolution paths.
- **Syntax**: `dbl checkout feature/auth`
- **Important**: Cannot checkout while in an active sandbox; apply or rollback first.

### pull
Pull layers from another branch without destroying it (git-like).
- **What it does**: 
  - Finds layers in the source branch that don't exist in the current branch.
  - Copies those layer references into the current branch.
  - Does NOT modify the source branch.
- **When to use**: To bring in changes from `main` or another feature branch without switching away from your current work.
- **Syntax**: `dbl pull main`
- **Difference from merge**: Similar effect, but the name suggests fetching from a remote-like source.

### merge
Merge changes from another branch into the current one.
- **What it does**: Identical to `pull` — adds layers from the target branch that aren't in the current branch.
- **When to use**: To integrate another branch's layers into your current branch (e.g., merging `develop` into `feature/reporting`).
- **Syntax**: `dbl merge develop`
- **Note**: This is a simple "layer union" merge; no conflict resolution (yet).

### rev-parse
Resolve references (HEAD, current branch, hashes, etc.).
- **What it does**: Translates symbolic references like `HEAD` into concrete values (current branch name, layer count, last layer file).
- **When to use**: Scripting, debugging, or when you need programmatic access to branch metadata.
- **Syntax**: `dbl rev-parse HEAD`

## Advanced

### validate
Analyze anomalies across layers (warn-only by default).
- **What it does**: 
  - Scans all layers in a branch and checks for risky patterns:
    - Contract operations (DROP, NOT NULL) before expand/backfill.
    - Uncommented DROP statements.
    - NOT NULL constraints without data preparation.
    - Mixed data/schema changes in a single layer.
    - Inconsistent commit type metadata.
    - Column type changes (can break compatibility).
  - Reports warnings (yellow) or errors (red) based on config.
  - Does NOT execute any SQL or modify the DB.
- **Configuration** (`dbl.yaml` → `validate`):
  - `strict: false` → treat warnings as errors and exit with non-zero code (useful for CI).
  - `allow_orphaned: false` → permit backfill without prior expand phase.
  - `require_comments: false` → require explanatory comments for contract operations.
  - `detect_type_changes: true` → warn when column types change (e.g., `varchar(100)` → `varchar(255)`).
- **When to use**: 
  - Before merging feature branches.
  - In CI pipelines to catch risky migrations.
  - After rebase to ensure layer order is sane.
  - As a learning tool to understand phase discipline.
- **Syntax**: 
  - `dbl validate` (current branch)
  - `dbl validate feature/auth` (specific branch)
  - `dbl validate --fix` (placeholder for future autofix; currently does nothing)
- **Output**: Warnings/errors with layer file names and line numbers. Always exits with a reminder that validation is informational only.

### rebase
Rebase current branch onto another (git-style).
- **What it does**: 
  - Takes all layers from the base branch (`onto`).
  - Adds layers from the current branch that aren't in the base.
  - Reorders the current branch's layer list to reflect this new history.
  - Optionally creates a backup branch before applying (e.g., `feature/auth_backup_1735567890`).
- **Effects**: Changes layer order in the manifest; does NOT modify layer files or the DB directly.
- **When to use**: 
  - To bring your feature branch up-to-date with `main` without merging `main` into your branch.
  - To clean up history by consolidating base layers.
  - To resolve dependency order (e.g., ensuring a shared layer comes before feature-specific layers).
- **Syntax**:
  - `dbl rebase main --dry-run` (preview changes)
  - `dbl rebase main` (apply with backup)
  - `dbl rebase main --no-backup` (apply without backup)
- **Important**: After rebase, run `dbl reset` to rebuild the DB with the new layer order.
- **Dry-run output**: Shows base layer count, current layer count, resulting layer count, and which layers would be skipped.

### import
Import a SQL snapshot to reset the master state (destructive; confirmation required).
- **What it does**: 
  - Copies the provided SQL file to `.dbl/snapshot.sql`.
  - Drops and recreates the main database.
  - Executes the snapshot SQL to restore the baseline state.
  - Resets the manifest to a clean `master` branch with no layers.
- **Effects**: **HIGHLY DESTRUCTIVE** — wipes the main DB and all layer history.
- **When to use**: 
  - Initial setup when you have an existing DB dump.
  - Starting fresh after major schema refactoring.
  - Importing a production snapshot for local development.
- **Syntax**: `dbl import path/to/snapshot.sql`
- **Warning**: Requires explicit confirmation. This cannot be undone without a backup.

## Phases (optional metadata)
Use comments in your layer SQL to declare intent:
- `expand`: Add columns/tables (safe, no data loss)
- `backfill`: Update/populate data (optional; use `--with-data` for commit)
- `contract`: Remove/constrain (careful; review before executing)

Example header (auto-inserted by DBL when generating SQL):
```sql
-- DBL Migration Layer: 2025-12-29 12:34:56
-- From: backup_db To: active_db
--
-- Phases:
--   expand:   Add columns/tables (safe, no data loss)
--   backfill: Update/populate data (optional)
--   contract: Remove/constrain (careful, review)
```

## Examples
- Add a new table (schema-only):
  ```bash
  dbl sandbox start
  # create table in the sandbox via your tooling
  dbl diff
  dbl commit -m "Add orders table"
  dbl sandbox apply
  ```
- Seed data (with data sync):
  ```bash
  dbl sandbox start
  # insert rows in sandbox
  dbl diff
  dbl commit -m "Seed initial orders" --with-data
  dbl sandbox apply
  ```
- Rebase a feature branch onto `main`:
  ```bash
  dbl checkout feature/reporting
  dbl rebase main --dry-run
  dbl rebase main
  dbl reset
  ```

## Tips
- Keep data changes opt-in: use `--with-data` only when needed.
- Prefer idempotent DDL: DBL emits `CREATE TABLE IF NOT EXISTS` and `ADD COLUMN IF NOT EXISTS` where possible.
- Use validation in CI: enable `validate.strict: true` in `dbl.yaml` to fail on warnings.
- Docker users: set `container_name` to run DB commands inside your container.
- Postgres vs MySQL: DBL adapts to your `engine`, but client tools must be available in your environment.
