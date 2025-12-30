# dbl update

Check for and install DBL updates.

## Synopsis

```bash
dbl update              # Interactive mode
dbl update -y           # Auto-confirm
dbl update --yes        # Auto-confirm (long form)
```

## Description

Checks GitHub for the latest DBL release, compares with your current version, and optionally installs the update automatically via pip.

## Options

| Option | Description |
|--------|-------------|
| `-y, --yes` | Auto-confirm update installation without prompting |

## What It Does

1. **Checks dependencies** - Verifies PyYAML and other requirements
2. **Queries GitHub** - Fetches latest release information
3. **Compares versions** - Checks if update is available
4. **Shows release notes** - Displays what's new
5. **Installs update** - Updates via pip (if confirmed)

## Usage Examples

### Interactive Update

```bash
dbl update
```

**Output:**
```
Checking for updates...
Current version: 0.0.1-alpha
Latest version: 0.1.0-beta.1

============================================================
🎉 A new version is available!
============================================================

Release notes:
### Added
- New sandbox features
- Improved validation
- Better error messages

### Fixed
- Bug in diff command
- Connection issues with MySQL

Do you want to update to version 0.1.0-beta.1? (y/n): y

Installing update...
✓ Update successful!
DBL has been updated to version 0.1.0-beta.1

Please restart your terminal or run 'hash -r' to use the new version.
```

### Auto-confirm

```bash
dbl update -y
```

**Output:**
```
Checking for updates...
Current version: 0.0.1-alpha
Latest version: 0.1.0-beta.1

🎉 A new version is available!

Installing update...
✓ Update successful!
```

### Already Up to Date

```bash
dbl update
```

**Output:**
```
Checking for updates...
Current version: 0.1.0
Latest version: 0.1.0

✓ You are already using the latest version!
```

## Dependency Management

`dbl update` also checks and installs missing dependencies:

```bash
dbl update
```

**Output:**
```
⚠️  Missing required dependencies (PyYAML)
Do you want to install missing dependencies? (y/n): y

Installing missing dependencies...
✓ Dependencies installed successfully!

Checking for updates...
...
```

## How It Works

1. **Queries GitHub API**:
   ```
   https://api.github.com/repos/alann-estrada-KSH/dbl-sandbox/releases/latest
   ```

2. **Compares versions**:
   - Strips pre-release tags for comparison
   - `0.0.1-alpha` vs `0.1.0-beta` → compares `0.0.1` vs `0.1.0`

3. **Installs via pip**:
   ```bash
   pip install --upgrade git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
   ```

## CI/CD Integration

### Auto-update in CI

```yaml
# .github/workflows/update-dbl.yml
name: Update DBL
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Update DBL
        run: dbl update -y
```

### Pre-deployment Check

```bash
# Before deploying migrations
dbl update -y
dbl version
```

## Manual Update Alternative

If `dbl update` fails:

```bash
# Via pip
pip install --upgrade git+https://github.com/alann-estrada-KSH/dbl-sandbox.git

# Verify
dbl version
```

## Important Notes

!!! warning "Internet Required"
    This command requires an internet connection to check GitHub.

!!! tip "Restart Terminal"
    After updating, restart your terminal or run `hash -r` (Unix) / `refreshenv` (Windows) to ensure the new version is used.

!!! info "Pre-releases"
    DBL update includes alpha and beta versions. Check release notes before updating.

## Troubleshooting

### Connection Error

**Error:**
```
Could not connect to GitHub
Please check your internet connection.
```

**Solution:**
1. Check internet connection
2. Verify GitHub is accessible
3. Try manual update with pip

### Permission Error

**Error:**
```
Permission denied during installation
```

**Solution:**
```bash
# User install
pip install --user --upgrade git+https://github.com/...

# Or use sudo (Unix)
sudo dbl update -y
```

### Pip Not Found

**Error:**
```
pip: command not found
```

**Solution:**
```bash
python -m pip install --upgrade git+https://github.com/...
```

### No Releases Found

**Error:**
```
No releases found in repository
```

**Solution:**
- Wait for first release to be published
- Use manual git pull and install

## Version Comparison Logic

DBL compares versions intelligently:

```python
# Example comparisons
"0.0.1-alpha" < "0.1.0-beta"   # True
"0.1.0" == "0.1.0-alpha"       # True (ignores pre-release for comparison)
"1.0.0" > "0.9.9"              # True
```

## Release Information

Each update shows:

- **Version number**
- **Release date**
- **Release notes**:
  - Added features
  - Changed behavior
  - Fixed bugs
  - Breaking changes

## Automation Scripts

### Daily Update Check

```bash
#!/bin/bash
# check-updates.sh

OUTPUT=$(dbl update -y 2>&1)
if echo "$OUTPUT" | grep -q "Update successful"; then
    echo "DBL updated successfully"
    # Notify team
    curl -X POST webhook-url -d "DBL updated"
fi
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Ensure DBL is up to date
dbl update -y --quiet
```

## Configuration

Control update behavior in `dbl.yaml` (future):

```yaml
# Future feature
updates:
  auto_check: true         # Check on every command
  auto_install: false      # Don't auto-install
  channel: stable          # stable, beta, alpha
```

## See Also

- [`dbl version`](version.md) - Check current version
- [Changelog](../../changelog.md) - See what's new
- [Installation](../../getting-started/installation.md) - Install methods
