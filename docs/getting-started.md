# Getting Started with DBL

This guide will help you get started with DBL in under 10 minutes.

---

## Installation

### Prerequisites

Before installing DBL, ensure you have:

1. **Python 3.8+** (3.10+ recommended)
   ```bash
   python --version
   ```

2. **Database CLI tools** (one of):
   - PostgreSQL: `psql` and `pg_dump`
   - MySQL: `mysql` and `mysqldump`

3. **Optional**: Docker (if using containerized databases)

### Install DBL

```bash
# Clone the repository
git clone https://github.com/alann-estrada-KSH/dbl-sandbox.git
cd dbl-sandbox

# Install Python dependencies
pip install pyyaml

# Make executable (Unix/Linux/Mac)
chmod +x dbl.py

# Test installation
python dbl.py version
# Output: 🚀 DBL (Database Layering) v0.0.1-alpha
```

### Optional: Add to PATH

For convenience, add DBL to your PATH:

**Unix/Linux/Mac:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/dbl-sandbox"
alias dbl='python /path/to/dbl-sandbox/dbl.py'

# Reload shell
source ~/.bashrc
```

**Windows:**
```powershell
# Add to PowerShell profile
notepad $PROFILE

# Add this line:
function dbl { python C:\path\to\dbl-sandbox\dbl.py $args }
```

---

## Quick Start Tutorial

### Step 1: Initialize Project

```bash
cd your-project-directory
dbl init
```

This creates:
- `dbl.yaml` - Configuration file
- `.dbl/` - DBL data directory

### Step 2: Configure Database

Edit `dbl.yaml`:

```yaml
engine: postgres
host: localhost
port: 5432
db_name: myapp
user: postgres
password: yourpassword

# Optional: Docker container
container_name: ""

# Tables to ignore
ignore_tables:
  - migrations
  - sessions

# Safety policies
policies:
  allow_drop_table: false
  allow_drop_column: false
```

### Step 3: Import Existing Database (Optional)

If you have an existing database:

```bash
# Export current database
pg_dump myapp > snapshot.sql

# Import into DBL
dbl import snapshot.sql
```

Or start with an empty database:

```bash
# DBL will work with whatever is in your configured database
dbl sandbox start
```

### Step 4: Make Your First Change

```bash
# 1. Start sandbox
dbl sandbox start

# 2. Make changes in your database
# Use psql, pgAdmin, DBeaver, or any SQL client:
psql myapp
# > ALTER TABLE users ADD COLUMN email VARCHAR(255);
# > \q

# 3. Check what changed
dbl diff

# 4. Commit the change
dbl commit -m "Add email column to users"

# 5. Apply changes
dbl sandbox apply
```

### Step 5: View History

```bash
# View layer history
dbl log

# View in compact format
dbl log --oneline
```

---

## Common Workflows

### Workflow 1: Feature Development

```bash
# Create feature branch
dbl branch feature/add-notifications

# Start sandbox
dbl sandbox start

# Make database changes
# ... use your SQL client ...

# Commit changes
dbl commit -m "Add notifications table"

# Apply
dbl sandbox apply

# Merge back to master
dbl checkout master
dbl merge feature/add-notifications
```

### Workflow 2: Experimentation

```bash
# Start sandbox
dbl sandbox start

# Try different approaches
# ... experiment freely ...

# Don't like the result?
dbl sandbox rollback

# Or commit if satisfied
dbl commit -m "Experimental feature"
dbl sandbox apply
```

### Workflow 3: Rebuilding Database

```bash
# Rebuild from scratch
dbl reset

# This replays all layers in order
# Useful for:
# - Switching branches
# - Verifying reproducibility
# - Fresh start
```

---

## Next Steps

Now that you have DBL running:

1. **Read the [Commands Reference](commands.md)** - Learn all available commands
2. **Study [Migration Patterns](patterns.md)** - Best practices for migrations
3. **Review [Best Practices](best-practices.md)** - Avoid common pitfalls
4. **Understand [Architecture](architecture.md)** - How DBL works internally

---

## Troubleshooting

### Can't connect to database

```bash
# Test connection manually first
psql -h localhost -p 5432 -U postgres -d myapp

# Check dbl.yaml configuration
# Verify credentials and host/port
```

### Permission denied errors

```bash
# Make sure dbl.py is executable
chmod +x dbl.py

# Or run with python explicitly
python dbl.py version
```

### "Sandbox already active" error

```bash
# Check status
dbl sandbox status

# Apply or rollback existing sandbox
dbl sandbox apply
# or
dbl sandbox rollback
```

### Layer files not found

```bash
# Verify .dbl directory exists
ls -la .dbl/

# Check manifest
cat .dbl/layers/manifest.json
```

---

## Getting Help

- 📖 [Full Documentation](index.md)
- 🐛 [Report Issues](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)
- 💬 [Discussions](https://github.com/alann-estrada-KSH/dbl-sandbox/discussions)

---

## What's Next?

Ready to dive deeper? Check out:

- [Command Reference](commands.md) - Complete command documentation
- [Migration Patterns](patterns.md) - Learn expand/backfill/contract
- [Best Practices](best-practices.md) - Professional tips and tricks
