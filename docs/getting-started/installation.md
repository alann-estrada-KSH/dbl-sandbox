# Installation Guide

Complete guide to installing DBL on different platforms.

## Quick Install

```bash
# Recommended: Install via pip
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git

# Verify installation
dbl version
dbl help
```

---

## Prerequisites

### 1. Python

**Required**: Python 3.7 or higher (3.10+ recommended)

Check your Python version:
```bash
python --version
# or
python3 --version
```

**Install Python** if needed:

=== "Ubuntu/Debian"
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip
    ```

=== "macOS"
    ```bash
    # Using Homebrew
    brew install python3
    ```

=== "Windows"
    Download from [python.org](https://www.python.org/downloads/)
    
    ✅ Check "Add Python to PATH" during installation

### 2. Database CLI Tools

Install based on your database engine:

=== "PostgreSQL"
    **Required tools**: `psql`, `pg_dump`
    
    ```bash
    # Ubuntu/Debian
    sudo apt install postgresql-client
    
    # macOS
    brew install postgresql
    
    # Windows
    # Download from postgresql.org
    ```

=== "MySQL"
    **Required tools**: `mysql`, `mysqldump`
    
    ```bash
    # Ubuntu/Debian
    sudo apt install mysql-client
    
    # macOS
    brew install mysql-client
    
    # Windows
    # Download from mysql.com
    ```

### 3. pip (Python Package Manager)

Usually included with Python. Verify:
```bash
pip --version
```

If missing:
```bash
python -m ensurepip --upgrade
```

---

## Installation Methods

### Method 1: pip Install (Recommended)

Install directly from GitHub:

```bash
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```

✅ **Benefits:**
- Installs all dependencies automatically
- Creates global `dbl` command
- Easy to update with `dbl update`
- Works on all platforms

**Verify:**
```bash
dbl version
# Output: DBL (Database Layering) v0.0.1-alpha
```

### Method 2: Development Install

For development or contributing:

```bash
# Clone repository
git clone https://github.com/alann-estrada-KSH/dbl-sandbox.git
cd dbl-sandbox

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .
```

### Method 3: Manual Install

For systems without pip or custom setups:

#### Unix/Linux/macOS

```bash
# Clone repository
git clone https://github.com/alann-estrada-KSH/dbl-sandbox.git
cd dbl-sandbox

# Install dependencies
pip install PyYAML>=6.0

# Make executable
chmod +x dbl.py

# Create symlink
sudo ln -sf $(pwd)/dbl.py /usr/local/bin/dbl

# Test
dbl version
```

#### Windows

```powershell
# Clone repository
git clone https://github.com/alann-estrada-KSH/dbl-sandbox.git
cd dbl-sandbox

# Install dependencies
pip install PyYAML>=6.0

# Create launcher
mkdir $env:USERPROFILE\bin
@"
@echo off
python "$PWD\dbl.py" %*
"@ | Out-File -FilePath $env:USERPROFILE\bin\dbl.cmd -Encoding ASCII

# Add to PATH (run as Administrator)
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\bin",
    "User"
)
```

---

## Platform-Specific Instructions

### Docker Containers

If your database runs in Docker:

1. Install DBL on host system
2. Configure `container_name` in `dbl.yaml`:
   ```yaml
   container_name: my_postgres_container
   ```
3. DBL will automatically use `docker exec` for all database operations

**Example:**
```bash
dbl sandbox start
# Runs: docker exec my_postgres_container createdb mydb_sandbox
```

### WSL (Windows Subsystem for Linux)

Recommended for Windows users:

```bash
# Inside WSL
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git

# Use from Windows
wsl dbl help

# Or add WSL to PATH
```

### Virtual Environments

For isolated Python environments:

```bash
# Create virtualenv
python -m venv dbl-env

# Activate
source dbl-env/bin/activate  # Unix
.\dbl-env\Scripts\activate   # Windows

# Install
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git

# Use
dbl help
```

---

## Verification

After installation, verify everything works:

```bash
# Check version
dbl version

# Show help
dbl help

# Check dependencies
python -c "import yaml; print('✓ PyYAML installed')"

# Check database tools
psql --version    # PostgreSQL
mysql --version   # MySQL
```

---

## Updating DBL

### Automatic Update

```bash
dbl update         # Interactive
dbl update -y      # Auto-confirm
```

### Manual Update

```bash
pip install --upgrade git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```

---

## Uninstallation

### pip Install

```bash
pip uninstall dbl-sandbox
```

### Manual Install

```bash
# Remove symlink
sudo rm /usr/local/bin/dbl  # Unix
rm $env:USERPROFILE\bin\dbl.cmd  # Windows

# Remove directory
rm -rf dbl-sandbox/
```

---

## Troubleshooting

### Command Not Found

**Problem**: `dbl: command not found`

**Solutions:**
1. Reinstall with pip: `pip install git+https://github.com/...`
2. Check PATH: `echo $PATH` (Unix) or `echo $env:PATH` (Windows)
3. Run directly: `python -m dbl help`

### Missing Dependencies

**Problem**: `ImportError: No module named 'yaml'`

**Solution:**
```bash
pip install PyYAML>=6.0
# Or
dbl update  # Auto-installs dependencies
```

### Permission Errors

**Problem**: Permission denied during installation

**Solutions:**
1. User install: `pip install --user git+https://github.com/...`
2. Virtual environment (recommended)
3. Fix permissions: `sudo` (Unix) or run as Administrator (Windows)

### Database Tools Not Found

**Problem**: `psql: command not found`

**Solution**: Install database client tools (see [Prerequisites](#2-database-cli-tools))

---

## Next Steps

After installation:

1. 📖 [Quick Start Tutorial](quick-start.md)
2. 🎯 [Your First Migration](first-migration.md)
3. ⚙️ [Configuration Guide](../guide/configuration.md)
4. 💡 [Best Practices](../guide/best-practices.md)

---

## Additional Resources

- [GitHub Repository](https://github.com/alann-estrada-KSH/dbl-sandbox)
- [Issue Tracker](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)
- [Changelog](../changelog.md)
