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
- Python: 3.8+ (recommended 3.10+)
- Database client tools (match your engine):
  - Postgres: `psql`, `pg_dump`
  - MySQL: `mysql`, `mysqldump`
- Optional: Docker (if you use a containerized DB) and an editor (`nano`, `vim`, or your default editor).

## Install so you can run `dbl`

### Linux (native) and macOS
1. Make the CLI executable:
	```bash
	chmod +x /path/to/dbl.py
	```
2. Create a symlink in your PATH:
	```bash
	# macOS/Linux (requires sudo for /usr/local/bin)
	sudo ln -sf /path/to/dbl.py /usr/local/bin/dbl
	```
3. Test:
	```bash
	dbl help
	```

Notes:
- If you prefer a per-user install, use `~/bin` and add it to `PATH`:
  ```bash
  mkdir -p ~/bin
  ln -sf /path/to/dbl.py ~/bin/dbl
  echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
  ```

### Windows (PowerShell / CMD)
Option A — simple launcher script:
1. Create a user bin folder and add it to PATH:
	- Create `%USERPROFILE%\bin`
	- Add `%USERPROFILE%\bin` to System/User `PATH`
2. Create a launcher file `%USERPROFILE%\bin\dbl.cmd` with:
	```bat
	@echo off
	REM Update the path below to your dbl.py
	python "C:\\Users\\alann\\KSH\\Tests\\dbl-sandbox\\dbl.py" %*
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
- To update, replace `/path/to/dbl.py` and recreate the symlink if needed.
- To uninstall, remove the symlink (`/usr/local/bin/dbl`) or delete `%USERPROFILE%\bin\dbl.cmd`.

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
- "dbl: command not found": ensure the symlink (`/usr/local/bin/dbl`) or `%USERPROFILE%\bin\dbl.cmd` is on `PATH` and points to the correct `dbl.py`.
- Postgres errors like `psql not found`: install client tools (on macOS via Homebrew: `brew install postgresql`; on Linux via your package manager; on Windows consider WSL).
- Docker usage: set `container_name` in `dbl.yaml` to make DBL run commands inside the container.
- Permission issues on symlink: use a per-user `~/bin` directory and add it to `PATH`.


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