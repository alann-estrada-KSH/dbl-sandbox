# dbl sandbox status

Check the current sandbox state.

## Synopsis

```bash
dbl sandbox status
```

## Description

Displays information about the active sandbox, including uncommitted changes, committed layers pending apply, and sandbox database details.

## Usage Example

```bash
dbl sandbox status
```

**Output:**
```
Active Sandbox: myapp_sandbox
Base Database: myapp
Created: 2024-12-30 10:23:15
Branch: feature-auth

Uncommitted Changes:
  + 1 table added (user_sessions)
  + 2 columns added
  ~ 1 table modified

Committed Layers (not yet applied):
  L012 - Add user preferences (2024-12-30 10:45:22)
  L013 - Add session tracking (2024-12-30 11:02:05)

Status: Ready to apply (2 layers pending)

Next steps:
  - Review changes: dbl diff
  - Commit changes: dbl commit -m "message"
  - Apply to main: dbl sandbox apply
  - Discard sandbox: dbl sandbox rollback
```

## Output Sections

### Sandbox Information

```
Active Sandbox: myapp_sandbox
Base Database: myapp
Created: 2024-12-30 10:23:15
Branch: feature-auth
```

Shows:
- **Sandbox name**: Temporary database name
- **Base database**: Original database
- **Created timestamp**: When sandbox started
- **Branch**: Current DBL branch

### Uncommitted Changes

```
Uncommitted Changes:
  + 3 tables added
  + 5 columns added
  ~ 2 tables modified
  - 1 table dropped
```

Shows diff summary before commit.

### Committed Layers

```
Committed Layers (not yet applied):
  L015 - Add notifications (2024-12-30 14:32:11)
  L016 - Add indexes (2024-12-30 14:35:28)
```

Shows layers created in sandbox but not yet applied to main.

### Status Summary

```
Status: Ready to apply (2 layers pending)
```

Possible statuses:
- `Clean` - No changes
- `Uncommitted changes` - Changes not yet committed
- `Ready to apply` - Commits ready for main DB
- `Empty sandbox` - No changes made yet

## When No Sandbox

```bash
$ dbl sandbox status
No active sandbox

Your main database: myapp
Last applied layer: L014
Current branch: main

To start a sandbox: dbl sandbox start
```

## Complete Examples

### During Development

```bash
# Start sandbox
$ dbl sandbox start
✓ Sandbox: myapp_sandbox

# Check status (empty)
$ dbl sandbox status
Active Sandbox: myapp_sandbox
Status: Empty sandbox (no changes)

# Make changes
$ psql -d myapp_sandbox -c "CREATE TABLE comments (id SERIAL);"

# Check status (uncommitted)
$ dbl sandbox status
Active Sandbox: myapp_sandbox
Uncommitted Changes:
  + 1 table added (comments)
Status: Uncommitted changes

# Commit
$ dbl commit -m "Add comments"

# Check status (ready)
$ dbl sandbox status
Active Sandbox: myapp_sandbox
Committed Layers (not yet applied):
  L008 - Add comments (2024-12-30 15:12:33)
Status: Ready to apply (1 layer pending)

# Apply
$ dbl sandbox apply

# Check status (no sandbox)
$ dbl sandbox status
No active sandbox
```

### Multiple Commits

```bash
$ dbl sandbox status

Active Sandbox: blog_sandbox
Base Database: blog

Uncommitted Changes:
  + 1 table added (comments)
  ~ 1 table modified (posts)

Committed Layers (not yet applied):
  L020 - Add user profiles (2024-12-30 09:15:33)
  L021 - Add social login (2024-12-30 10:22:41)
  L022 - Add rate limiting (2024-12-30 11:45:19)

Status: Ready to apply (3 layers pending)
Uncommitted: 2 changes

Next steps:
  1. Commit remaining changes: dbl commit -m "Add comments"
  2. Apply all layers: dbl sandbox apply
  3. Or rollback everything: dbl sandbox rollback
```

## Use Cases

### Before Committing

```bash
# Check what needs to be committed
$ dbl sandbox status
Uncommitted Changes:
  + 3 tables added
  
$ dbl diff  # See details
$ dbl commit -m "Add feature X"
```

### Before Applying

```bash
# Review what will be applied
$ dbl sandbox status
Committed Layers (not yet applied):
  L015 - Add notifications
  L016 - Add webhooks
  
# Review each layer
$ cat .dbl/layers/L015_*.sql
$ cat .dbl/layers/L016_*.sql

# Apply
$ dbl sandbox apply
```

### CI/CD Checks

```bash
# Verify sandbox is clean before merging
$ dbl sandbox status
if [ "$?" -ne 0 ]; then
    echo "Sandbox has uncommitted changes!"
    exit 1
fi
```

### Team Coordination

```bash
# Share status with team
$ dbl sandbox status > sandbox-status.txt
$ cat sandbox-status.txt

Active Sandbox: myapp_sandbox
Committed Layers (not yet applied):
  L030 - Add payment system (3 hours ago)
  L031 - Add webhooks (1 hour ago)
  
# Team knows what's being worked on
```

## Status Indicators

### Clean State

```
Status: Clean
```
- No uncommitted changes
- No pending layers
- Safe to close sandbox or switch branches

### Uncommitted Work

```
Status: Uncommitted changes
```
- Changes not yet committed
- Should commit or discard before applying

### Ready to Apply

```
Status: Ready to apply (N layers pending)
```
- Has committed layers
- Can apply to main database
- May also have uncommitted changes

### Mixed State

```
Status: Ready to apply (2 layers pending)
Uncommitted: 1 table added
```
- Has both committed and uncommitted changes
- Can apply committed layers
- Uncommitted changes stay in sandbox or get discarded

## Integration Examples

### Git Hook

```bash
#!/bin/bash
# .git/hooks/pre-push

# Ensure sandbox is applied before push
STATUS=$(dbl sandbox status)

if echo "$STATUS" | grep -q "Active Sandbox"; then
    echo "Error: Active sandbox detected"
    echo "Apply or rollback sandbox before pushing"
    exit 1
fi
```

### Monitoring Script

```bash
#!/bin/bash
# monitor-sandbox.sh

while true; do
    clear
    echo "=== Sandbox Status ==="
    dbl sandbox status
    echo ""
    echo "Press Ctrl+C to exit"
    sleep 5
done
```

### Status API

```python
# get_sandbox_status.py
import subprocess
import json

result = subprocess.run(['dbl', 'sandbox', 'status'], 
                       capture_output=True, text=True)

if result.returncode == 0:
    print(f"Status: {result.stdout}")
else:
    print("No active sandbox")
```

## Output Formats

### Compact Format

```bash
$ dbl sandbox status --compact
myapp_sandbox: 2 uncommitted, 3 pending
```

### JSON Format (future)

```bash
$ dbl sandbox status --json
{
  "sandbox": "myapp_sandbox",
  "base": "myapp",
  "created": "2024-12-30T10:23:15Z",
  "branch": "feature-auth",
  "uncommitted": 2,
  "pending_layers": [
    {"id": "L012", "message": "Add user preferences"},
    {"id": "L013", "message": "Add session tracking"}
  ],
  "status": "ready"
}
```

## Error Messages

### No Database Connection

```
Error: Cannot connect to database
Check your database configuration in dbl.yaml
```

### Sandbox Database Missing

```
Warning: Sandbox metadata exists but database not found
The sandbox may have been deleted manually.
Run: dbl sandbox rollback
```

### Corrupted State

```
Error: Sandbox state appears corrupted
Metadata: myapp_sandbox
Database: Not found

To recover:
  1. dbl sandbox rollback (clear state)
  2. dbl sandbox start (start fresh)
```

## Performance

Status check is fast:
- Queries database metadata only
- No table scanning
- Caches results briefly

```bash
$ time dbl sandbox status
# ~0.1s for most databases
```

## Important Notes

!!! info "Read-Only"
    Status command only reads state, never modifies anything.

!!! tip "Check Often"
    Run `dbl sandbox status` frequently during development to track progress.

!!! warning "Metadata vs Reality"
    Status shows DBL's view. Always verify with database tools if something seems wrong.

## Aliases and Shortcuts

```bash
# Short form (if implemented)
dbl status
dbl s

# Watch mode
watch -n 2 dbl sandbox status
```

## Related Workflows

### Development Workflow

```bash
# 1. Check initial state
dbl sandbox status

# 2. Make changes
# ... edit database ...

# 3. Check progress
dbl sandbox status

# 4. Commit when ready
dbl commit -m "Changes"

# 5. Verify commits
dbl sandbox status

# 6. Apply
dbl sandbox apply
```

### Review Workflow

```bash
# Before code review
dbl sandbox status > status.txt
dbl diff > changes.sql

# Share with team
git add status.txt changes.sql
git commit -m "Database changes for review"
```

## See Also

- [`dbl diff`](../changes/diff.md) - See detailed changes
- [`dbl commit`](../changes/commit.md) - Commit changes
- [`dbl sandbox apply`](apply.md) - Apply sandbox
- [`dbl sandbox rollback`](rollback.md) - Discard sandbox
- [`dbl log`](../history/log.md) - View layer history
