# dbl sandbox apply

Aplicar cambios del sandbox a la base de datos principal.

## Sinopsis

```bash
dbl sandbox apply
```

## Descripción

Aplica todos los cambios del sandbox a tu base de datos principal, haciéndolos permanentes. También limpia automáticamente la base de datos sandbox.

## Qué Hace

1. **Valida estado del sandbox** - Asegura que sandbox esté activo y tenga commits
2. **Aplica capas** - Ejecuta SQL de capas en base principal
3. **Actualiza estado** - Marca capas como aplicadas
4. **Elimina sandbox** - Borra base de datos temporal
5. **Limpia metadata** - Elimina archivos de rastreo

## Ejemplo de Uso

```bash
# Flujo completo
dbl sandbox start
# Hacer cambios...
dbl diff
dbl commit -m "Add user preferences"
dbl sandbox apply
```

**Salida:**
```
Applying sandbox changes to main database...
✓ Executing layer L005
✓ Changes applied successfully
✓ Sandbox database dropped
✓ Sandbox metadata cleared

Your main database (myapp) now includes all sandbox changes.
```

## Flujo Detallado

### Paso a Paso

```bash
# 1. Crear sandbox
$ dbl sandbox start
✓ Sandbox created: myapp_sandbox

# 2. Hacer cambios
$ psql -d myapp_sandbox -c "
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT,
    read BOOLEAN DEFAULT false
);
"

# 3. Revisar cambios
$ dbl diff
+ CREATE TABLE notifications (...)

# 4. Guardar
$ dbl commit -m "Add notifications feature"
✓ Layer L008 created

# 5. Aplicar a principal
$ dbl sandbox apply
✓ Applied layer L008 to myapp
✓ Sandbox cleaned up

# 6. Verificar
$ psql -d myapp -c "\dt"
         List of relations
 Schema |      Name       | Type  
--------+-----------------+-------
 public | users           | table
 public | posts           | table
 public | notifications   | table  ← ¡Nuevo!
```

## Características de Seguridad

### Verificaciones Previas

DBL valida antes de aplicar:

- ✅ Sandbox está activo
- ✅ Hay commits para aplicar
- ✅ Base principal es accesible
- ✅ No hay cambios conflictivos

### Solo Se Aplican Commits

Solo se aplican **capas guardadas** (commits):

```bash
# Sandbox tiene cambios sin guardar
$ dbl diff
+ ALTER TABLE users ADD COLUMN email TEXT;

$ dbl sandbox apply
Error: Uncommitted changes detected
Commit your changes first with: dbl commit -m "message"

# Después de guardar
$ dbl commit -m "Add email column"
$ dbl sandbox apply
✓ Applied successfully
```

## Ejemplo Completo

### Agregar Feature de Comentarios

```bash
# 1. Iniciar sandbox
$ dbl sandbox start
✓ Sandbox: myapp_sandbox

# 2. Agregar tablas
$ psql -d myapp_sandbox << EOF
-- Tabla de comentarios
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_comments_post ON comments(post_id);
CREATE INDEX idx_comments_user ON comments(user_id);
EOF

# 3. Revisar
$ dbl diff
+ CREATE TABLE comments (...)
+ CREATE INDEX idx_comments_post ...
+ CREATE INDEX idx_comments_user ...

# 4. Guardar
$ dbl commit -m "Add comments feature with indexes"
✓ Layer L012 created

# 5. Aplicar a principal
$ dbl sandbox apply

Applying sandbox changes to main database (myapp)...
  → Executing L012_add_comments_feature.sql
  → Creating table comments
  → Creating indexes
✓ All changes applied successfully

Cleaning up sandbox...
  → Dropping database myapp_sandbox
  → Removing sandbox metadata
✓ Sandbox cleaned up

Summary:
  Database: myapp
  Layers applied: 1 (L012)
  Tables added: 1 (comments)
  Indexes added: 2
```

## Estado de la Base de Datos

### Antes y Después

```
Antes:
  Base Principal: myapp          (esquema antiguo)
  Sandbox: myapp_sandbox         (esquema nuevo)

Después:
  Base Principal: myapp          (esquema nuevo) ✓
  Sandbox: (eliminado)
```

### Archivos Actualizados

```
.dbl/
├── state.json          ← Actualizado (no hay sandbox activo)
├── layers/
│   └── L012_*.sql      ← Aplicada a principal
└── sandbox.json        ← Eliminado
```

## Notas Importantes

!!! danger "Cambios Permanentes"
    Después de `sandbox apply`, los cambios están en tu base de datos principal. **No hay deshacer** excepto con backups.

!!! warning "Posible Downtime"
    Algunas operaciones pueden bloquear tablas brevemente. Planifica en horarios de bajo uso.

!!! tip "Prueba Primero"
    Usa `dbl reset` en ambiente de prueba para verificar que las capas se replayan correctamente.

## Alternativa de Rollback

Si no estás listo para aplicar:

```bash
# Descartar sandbox
dbl sandbox rollback

# Sandbox y cambios se eliminan
# Base principal sin cambios
```

## Despliegue en Producción

### Aplicación Segura en Producción

```bash
# 1. Hacer backup primero
pg_dump myapp_prod > backup_$(date +%Y%m%d).sql

# 2. Probar en staging
dbl --config staging.yaml sandbox apply

# 3. Verificar que app funciona
./run-tests.sh

# 4. Aplicar a producción (en ventana de mantenimiento)
dbl --config production.yaml sandbox apply

# 5. Verificar
./verify-schema.sh
```

### Despliegue sin Downtime

Usa patrón expand-contract:

```bash
# Semana 1: Expand (agregar columnas)
dbl sandbox start
ALTER TABLE users ADD COLUMN email TEXT;
dbl commit -m "expand: Add email column"
dbl sandbox apply
# Deploy app v1.1 (lee de ambas columnas)

# Semana 2: Backfill
dbl sandbox start
UPDATE users SET email = username || '@example.com';
dbl commit -m "backfill: Populate email"
dbl sandbox apply

# Semana 3: Contract (aplicar constraints)
dbl sandbox start
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
dbl commit -m "contract: Make email required"
dbl sandbox apply
# Deploy app v1.2 (usa solo columna nueva)
```

## Manejo de Errores

### Cambios Conflictivos

**Error:**
```
Error: Main database has conflicting changes
The following tables were modified outside of DBL:
  - users (column added)
```

**Solución:**
1. Revisar cambios en base principal
2. Decidir: fusionar o resetear
3. Si se fusionan, hacer commit manualmente
4. Si se resetean, usar `dbl reset`

### Conexión Perdida

**Error:**
```
Error: Lost connection to main database
```

**Solución:**
- Sandbox permanece intacto
- Arreglar conexión
- Ejecutar `dbl sandbox apply` de nuevo
- Cambios ya aplicados se omiten (idempotente)

### Permisos Insuficientes

**Error:**
```
Error: Permission denied
User 'dbl_user' cannot DROP TABLE
```

**Solución:**
```sql
-- Otorgar permisos
ALTER USER dbl_user WITH SUPERUSER;
-- O grants específicos
GRANT ALL ON DATABASE myapp TO dbl_user;
```

## Consideraciones de Rendimiento

### Bases Grandes

Para bases > 100GB:

- **Tiempo**: Apply puede tomar varios minutos
- **Locks**: Algunas operaciones bloquean tablas
- **Monitoreo**: Usar `pg_stat_activity` para progreso

### Optimizar Apply

```bash
# Para migraciones de datos grandes
dbl commit -m "Add indexes" --with-data

# Índices creados DESPUÉS de datos cargados (más rápido)
```

## Integración CI/CD

### Despliegue Automatizado

```yaml
# .github/workflows/deploy.yml
name: Deploy Database Changes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Apply sandbox
        run: |
          dbl sandbox start
          # Run migrations
          dbl reset
          dbl sandbox apply
          
      - name: Verify
        run: ./verify-schema.sh
```

## Próximos Pasos

Después de aplicar:

- **Verificar cambios**: Revisar que base principal tenga esquema esperado
- **Probar aplicación**: Asegurar que app funciona con nuevo esquema
- **Monitorear logs**: Buscar errores
- **Actualizar documentación**: Documentar cambios de esquema

## Ver También

- [`dbl sandbox start`](start.md) - Crear sandbox
- [`dbl sandbox rollback`](rollback.md) - Descartar cambios
- [`dbl diff`](../changes/diff.md) - Revisar cambios
- [`dbl commit`](../changes/commit.md) - Guardar cambios
- [`dbl reset`](../changes/reset.md) - Reconstruir base de datos
