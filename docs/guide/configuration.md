# Configuration Guide

Complete reference for `dbl.yaml` configuration.

## Configuration File Location

DBL expects `dbl.yaml` in your project root:

```
your-project/
├── dbl.yaml          ← Configuration file
├── .dbl/             ← DBL workspace
└── your-app-code/
```

---

## Basic Configuration

Minimal configuration:

```yaml
engine: postgres

host: localhost
port: 5432
user: myuser
password: mypassword
database: mydb
```

---

## Complete Reference

### Database Connection

#### PostgreSQL

```yaml
engine: postgres

# Connection details
host: localhost
port: 5432
user: postgres
password: secretpassword
database: myapp_db

# Optional: SSL settings
sslmode: require              # disable, allow, prefer, require, verify-ca, verify-full
sslcert: /path/to/client.crt
sslkey: /path/to/client.key
sslrootcert: /path/to/ca.crt
```

#### MySQL

```yaml
engine: mysql

# Connection details
host: localhost
port: 3306
user: root
password: secretpassword
database: myapp_db

# Optional: SSL settings
ssl_ca: /path/to/ca.pem
ssl_cert: /path/to/client-cert.pem
ssl_key: /path/to/client-key.pem
```

### Docker Support

Run database commands inside containers:

```yaml
# For Docker containers
container_name: my_postgres_container

# DBL will use: docker exec my_postgres_container <command>
```

**Example:**
```yaml
engine: postgres
container_name: myapp_db

host: localhost  # Not used when container_name is set
port: 5432       # Not used when container_name is set
user: postgres
password: password
database: myapp
```

### Table Filtering

Control which tables DBL tracks:

```yaml
# Option 1: Ignore specific tables
ignore_tables:
  - sessions
  - cache
  - _prisma_migrations
  - django_migrations
  - knex_migrations

# Option 2: Only track specific tables
track_tables:
  - users
  - posts
  - comments
  
# Note: Use either ignore_tables OR track_tables, not both
```

**When to use:**
- `ignore_tables`: Track everything except these
- `track_tables`: Only track these specific tables

### Safety Policies

Prevent accidental data loss:

```yaml
policies:
  # Require sandbox for all commits
  require_sandbox: true          # Default: true
  
  # Prevent DROP operations
  allow_data_loss: false         # Default: false
  
  # Require confirmation for destructive ops
  confirm_destructive: true      # Default: true
```

**Policy effects:**

| Policy | Effect |
|--------|--------|
| `require_sandbox: true` | Cannot commit without active sandbox |
| `allow_data_loss: false` | Blocks DROP TABLE, DROP DATABASE |
| `confirm_destructive: true` | Prompts before DROP, TRUNCATE |

### Validation Rules

Configure migration validation:

```yaml
validate:
  # Treat warnings as errors
  strict: false                   # Default: false
  
  # Allow backfill without expand
  allow_orphaned: false           # Default: false
  
  # Require comments for contract phase
  require_comments: false         # Default: false
  
  # Detect type changes
  detect_type_changes: true       # Default: true
  
  # Warn about missing indexes on foreign keys
  check_foreign_key_indexes: true  # Default: true
```

**Validation examples:**

```yaml
# Strict mode: warnings fail validation
validate:
  strict: true
  
# Development mode: permissive
validate:
  strict: false
  allow_orphaned: true
  
# Production mode: careful
validate:
  strict: true
  require_comments: true
  detect_type_changes: true
```

---

## Complete Example

Production-ready configuration:

```yaml
# Database engine
engine: postgres

# Connection
host: localhost
port: 5432
user: myapp_user
password: ${DB_PASSWORD}  # Use environment variable
database: myapp_production

# Docker support (optional)
# container_name: myapp_postgres

# Table management
ignore_tables:
  # System/framework tables
  - pg_stat_statements
  - _prisma_migrations
  - knex_migrations
  - django_migrations
  
  # High-churn tables
  - sessions
  - cache
  - audit_logs

# Safety policies
policies:
  require_sandbox: true
  allow_data_loss: false
  confirm_destructive: true

# Validation rules
validate:
  strict: false
  allow_orphaned: false
  require_comments: true
  detect_type_changes: true
  check_foreign_key_indexes: true

# Migration phases (optional metadata)
phases:
  expand:
    - "CREATE TABLE"
    - "ADD COLUMN"
    - "CREATE INDEX"
  backfill:
    - "INSERT"
    - "UPDATE"
  contract:
    - "DROP TABLE"
    - "DROP COLUMN"
    - "ALTER.*NOT NULL"
```

---

## Environment Variables

Use environment variables for secrets:

```yaml
# dbl.yaml
user: ${DB_USER}
password: ${DB_PASSWORD}
database: ${DB_NAME}
```

```bash
# .env file
export DB_USER=myapp
export DB_PASSWORD=secretpassword
export DB_NAME=myapp_db
```

---

## Multiple Environments

### Option 1: Multiple Config Files

```bash
# Development
dbl.dev.yaml

# Staging
dbl.staging.yaml

# Production
dbl.prod.yaml
```

Use with custom flag (if supported):
```bash
dbl --config dbl.prod.yaml init
```

### Option 2: Environment Variables

```yaml
# dbl.yaml
engine: postgres
host: ${DB_HOST:-localhost}
port: ${DB_PORT:-5432}
user: ${DB_USER}
password: ${DB_PASSWORD}
database: ${DB_NAME}
```

```bash
# Development
export DB_HOST=localhost
export DB_USER=dev_user
export DB_PASSWORD=dev_pass
export DB_NAME=myapp_dev

# Production
export DB_HOST=prod.example.com
export DB_USER=prod_user
export DB_PASSWORD=prod_pass
export DB_NAME=myapp_prod
```

---

## Docker Compose Integration

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    container_name: myapp_db
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    ports:
      - "5432:5432"
```

```yaml
# dbl.yaml
engine: postgres
container_name: myapp_db
user: myapp
password: password
database: myapp
```

**Usage:**
```bash
docker-compose up -d
dbl init
dbl sandbox start  # Runs inside container
```

---

## Configuration Validation

Check your configuration:

```bash
# Test database connection
psql -h localhost -U myuser -d mydb -c "SELECT version();"

# MySQL
mysql -h localhost -u myuser -p mydb -e "SELECT version();"

# Test DBL config
dbl init
dbl sandbox start
```

---

## Security Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore
dbl.yaml
.env
*.local.yaml
```

### 2. Use Environment Variables

```yaml
password: ${DB_PASSWORD}
```

### 3. Use Separate Credentials

```yaml
# Development
user: dev_user

# Production
user: prod_readonly  # Limited permissions
```

### 4. Restrict Permissions

```sql
-- Create limited user
CREATE USER dbl_user WITH PASSWORD 'password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE myapp TO dbl_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO dbl_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO dbl_user;

-- For sandboxes, also grant CREATE DATABASE
ALTER USER dbl_user CREATEDB;
```

---

## Common Configurations

### Local Development

```yaml
engine: postgres
host: localhost
port: 5432
user: postgres
password: password
database: myapp_dev

ignore_tables:
  - sessions

policies:
  require_sandbox: true

validate:
  strict: false
  allow_orphaned: true
```

### CI/CD Environment

```yaml
engine: postgres
host: postgres
port: 5432
user: ci_user
password: ${CI_DB_PASSWORD}
database: test_db

ignore_tables:
  - sessions
  - cache

policies:
  require_sandbox: false  # CI can run without sandbox

validate:
  strict: true
  detect_type_changes: true
```

### Team Development

```yaml
engine: postgres
container_name: team_db
user: team_user
password: ${DB_PASSWORD}
database: team_dev

track_tables:
  - users
  - posts
  - comments

policies:
  require_sandbox: true
  allow_data_loss: false

validate:
  strict: false
  require_comments: true
```

---

## Troubleshooting

### Connection Issues

```yaml
# Try with explicit settings
engine: postgres
host: 127.0.0.1  # Instead of localhost
port: 5432
user: postgres
password: password
database: postgres  # Connect to postgres first
```

### Docker Issues

```bash
# Verify container name
docker ps

# Test connection
docker exec myapp_db psql -U postgres -c "SELECT 1"
```

### Permission Issues

```sql
-- Check user permissions
\du  -- PostgreSQL

-- Grant create database
ALTER USER myuser CREATEDB;
```

---

## Next Steps

- [Quick Start Tutorial](../getting-started/quick-start.md)
- [Best Practices](best-practices.md)
- [Troubleshooting Guide](troubleshooting.md)
