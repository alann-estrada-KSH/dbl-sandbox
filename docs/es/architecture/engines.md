# Motores de Base de Datos

DBL soporta múltiples sistemas de bases de datos.

## PostgreSQL

Motor principal y recomendado de DBL.

### Ventajas

- ✅ Mejor soporte en DBL
- ✅ Transacciones ACID robustas
- ✅ Excelente para migraciones
- ✅ Herramientas avanzadas

### Configurar

```yaml
# dbl.yaml
engine: postgres
database:
  host: localhost
  port: 5432
  database: myapp
  user: postgres
  password: secret
```

### Características Especiales

```sql
-- Schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS app;

-- Tipos personalizados
CREATE TYPE user_role AS ENUM ('admin', 'user', 'guest');

-- JSON
ALTER TABLE users ADD COLUMN metadata JSONB;

-- Full-text search
CREATE INDEX idx_posts_search ON posts USING gin(to_tsvector('spanish', content));
```

## MySQL

Soporte completo para MySQL 5.7+.

### Ventajas

- ✅ Muy popular
- ✅ Buenas transacciones (InnoDB)
- ✅ Rendimiento en OLTP

### Diferencias con PostgreSQL

```sql
-- No hay SCHEMAS (usar databases)
USE myapp;

-- Tipos enum
ALTER TABLE users ADD COLUMN status ENUM('active', 'inactive');

-- JSON
ALTER TABLE users ADD COLUMN metadata JSON;

-- Full-text search
ALTER TABLE posts ADD FULLTEXT INDEX ft_search (title, content);
```

### Configurar

```yaml
# dbl.yaml
engine: mysql
database:
  host: localhost
  port: 3306
  database: myapp
  user: root
  password: secret
```

### Consideraciones Especiales

```sql
-- Cuidado: MySQL no soporta TRUNCATE CASCADE
-- Usar DELETE en su lugar
DELETE FROM comments WHERE post_id IN (SELECT id FROM posts);
DELETE FROM posts;

-- Cuidado: Sin transacciones explícitas por defecto
BEGIN;
CREATE TABLE users (...);
INSERT INTO users VALUES (...);
COMMIT;
```

## Soportados

### Version Matrix

| Base de Datos | Versión Mínima | Estado |
|---|---|---|
| PostgreSQL | 11+ | ✅ Soportado |
| PostgreSQL | 9.6-10 | ⚠️ Legacy |
| MySQL | 5.7+ | ✅ Soportado |
| MySQL | 5.6 | ❌ No soportado |

### Planes Futuros

- 🔄 MariaDB (próximamente)
- 🔄 SQLite (development)
- 🔄 SQL Server (roadmap)

## Compatibilidad de Features

### Transacciones

| Feature | PostgreSQL | MySQL |
|---|---|---|
| BEGIN/COMMIT | ✅ | ✅ |
| Rollback | ✅ | ✅ (InnoDB) |
| Savepoints | ✅ | ✅ |

### Constraints

| Constraint | PostgreSQL | MySQL |
|---|---|---|
| PRIMARY KEY | ✅ | ✅ |
| FOREIGN KEY | ✅ | ✅ |
| UNIQUE | ✅ | ✅ |
| CHECK | ✅ | ⚠️ (ignored) |

### Tipos de Datos

| Tipo | PostgreSQL | MySQL |
|---|---|---|
| INTEGER | ✅ | ✅ |
| VARCHAR | ✅ | ✅ |
| TEXT | ✅ | ✅ |
| JSONB | ✅ | JSON |
| UUID | ✅ | VARCHAR(36) |
| ARRAY | ✅ | ❌ |

## Ejemplos por Engine

### PostgreSQL

```sql
-- Crear tabla con UUID
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- JSON avanzado
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL
);
CREATE INDEX idx_events_data ON events USING gin(data);
```

### MySQL

```sql
-- UUID alternativo
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- JSON básico
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data JSON NOT NULL
);
```

## Diferencias de Sintaxis

### CREATE TABLE

```
PostgreSQL:
  SERIAL      → Auto-increment
  TIMESTAMP   → Timestamp
  TEXT        → Texto largo

MySQL:
  AUTO_INCREMENT  → Auto-increment
  DATETIME        → Timestamp
  VARCHAR(255)    → Texto máx 255
```

### Índices

```sql
-- PostgreSQL
CREATE UNIQUE INDEX idx_name ON table(column);

-- MySQL
CREATE UNIQUE INDEX idx_name ON table(column);
-- Iguales
```

### Foreign Keys

```sql
-- Ambos soportan
ALTER TABLE posts ADD CONSTRAINT fk_posts_users
FOREIGN KEY (user_id) REFERENCES users(id);
```

## Características Únicas

### PostgreSQL Único

```sql
-- Particionamiento
CREATE TABLE events_2024 PARTITION OF events
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Materialized Views
CREATE MATERIALIZED VIEW user_stats AS
SELECT user_id, COUNT(*) as posts
FROM posts
GROUP BY user_id;

-- Función PL/pgSQL
CREATE FUNCTION update_timestamp() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### MySQL Único

```sql
-- Particionamiento RANGE
CREATE TABLE orders (
    id INT,
    order_date DATE
) PARTITION BY RANGE (YEAR(order_date)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025)
);

-- Generated Columns
CREATE TABLE users (
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(101) GENERATED ALWAYS AS
    (CONCAT(first_name, ' ', last_name)) STORED
);
```

## Migración Entre Engines

### PostgreSQL → MySQL

```sql
-- Cambios necesarios:
1. UUID → CHAR(36) con UUID()
2. JSONB → JSON
3. Triggers PL/pgSQL → triggers MySQL
4. Schemas → Usar databases
5. ENUM → VARCHAR o ENUM (MySQL)
```

### Proceso

```bash
# 1. Extraer schema actual
pg_dump --schema-only myapp > schema.sql

# 2. Adaptarlo a MySQL
sed 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' schema.sql

# 3. Importar en DBL
dbl commit -m "Migrate to MySQL"

# 4. Testear
dbl reset --engine mysql
```

## Troubleshooting por Engine

### PostgreSQL

**Problema:** `UNIQUE constraint violation`
**Solución:** Revisar índices y datos duplicados

### MySQL

**Problema:** `Deadlock detected`
**Solución:** Revisar orden de operaciones, usar transacciones

## Próximos Pasos

- [Configuración de engines](../guide/configuration.md)
- [Mejores prácticas](../guide/best-practices.md)
- [Troubleshooting](../reference/troubleshooting.md)
