# Database Engines

Guide to using DBL with different database engines.

## Supported Engines

DBL currently supports:

| Engine | Status | Version | Features |
|--------|--------|---------|----------|
| PostgreSQL | ✅ Stable | 9.6+ | Full support |
| MySQL | ✅ Stable | 5.7+ | Full support |
| SQLite | 🔄 Planned | - | Coming soon |
| MariaDB | 🔄 Planned | - | Coming soon |
| SQL Server | 🔄 Planned | - | Under consideration |

## PostgreSQL

### Configuration

```yaml
# dbl.yaml
database:
  name: myapp
  engine: postgres
  host: localhost
  port: 5432
  user: dbuser
  password: ${DB_PASSWORD}
```

### Features

Fully supported:
- ✅ Tables, views, materialized views
- ✅ Indexes (B-tree, Hash, GiST, GIN, BRIN)
- ✅ Constraints (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK)
- ✅ Triggers and functions
- ✅ Sequences
- ✅ Extensions
- ✅ Schemas
- ✅ Enums, domains, composite types
- ✅ Partitioning

### Example Workflow

```bash
# Initialize with PostgreSQL
dbl init

# Verify connection
psql -d myapp -c "SELECT version();"

# Create sandbox
dbl sandbox start

# Make changes
psql -d myapp_sandbox << EOF
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
EOF

# Commit
dbl commit -m "Add users table"
dbl sandbox apply
```

### PostgreSQL-specific Features

#### Extensions

```sql
-- Layer: L003_enable_extensions.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

#### Full-text Search

```sql
-- Layer: L008_add_search.sql
ALTER TABLE posts 
ADD COLUMN search_vector tsvector;

CREATE INDEX idx_posts_search 
ON posts USING GIN(search_vector);

CREATE TRIGGER posts_search_update
BEFORE INSERT OR UPDATE ON posts
FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content);
```

#### Partitioning

```sql
-- Layer: L010_partition_logs.sql
CREATE TABLE logs (
    id BIGSERIAL,
    created_at TIMESTAMP NOT NULL,
    message TEXT
) PARTITION BY RANGE (created_at);

CREATE TABLE logs_2024_12 PARTITION OF logs
FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
```

### Connection Options

```yaml
# Advanced PostgreSQL config
database:
  name: myapp
  engine: postgres
  host: localhost
  port: 5432
  user: dbuser
  password: ${DB_PASSWORD}
  options:
    sslmode: require
    connect_timeout: 10
    application_name: dbl
```

### PostgreSQL Best Practices

1. **Use transactions**:
   ```sql
   BEGIN;
   -- Multiple operations
   COMMIT;
   ```

2. **Create indexes concurrently**:
   ```sql
   CREATE INDEX CONCURRENTLY idx_users_email 
   ON users(email);
   ```

3. **Use constraints**:
   ```sql
   ALTER TABLE users
   ADD CONSTRAINT check_email 
   CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$');
   ```

## MySQL

### Configuration

```yaml
# dbl.yaml
database:
  name: myapp
  engine: mysql
  host: localhost
  port: 3306
  user: dbuser
  password: ${DB_PASSWORD}
```

### Features

Fully supported:
- ✅ Tables and views
- ✅ Indexes (B-tree, Full-text, Spatial)
- ✅ Constraints (PRIMARY KEY, FOREIGN KEY, UNIQUE)
- ✅ Triggers and stored procedures
- ✅ Auto-increment
- ✅ Character sets and collations
- ⚠️ Limited: CHECK constraints (MySQL 8.0.16+)

Limitations:
- ❌ No native schemas (use databases)
- ❌ No materialized views
- ❌ Limited functional indexes

### Example Workflow

```bash
# Initialize with MySQL
dbl init

# Verify connection
mysql -u dbuser -p myapp -e "SELECT VERSION();"

# Create sandbox
dbl sandbox start

# Make changes
mysql -u dbuser -p myapp_sandbox << EOF
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_users_email ON users(email);
EOF

# Commit
dbl commit -m "Add users table"
dbl sandbox apply
```

### MySQL-specific Features

#### Storage Engines

```sql
-- Layer: L002_setup_tables.sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE cache (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT
) ENGINE=MEMORY;
```

#### Full-text Search

```sql
-- Layer: L006_add_search.sql
ALTER TABLE posts 
ADD FULLTEXT INDEX ft_posts_content (title, content);

-- Usage:
-- SELECT * FROM posts 
-- WHERE MATCH(title, content) AGAINST('search term');
```

#### Character Sets

```sql
-- Layer: L001_setup_charset.sql
ALTER DATABASE myapp 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

CREATE TABLE messages (
    id INT PRIMARY KEY,
    text TEXT CHARACTER SET utf8mb4 
             COLLATE utf8mb4_unicode_ci
);
```

### Connection Options

```yaml
# Advanced MySQL config
database:
  name: myapp
  engine: mysql
  host: localhost
  port: 3306
  user: dbuser
  password: ${DB_PASSWORD}
  options:
    charset: utf8mb4
    ssl_ca: /path/to/ca.pem
    connect_timeout: 10
```

### MySQL Best Practices

1. **Always specify engine**:
   ```sql
   CREATE TABLE users (...) ENGINE=InnoDB;
   ```

2. **Use proper character set**:
   ```sql
   CREATE TABLE messages (
       content TEXT
   ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Disable foreign key checks for migrations** (when needed):
   ```sql
   SET FOREIGN_KEY_CHECKS=0;
   -- Migrations
   SET FOREIGN_KEY_CHECKS=1;
   ```

## Engine Comparison

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Schemas | ✅ Native | ❌ Use databases |
| Materialized Views | ✅ Yes | ❌ No |
| Full-text Search | ✅ Native (tsvector) | ✅ FULLTEXT indexes |
| JSON | ✅ JSONB (binary) | ✅ JSON |
| Arrays | ✅ Native | ❌ Use JSON |
| Window Functions | ✅ Yes | ✅ Yes (8.0+) |
| CTEs (WITH) | ✅ Yes | ✅ Yes (8.0+) |
| Partial Indexes | ✅ Yes | ❌ No |
| Concurrent Indexes | ✅ Yes | ❌ No |

## Switching Engines

### PostgreSQL → MySQL

Considerations:
- Remove schema references
- Change `SERIAL` → `AUTO_INCREMENT`
- Change `TEXT` → `TEXT` or `VARCHAR(n)`
- Remove PostgreSQL-specific types (arrays, JSONB)

```sql
-- PostgreSQL
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    tags TEXT[]
);

-- MySQL equivalent
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tags JSON
) ENGINE=InnoDB;
```

### MySQL → PostgreSQL

Considerations:
- Can use schemas
- Change `AUTO_INCREMENT` → `SERIAL`
- Can use advanced types
- Remove `ENGINE=InnoDB` clauses

```sql
-- MySQL
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY
) ENGINE=InnoDB;

-- PostgreSQL equivalent
CREATE TABLE users (
    id SERIAL PRIMARY KEY
);
```

## Engine Detection

DBL auto-detects engine from connection:

```yaml
# Auto-detect from connection
database:
  name: myapp
  host: localhost
  # engine: auto-detected
```

Or specify explicitly:

```yaml
database:
  engine: postgres  # or mysql
```

## Testing Across Engines

Test your layers on both engines:

```bash
# Test PostgreSQL
dbl --config dbl-postgres.yaml reset

# Test MySQL
dbl --config dbl-mysql.yaml reset
```

## Engine-specific Commands

### PostgreSQL Tools

```bash
# Dump schema only
pg_dump -s myapp > schema.sql

# Restore
psql myapp < schema.sql

# Analyze database
psql myapp -c "ANALYZE VERBOSE;"
```

### MySQL Tools

```bash
# Dump schema only
mysqldump --no-data myapp > schema.sql

# Restore
mysql myapp < schema.sql

# Analyze database
mysql myapp -e "ANALYZE TABLE users;"
```

## Future Support

### SQLite

Planned features:
- File-based databases
- Embedded use cases
- Local development

### MariaDB

Planned features:
- Full compatibility with MySQL
- MariaDB-specific features (virtual columns, etc.)

### SQL Server

Under consideration:
- Windows authentication
- SSMS integration
- Azure SQL Database

## See Also

- [Configuration Guide](../guide/configuration.md)
- [Getting Started](../getting-started/installation.md)
- [Best Practices](../guide/best-practices.md)
- [Troubleshooting](troubleshooting.md)
