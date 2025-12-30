# DBL — Database Layering CLI

> **Version: v0.0.1-alpha**  
> **Status: Experimental** — Not production-ready. Use at your own risk in development environments only.

A lightweight, git-like workflow for database schema and data changes, with sandboxing, validation, and branch/layer history.

## 📂 Project Structure

DBL now uses a **modular architecture** for better maintainability and extensibility. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

```
dbl-sandbox/
├── dbl.py                 # CLI entry point
├── dbl/                   # Core package (26 modular files)
│   ├── engines/          # Database abstractions (PostgreSQL, MySQL)
│   ├── commands/         # CLI command implementations
│   └── *.py              # Core logic (config, state, planner, etc)
└── dbl_legacy.py         # Original monolithic version (backup)
```

## What is DBL?

DBL is a **local development tool** for:
- **Versioning database changes** as discrete layers (like git commits).
- **Sandboxing experiments** to avoid breaking your main database.
- **Branching schema evolution** to work on multiple features in parallel.
- **Validating migration patterns** (expand/backfill/contract phases).
- **Replaying changes deterministically** for reproducible DB state.

It's designed for developers who want git-like workflows for database schema and optional data tracking.

---

## 📚 Documentation

**📖 Full documentation:** [https://alann-estrada-ksh.github.io/dbl-sandbox/](https://alann-estrada-ksh.github.io/dbl-sandbox/)

Quick links:
- [Getting Started Guide](https://alann-estrada-ksh.github.io/dbl-sandbox/getting-started/)
- [Command Reference](https://alann-estrada-ksh.github.io/dbl-sandbox/commands/)
- [Changelog & Versions](https://alann-estrada-ksh.github.io/dbl-sandbox/changelog/)
- [Architecture Details](ARCHITECTURE.md)
- [Release Process](RELEASE.md)

---

## What DBL is NOT

⚠️ **Important Disclaimers:**

- **NOT a replacement for migration frameworks** like Flyway, Liquibase, or Rails migrations. DBL complements them; it doesn't replace them.
- **NOT production-ready**. This is alpha software. Expect bugs, breaking changes, and missing features.
- **NOT automatic or zero-config**. You must understand your database, write SQL, and review generated migrations.
- **NOT zero-risk**. DBL can drop databases, delete data, and generate destructive SQL. Always use sandboxes and backups.
- **NOT a deployment tool**. DBL tracks changes locally; it does NOT deploy to production servers.
- **NOT safe for sensitive data**. DBL writes plaintext SQL files. Do NOT use with real user data or credentials in git.

If you need battle-tested, production-grade schema management, use established migration tools.


## Quick Summary
- Purpose: Safely evolve schemas and optionally data, track changes as layers, and rebuild deterministically.
- Engines: Postgres and MySQL (via client CLIs). Docker supported.
- CLI: Single script executable as `dbl` from any shell.

## Prerequisites
- Python: 3.7+ (recommended 3.10+)
- pip: Python package installer (usually included with Python)
- Database client tools (match your engine):
  - Postgres: `psql`, `pg_dump`
  - MySQL: `mysql`, `mysqldump`
- Optional: Docker (if you use a containerized DB) and an editor (`nano`, `vim`, or your default editor).

## Installation

### Option 1: Install via pip (Recommended)

Install directly from GitHub (includes all dependencies):

```bash
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```

This will:
- ✅ Install DBL and all dependencies (PyYAML)
- ✅ Create a global `dbl` command
- ✅ Work on Linux, macOS, and Windows

Test the installation:
```bash
dbl help
dbl version
```

### Option 2: Development/Local Install

For development or if you want to modify the code:

1. Clone the repository:
```bash
git clone https://github.com/alann-estrada-KSH/dbl-sandbox.git
cd dbl-sandbox
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install in editable mode:
```bash
pip install -e .
```

Or create a symlink manually:

#### Linux and macOS
```bash
chmod +x /path/to/dbl.py
sudo ln -sf /path/to/dbl.py /usr/local/bin/dbl
```

#### macOS with Homebrew Python
If using Homebrew Python:
```bash
chmod +x /path/to/dbl.py
ln -sf /path/to/dbl.py /opt/homebrew/bin/dbl
```

Test:
```bash
dbl help
```

### Option 3: Windows Installation

#### Via pip (Recommended)
```powershell
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```

#### Manual Installation
1. Install dependencies:
```powershell
pip install -r requirements.txt
```

2. Create a batch file `dbl.cmd` in `%USERPROFILE%\bin\`:
```batch
@echo off
python "C:\path\to\dbl.py" %*
```

3. Add `%USERPROFILE%\bin` to your PATH if not already there.

### Option 4: WSL (Windows Subsystem for Linux)
1. Install in WSL:
```bash
```bash
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```
2. Use `wsl dbl help` from Windows or run directly inside WSL.

### Updating or uninstalling
	python "C:\\Users\\your_name\\your\\route\\dbl-sandbox\\dbl.py" %*
	```
3. Open a new terminal and test:
	```powershell
	dbl help
	```

Option B — WSL (recommended for Postgres tooling):
1. Put `dbl.py` inside your WSL home, make it executable and symlink:
	```bash
	chmod +x /home/<user>/dbl.py
	sudo ln -sf /home/<user>/dbl.py /usr/local/bin/dbl
	```
2. Use `wsl dbl help` from Windows or run directly inside WSL.

### Updating or uninstalling

**Automatic update (recommended)**:
```bash
dbl update          # Interactive - asks for confirmation
dbl update -y       # Auto-confirm installation
```
This checks GitHub for the latest release and installs it automatically via pip.

**Manual update**:
- To update manually, replace `/path/to/dbl.py` and recreate the symlink if needed.
- Or use pip: `pip install --upgrade git+https://github.com/alann-estrada-KSH/dbl-sandbox.git`

**Uninstalling**:
- Remove the symlink (`/usr/local/bin/dbl`) or delete `%USERPROFILE%\bin\dbl.cmd`.

## Project Layout
Real-world usage per project:

```
myapp/
├── dbl.yaml        # project configuration
├── .dbl/           # internal state (NOT in git)
└── src/            # your application code
```

What each part does:
- `dbl.yaml`: engine (postgres/mysql), host/port, credentials, tracked/ignored tables, validate rules.
- `.dbl/`: snapshot/state/manifest and layer files maintained by the CLI.
- `src/`: your app; DBL does not touch it.

## First Run (suggested flow)

**Basic workflow** (sandbox → change → commit → apply):

1. Initialize the project:
   ```bash
   cd myapp
   dbl init
   ```
2. Start a sandbox to isolate changes:
   ```bash
   dbl sandbox start
   ```
3. Make DB changes in the sandbox (via migrations, manual DDL, etc).
4. Detect changes:
   ```bash
   dbl diff
   ```
5. Commit a layer (schema-only by default):
   ```bash
   dbl commit -m "Add users table"           # schema only
   dbl commit -m "Seed users" --with-data   # includes data sync
   ```
6. Apply or rollback the sandbox:
   ```bash
   dbl sandbox apply
   # or
   dbl sandbox rollback
   ```
7. Inspect history and rebuild if needed:
   ```bash
   dbl log
   dbl reset
   ```

**Reminder**: Always work in a sandbox. Never commit changes without reviewing the generated SQL.
## Configuration Basics (`dbl.yaml`)
- `engine`: `postgres` or `mysql`
- `container_name`: optional Docker container name (enables `docker exec`)
- `host`, `port`, `user`, `password`: DB connection
- `ignore_tables`, `track_tables`: control what DBL tracks
- `policies`: guard rails for drops
- `validate`: rules for warn-only vs strict behavior (see COMMANDS.md)

## Troubleshooting

### Command Not Found
- **Issue**: "dbl: command not found"
- **Solution**: 
  - Ensure pip installed correctly: `pip show dbl-sandbox`
  - Or check symlink: `/usr/local/bin/dbl` (Linux/macOS) or `%USERPROFILE%\bin\dbl.cmd` (Windows)
  - Try running directly: `python -m dbl help`

### Missing Dependencies
- **Issue**: ImportError or "No module named 'yaml'"
- **Solution**:
  ```bash
  pip install PyYAML>=6.0
  # Or install all dependencies
  pip install -r requirements.txt
  ```
- **Auto-fix**: Run `dbl update` to automatically check and install missing dependencies

### Database Client Tools
- **Postgres**: `psql not found`
  - macOS: `brew install postgresql`
  - Ubuntu/Debian: `sudo apt-get install postgresql-client`
  - Windows: Install PostgreSQL or use WSL
- **MySQL**: `mysql not found`
  - macOS: `brew install mysql-client`
  - Ubuntu/Debian: `sudo apt-get install mysql-client`
  - Windows: Install MySQL or use WSL

### Docker Issues
- **Issue**: DBL can't connect to database in container
- **Solution**: Set `container_name` in `dbl.yaml` to run commands inside the container

### Permission Issues
- **Issue**: Can't create symlink (macOS/Linux)
- **Solution**: Use per-user directory:
  ```bash
  mkdir -p ~/bin
  ln -sf /path/to/dbl.py ~/bin/dbl
  echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
  ```


## ⚠️ Important Warnings

- **Data Loss Risk**: DBL can DROP databases and tables. Always use sandboxes and maintain external backups.
- **SQL Review Required**: DBL generates SQL, but you must review it before committing. It can produce destructive operations.
- **Not Idempotent by Default**: While DBL emits `IF NOT EXISTS` clauses where possible, complex migrations may not be idempotent. Test with `reset`.
- **No Rollback for Applied Changes**: Once you `sandbox apply`, changes are permanent in the main DB. Use `rollback` before `apply` if unsure.
- **No Conflict Resolution**: Branch merges are simple layer unions. Manual conflict resolution may be needed for overlapping changes.
- **Alpha Software**: Expect breaking changes between versions. Pin to a specific commit in production-like environments.
- **Credentials in Config**: `dbl.yaml` contains plaintext passwords. Do NOT commit it to git. Use `.gitignore` or environment variables.


## Commands Reference
See the full command guide in [COMMANDS.md](./COMMANDS.md) for detailed explanations, use cases, and examples.

Quick entry points:
- `dbl help` — list commands and validation config
- `dbl validate` — analyze layers; warn by default, strict via config
- `dbl rebase <onto> --dry-run` — preview rebase results before applying


## Contributing & Feedback

DBL is in early alpha. If you encounter bugs, have feature requests, or want to contribute:
- Open an issue in the repository
- Submit a pull request with improvements
- Share your use cases and workflows

**Remember**: This tool is experimental. Use responsibly and always maintain backups of your databases.


## License

DBL is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

## Credits

Developed by [Alan Estrada](https://github.com/alannnn-estrada). Inspired by git workflows and database migration best practices.

*Happy database layering!*