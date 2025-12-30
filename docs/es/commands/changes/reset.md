# dbl reset

Reconstruir la base de datos principal desde las capas guardadas.

## Sinopsis

```bash
dbl reset
```

## Descripción

Elimina todo del esquema en la base de datos principal y lo reconstruye desde cero ejecutando todas las capas en orden. Útil para verificar que tus capas se replayan correctamente.

## Qué Hace

1. **Respalda datos** (opcional) - Crea backup antes de reset
2. **Limpia esquema** - Elimina todas las tablas, índices, etc.
3. **Ejecuta capas** - Aplica cada capa en orden desde cero
4. **Valida** - Verifica integridad del resultado

## Ejemplo de Uso

```bash
dbl reset
```

**Salida:**
```
Resetting database to initial state...
Backing up current schema...
✓ Backup created: myapp_backup_20241230.sql

Clearing existing schema...
✓ Dropped 45 tables, 28 indexes, 12 constraints

Replaying layers from scratch...
  ✓ L001 - Initial schema (0.1s)
  ✓ L002 - Add users table (0.2s)
  ✓ L003 - Add posts table (0.3s)
  ✓ L004 - Add comments (0.1s)
  ✓ L005 - Add indexes (2.1s)

Schema validation:
  ✓ 45 tables
  ✓ 28 indexes
  ✓ 12 constraints
  ✓ Referential integrity OK

Reset complete in 2.8s
```

## Cuándo Usar

### ✅ Usa Reset Cuando:

- **Verificar capas**: Asegurar que se replayan correctamente
- **Ambiente limpio**: Necesitas empezar desde cero
- **Eliminar datos**: Limpiar base de datos en desarrollo
- **Resolver corrupción**: Reconstruir después de errores
- **Testing**: Recrear estado inicial en tests

### ❌ No Uses Cuando:

- **Producción**: ¡Peligro de pérdida de datos!
- **Datos importantes**: Usar en dev/test solamente
- **Querydepis guardadas**: Verificarlas antes de reset

## Ejemplos Detallados

### Resetear Desarrollo

```bash
# Base de datos con datos de prueba old
$ dbl reset

Resetting blog database...
✓ Backed up as blog_backup_20241230.sql
✓ Cleared 50 tables
✓ Replayed 12 layers
✓ Done in 3.2s

# Ahora tienes esquema limpio desde capas
```

### Verificar Que Capas Sean Correctas

```bash
# Crear sandbox con cambios
$ dbl sandbox start
$ psql -d blog_sandbox -c "ALTER TABLE posts ADD COLUMN featured BOOLEAN;"
$ dbl commit -m "Add featured column"
$ dbl sandbox apply

# Verificar que se replaya correctamente
$ dbl reset  # Reconstruir desde cero
$ psql -d blog -c "\d posts"  # Verificar featured existe

      Column      |  Type
------------------+---------
 id               | integer
 title            | text
 featured         | boolean  ← ¡Correcto!
```

### Resolver Errores de Replayabilidad

```bash
# Intentar reset
$ dbl reset
Error: Layer L008 failed to replay
  SQL Error in L008_add_comments.sql line 15:
  Column "user_id" does not exist

# Problema: L008 asume que existe "user_id" de L007
# Pero L007 tiene el nombre "author_id"

# Solución: Arreglar L008
$ nano .dbl/layers/L008_add_comments.sql
# Cambiar user_id a author_id

# Reintentar
$ dbl reset
✓ Reset successful
```

## Alternativas

### Sandbox Reset (Seguro)

Para probar reset sin afectar base principal:

```bash
# Crear sandbox limpio
$ dbl sandbox start

# Sandbox comienza desde cero automáticamente
# Ya está rebuildizado desde capas
$ dbl sandbox status
Status: Clean (freshly built)
```

### Reset Selectivo

Para resetear solo ciertos datos:

```bash
# Borrar solo datos, mantener esquema
$ psql -d myapp -c "
  TRUNCATE users, posts, comments CASCADE;
"

# O usar seed script
$ dbl seed --file seeds.sql
```

## Seguridad y Backups

### Backup Automático

DBL crea backup antes de reset:

```
myapp_backup_20241230_143022.sql
```

Puedes restaurar si algo sale mal:

```bash
$ psql myapp < myapp_backup_20241230_143022.sql
```

### Sin Backup en Ciertos Casos

```bash
# Force reset sin backup (¡cuidado!)
dbl reset --no-backup
```

!!! danger "Sin Backup = Datos Perdidos"
    Siempre hacer backup manual primero si es importante:
    ```bash
    pg_dump myapp > myapp_manual_backup.sql
    dbl reset
    ```

## Flujo Completo

### Desarrollo con Reset

```bash
# 1. Empezar
$ dbl init blog

# 2. Crear tabla usuarios
$ dbl sandbox start
$ psql -d blog_sandbox -c "CREATE TABLE users (...);"
$ dbl commit -m "Create users table"
$ dbl sandbox apply

# 3. Agregar columnas
$ dbl sandbox start
$ psql -d blog_sandbox -c "ALTER TABLE users ADD COLUMN email TEXT;"
$ dbl commit -m "Add email column"
$ dbl sandbox apply

# 4. Verificar que se replaya desde cero
$ dbl reset
✓ Database rebuilt from 2 layers

# 5. Agregar datos de test
$ psql blog < seeds.sql

# 6. Desarrollar
# ...

# 7. Limpiar para nuevo developer
$ dbl reset
```

## Casos de Uso

### Integración Continua

```yaml
# .github/workflows/test.yml
name: Test Schema

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Reset to clean state
        run: dbl reset
        
      - name: Run migrations
        run: ./migrations/run.sh
        
      - name: Run tests
        run: pytest tests/
```

### Onboarding de Developers

```bash
#!/bin/bash
# setup-dev.sh

# Nuevo developer ejecuta:
# 1. Clonar repo
git clone <repo>

# 2. Instalar DBL
pip install dbl

# 3. Crear base de datos limpia
dbl reset

# 4. Cargar datos de test
psql myapp < fixtures/seed.sql

echo "✓ Development environment ready!"
```

### Debugging de Capas

```bash
# Problema: Layer L015 no se aplica correctamente
$ dbl reset
Error: L015 failed

# Investigar
$ cat .dbl/layers/L015_*.sql

# Arreglar
$ vim .dbl/layers/L015_*.sql

# Reintentar
$ dbl reset
✓ Success
```

## Estados Post-Reset

### Después de Reset

```bash
# Base está limpia, sin cambios sin guardar
$ dbl sandbox status
No active sandbox

# Logs siguen ahí
$ dbl log
* L005 - Add indexes
* L004 - Add comments
...

# Puedes crear sandbox fresco
$ dbl sandbox start
$ dbl sandbox status
Status: Clean (freshly built)
```

## Ejemplos de Replayabilidad

### ❌ Problemas Comunes

```sql
-- MALO: Asume estado previo
ALTER TABLE users ADD COLUMN email TEXT;
-- ¿Y si la tabla no existe?

-- BUENO: Crea si no existe
CREATE TABLE IF NOT EXISTS users (...);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT;
```

### ✅ Prácticas Correctas

```sql
-- Usar IF NOT EXISTS en todo
CREATE TABLE IF NOT EXISTS users (...);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Estar explícito
CREATE SCHEMA IF NOT EXISTS public;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- Usar transacciones
BEGIN;
  -- Cambios atómicos
COMMIT;
```

## Limpieza de Backups

Los backups se acumulan. Limpiar periódicamente:

```bash
# Encontrar backups antiguos
find . -name "*_backup_*.sql" -mtime +30

# Eliminar backups más viejos de 30 días
find . -name "*_backup_*.sql" -mtime +30 -delete

# O manualmente
rm myapp_backup_20241220*.sql
```

## Mejores Prácticas

1. **Testear replayabilidad**: Ejecutar reset regularmente
2. **Usar IF NOT EXISTS**: Hacer capas idempotentes
3. **Ordenar capas**: Dependencias en orden correcto
4. **Backup antes**: Siempre hacer backup en datos importantes
5. **Documentar**: Anotar por qué cada cambio es necesario

## Ver También

- [`dbl sandbox start`](sandbox/start.md) - Crear sandbox limpio
- [`dbl commit`](commit.md) - Guardar cambios en capas
- [`dbl log`](../history/log.md) - Ver historial de capas
- [`dbl diff`](diff.md) - Comparar cambios
- [Troubleshooting](../../reference/troubleshooting.md) - Resolver problemas
