# Commands Overview

DBL provides a comprehensive set of commands organized by functionality. This guide will help you understand what each command does and when to use it.

## Command Categories

### 🔧 Setup Commands
Commands for initializing and maintaining your DBL installation.

| Command | Description |
|---------|-------------|
| [`dbl init`](setup/init.md) | Initialize DBL in your project |
| [`dbl version`](setup/version.md) | Show DBL version information |
| [`dbl update`](setup/update.md) | Check and install DBL updates |

### 🏖️ Sandbox Commands
Safe testing environment for database changes.

| Command | Description |
|---------|-------------|
| [`dbl sandbox start`](sandbox/start.md) | Create an isolated sandbox database |
| [`dbl sandbox apply`](sandbox/apply.md) | Apply sandbox changes to main database |
| [`dbl sandbox rollback`](sandbox/rollback.md) | Discard all sandbox changes |
| [`dbl sandbox status`](sandbox/status.md) | Check sandbox state |

### 📝 Change Management
Commands for tracking and committing database changes.

| Command | Description |
|---------|-------------|
| [`dbl diff`](changes/diff.md) | Show changes in sandbox vs baseline |
| [`dbl commit`](changes/commit.md) | Save changes as a versioned layer |
| [`dbl reset`](changes/reset.md) | Rebuild database from layers |

### 🌿 Branching
Git-like branching for parallel development.

| Command | Description |
|---------|-------------|
| [`dbl branch`](branching/branch.md) | List, create, or delete branches |
| [`dbl checkout`](branching/checkout.md) | Switch to a different branch |
| [`dbl merge`](branching/merge.md) | Merge changes from another branch |
| [`dbl pull`](branching/pull.md) | Pull changes from another branch |
| [`dbl rebase`](branching/rebase.md) | Rebase current branch onto another |

### 📜 History & Inspection
View and validate your database history.

| Command | Description |
|---------|-------------|
| [`dbl log`](history/log.md) | View layer history |
| [`dbl rev-parse`](history/rev-parse.md) | Resolve references (HEAD, branches) |
| [`dbl validate`](history/validate.md) | Validate migration patterns |

## Quick Reference

### Common Workflows

**Basic workflow:**
```bash
dbl sandbox start      # Create sandbox
# Make changes in database...
dbl diff              # Review changes
dbl commit -m "msg"   # Save changes
dbl sandbox apply     # Apply to main DB
```

**Branch workflow:**
```bash
dbl branch feature-x  # Create branch
dbl checkout feature-x # Switch to branch
# Work on feature...
dbl checkout master   # Back to master
dbl merge feature-x   # Merge changes
```

**Review history:**
```bash
dbl log               # Full history
dbl log --oneline     # Compact view
dbl log -n 5          # Last 5 layers
```

## Command Syntax Patterns

DBL follows consistent patterns across commands:

- **Flags**: Options starting with `-` or `--`
- **Arguments**: Required or optional parameters
- **Subcommands**: Commands with actions (e.g., `sandbox start`)

### Examples:
```bash
dbl command [options] [arguments]
dbl command subcommand [options]
dbl command --flag value argument
```

## Getting Help

For detailed help on any command:
```bash
dbl help
dbl <command> --help
```

## Next Steps

- [Quick Start Tutorial](../getting-started/quick-start.md)
- [Best Practices](../guide/best-practices.md)
- [Configuration Guide](../guide/configuration.md)
