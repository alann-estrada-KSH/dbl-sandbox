# dbl reset

Rebuild the database from scratch using committed layers.

## Synopsis

```bash
dbl reset                  # Reset current database
dbl reset --hard           # Force reset, ignore errors
dbl reset --to L005        # Reset to specific layer
```

## Description

Drops and recreates the database, then replays all committed layers in order. This is useful for:

- Testing that migrations are reproducible
- Recovering from manual errors
- Creating clean database from layer history
- Verifying layer sequence integrity

## Options

| Option | Description |
|--------|-------------|
| `--hard` | Force reset, continue even on errors |
| `--to L00X` | Stop at specific layer (don't apply later layers) |

## What It Does

1. **Drops database** - Removes existing database completely
2. **Recreates database** - Creates fresh empty database
3. **Replays layers** - Applies committed layers in order (L001, L002, ...)
4. **Updates state** - Marks layers as applied

## Usage Examples

### Basic Reset

```bash
dbl reset
```

**Output:**
```
⚠️  Warning: This will DROP and RECREATE the database 'myapp'
All data will be lost. Only committed layers will be replayed.

Are you sure? (y/n): y

Dropping database myapp...
✓ Database dropped

Creating database myapp...
✓ Database created

Replaying layers:
  → L001_initial_schema.sql
  → L002_add_users.sql
  → L003_add_posts.sql
  → L004_add_indexes.sql
  → L005_add_comments.sql
  
✓ Reset complete
✓ 5 layers applied
Database myapp is now at layer L005
```

### Reset to Specific Layer

```bash
dbl reset --to L003
```

**Output:**
```
Resetting to layer L003...

Dropping database myapp...
Creating database myapp...

Replaying layers:
  → L001_initial_schema.sql
  → L002_add_users.sql
  → L003_add_posts.sql
  
✓ Reset complete (stopped at L003)
Layers L004 and L005 were NOT applied
```

### Force Reset

```bash
dbl reset --hard
```

**Output:**
```
Force reset enabled (--hard)

Dropping database myapp...
Creating database myapp...

Replaying layers:
  → L001_initial_schema.sql ✓
  → L002_add_users.sql ✗ Error: column already exists
    (continuing due to --hard)
  → L003_add_posts.sql ✓
  
⚠️  Reset completed with 1 error
Check layer L002 for issues
```

## Complete Examples

### Test Migration Reproducibility

```bash
# Current state
$ dbl log
* L005 - Add comments
* L004 - Add indexes
* L003 - Add posts
* L002 - Add users
* L001 - Initial schema

# Reset to verify all layers replay correctly
$ dbl reset

Dropping database myapp...
Creating database myapp...
Replaying layers:
  → L001 ✓
  → L002 ✓
  → L003 ✓
  → L004 ✓
  → L005 ✓
  
✓ All layers replayed successfully

# Verify final state
$ psql -d myapp -c "\dt"
         List of relations
 Schema |      Name       | Type  
--------+-----------------+-------
 public | users           | table
 public | posts           | table
 public | comments        | table

# Schema matches expected state!
```

### Recover from Manual Changes

```bash
# Accidentally modified database directly
$ psql -d myapp
myapp=# DROP TABLE users;  -- Oops!

# Recover by resetting
$ dbl reset

Dropping database myapp...
Creating database myapp...
Replaying layers...
✓ Reset complete

# Database restored from layers
```

### Test Partial History

```bash
# Test up to specific point
$ dbl reset --to L003

Replaying layers:
  → L001_initial_schema
  → L002_add_users
  → L003_add_posts
  
Database now at L003

# App testing at this state
$ ./run-tests.sh

# Continue to next layer
$ dbl reset --to L004
```

### CI/CD Testing

```bash
# .github/workflows/test-migrations.yml
name: Test Migrations

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install DBL
        run: pip install git+https://github.com/...
      
      - name: Initialize
        run: dbl init
      
      - name: Test full replay
        run: dbl reset
      
      - name: Verify schema
        run: |
          dbl reset
          ./verify-schema.sh
      
      - name: Test incremental
        run: |
          for layer in L001 L002 L003; do
            dbl reset --to $layer
            ./test-at-layer.sh $layer
          done
```

## Safety Features

### Confirmation Prompt

By default, `reset` requires confirmation:

```bash
$ dbl reset
⚠️  Warning: This will DROP and RECREATE the database
All data will be lost.
Are you sure? (y/n): 
```

Skip with `--yes`:

```bash
dbl reset --yes  # No prompt
```

### Backup Recommendation

```bash
# Always backup before reset in production
$ pg_dump myapp > backup_$(date +%Y%m%d).sql
$ dbl reset
```

## What Gets Deleted

### Deleted:
- ❌ Entire database
- ❌ All tables
- ❌ All data
- ❌ All indexes, views, functions
- ❌ Manual changes not in layers

### Preserved:
- ✅ Layer files (`.dbl/layers/`)
- ✅ DBL metadata
- ✅ Branches
- ✅ Configuration

## Use Cases

### Development

```bash
# Clean slate for testing
dbl reset
```

### Testing

```bash
# Verify migrations work
dbl reset && ./run-tests.sh
```

### Production Deploy (Caution!)

```bash
# In staging first
dbl --config staging.yaml reset
./verify-schema.sh

# Then production (during maintenance)
pg_dump production > backup.sql
dbl --config production.yaml reset
```

### Debugging Layers

```bash
# Find which layer breaks
for i in {1..10}; do
    echo "Testing up to L00$i"
    dbl reset --to L00$i || break
done
```

## Performance

Reset speed depends on:
- **Number of layers**: More layers = slower
- **Layer complexity**: Complex SQL = slower
- **Database size**: Dropping large DB takes time

### Optimization

```bash
# Combine small layers
# Instead of:
L001: CREATE TABLE users
L002: CREATE TABLE posts
L003: CREATE TABLE comments

# Better:
L001: CREATE TABLE users; CREATE TABLE posts; CREATE TABLE comments;
```

## Error Handling

### Layer Fails to Apply

**Error:**
```
Replaying layers:
  → L001 ✓
  → L002 ✗ ERROR: relation "users" already exists
  
Reset failed at layer L002
```

**Solution:**
```bash
# Check layer SQL
cat .dbl/layers/L002_*.sql

# Fix the layer
# Then try again
dbl reset
```

### Database Connection Lost

**Error:**
```
Error: Lost connection during reset
Database may be in incomplete state
```

**Solution:**
```bash
# Database was dropped but not fully recreated
# Run reset again
dbl reset

# Or manually cleanup and retry
dropdb myapp
createdb myapp
dbl reset
```

### Permission Denied

**Error:**
```
Error: Permission denied to drop database
```

**Solution:**
```sql
-- Grant database creation/drop permissions
ALTER USER myuser WITH CREATEDB;

-- Or use superuser
sudo -u postgres psql
ALTER USER myuser WITH SUPERUSER;
```

## Important Notes

!!! danger "Data Loss"
    `dbl reset` **permanently deletes** all data in the database. Only use in development or after backing up.

!!! warning "Production Use"
    **Never** run `reset` on production without:
    1. Maintenance window
    2. Complete backup
    3. Tested in staging
    4. Team approval

!!! tip "Test Often"
    Reset frequently in development to ensure layers are reproducible.

## Comparison with Other Commands

| Command | Effect | Data Loss | Use When |
|---------|--------|-----------|----------|
| `reset` | Rebuild from layers | Yes | Testing, recovery |
| `sandbox apply` | Apply sandbox to main | No | Normal development |
| `sandbox rollback` | Delete sandbox | Sandbox only | Discard experiment |

## Advanced Usage

### Automated Testing

```bash
#!/bin/bash
# test-migrations.sh

LAYERS=$(ls .dbl/layers/ | grep -oE 'L[0-9]+' | sort -u)

for layer in $LAYERS; do
    echo "Testing up to $layer..."
    dbl reset --to $layer --yes
    
    if ! ./verify-schema.sh $layer; then
        echo "FAILED at $layer"
        exit 1
    fi
done

echo "All layers verified!"
```

### Reset with Seed Data

```bash
# After reset, load seed data
dbl reset --yes

# Load fixtures
psql -d myapp -f fixtures/seed_users.sql
psql -d myapp -f fixtures/seed_posts.sql
```

### Branch Switching

```bash
# Switch branches and reset to that branch's state
dbl checkout feature-xyz
dbl reset

# Now database matches feature-xyz layers
```

## Partial Reset (Future)

```bash
# Drop specific schemas only (future feature)
dbl reset --schema public

# Reset specific tables (future feature)
dbl reset --tables users,posts
```

## Recovery Strategies

### If Reset Fails

1. **Check logs**: Review error messages
2. **Verify layer SQL**: Ensure SQL is valid
3. **Test layer manually**: Run SQL directly
4. **Fix layer**: Edit layer file
5. **Retry reset**: Run `dbl reset` again

### If Database Corrupted

```bash
# Manual cleanup
dropdb myapp
createdb myapp

# Re-init DBL
dbl init

# Reset
dbl reset
```

## See Also

- [`dbl commit`](../changes/commit.md) - Create layers
- [`dbl log`](../history/log.md) - View layers
- [`dbl branch`](../branching/branch.md) - Manage branches
- [`dbl sandbox apply`](../sandbox/apply.md) - Apply sandbox changes
- [Best Practices](../../guide/best-practices.md) - Reset guidelines
