# Frequently Asked Questions

Common questions about DBL and database version control.

## General Questions

### What is DBL?

DBL (Database Layering) is a Git-like version control system for database schemas. It lets you:
- Track schema changes over time
- Test changes in isolated sandboxes
- Collaborate with teams without conflicts
- Replay migrations reliably

### How is DBL different from traditional migrations?

| Traditional Migrations | DBL |
|----------------------|-----|
| Manual SQL scripts | Automatic diff capture |
| Up/down scripts | Layer-based |
| Sequential only | Branch support |
| No sandbox | Built-in sandboxes |
| Manual rollback | Automated replay |

### Which databases does DBL support?

Currently:
- ✅ PostgreSQL (9.6+)
- ✅ MySQL (5.7+)

Planned:
- 🔄 SQLite
- 🔄 MariaDB
- 🔄 SQL Server

### Is DBL production-ready?

DBL is currently in **alpha**. It's suitable for:
- ✅ Development environments
- ✅ Testing/staging
- ⚠️ Production (with caution and backups)

## Installation & Setup

### How do I install DBL?

```bash
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```

See [Installation Guide](../getting-started/installation.md) for details.

### Do I need to install anything else?

Yes, you need:
1. Python 3.7+
2. Database (PostgreSQL or MySQL)
3. PyYAML (auto-installed by `dbl update`)

### How do I upgrade DBL?

```bash
dbl update
```

Or manually:
```bash
pip install --upgrade git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```

### Can I use DBL with Docker?

Yes! Example:

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: dbuser
      POSTGRES_PASSWORD: dbpass
  
  app:
    build: .
    depends_on:
      - db
    command: dbl sandbox start
```

## Working with DBL

### How do I start using DBL on an existing database?

```bash
# Initialize DBL
dbl init

# Capture current schema as first layer
dbl sandbox start
# DBL will diff against empty → captures all
dbl commit -m "Initial schema import"
dbl sandbox apply
```

### Can I use DBL with an existing migration tool?

Yes, but you should choose one:
- **Option 1**: Migrate to DBL completely
- **Option 2**: Use DBL for new changes only
- **Option 3**: Use both (not recommended - can cause conflicts)

### How do I share changes with my team?

```bash
# Commit changes
dbl commit -m "Add user preferences"

# Push layers to Git
git add .dbl/
git commit -m "Database: Add user preferences"
git push

# Team pulls and applies
git pull
dbl sandbox start
dbl reset  # Rebuild with new layers
```

### Can multiple developers work simultaneously?

Yes! Use branches:

```bash
# Developer 1
dbl branch feature-auth
dbl checkout feature-auth

# Developer 2
dbl branch feature-payments
dbl checkout feature-payments

# Both work independently
```

## Sandboxes

### What is a sandbox?

A sandbox is a temporary copy of your database where you can experiment safely. Changes don't affect the main database until you apply them.

### Can I have multiple sandboxes?

Not yet. Currently, one sandbox per database at a time. Planned for future releases.

### What happens if I delete a sandbox manually?

```bash
# If you manually dropped the database
dropdb myapp_sandbox

# Clean up DBL metadata
dbl sandbox rollback
```

### Can I access the sandbox from other tools?

Yes! The sandbox is a regular database:

```bash
# Connect with psql
psql -d myapp_sandbox

# Or any database tool
# Host: localhost
# Database: myapp_sandbox
```

## Layers

### What are layers?

Layers are committed database changes (like Git commits). Each layer is a SQL file containing the changes made.

### Can I edit layers after committing?

Yes, but be careful:

```bash
# Edit layer file
nano .dbl/layers/L005_add_users.sql

# Verify it's valid
dbl validate --layers

# Reset to apply changes
dbl reset
```

!!! warning
    Editing historical layers can break team members' databases.

### How do I undo a layer?

```bash
# Option 1: Reset to before that layer
dbl reset --to L004  # If you want to undo L005

# Option 2: Create a new layer that reverts changes
dbl sandbox start
psql -d myapp_sandbox -c "DROP TABLE users;"
dbl commit -m "Revert: Remove users table"
dbl sandbox apply
```

### Can layers be merged/squashed?

Not automatically yet. Manual process:

```bash
# Combine L003, L004, L005 into one
cat .dbl/layers/L003_*.sql \
    .dbl/layers/L004_*.sql \
    .dbl/layers/L005_*.sql \
    > combined.sql

# Delete originals
rm .dbl/layers/L003_*.sql \
   .dbl/layers/L004_*.sql \
   .dbl/layers/L005_*.sql

# Create new combined layer
mv combined.sql .dbl/layers/L003_combined.sql

# Renumber remaining
dbl validate --fix
```

## Branching

### How do branches work?

Like Git branches:

```bash
# Create branch
dbl branch feature-xyz

# Switch branches
dbl checkout feature-xyz

# Work independently from main
```

### Can I merge branches?

Manual merge currently:

```bash
# Copy layers from feature branch
cp .dbl/layers/L008_* ../temp/

# Switch to main
dbl checkout main

# Move layers
mv ../temp/L008_* .dbl/layers/L009_*.sql

# Apply
dbl reset
```

Auto-merge is planned for future releases.

### What happens when I switch branches?

- Layer history changes to that branch
- Database remains unchanged (until you reset)
- Active sandboxes are preserved

## Errors & Troubleshooting

### "Could not connect to database"

Check:
1. Database is running (`pg_isready`)
2. Credentials in `dbl.yaml` are correct
3. Database exists (`psql -l`)
4. User has permissions

### "Layer syntax error"

```bash
# Find problematic layer
dbl validate --layers

# Fix SQL
nano .dbl/layers/L005_*.sql

# Test manually
psql -d myapp -f .dbl/layers/L005_*.sql
```

### "Sandbox already exists"

```bash
# Apply existing sandbox
dbl sandbox apply

# Or discard it
dbl sandbox rollback
```

### "Uncommitted changes detected"

```bash
# View changes
dbl diff

# Commit them
dbl commit -m "Your changes"

# Or discard
dbl sandbox rollback
```

### DBL commands are slow

Possible causes:
1. **Large database**: Use indexes, optimize queries
2. **Remote database**: Use local database for development
3. **Many layers**: Consider squashing old layers
4. **Network issues**: Check connection

## Advanced Usage

### Can I use DBL in CI/CD?

Yes!

```yaml
# .github/workflows/test.yml
- name: Test migrations
  run: |
    dbl init
    dbl reset
    ./run-tests.sh
```

### Can I customize layer file naming?

Not currently. DBL uses:
```
L{number}_{message_slug}.sql
```

This ensures consistent ordering.

### Can I run custom SQL before/after layers?

Yes, through hooks (future feature). Currently:

```bash
# Run manually
psql -d myapp -f pre-layer.sql
dbl reset
psql -d myapp -f post-layer.sql
```

### How do I backup my database?

DBL doesn't handle backups. Use standard tools:

```bash
# PostgreSQL
pg_dump myapp > backup.sql

# MySQL
mysqldump myapp > backup.sql
```

### Can I use DBL with microservices?

Yes! Each service can have its own `dbl.yaml`:

```
services/
├── auth/
│   ├── dbl.yaml  (auth database)
│   └── .dbl/
├── payments/
│   ├── dbl.yaml  (payments database)
│   └── .dbl/
└── users/
    ├── dbl.yaml  (users database)
    └── .dbl/
```

## Performance

### How many layers is too many?

Guidelines:
- < 100 layers: Excellent
- 100-500 layers: Good
- 500-1000 layers: Consider squashing
- \> 1000 layers: Definitely squash

### Does DBL slow down my database?

No. DBL only:
- Reads schema metadata (fast)
- Doesn't add triggers or overhead
- Doesn't affect runtime performance

### How big can layer files be?

Recommendations:
- Ideal: < 100 KB per layer
- Acceptable: < 1 MB per layer
- Large: > 1 MB (consider splitting)

## Data Migrations

### Can DBL handle data migrations?

Yes, but with caution:

```sql
-- Layer: L005_migrate_user_emails.sql
BEGIN;

-- Add new column
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;

-- Migrate data
UPDATE users SET email_verified = true 
WHERE email IS NOT NULL;

COMMIT;
```

Commit with flag:
```bash
dbl commit -m "Migrate email verification" --with-data
```

### Should I version control data?

Generally no:
- ✅ Reference data (countries, categories)
- ✅ Configuration data
- ❌ User data
- ❌ Large datasets
- ❌ Sensitive data

### How do I handle large data migrations?

```sql
-- Break into chunks
UPDATE users SET migrated = true 
WHERE id >= 1 AND id < 10000;

UPDATE users SET migrated = true 
WHERE id >= 10000 AND id < 20000;
-- etc.
```

Or use external scripts:
```bash
# Run before applying layer
python migrate_data.py
dbl sandbox apply
```

## Security

### Is it safe to commit database credentials?

**NO!** Use environment variables:

```yaml
# dbl.yaml
database:
  name: myapp
  user: ${DB_USER}
  password: ${DB_PASSWORD}
```

```bash
export DB_USER=myuser
export DB_PASSWORD=secret
dbl sandbox start
```

### What about sensitive data in layers?

**Don't commit sensitive data!**

```sql
-- BAD
INSERT INTO users (email, password) 
VALUES ('admin@example.com', 'plaintext123');

-- GOOD (reference only)
-- INSERT admin user with strong password
-- Password must be set separately via admin panel
```

### Can I encrypt layer files?

DBL doesn't provide encryption. Use Git encryption tools:
- git-crypt
- Blackbox
- git-secret

## Compatibility

### Can I use DBL with ORM migrations?

Yes, but:
- Use one as source of truth
- DBL captures ORM migration results
- Or use ORM to generate DBL layers

### Does DBL work with Django/Rails/etc?

Yes! DBL is database-agnostic. Works alongside:
- Django migrations
- Rails Active Record
- Alembic (SQLAlchemy)
- Flyway
- Liquibase

### Can I migrate from other tools to DBL?

Yes:

```bash
# 1. Apply all existing migrations
python manage.py migrate  # Django
# or
rake db:migrate  # Rails

# 2. Capture current state in DBL
dbl init
dbl sandbox start
dbl commit -m "Import from Django/Rails"
dbl sandbox apply

# 3. Use DBL for future changes
```

## Contributing

### How can I contribute?

1. Report bugs
2. Suggest features
3. Improve documentation
4. Submit pull requests

See GitHub: https://github.com/alann-estrada-KSH/dbl-sandbox

### Where can I get help?

1. Read the docs: [DBL Documentation](../index.md)
2. Check [Troubleshooting](troubleshooting.md)
3. Open an issue on GitHub
4. Ask in discussions

### Is DBL open source?

Yes! Licensed under Apache 2.0.

## Roadmap

### What features are coming?

Planned:
- ⏳ Auto-merge branches
- ⏳ Multiple simultaneous sandboxes
- ⏳ Layer squashing
- ⏳ Rollback scripts
- ⏳ Web UI
- ⏳ Cloud hosting

### Can I request features?

Yes! Open an issue on GitHub with:
- Description of feature
- Use case
- Example workflow

## See Also

- [Getting Started](../getting-started/quick-start.md)
- [Troubleshooting](troubleshooting.md)
- [Best Practices](../guide/best-practices.md)
- [All Commands](../commands/index.md)
