# dbl sandbox rollback

Discard all sandbox changes and delete the sandbox.

## Synopsis

```bash
dbl sandbox rollback
```

## Description

Deletes the sandbox database and all uncommitted changes, leaving your main database untouched. This is a safe way to discard experimental changes.

## What It Does

1. **Drops sandbox database** - Removes `{database}_sandbox`
2. **Clears metadata** - Deletes sandbox tracking files
3. **Resets state** - Marks no sandbox as active

## Usage Example

```bash
# Create sandbox and make changes
dbl sandbox start
psql -d myapp_sandbox -c "CREATE TABLE test (id INT);"

# Decide you don't want these changes
dbl sandbox rollback
```

**Output:**
```
Rolling back sandbox changes...
✓ Dropped sandbox database (myapp_sandbox)
✓ Cleared sandbox metadata
✓ No active sandbox

Your main database (myapp) remains unchanged.
```

## When to Use

### ✅ Use Rollback When:

- **Experimenting**: Tried something that didn't work
- **Testing**: Wanted to see the effect of changes
- **Mistakes**: Made errors you want to discard
- **Changing direction**: Decided on a different approach

### ❌ Don't Use When:

- **Want to keep changes**: Use `dbl sandbox apply` instead
- **Partially done**: Commit what you have first
- **Already applied**: Can't rollback after `sandbox apply`

## Complete Examples

### Experiment Gone Wrong

```bash
# 1. Start experimenting
$ dbl sandbox start
✓ Sandbox: myapp_sandbox

# 2. Try something
$ psql -d myapp_sandbox
myapp_sandbox=# DROP TABLE users CASCADE;
DROP TABLE
myapp_sandbox=# -- Oops, didn't mean to do that!

# 3. Rollback
$ dbl sandbox rollback
✓ Sandbox dropped
✓ Main database unchanged

# 4. Start fresh
$ dbl sandbox start
✓ New clean sandbox created
```

### Multiple Rollbacks

```bash
# Try approach 1
$ dbl sandbox start
# Make changes...
$ dbl diff
# Don't like it
$ dbl sandbox rollback

# Try approach 2
$ dbl sandbox start
# Make different changes...
$ dbl diff
# Don't like this either
$ dbl sandbox rollback

# Try approach 3
$ dbl sandbox start
# Finally got it right!
$ dbl commit -m "Final approach"
$ dbl sandbox apply
```

### Save Some, Discard Rest

```bash
# Make several changes
$ dbl sandbox start

# Change 1: Good
$ psql -d myapp_sandbox -c "CREATE TABLE comments (...);"
$ dbl commit -m "Add comments table"

# Change 2: Good
$ psql -d myapp_sandbox -c "CREATE INDEX idx_comments_post (...);"
$ dbl commit -m "Add comments index"

# Change 3: Bad idea
$ psql -d myapp_sandbox -c "DROP TABLE users;"
# Don't commit this!

# Rollback to discard uncommitted changes
$ dbl sandbox rollback

# Previously committed changes are safe in layers
# Can apply them later in a new sandbox
```

## What Gets Deleted

### Deleted:
- ❌ Sandbox database (`myapp_sandbox`)
- ❌ Uncommitted changes
- ❌ Sandbox metadata (`.dbl/sandbox.json`)

### Preserved:
- ✅ Main database (untouched)
- ✅ Committed layers (`.dbl/layers/`)
- ✅ Branch history
- ✅ All previous work

## Comparison with Apply

| Aspect | Rollback | Apply |
|--------|----------|-------|
| Sandbox DB | Deleted | Deleted |
| Changes | Discarded | Applied to main |
| Main DB | Unchanged | Updated |
| Use when | Don't want changes | Want changes |

## Safety Features

### Confirmation Prompt

By default, DBL may prompt before rolling back:

```bash
$ dbl sandbox rollback
Warning: This will discard all sandbox changes.
Are you sure? (y/n): y
✓ Sandbox rolled back
```

### No Undo

!!! danger "Permanent Deletion"
    After rollback, sandbox changes are **permanently lost**. There is no undo.

!!! tip "Commit First"
    If unsure, commit changes before rolling back. You can always create a new sandbox and not apply those commits.

## Workflow Patterns

### Quick Experiment

```bash
# Quick test
dbl sandbox start
# Test something...
dbl sandbox rollback  # Discard
```

### Iterative Development

```bash
# Loop until satisfied
while true; do
    dbl sandbox start
    # Make changes...
    dbl diff
    read -p "Keep? (y/n): " keep
    if [ "$keep" = "y" ]; then
        dbl commit -m "Changes"
        dbl sandbox apply
        break
    else
        dbl sandbox rollback
    fi
done
```

### Feature Exploration

```bash
# Try feature in sandbox
dbl branch feature-xyz
dbl checkout feature-xyz
dbl sandbox start

# Explore implementation
# ... make changes ...

# Not ready yet
dbl sandbox rollback

# Later, try again
dbl sandbox start
# ... better implementation ...
dbl commit -m "Feature XYZ"
dbl sandbox apply
```

## Error Handling

### No Active Sandbox

**Error:**
```
Error: No active sandbox found
```

**Solution:**
- Nothing to rollback
- Already clean state

### Sandbox Already Gone

**Error:**
```
Error: Sandbox database not found
```

**Solution:**
```bash
# Clean up metadata
rm .dbl/sandbox.json
```

### Permission Issues

**Error:**
```
Error: Permission denied to drop database
```

**Solution:**
```sql
-- Grant drop permission
ALTER USER myuser WITH CREATEDB;
```

## Important Notes

!!! warning "Uncommitted Changes Lost"
    Only **uncommitted** changes are lost. Committed layers are safe.

!!! info "Main DB Safe"
    Your main database is never affected by rollback.

!!! tip "No Cleanup Needed"
    DBL automatically cleans up all sandbox artifacts.

## After Rollback

### Check Status

```bash
$ dbl sandbox status
No active sandbox
```

### Start Fresh

```bash
$ dbl sandbox start
✓ New sandbox created
```

### Review Committed Layers

```bash
# Committed changes are safe
$ dbl log
* L005 - Add comments feature
* L004 - Add indexes
...
```

## CI/CD Integration

### Auto-rollback on Failure

```yaml
# .github/workflows/test.yml
name: Test Migrations

on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test migrations
        run: |
          dbl sandbox start
          dbl reset || dbl sandbox rollback
          
      - name: Cleanup on failure
        if: failure()
        run: dbl sandbox rollback
```

### Cleanup Script

```bash
#!/bin/bash
# cleanup.sh

# Always rollback at end
trap "dbl sandbox rollback 2>/dev/null" EXIT

# Run tests
dbl sandbox start
./run-migrations.sh
./run-tests.sh
```

## Comparison with Reset

| Command | Purpose | Scope |
|---------|---------|-------|
| `rollback` | Discard sandbox | Sandbox only |
| `reset` | Rebuild from layers | Main database |

```bash
# Rollback: discard sandbox changes
dbl sandbox rollback

# Reset: rebuild main DB from layers
dbl reset
```

## Best Practices

1. **Rollback freely** - Don't be afraid to discard experiments
2. **Commit good parts** - Save what works before rolling back rest
3. **Use branches** - Isolate experiments in feature branches
4. **Document why** - Note why you rolled back for team awareness

## Next Steps

After rollback:

- [Start new sandbox](start.md) and try again
- [Review committed layers](../history/log.md)
- [Switch branches](../branching/checkout.md) to try different approach
- [Reset database](../changes/reset.md) to test layer replay

## See Also

- [`dbl sandbox start`](start.md) - Create sandbox
- [`dbl sandbox apply`](apply.md) - Apply changes
- [`dbl sandbox status`](status.md) - Check sandbox state
- [`dbl commit`](../changes/commit.md) - Save changes before rollback
