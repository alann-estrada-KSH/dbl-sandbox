# dbl validate

Validate layer integrity and database schema consistency.

## Synopsis

```bash
dbl validate                    # Validate everything
dbl validate --layers           # Validate layers only
dbl validate --schema           # Validate schema only
dbl validate --fix              # Auto-fix issues
```

## Description

Checks for:
- Layer file integrity
- SQL syntax errors
- Schema consistency
- State file corruption
- Missing dependencies

## Options

| Option | Description |
|--------|-------------|
| `--layers` | Validate layer files only |
| `--schema` | Validate database schema only |
| `--fix` | Automatically fix detected issues |
| `--strict` | Fail on warnings (not just errors) |

## Usage Examples

### Full Validation

```bash
dbl validate
```

**Output:**
```
Validating DBL repository...

✓ Configuration (dbl.yaml)
✓ State file (.dbl/state.json)
✓ Layer files (15 layers)
✓ SQL syntax
✓ Database schema
✓ Layer sequence

All checks passed!
Repository is healthy.
```

### Layer Validation

```bash
dbl validate --layers
```

**Output:**
```
Validating layers...

✓ L001_initial_schema.sql - OK
✓ L002_add_users.sql - OK
✓ L003_add_posts.sql - OK
⚠ L004_add_indexes.sql - Warning: Index already exists
✓ L005_add_comments.sql - OK

5 layers checked, 1 warning
```

### Schema Validation

```bash
dbl validate --schema
```

**Output:**
```
Validating database schema...

✓ Tables match expected state
✓ Indexes are correct
✓ Foreign keys intact
✓ Constraints valid

Schema is consistent with layers.
```

### With Auto-fix

```bash
dbl validate --fix
```

**Output:**
```
Validating with auto-fix...

⚠ Issue: Missing layer index in state file
  → Fixed: Regenerated state index

⚠ Issue: Duplicate layer L005
  → Fixed: Renamed to L006

✓ All issues resolved
```

## What It Checks

### 1. Configuration

```yaml
# Checks dbl.yaml
✓ File exists
✓ Valid YAML syntax
✓ Required fields present
✓ Database connection valid
```

### 2. State Files

```
✓ .dbl/state.json exists
✓ Valid JSON
✓ Branch information correct
✓ Layer tracking accurate
```

### 3. Layer Files

```
✓ Sequential numbering (L001, L002, L003...)
✓ No gaps in sequence
✓ Valid SQL syntax
✓ File naming convention
✓ Commit messages present
```

### 4. SQL Syntax

```sql
-- Validates SQL in each layer
✓ CREATE TABLE syntax
✓ ALTER TABLE syntax
✓ INDEX definitions
✓ Constraint syntax
```

### 5. Database Schema

```
✓ Current schema matches layers
✓ No manual changes detected
✓ All tables accounted for
✓ Indexes match definitions
```

### 6. Dependencies

```
✓ Database engine available
✓ Required Python packages
✓ Database credentials valid
```

## Complete Examples

### Pre-deployment Check

```bash
# Before deploying to production
$ dbl validate --strict

Validating DBL repository (strict mode)...

✓ Configuration
✓ State files
✓ Layer files (20 layers)
✓ SQL syntax
⚠ Warning: Layer L015 has no rollback
✗ Error: Strict mode - warnings treated as errors

Validation failed.
Fix warnings before deploying.
```

### Find Corrupted Layers

```bash
$ dbl validate --layers

Validating layers...

✓ L001_initial_schema.sql
✓ L002_add_users.sql
✗ L003_add_posts.sql - Syntax error at line 15
✓ L004_add_indexes.sql

Layer L003 has errors. Check SQL syntax.
```

### Verify After Reset

```bash
# Reset database
$ dbl reset

# Validate result
$ dbl validate --schema

✓ Schema matches layer L015
✓ All tables present
✓ No extra tables found

Database is in expected state.
```

## Issue Detection

### Common Issues

#### Missing Layers

```
✗ Layer L003 missing
  Expected: L001, L002, L003, L004
  Found: L001, L002, L004
```

**Fix:**
```bash
# Renumber layers
mv .dbl/layers/L004_*.sql .dbl/layers/L003_*.sql
dbl validate --fix
```

#### SQL Syntax Error

```
✗ L005_add_comments.sql:12
  ERROR: syntax error at or near "TALBE"
  CREATE TALBE comments (...)
         ^
```

**Fix:**
```bash
# Edit layer file
nano .dbl/layers/L005_add_comments.sql
# Fix: TALBE → TABLE
dbl validate
```

#### Schema Mismatch

```
⚠ Database has extra table 'temp_data'
  Not defined in any layer.
```

**Fix:**
```bash
# Option 1: Commit the change
dbl sandbox start
# Make matching changes
dbl commit -m "Add temp_data table"

# Option 2: Drop manual change
psql -d myapp -c "DROP TABLE temp_data;"
```

#### Duplicate Layer ID

```
✗ Duplicate layer ID: L008
  Files: L008_add_auth.sql, L008_add_profiles.sql
```

**Fix:**
```bash
# Renumber one
mv .dbl/layers/L008_add_profiles.sql \
   .dbl/layers/L009_add_profiles.sql
dbl validate --fix
```

## CI/CD Integration

### Pre-merge Validation

```yaml
# .github/workflows/validate.yml
name: Validate DBL

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install DBL
        run: pip install git+https://github.com/...
      
      - name: Validate
        run: dbl validate --strict
      
      - name: Validate SQL
        run: dbl validate --layers
```

### Pre-deployment Gate

```bash
#!/bin/bash
# deploy.sh

# Validate before deploying
if ! dbl validate --strict; then
    echo "Validation failed. Aborting deployment."
    exit 1
fi

# Deploy
dbl --config production.yaml sandbox apply
```

### Scheduled Checks

```yaml
# .github/workflows/nightly-validation.yml
name: Nightly Validation

on:
  schedule:
    - cron: '0 0 * * *'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Full validation
        run: dbl validate --strict
```

## Validation Levels

### Basic (default)

```bash
dbl validate
# Checks: layers, state, configuration
# Fails on: errors only
```

### Strict

```bash
dbl validate --strict
# Checks: layers, state, configuration, best practices
# Fails on: errors AND warnings
```

### Quick

```bash
dbl validate --quick
# Checks: basic file integrity
# Skips: SQL parsing, schema checks
```

## Auto-fix Capabilities

### What Can Be Fixed

- ✅ State file regeneration
- ✅ Layer renumbering
- ✅ Metadata updates
- ✅ File naming standardization

### What Requires Manual Fix

- ❌ SQL syntax errors
- ❌ Schema conflicts
- ❌ Missing database
- ❌ Logic errors in layers

## Performance

Validation speed:

- **Layers only**: ~0.1s per layer
- **Schema check**: ~0.5s per database
- **Full validation**: ~2-5s typical

```bash
$ time dbl validate
real    0m2.341s
```

## Error Codes

DBL validate returns exit codes:

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Warnings found (non-strict) |
| 2 | Errors found |
| 3 | Critical failure |

```bash
# Use in scripts
if dbl validate; then
    echo "Valid"
else
    echo "Invalid (code: $?)"
fi
```

## Reporting

### Summary Report

```bash
$ dbl validate

Summary:
  Layers: 15 checked, 0 errors, 1 warning
  Schema: Consistent
  State: Valid
  Config: Valid

Overall: PASS (with warnings)
```

### Detailed Report

```bash
$ dbl validate --verbose

Configuration Check:
  ✓ dbl.yaml found
  ✓ Database: myapp
  ✓ Engine: postgres
  ✓ Connection: OK

State Check:
  ✓ .dbl/state.json valid
  ✓ Current branch: main
  ✓ Last layer: L015

Layer Check:
  ✓ L001_initial_schema.sql (345 bytes)
  ✓ L002_add_users.sql (521 bytes)
  ...
  ✓ L015_add_webhooks.sql (892 bytes)

Schema Check:
  ✓ Tables: 12 expected, 12 found
  ✓ Indexes: 24 expected, 24 found
  ✓ Constraints: 8 expected, 8 found

All checks passed!
```

### JSON Output

```bash
$ dbl validate --json
{
  "status": "pass",
  "errors": 0,
  "warnings": 1,
  "checks": {
    "config": "pass",
    "state": "pass",
    "layers": "pass",
    "schema": "pass"
  },
  "warnings": [
    {
      "layer": "L004",
      "message": "Index already exists"
    }
  ]
}
```

## Important Notes

!!! tip "Validate Often"
    Run `dbl validate` frequently during development to catch issues early.

!!! warning "Strict in CI"
    Always use `--strict` in CI/CD pipelines to enforce quality.

!!! info "Read-only"
    Validation without `--fix` never modifies anything.

## Best Practices

1. **Validate before commit**:
   ```bash
   dbl validate && dbl commit -m "Changes"
   ```

2. **Validate before apply**:
   ```bash
   dbl validate --strict && dbl sandbox apply
   ```

3. **Regular checks**:
   ```bash
   # Add to daily routine
   dbl validate
   ```

4. **CI integration**:
   ```yaml
   # Always validate in CI
   - run: dbl validate --strict
   ```

## Troubleshooting

### False Positives

Some warnings may be expected:

```bash
# Suppress specific warnings
dbl validate --ignore-warning index-exists
```

### Validation Hangs

If validation hangs on schema check:

```bash
# Check database connection
psql -d myapp -c "SELECT 1;"

# Skip schema check if needed
dbl validate --layers
```

### Permission Issues

```bash
# Validate without database access
dbl validate --no-db
```

## See Also

- [`dbl reset`](reset.md) - Rebuild and test layers
- [`dbl commit`](../changes/commit.md) - Create validated layers
- [`dbl log`](log.md) - Review layer history
- [Best Practices](../../guide/best-practices.md) - Validation guidelines
