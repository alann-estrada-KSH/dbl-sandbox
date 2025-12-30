# Quick Start

Get started with DBL in under 10 minutes.

## What You'll Learn

- ✅ Initialize a DBL project
- ✅ Create a safe sandbox
- ✅ Make and commit your first migration
- ✅ Apply changes to your database

**Time**: ~10 minutes  
**Prerequisites**: DBL installed, database running

---

## Step 1: Initialize Project

Create a new DBL project:

```bash
cd your-project
dbl init
```

**Output:**
```
✓ Created dbl.yaml configuration file
✓ Created .dbl directory structure
✓ Initialized master branch
```

---

## Step 2: Configure Database

Edit `dbl.yaml` with your database credentials:

```yaml
engine: postgres  # or mysql

# Database connection
host: localhost
port: 5432
user: your_user
password: your_password
database: your_database

# Optional: Docker container
# container_name: my_postgres_container
```

**Test connection:**
```bash
# PostgreSQL
psql -h localhost -U your_user -d your_database -c "SELECT version();"

# MySQL
mysql -h localhost -u your_user -p your_database -e "SELECT version();"
```

---

## Step 3: Create Sandbox

Create a safe testing environment:

```bash
dbl sandbox start
```

**Output:**
```
Creating sandbox database your_database_sandbox...
✓ Sandbox created successfully
✓ You are now working in the sandbox

Make your changes, then:
  dbl diff            - See what changed
  dbl commit -m "msg" - Save changes
  dbl sandbox apply   - Apply to main DB
```

!!! tip "What's a Sandbox?"
    A sandbox is a complete copy of your database where you can safely experiment. Changes don't affect your main database until you explicitly apply them.

---

## Step 4: Make Database Changes

Use your favorite database tool to make changes:

=== "SQL Command Line"
    ```bash
    # PostgreSQL
    psql -h localhost -U your_user -d your_database_sandbox
    
    # In psql:
    CREATE TABLE user_preferences (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        theme VARCHAR(50) DEFAULT 'light',
        language VARCHAR(10) DEFAULT 'en'
    );
    
    ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
    ```

=== "pgAdmin / DBeaver"
    1. Connect to `your_database_sandbox`
    2. Use GUI to create tables/columns
    3. Execute SQL scripts

=== "MySQL Workbench"
    1. Connect to `your_database_sandbox`
    2. Use Schema Designer
    3. Execute SQL scripts

---

## Step 5: Review Changes

See what you changed:

```bash
dbl diff
```

**Output:**
```sql
-- Schema changes detected:

+ CREATE TABLE user_preferences (
+     id SERIAL PRIMARY KEY,
+     user_id INTEGER NOT NULL,
+     theme VARCHAR(50) DEFAULT 'light',
+     language VARCHAR(10) DEFAULT 'en'
+ );

+ ALTER TABLE users 
+   ADD COLUMN last_login TIMESTAMP;

Changes detected: 2 schema modifications
Exit code: 1 (changes detected)
```

!!! info "Exit Codes"
    - `0` = No changes detected
    - `1` = Changes detected (useful for CI/CD)

---

## Step 6: Commit Changes

Save your changes as a versioned layer:

```bash
dbl commit -m "Add user preferences and last login tracking"
```

**Output:**
```
✓ Changes captured in layer L001
✓ Layer metadata saved
✓ Migration SQL generated: .dbl/layers/L001_add_user_preferences.sql

Layer details:
  ID: L001
  Message: Add user preferences and last login tracking
  Timestamp: 2025-12-30 10:30:45
  Branch: master
```

**Generated SQL file:**
```sql
-- Layer: L001
-- Message: Add user preferences and last login tracking
-- Author: DBL
-- Date: 2025-12-30 10:30:45

-- Phase: expand (safe additions)
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    theme VARCHAR(50) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en'
);

ALTER TABLE users 
  ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
```

---

## Step 7: Apply to Main Database

Apply sandbox changes to your main database:

```bash
dbl sandbox apply
```

**Output:**
```
Applying sandbox changes to main database...
✓ Executing layer L001
✓ Changes applied successfully
✓ Sandbox database dropped
✓ Sandbox metadata cleared

Your main database (your_database) now includes:
  - user_preferences table
  - users.last_login column
```

!!! success "Done!"
    Your changes are now in your main database. The sandbox has been cleaned up automatically.

---

## What You Just Did

1. **Initialized DBL** - Set up version control for your database
2. **Created Sandbox** - Isolated testing environment
3. **Made Changes** - Modified schema safely
4. **Reviewed with diff** - Previewed all changes
5. **Committed Layer** - Versioned your migration
6. **Applied Changes** - Updated main database

---

## View Your History

Check your migration history:

```bash
dbl log
```

**Output:**
```
* L001 - Add user preferences and last login tracking
         2025-12-30 10:30:45
         Branch: master
```

---

## Next Steps

### Try Branching

Work on multiple features in parallel:

```bash
# Create feature branch
dbl branch add-comments

# Switch to it
dbl checkout add-comments

# Make changes in sandbox
dbl sandbox start
# ... make changes ...
dbl commit -m "Add comments table"

# Merge back to master
dbl checkout master
dbl merge add-comments
```

### Experiment Without Fear

```bash
dbl sandbox start
# Try something risky...
dbl diff
# Don't like it?
dbl sandbox rollback  # All changes discarded!
```

### Rebuild From Layers

```bash
# Rebuild entire database from layers
dbl reset

# Your database is recreated from version history
```

---

## Common Workflows

### Daily Development
```bash
dbl sandbox start
# Work on feature...
dbl diff
dbl commit -m "Feature X"
dbl sandbox apply
```

### Experimenting
```bash
dbl sandbox start
# Try something...
dbl sandbox rollback  # Discard if not good
```

### Team Collaboration
```bash
dbl log                    # See team's changes
dbl branch feature-name    # Work on your feature
dbl checkout master        # Review main branch
dbl merge feature-name     # Integrate your work
```

---

## Troubleshooting

### Sandbox Already Exists

```bash
# Check status
dbl sandbox status

# Clean up if needed
dbl sandbox rollback
```

### Can't Connect to Database

```bash
# Test connection directly
psql -h localhost -U user -d database

# Check dbl.yaml settings
cat dbl.yaml
```

### Changes Not Detected

```bash
# Ensure you're in sandbox
dbl sandbox status

# Check state file
cat .dbl/state.json
```

---

## Learning Resources

- 📖 [Complete Commands Guide](../commands/index.md)
- 🎯 [Your First Migration Tutorial](first-migration.md)
- 💡 [Best Practices](../guide/best-practices.md)
- ⚙️ [Configuration Guide](../guide/configuration.md)

---

## Need Help?

- Run `dbl help` for command reference
- Check [Troubleshooting Guide](../guide/troubleshooting.md)
- [Open an issue](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)

---

**Ready for more?** → [Your First Migration Tutorial](first-migration.md)
