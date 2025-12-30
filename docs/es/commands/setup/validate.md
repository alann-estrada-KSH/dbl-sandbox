# dbl validate

Verificar que el esquema de la base de datos es válido y consistente con las capas.

## Sinopsis

```bash
dbl validate
dbl validate --check-layers
dbl validate --check-schema
dbl validate --fix
```

## Descripción

Valida la integridad de tu base de datos y las capas de DBL. Verifica que:

- Todas las capas se pueden ejecutar correctamente
- Esquema está sincronizado con capas
- No hay inconsistencias
- Integridad referencial es correcta

## Ejemplo de Uso

```bash
dbl validate
```

**Salida:**
```
Validating database...

Layers:
  ✓ All 15 layers are valid
  ✓ Layers can be replayed

Schema:
  ✓ 42 tables found
  ✓ 28 indexes found
  ✓ 12 constraints valid
  ✓ No orphaned objects

Consistency:
  ✓ Schema matches layers
  ✓ Referential integrity OK
  ✓ All columns properly typed

✓ Database validation complete (2.3s)
```

## Opciones

### `--check-layers`

Solo validar capas:

```bash
$ dbl validate --check-layers

Checking layers...
  ✓ L001_initial_schema.sql - OK
  ✓ L002_add_users.sql - OK
  ✓ L003_add_posts.sql - OK
  ...
✓ All layers valid
```

### `--check-schema`

Solo validar esquema:

```bash
$ dbl validate --check-schema

Checking schema...
  ✓ All tables reachable
  ✓ All indexes valid
  ✓ No broken constraints
  ✓ Referential integrity OK
```

### `--fix`

Intentar arreglar problemas encontrados:

```bash
$ dbl validate --fix

Found 3 issues:
  ⚠ Missing index on users.email
  ⚠ Unused table: old_data
  ⚠ Invalid constraint: fk_users_posts

Attempting fixes...
  ✓ Created index idx_users_email
  ⚠ Old_data not removed (manual review needed)
  ✓ Recreated constraint
```

## Ejemplos Completos

### Validación Básica

```bash
$ dbl validate

✓ Database valid
  Layers: 12
  Tables: 35
  Indexes: 18
```

### Validación Detallada

```bash
$ dbl validate --verbose

Validating layers...
  L001_initial_schema.sql
    - 5 tables
    - 2 indexes
    ✓ OK
  
  L002_add_users.sql
    - 1 table (users)
    - 2 indexes
    - 3 constraints
    ✓ OK
    
  ... (12 capas más) ...

Schema validation...
  Tables:
    ✓ users (35 rows)
    ✓ posts (142 rows)
    ✓ comments (892 rows)
    ...
  
  Constraints:
    ✓ fk_posts_users
    ✓ fk_comments_posts
    ✓ fk_comments_users
    ...

✓ All valid
```

## Validaciones Realizadas

### Validación de Capas

```
✓ Todas las capas existen
✓ Sintaxis SQL es correcta
✓ Capas se pueden ejecutar
✓ No hay duplicados
✓ Nombrado correctamente
```

### Validación de Esquema

```
✓ Todas las tablas accesibles
✓ Todas las columnas tipadas
✓ Índices son válidos
✓ Constraints son válidos
✓ Integridad referencial OK
```

### Validación de Consistencia

```
✓ Esquema coincide con capas
✓ No hay objetos huérfanos
✓ No hay conflictos de nombres
✓ Permisos correctos
```

## Casos de Uso

### Después de Migrations

```bash
# Ejecutar migraciones
dbl reset

# Validar que todo está bien
$ dbl validate
✓ Database valid
```

### Antes de Deploy

```bash
#!/bin/bash
# pre-deploy-check.sh

# Validar antes de desplegar
if dbl validate --check-layers; then
    echo "✓ Layers valid, safe to deploy"
    dbl sandbox apply
else
    echo "✗ Layers have issues"
    exit 1
fi
```

### Debugging de Problemas

```bash
# Algo está mal?
$ dbl validate

✗ Database validation failed

Issues found:
  ⚠ Layer L008 uses undefined column
  ⚠ Table users has no primary key
  ⚠ Missing index on posts.user_id

# Arreglar
$ dbl validate --fix
```

### CI/CD Validation

```yaml
# .github/workflows/validate.yml
name: Validate Database

on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Run validation
        run: dbl validate --check-layers
        
      - name: Check schema consistency
        run: dbl validate --check-schema
```

## Problemas Comunes

### Capas Con Errores

**Error:**
```
✗ Layer L015 has syntax error
  Line 12: Unexpected token
  ... CREATE TABLE users (
       ^
```

**Solución:**
```bash
# Revisar y arreglar SQL
$ vim .dbl/layers/L015_*.sql

# Revalidar
$ dbl validate
```

### Esquema Desincronizado

**Error:**
```
✗ Schema doesn't match layers
  Expected table 'comments' from L008
  Not found in actual schema
```

**Solución:**
```bash
# Reconstruir desde capas
$ dbl reset

# Revalidar
$ dbl validate
```

### Integridad Referencial Rota

**Error:**
```
✗ Referential integrity violation
  posts.user_id references non-existent user
  Orphaned rows: 42
```

**Solución:**
```bash
# Encontrar y limpiar datos huérfanos
$ psql myapp -c "
  DELETE FROM posts 
  WHERE user_id NOT IN (SELECT id FROM users);
"

# Revalidar
$ dbl validate
```

### Índices Faltantes

**Error:**
```
⚠ Missing index on users.email
  Suggested: CREATE INDEX idx_users_email ON users(email)
```

**Solución:**
```bash
# Crear en sandbox
$ dbl sandbox start
$ psql -d myapp_sandbox -c "CREATE INDEX idx_users_email ON users(email);"
$ dbl commit -m "Add index on users.email"
$ dbl sandbox apply

# Revalidar
$ dbl validate
```

## Reparación Automática

### Con --fix

```bash
$ dbl validate --fix

Attempting to fix issues:
  [1/3] Creating missing index idx_users_email
    ✓ Created
  
  [2/3] Removing orphaned table old_users
    ✓ Removed
  
  [3/3] Rebuilding constraint fk_posts_users
    ✓ Rebuilt

✓ Fixed 3 issues
```

### Reparación Manual

```bash
# 1. Identificar problema
$ dbl validate
✗ Issue: ...

# 2. Investigar
$ dbl diff
$ cat .dbl/layers/L015_*.sql

# 3. Arreglar
$ dbl sandbox start
$ # ... hacer cambios ...
$ dbl commit -m "Fix validation issue"
$ dbl sandbox apply

# 4. Revalidar
$ dbl validate
✓ All valid
```

## Integración en Desarrollo

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validar antes de commit
if ! dbl validate --check-layers; then
    echo "Database validation failed"
    echo "Fix issues before committing"
    exit 1
fi
```

### Script de Deployment

```bash
#!/bin/bash
# deploy.sh

echo "Validating database schema..."
if dbl validate; then
    echo "✓ Validation passed"
    dbl sandbox apply
else
    echo "✗ Validation failed"
    exit 1
fi
```

## Reportes de Validación

### Generar Reporte

```bash
$ dbl validate --verbose > validation-report.txt
$ cat validation-report.txt

✓ Layer validation: PASSED
✓ Schema validation: PASSED
✓ Consistency check: PASSED
✓ Integrity check: PASSED
```

### Programa Monitor

```bash
#!/bin/bash
# monitor-validation.sh

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
STATUS=$(dbl validate && echo "PASS" || echo "FAIL")

echo "[$TIMESTAMP] Validation: $STATUS" >> validation.log
```

## Mejores Prácticas

1. **Validar regularmente**: Ejecutar después de cambios importantes
2. **Pre-deployment**: Siempre validar antes de desplegar
3. **CI/CD**: Incluir en pipeline de tests
4. **Arreglar rápido**: No ignorar advertencias
5. **Documentar**: Anotar por qué cambios fueron necesarios

## Ver También

- [`dbl reset`](reset.md) - Reconstruir desde capas
- [`dbl sandbox start`](sandbox/start.md) - Crear sandbox limpio
- [`dbl diff`](diff.md) - Ver cambios
- [`dbl log`](../history/log.md) - Ver historial
