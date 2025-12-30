# Troubleshooting Guide

Common DBL issues and solutions.

## Connection Issues

### Cannot Connect to Database

**Symptoms:**
```
Error: Could not connect to database 'myapp'
Connection refused
```

**Solutions:**

1. **Check database is running:**
   ```bash
   # PostgreSQL
   pg_isready
   sudo systemctl status postgresql
   
   # MySQL
   mysqladmin ping
   sudo systemctl status mysql
   ```

2. **Verify connection details:**
   ```yaml
   # dbl.yaml
   database:
     name: myapp
     host: localhost    # Correct host?
     port: 5432        # Correct port?
     user: dbuser      # User exists?
   ```

3. **Test connection manually:**
   ```bash
   # PostgreSQL
   psql -h localhost -U dbuser -d myapp
   
   # MySQL
   mysql -h localhost -u dbuser -p myapp
   ```

4. **Check firewall:**
   ```bash
   # PostgreSQL
   sudo ufw allow 5432/tcp
   
   # MySQL
   sudo ufw allow 3306/tcp
   ```

### Permission Denied

**Symptoms:**
```
Error: Permission denied for database 'myapp'
FATAL: role "dbuser" does not exist
```

**Solutions:**

1. **Create user:**
   ```sql
   -- PostgreSQL
   CREATE USER dbuser WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE myapp TO dbuser;
   
   -- MySQL
   CREATE USER 'dbuser'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON myapp.* TO 'dbuser'@'localhost';
   ```

2. **Grant superuser (if needed):**
   ```sql
   -- PostgreSQL
   ALTER USER dbuser WITH SUPERUSER;
   ```

3. **Check authentication:**
   ```bash
   # PostgreSQL: Edit pg_hba.conf
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   # Add:
   local   all   dbuser   md5
   
   # Reload
   sudo systemctl reload postgresql
   ```

## Layer Issues

### Layer Syntax Error

**Symptoms:**
```
Error: SQL syntax error in layer L005
ERROR: syntax error at or near "TALBE"
LINE 1: CREATE TALBE users (
               ^
```

**Solutions:**

1. **Check layer file:**
   ```bash
   cat .dbl/layers/L005_add_users.sql
   ```

2. **Test SQL manually:**
   ```bash
   psql -d myapp -f .dbl/layers/L005_add_users.sql
   ```

3. **Fix syntax:**
   ```bash
   nano .dbl/layers/L005_add_users.sql
   # Fix: TALBE → TABLE
   ```

4. **Validate:**
   ```bash
   dbl validate --layers
   ```

### Missing Layer

**Symptoms:**
```
Error: Layer L003 not found
Expected sequence: L001, L002, L003, L004
Found: L001, L002, L004
```

**Solutions:**

1. **Renumber layers:**
   ```bash
   cd .dbl/layers/
   mv L004_add_posts.sql L003_add_posts.sql
   mv L005_add_comments.sql L004_add_comments.sql
   # ... continue renumbering
   ```

2. **Or use validate fix:**
   ```bash
   dbl validate --fix
   ```

### Duplicate Layer ID

**Symptoms:**
```
Error: Duplicate layer ID L008
Files: L008_add_auth.sql, L008_add_profiles.sql
```

**Solutions:**

```bash
# Renumber one file
mv .dbl/layers/L008_add_profiles.sql \
   .dbl/layers/L009_add_profiles.sql
```

## Sandbox Issues

### Sandbox Already Exists

**Symptoms:**
```
Error: Sandbox 'myapp_sandbox' already exists
```

**Solutions:**

1. **Apply existing sandbox:**
   ```bash
   dbl sandbox apply
   ```

2. **Or rollback:**
   ```bash
   dbl sandbox rollback
   ```

3. **Or force cleanup:**
   ```bash
   dropdb myapp_sandbox
   rm .dbl/sandbox.json
   dbl sandbox start
   ```

### Sandbox Database Not Found

**Symptoms:**
```
Error: Sandbox database 'myapp_sandbox' not found
Metadata indicates sandbox should exist
```

**Solutions:**

```bash
# Clean up metadata
rm .dbl/sandbox.json
rm .dbl/sandbox/

# Start fresh
dbl sandbox start
```

### Cannot Apply Sandbox

**Symptoms:**
```
Error: Cannot apply sandbox
Uncommitted changes detected
```

**Solutions:**

1. **Commit changes first:**
   ```bash
   dbl diff
   dbl commit -m "Your changes"
   dbl sandbox apply
   ```

2. **Or discard uncommitted:**
   ```bash
   dbl sandbox rollback
   dbl sandbox start
   # Re-apply only what you want
   ```

## State Issues

### Corrupted State File

**Symptoms:**
```
Error: Invalid state file
JSON parse error in .dbl/state.json
```

**Solutions:**

1. **Backup first:**
   ```bash
   cp .dbl/state.json .dbl/state.json.backup
   ```

2. **Validate JSON:**
   ```bash
   python -m json.tool .dbl/state.json
   ```

3. **Regenerate state:**
   ```bash
   rm .dbl/state.json
   dbl validate --fix
   ```

4. **Manual recovery:**
   ```json
   // .dbl/state.json
   {
     "database": "myapp",
     "engine": "postgres",
     "branch": "main",
     "last_layer": "L015",
     "active_sandbox": null
   }
   ```

### State Out of Sync

**Symptoms:**
```
Warning: State file indicates L015 applied
But database shows L012
```

**Solutions:**

```bash
# Option 1: Trust database, rebuild state
dbl validate --fix

# Option 2: Trust state, reset database
dbl reset
```

## Reset Issues

### Reset Fails Partway

**Symptoms:**
```
Replaying layers:
  → L001 ✓
  → L002 ✗ ERROR
  
Database may be in incomplete state
```

**Solutions:**

1. **Check error:**
   ```bash
   # View layer that failed
   cat .dbl/layers/L002_*.sql
   ```

2. **Manual cleanup:**
   ```bash
   dropdb myapp
   createdb myapp
   ```

3. **Fix layer:**
   ```bash
   # Edit problematic layer
   nano .dbl/layers/L002_*.sql
   ```

4. **Retry reset:**
   ```bash
   dbl reset
   ```

### Reset Takes Too Long

**Symptoms:**
```
Reset running for > 10 minutes
```

**Solutions:**

1. **Check progress:**
   ```sql
   -- In another terminal
   SELECT * FROM pg_stat_activity 
   WHERE datname = 'myapp';
   ```

2. **Optimize layers:**
   ```bash
   # Combine small layers
   # Add indexes after data loads
   # Use transactions efficiently
   ```

3. **Use --hard (careful):**
   ```bash
   dbl reset --hard
   ```

## Installation Issues

### DBL Command Not Found

**Symptoms:**
```
bash: dbl: command not found
```

**Solutions:**

1. **Check installation:**
   ```bash
   pip list | grep dbl
   ```

2. **Reinstall:**
   ```bash
   pip install --user git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
   ```

3. **Add to PATH:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export PATH="$HOME/.local/bin:$PATH"
   
   # Reload
   source ~/.bashrc
   ```

4. **Use python -m:**
   ```bash
   python -m dbl version
   ```

### Missing Dependencies

**Symptoms:**
```
Error: No module named 'yaml'
```

**Solutions:**

```bash
# Install dependencies
pip install PyYAML

# Or use dbl update
dbl update
```

## Performance Issues

### Slow Diff Command

**Symptoms:**
```
dbl diff takes > 30 seconds
```

**Solutions:**

1. **Large database:**
   ```bash
   # Diff specific tables
   dbl diff --tables users,posts
   ```

2. **Network latency:**
   ```yaml
   # Use local database for development
   database:
     host: localhost  # Not remote
   ```

3. **Index main database:**
   ```sql
   -- Add indexes to speed up queries
   CREATE INDEX idx_pg_class_relname ON pg_class(relname);
   ```

### Slow Reset

**Symptoms:**
```
dbl reset takes > 5 minutes
```

**Solutions:**

1. **Combine layers:**
   ```bash
   # Instead of 100 small layers, use 10 larger ones
   ```

2. **Optimize SQL:**
   ```sql
   -- Use transactions
   BEGIN;
   -- Multiple operations
   COMMIT;
   
   -- Defer constraints
   SET CONSTRAINTS ALL DEFERRED;
   ```

3. **Parallel execution (future):**
   ```bash
   dbl reset --parallel
   ```

## Configuration Issues

### Invalid YAML

**Symptoms:**
```
Error: Invalid YAML in dbl.yaml
mapping values are not allowed here
```

**Solutions:**

1. **Validate YAML:**
   ```bash
   python -c "import yaml; yaml.safe_load(open('dbl.yaml'))"
   ```

2. **Check indentation:**
   ```yaml
   # Bad
   database:
   name: myapp
   
   # Good
   database:
     name: myapp
   ```

3. **Quote special characters:**
   ```yaml
   # Bad
   password: p@ssw0rd!
   
   # Good
   password: "p@ssw0rd!"
   ```

### Environment Variables Not Working

**Symptoms:**
```
Database connection failed
Using literal '${DB_PASSWORD}' instead of value
```

**Solutions:**

```bash
# Export variables before running DBL
export DB_PASSWORD="mypassword"
dbl sandbox start

# Or use .env file (if supported)
echo "DB_PASSWORD=mypassword" > .env
dbl sandbox start
```

## Common Error Messages

### "No active sandbox"

```bash
# You need to start a sandbox first
dbl sandbox start
```

### "Uncommitted changes detected"

```bash
# Commit or discard changes
dbl commit -m "Changes"
# Or
dbl sandbox rollback
```

### "Layer sequence broken"

```bash
# Renumber layers
dbl validate --fix
```

### "Database already exists"

```bash
# Drop existing database
dropdb myapp

# Or use different name
# Edit dbl.yaml
database:
  name: myapp_v2
```

## Getting Help

### Check Version

```bash
dbl version
```

### Validate Setup

```bash
dbl validate --verbose
```

### View Logs

```bash
# Enable debug mode
export DBL_DEBUG=1
dbl sandbox start

# Check system logs
journalctl -u postgresql
```

### Report Bug

Include:
1. DBL version (`dbl version`)
2. Database engine and version
3. Full error message
4. Steps to reproduce
5. Relevant configuration

```bash
# Generate bug report
dbl version > bug-report.txt
dbl validate --verbose >> bug-report.txt
cat dbl.yaml >> bug-report.txt
```

## See Also

- [Configuration Guide](../guide/configuration.md)
- [Best Practices](../guide/best-practices.md)
- [FAQ](faq.md)
- [Commands Reference](../commands/index.md)
