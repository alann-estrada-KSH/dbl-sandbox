# dbl init

Initialize a DBL project in the current directory.

## Synopsis

```bash
dbl init
```

## Description

The `init` command sets up DBL in your project by creating the necessary configuration files and directory structure. This is the first command you should run when starting to use DBL with a database.

## What It Does

1. **Creates `dbl.yaml`**: The main configuration file containing database connection details and settings
2. **Creates `.dbl/` directory**: Internal DBL workspace for storing:
   - `layers/`: Version-controlled SQL migrations
   - `manifest.json`: Branch and layer metadata
   - `state.json`: Current database state tracking
   - `snapshot.sql`: Baseline database dump
3. **Initializes `master` branch**: Creates the default branch in the manifest

## Usage Example

```bash
# Navigate to your project
cd my-project

# Initialize DBL
dbl init

# Output:
# ✓ Created dbl.yaml configuration file
# ✓ Created .dbl directory structure
# ✓ Initialized master branch
```

## What Happens After Init

After running `init`, you need to:

1. **Edit `dbl.yaml`** with your database credentials:
   ```yaml
   engine: postgres  # or mysql
   host: localhost
   port: 5432
   user: myuser
   password: mypassword
   database: mydb
   ```

2. **Import your database** (optional):
   ```bash
   dbl import snapshot.sql
   ```

3. **Start working** with sandboxes:
   ```bash
   dbl sandbox start
   ```

## Configuration File (dbl.yaml)

The generated `dbl.yaml` contains:

```yaml
engine: postgres  # Database engine (postgres or mysql)

# Connection details
host: localhost
port: 5432
user: your_user
password: your_password
database: your_database

# Optional: Docker support
# container_name: my_postgres_container

# Optional: Table filtering
ignore_tables: []   # Tables to exclude from tracking
track_tables: []    # Only track these tables (if set)

# Optional: Safety policies
policies:
  allow_data_loss: false  # Prevent destructive operations
  require_sandbox: true   # Force sandbox usage

# Optional: Validation rules
validate:
  strict: false              # Treat warnings as errors
  allow_orphaned: false      # Allow backfill without expand
  require_comments: false    # Require comments for contract phase
  detect_type_changes: true  # Warn about column type changes
```

## Directory Structure

After initialization:

```
my-project/
├── dbl.yaml              # Configuration file
├── .dbl/                 # DBL workspace (add to .gitignore)
│   ├── layers/           # Migration layers
│   │   └── manifest.json # Branch and layer metadata
│   ├── snapshot.sql      # Database baseline
│   ├── state.json        # Current state
│   └── sandbox.json      # Sandbox metadata (when active)
└── .gitignore            # (recommended) Add .dbl/ here
```

## Important Notes

!!! warning "Security"
    The `dbl.yaml` file contains database credentials. **Never commit it to version control** if it contains sensitive information.

!!! tip "Version Control"
    Add `.dbl/` to your `.gitignore`:
    ```bash
    echo ".dbl/" >> .gitignore
    ```
    
    Only track migration layers separately if needed for team collaboration.

!!! info "Docker Support"
    If using Docker, uncomment and set `container_name` in `dbl.yaml` to run commands inside the container.

## Common Issues

### Already Initialized

If DBL is already initialized:
```
Error: dbl.yaml already exists
```

**Solution**: Remove existing `dbl.yaml` and `.dbl/` directory if you want to reinitialize:
```bash
rm dbl.yaml
rm -rf .dbl/
dbl init
```

### Permission Denied

If you get permission errors:
```
Error: Permission denied creating .dbl/
```

**Solution**: Ensure you have write permissions in the current directory or run with appropriate permissions.

## Next Steps

After initialization:

1. [Configure your database connection](../guide/configuration.md)
2. [Create your first sandbox](../sandbox/start.md)
3. [Make your first migration](../../getting-started/first-migration.md)

## See Also

- [`dbl import`](import.md) - Import an existing database
- [Configuration Guide](../guide/configuration.md)
- [Quick Start Tutorial](../../getting-started/quick-start.md)
