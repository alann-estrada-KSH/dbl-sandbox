# dbl version

Display DBL version information.

## Synopsis

```bash
dbl version
```

## Description

Shows the currently installed version of DBL along with the repository URL.

## Usage Example

```bash
dbl version
```

**Output:**
```
DBL (Database Layering) v0.0.1-alpha
Repository: https://github.com/alann-estrada-KSH/dbl-sandbox
```

## Version Format

DBL follows [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH-prerelease
```

### Examples

- `0.0.1-alpha` - Alpha pre-release
- `0.1.0-beta.1` - Beta pre-release  
- `0.1.0-rc.1` - Release candidate
- `1.0.0` - Stable release

### Pre-release Tags

| Tag | Stage | Stability |
|-----|-------|-----------|
| `alpha` | Early development | Unstable, frequent changes |
| `beta` | Feature complete | Stabilizing |
| `rc` | Release candidate | Final testing |
| (none) | Stable | Production ready |

## Checking for Updates

After checking your version, update to the latest:

```bash
# Check current version
dbl version

# Update to latest
dbl update
```

## Version History

View changelog:

```bash
# Online
# Visit: https://github.com/alann-estrada-KSH/dbl-sandbox/releases

# Or in docs
cat docs/changelog.md
```

## Use Cases

### Verify Installation

```bash
dbl version
# Confirms DBL is installed and accessible
```

### Bug Reports

Always include version when reporting issues:

```bash
$ dbl version
DBL (Database Layering) v0.0.1-alpha

# Include this in bug report
```

### CI/CD

Check version in pipelines:

```bash
# .github/workflows/test.yml
- name: Check DBL version
  run: dbl version
```

## See Also

- [`dbl update`](update.md) - Update to latest version
- [`dbl help`](../help.md) - Show available commands
- [Changelog](../../changelog.md) - Version history
