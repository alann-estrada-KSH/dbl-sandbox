# dbl diff

Mostrar diferencias entre el sandbox y la base de datos principal.

## Sinopsis

```bash
dbl diff                    # Ver todos los cambios
dbl diff --tables users     # Solo tabla específica
dbl diff --sql              # Solo SQL sin formato
```

## Descripción

Compara el esquema del sandbox con la base principal y muestra las diferencias en formato SQL. Esto te permite revisar exactamente qué cambios has hecho antes de guardarlos.

## Opciones

| Opción | Descripción |
|--------|-------------|
| `--tables T1,T2` | Mostrar diff solo para tablas específicas |
| `--sql` | Salida solo SQL sin formato |
| `--summary` | Solo resumen, sin SQL detallado |

## Ejemplo de Uso

```bash
dbl diff
```

**Salida:**
```sql
-- Changes in sandbox (not yet committed)

-- New tables
+ CREATE TABLE notifications (
+     id SERIAL PRIMARY KEY,
+     user_id INTEGER NOT NULL REFERENCES users(id),
+     message TEXT,
+     read BOOLEAN DEFAULT false,
+     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+ );

-- New indexes
+ CREATE INDEX idx_notifications_user ON notifications(user_id);

-- Modified tables
~ ALTER TABLE users ADD COLUMN last_login TIMESTAMP;

-- Summary
+ 1 table added (notifications)
+ 1 index added
~ 1 table modified (users)
  Total changes: 3
```

## Ejemplo Completo

### Desarrollo de Feature

```bash
# 1. Crear sandbox
$ dbl sandbox start

# 2. Agregar tabla de perfiles
$ psql -d myapp_sandbox << EOF
CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    avatar_url VARCHAR(500),
    location VARCHAR(100),
    website VARCHAR(200),
    twitter_handle VARCHAR(50),
    github_handle VARCHAR(50)
);

CREATE INDEX idx_profiles_location ON user_profiles(location);
EOF

# 3. Modificar tabla users
$ psql -d myapp_sandbox << EOF
ALTER TABLE users 
ADD COLUMN email_verified BOOLEAN DEFAULT false;
EOF

# 4. Ver todos los cambios
$ dbl diff
```

**Salida detallada:**
```sql
-- Changes in sandbox

-- New tables
+ CREATE TABLE user_profiles (
+     user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
+     bio TEXT,
+     avatar_url VARCHAR(500),
+     location VARCHAR(100),
+     website VARCHAR(200),
+     twitter_handle VARCHAR(50),
+     github_handle VARCHAR(50)
+ );

-- New indexes
+ CREATE INDEX idx_profiles_location ON user_profiles(location);

-- Modified tables
~ ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;

-- Summary
+ 1 table added (user_profiles)
+ 2 indexes added (user_profiles_pkey, idx_profiles_location)
~ 1 table modified (users: +1 column)
  Total changes: 4
```

## Tipos de Cambios

### Tablas Añadidas

```sql
+ CREATE TABLE comments (
+     id SERIAL PRIMARY KEY,
+     content TEXT NOT NULL
+ );
```

### Tablas Modificadas

```sql
~ ALTER TABLE users ADD COLUMN phone VARCHAR(20);
~ ALTER TABLE posts ADD COLUMN published_at TIMESTAMP;
```

### Tablas Eliminadas

```sql
- DROP TABLE temp_data;
```

### Índices

```sql
+ CREATE INDEX idx_users_email ON users(email);
- DROP INDEX idx_old_column;
```

### Constraints

```sql
+ ALTER TABLE posts 
+ ADD CONSTRAINT fk_author 
+ FOREIGN KEY (author_id) REFERENCES users(id);
```

## Filtrar Cambios

### Tabla Específica

```bash
dbl diff --tables users
```

**Salida:**
```sql
-- Changes for table: users
~ ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
~ ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0;
```

### Múltiples Tablas

```bash
dbl diff --tables users,posts,comments
```

### Solo Resumen

```bash
dbl diff --summary
```

**Salida:**
```
Summary of changes:
  + 2 tables added
  ~ 3 tables modified
  - 1 table dropped
  + 5 indexes added
  - 2 indexes dropped
  Total: 13 changes
```

## Casos de Uso

### Antes de Commit

```bash
# Revisar cambios antes de guardar
dbl diff

# Si se ven bien, guardar
dbl commit -m "Add user profiles feature"
```

### Code Review

```bash
# Generar diff para revisión
dbl diff > changes.sql

# Compartir con equipo
git add changes.sql
git commit -m "Database changes for review"
```

### Comparar con Capa Anterior

```bash
# Ver qué ha cambiado desde último commit
dbl diff

# vs historial
dbl log -n 1
```

### Depuración

```bash
# ¿Qué cambió?
dbl diff --summary

# Ver detalles de tabla problemática
dbl diff --tables problematic_table
```

## Formato de Salida

### Formato Estándar (default)

```sql
-- Comentarios explicativos
+ SQL para creaciones (verde)
~ SQL para modificaciones (amarillo)
- SQL para eliminaciones (rojo)

-- Summary al final
```

### Formato SQL Puro

```bash
dbl diff --sql
```

**Salida:**
```sql
CREATE TABLE notifications (...);
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
CREATE INDEX idx_notifications_user ON notifications(user_id);
```

Sin comentarios ni colores, listo para ejecutar.

## Integración con Herramientas

### Guardar en Archivo

```bash
# Para documentación
dbl diff > docs/migration-2024-12-30.sql

# Para revisión
dbl diff --sql > migration.sql
```

### Usar en Scripts

```bash
#!/bin/bash
# check-changes.sh

CHANGES=$(dbl diff --summary | grep "Total:")

if [[ $CHANGES == *"Total: 0"* ]]; then
    echo "No changes detected"
else
    echo "Changes found:"
    dbl diff --summary
fi
```

### Validar Antes de Aplicar

```bash
# Script de validación
dbl diff > /tmp/changes.sql

# Revisar SQL
if grep -q "DROP TABLE" /tmp/changes.sql; then
    echo "⚠️  Warning: Tables will be dropped!"
    read -p "Continue? (y/n): " confirm
    [[ $confirm == "y" ]] || exit 1
fi

dbl commit -m "Changes"
```

## Comparación con Git

DBL diff es similar a `git diff`:

| Git | DBL | Propósito |
|-----|-----|-----------|
| `git diff` | `dbl diff` | Ver cambios sin guardar |
| `git diff --staged` | (N/A) | DBL no tiene staging |
| `git diff HEAD~1` | `dbl log -n 1` | Ver último cambio |
| `git diff main` | (futuro) | Comparar ramas |

## Notas Importantes

!!! tip "Revisar Siempre"
    Siempre ejecuta `dbl diff` antes de `dbl commit` para verificar cambios.

!!! warning "Cambios Grandes"
    Para esquemas grandes, diff puede tomar tiempo. Usa `--tables` para filtrar.

!!! info "Solo Esquema"
    Diff solo muestra cambios de esquema, no datos.

## Solución de Problemas

### "No active sandbox"

```bash
# Necesitas crear un sandbox primero
dbl sandbox start
```

### Diff Toma Mucho Tiempo

```bash
# Filtrar por tablas específicas
dbl diff --tables tabla1,tabla2
```

### Diff Está Vacío

```bash
# Verificar que hiciste cambios
psql -d myapp_sandbox -c "\dt"

# Comparar manualmente
psql -d myapp -c "\dt"
psql -d myapp_sandbox -c "\dt"
```

## Ejemplos Avanzados

### Comparar Esquemas Complejos

```bash
# Ver cambios en estructura completa
dbl diff

# Ver solo nuevas tablas
dbl diff | grep "^+"

# Ver solo modificaciones
dbl diff | grep "^~"

# Ver solo eliminaciones
dbl diff | grep "^-"
```

### Generar Reporte

```bash
#!/bin/bash
# generate-report.sh

echo "# Database Changes Report" > report.md
echo "Date: $(date)" >> report.md
echo "" >> report.md
echo "## Summary" >> report.md
dbl diff --summary >> report.md
echo "" >> report.md
echo "## Detailed Changes" >> report.md
echo '```sql' >> report.md
dbl diff --sql >> report.md
echo '```' >> report.md
```

### CI/CD Integration

```yaml
# .github/workflows/db-changes.yml
- name: Show database changes
  run: |
    dbl diff --summary
    dbl diff > db-changes.sql
    
- name: Upload changes
  uses: actions/upload-artifact@v3
  with:
    name: db-changes
    path: db-changes.sql
```

## Ver También

- [`dbl commit`](commit.md) - Guardar cambios
- [`dbl sandbox status`](../sandbox/status.md) - Estado del sandbox
- [`dbl sandbox start`](../sandbox/start.md) - Crear sandbox
- [`dbl log`](../history/log.md) - Ver historial de cambios
