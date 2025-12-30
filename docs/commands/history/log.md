# dbl log

Display the history of committed layers.

## Synopsis

```bash
dbl log                    # Show all layers
dbl log -n 10              # Show last 10 layers
dbl log --oneline          # Compact format
dbl log L003..L007         # Show range
dbl log --branch main      # Show specific branch
```

## Description

Shows the chronological history of database changes (layers) with commit messages, timestamps, authors, and layer IDs.

## Options

| Option | Description |
|--------|-------------|
| `-n, --max-count N` | Limit output to N entries |
| `--oneline` | Show each layer on a single line |
| `--branch NAME` | Show layers for specific branch |
| `--all` | Show layers from all branches |
| `L001..L005` | Show specific range of layers |

## Usage Examples

### Basic Log

```bash
dbl log
```

**Output:**
```
* L005 - Add comments feature
  Date: 2024-12-30 14:32:11
  Branch: main
  
  Added comments table with foreign keys to posts and users.
  Includes indexes for common queries.

* L004 - Add search indexes
  Date: 2024-12-30 12:15:33
  Branch: main
  
  Added GIN indexes for full-text search on posts and users.

* L003 - Add posts table
  Date: 2024-12-29 16:45:22
  Branch: main
  
  Created posts table with author reference.

* L002 - Add users table
  Date: 2024-12-29 10:20:15
  Branch: main
  
  Basic user table with authentication fields.

* L001 - Initial schema
  Date: 2024-12-28 09:00:00
  Branch: main
  
  Database initialization.
```

### Compact Format

```bash
dbl log --oneline
```

**Output:**
```
L005 Add comments feature
L004 Add search indexes
L003 Add posts table
L002 Add users table
L001 Initial schema
```

### Last N Entries

```bash
dbl log -n 3
```

**Output:**
```
* L005 - Add comments feature (2024-12-30 14:32:11)
* L004 - Add search indexes (2024-12-30 12:15:33)
* L003 - Add posts table (2024-12-29 16:45:22)
```

### Specific Range

```bash
dbl log L002..L004
```

**Output:**
```
* L004 - Add search indexes
* L003 - Add posts table
* L002 - Add users table
```

## Output Format

### Full Format

```
* L005 - Add comments feature
  Date: 2024-12-30 14:32:11
  Author: john@example.com
  Branch: main
  Files: .dbl/layers/L005_add_comments_feature.sql
  
  Added comments table with foreign keys to posts and users.
  Includes indexes for common queries.
  
  Tables added: comments
  Indexes added: 2
```

### Oneline Format

```
L005 Add comments feature
```

### Graph Format (future)

```bash
dbl log --graph
```

**Output:**
```
* L008 - Merge feature-auth (main)
|\
| * L007 - Add session tracking (feature-auth)
| * L006 - Add auth tokens (feature-auth)
|/
* L005 - Add comments (main)
* L004 - Add indexes (main)
```

## Complete Examples

### Review Recent Work

```bash
# What did we do today?
$ dbl log -n 5

* L015 - Add webhooks system
  Date: 2024-12-30 15:45:00
  
* L014 - Add notification preferences
  Date: 2024-12-30 14:20:33
  
* L013 - Add email templates
  Date: 2024-12-30 11:32:15
  
* L012 - Add user settings
  Date: 2024-12-30 09:15:42
  
* L011 - Add admin dashboard
  Date: 2024-12-30 08:00:00
```

### Find Specific Change

```bash
# Search for layers mentioning "index"
$ dbl log --oneline | grep -i index

L014 Add indexes for performance
L008 Add search indexes
L003 Add initial indexes
```

### Compare Branches

```bash
# Main branch
$ dbl log --branch main -n 3
* L010 - Add admin features (main)
* L009 - Add user profiles (main)
* L008 - Add posts (main)

# Feature branch
$ dbl log --branch feature-auth -n 3
* L012 - Add 2FA (feature-auth)
* L011 - Add OAuth (feature-auth)
* L008 - Add posts (main)  ← Common ancestor
```

### Layer Details

```bash
# See what changed in L005
$ dbl log L005..L005

* L005 - Add comments feature
  Date: 2024-12-30 14:32:11
  Files: .dbl/layers/L005_add_comments_feature.sql
  
  Added comments table with foreign keys to posts and users.

# View the actual SQL
$ cat .dbl/layers/L005_add_comments_feature.sql
```

## Use Cases

### Code Review

```bash
# Review changes in PR
$ dbl log -n 5 --oneline > changes.txt
$ cat changes.txt

L015 Add webhooks
L014 Add notifications
L013 Add email templates

# Share with team
```

### Debugging

```bash
# When did we add that table?
$ dbl log --oneline | grep comments

L005 Add comments feature

# What was in that layer?
$ cat .dbl/layers/L005_*
```

### Documentation

```bash
# Generate changelog
$ dbl log --oneline > CHANGELOG.txt

# Or with dates
$ dbl log -n 20 | grep -E "^\* L" > release-notes.txt
```

### Release Planning

```bash
# What's in this release?
$ dbl log v1.0..v1.1

* L025 - Add payment processing
* L024 - Add subscription tiers
* L023 - Add billing history
```

## Integration Examples

### Git Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Verify layer history is clean
if ! dbl log -n 1; then
    echo "Error: DBL history corrupted"
    exit 1
fi
```

### CI/CD

```yaml
# .github/workflows/changelog.yml
name: Generate Changelog

on:
  release:
    types: [published]

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate changelog
        run: |
          dbl log --oneline > CHANGELOG.md
          git add CHANGELOG.md
          git commit -m "Update changelog"
          git push
```

### Monitoring Script

```python
# monitor_layers.py
import subprocess
import json

def get_layer_count():
    result = subprocess.run(['dbl', 'log', '--oneline'], 
                           capture_output=True, text=True)
    return len(result.stdout.strip().split('\n'))

count = get_layer_count()
print(f"Total layers: {count}")

# Alert if too many layers
if count > 100:
    print("Warning: Consider squashing old layers")
```

## Output Filtering

### By Date

```bash
# Layers from last week (manual filtering)
dbl log | grep "2024-12-2[3-9]"
```

### By Author

```bash
# Layers by specific author (future)
dbl log --author john@example.com
```

### By Message

```bash
# Find layers with specific keyword
dbl log --oneline | grep -i "auth"

L012 Add authentication
L007 Add auth tokens
L003 Add user auth
```

## Performance

Log is fast for most repositories:

- **< 100 layers**: Instant
- **100-1000 layers**: < 1s
- **> 1000 layers**: Consider pagination

```bash
# For large repos, use pagination
dbl log -n 50  # Show 50 at a time
```

## Error Handling

### No Layers

```bash
$ dbl log
No layers found

Initialize with: dbl init
```

### Corrupted History

```bash
$ dbl log
Error: Layer history corrupted
Missing layer L003

Check .dbl/layers/ directory
```

### Missing Branch

```bash
$ dbl log --branch nonexistent
Error: Branch 'nonexistent' not found

Available branches:
  - main
  - feature-auth
```

## Important Notes

!!! tip "Oneline for Scripts"
    Use `--oneline` in scripts for easier parsing.

!!! info "Chronological Order"
    Layers are always shown newest first (reverse chronological).

!!! warning "All Branches"
    By default, shows current branch only. Use `--all` for all branches.

## Advanced Usage

### Custom Format (future)

```bash
# Custom output format
dbl log --format "%id - %msg (%date)"

L005 - Add comments (2024-12-30)
L004 - Add indexes (2024-12-30)
```

### Export History

```bash
# Export to JSON
dbl log --json > history.json

# Export to CSV
dbl log --csv > history.csv
```

### Statistics

```bash
# Layer count
dbl log --oneline | wc -l

# Layers per day
dbl log | grep "Date:" | cut -d' ' -f3 | uniq -c

# Most active contributors
dbl log | grep "Author:" | sort | uniq -c | sort -nr
```

## Comparison with Git

DBL `log` is similar to `git log`:

| Git | DBL | Purpose |
|-----|-----|---------|
| `git log` | `dbl log` | Show history |
| `git log --oneline` | `dbl log --oneline` | Compact view |
| `git log -n 5` | `dbl log -n 5` | Limit output |
| `git log branch` | `dbl log --branch branch` | Branch history |

## Aliases

```bash
# Add to shell config
alias dlog='dbl log --oneline'
alias dlast='dbl log -n 1'
```

## Layer Files

Each layer in the log corresponds to a file:

```bash
# Layer L005 in log
$ dbl log --oneline | grep L005
L005 Add comments feature

# Corresponds to file
$ ls .dbl/layers/L005_*
.dbl/layers/L005_add_comments_feature.sql
```

## See Also

- [`dbl commit`](../changes/commit.md) - Create layers
- [`dbl diff`](../changes/diff.md) - Show uncommitted changes
- [`dbl branch`](../branching/branch.md) - View branches
- [`dbl reset`](reset.md) - Replay layers
- [Architecture: Layers](../../architecture/layers.md) - How layers work
