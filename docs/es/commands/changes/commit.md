# dbl commit

Guardar cambios del sandbox como una nueva capa versionada.

## Sinopsis

```bash
dbl commit -m "mensaje"              # Commit completo (esquema + datos)
dbl commit -m "mensaje" --schema-only  # Solo cambios de esquema
```

## Descripción

Guarda los cambios del sandbox como una "capa" (layer) - un archivo SQL versionado que puede ser replicado. Las capas son el equivalente de commits en Git, pero para esquemas de base de datos.

**Por defecto**, se incluyen tanto cambios de esquema (DDL) como datos (DML). Usa `--schema-only` para excluir cambios de datos.

## Opciones

| Opción | Descripción |
|--------|-------------|
| `-m, --message MSG` | Mensaje descriptivo del commit (requerido) |
| `--schema-only` | Guardar solo cambios de esquema (DDL), excluir datos (DML) |

## Ejemplo de Uso

```bash
dbl commit -m "Add notifications table"
```

**Salida:**
```
Creating layer from sandbox changes...
✓ Generated SQL from diff (schema+data)
✓ Layer L008 created: Add notifications table
✓ Layer saved to .dbl/layers/L008_add_notifications_table.sql

Your changes are now committed and can be applied.
```

## Ejemplo Completo

### Flujo de Trabajo Típico

```bash
# 1. Crear sandbox
$ dbl sandbox start
✓ Sandbox created: myapp_sandbox

# 2. Hacer cambios (esquema + datos)
$ psql -d myapp_sandbox << EOF
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_comments_post ON comments(post_id);
CREATE INDEX idx_comments_author ON comments(author_id);

-- Agregar datos de prueba
INSERT INTO comments (post_id, author_id, content) 
VALUES (1, 100, 'Comentario de prueba');
EOF

# 3. Revisar cambios
$ dbl diff
+ CREATE TABLE comments (...)
+ CREATE INDEX idx_comments_post ...
+ CREATE INDEX idx_comments_author ...
+ INSERT INTO comments (1 row changed)

# 4a. Guardar solo esquema (ignorar datos de prueba)
$ dbl commit -m "Add comments table with indexes" --schema-only
✓ Layer L005 created (schema)

# 4b. O guardar todo (esquema + datos)
$ dbl commit -m "Add comments table with sample data"
✓ Layer L005 created (schema+data)

# 5. Aplicar a base principal
$ dbl sandbox apply
✓ Changes applied to myapp
```

## Casos de Uso

### Commit con Datos (por defecto)

Útil cuando quieres migrar datos reales:

```bash
# Agregar datos de producción
psql -d myapp_sandbox -c "
INSERT INTO settings (key, value) VALUES 
    ('maintenance_mode', 'false'),
    ('api_version', 'v2');
"

# Commit incluye datos automáticamente
dbl commit -m "Add initial settings"
```

### Commit Solo Esquema

Útil cuando trabajas con datos de prueba que no quieres en producción:

```bash
# Hacer cambios con datos de prueba
psql -d myapp_sandbox -c "
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
INSERT INTO users (username, email, phone) VALUES 
    ('testuser', 'test@example.com', '555-0100');
"

# Commit solo el ALTER, no el INSERT
dbl commit -m "Add phone column" --schema-only
```

## Qué Crea un Commit

### Archivo de Capa

Cada commit crea un archivo:

```
.dbl/layers/L005_add_comments_table.sql
```

**Contenido:**
```sql
-- Layer: L005
-- Message: Add comments table with indexes
-- Date: 2024-12-30 14:32:11
-- Branch: main

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_comments_post ON comments(post_id);
CREATE INDEX idx_comments_author ON comments(author_id);
```

### Actualización de Estado

```json
// .dbl/state.json actualizado
{
  "database": "myapp",
  "branch": "main",
  "last_layer": "L005",  // ← actualizado
  "active_sandbox": "myapp_sandbox"
}
```

## Mensajes de Commit

### Buenos Mensajes

```bash
# ✅ Específico y claro
dbl commit -m "Add notifications table with user relationship"

# ✅ Describe el cambio
dbl commit -m "Add email_verified column to users table"

# ✅ Incluye contexto
dbl commit -m "Add indexes for post search performance"
```

### Malos Mensajes

```bash
# ❌ Vago
dbl commit -m "changes"

# ❌ Sin información
dbl commit -m "update"

# ❌ No descriptivo
dbl commit -m "fix"
```

### Convenciones

```bash
# Tipo: acción
dbl commit -m "feat: Add user preferences table"
dbl commit -m "fix: Correct foreign key constraint"
dbl commit -m "perf: Add index for email lookups"
dbl commit -m "refactor: Rename column user_name to username"
```

## Commits Múltiples

Puedes hacer múltiples commits en un sandbox:

```bash
# Sandbox activo
dbl sandbox start

# Commit 1: Tabla base
psql -d myapp_sandbox -c "CREATE TABLE tags (...);"
dbl commit -m "Add tags table"

# Commit 2: Relación
psql -d myapp_sandbox -c "CREATE TABLE post_tags (...);"
dbl commit -m "Add post-tag relationship"

# Commit 3: Índices
psql -d myapp_sandbox -c "CREATE INDEX idx_post_tags_post (...);"
dbl commit -m "Add indexes for tags"

# Ver todos los commits
dbl log -n 3

# Aplicar todos
dbl sandbox apply
```

## Commits con Datos

### Migración de Datos

```bash
# Hacer cambios de esquema Y datos
psql -d myapp_sandbox << EOF
-- Agregar columna
ALTER TABLE users ADD COLUMN full_name VARCHAR(200);

-- Migrar datos existentes
UPDATE users SET full_name = first_name || ' ' || last_name;

-- Eliminar columnas viejas
ALTER TABLE users DROP COLUMN first_name;
ALTER TABLE users DROP COLUMN last_name;
EOF

# Commit con flag de datos
dbl commit -m "Consolidate user names into full_name" --with-data
```

!!! warning "Precaución con Datos"
    El flag `--with-data` incluye las declaraciones UPDATE/INSERT en la capa. Úsalo solo cuando sea necesario.

## Casos de Uso

### Feature Development

```bash
# Nueva feature completa
dbl sandbox start

# Implementar tablas
psql -d myapp_sandbox -f migrations/feature-payments.sql

# Verificar
dbl diff

# Guardar
dbl commit -m "Add payment processing system"
dbl sandbox apply
```

### Hotfix

```bash
# Fix urgente
dbl sandbox start

# Corregir
psql -d myapp_sandbox << EOF
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE(email);
EOF

# Commit y aplicar rápido
dbl commit -m "hotfix: Add email constraints"
dbl sandbox apply
```

### Refactorización

```bash
# Mejorar estructura
dbl sandbox start

# Cambios de refactoring
psql -d myapp_sandbox << EOF
-- Renombrar para claridad
ALTER TABLE usr RENAME TO users;
ALTER TABLE pst RENAME TO posts;

-- Normalizar nombres de columnas
ALTER TABLE users RENAME COLUMN usrnm TO username;
ALTER TABLE posts RENAME COLUMN usr_id TO user_id;
EOF

# Guardar
dbl commit -m "refactor: Normalize table and column names"
dbl sandbox apply
```

## Estructura de Capas

### Numeración Secuencial

```
.dbl/layers/
├── L001_initial_schema.sql
├── L002_add_users.sql
├── L003_add_posts.sql
├── L004_add_comments.sql
└── L005_add_notifications.sql
```

Capas se numeran automáticamente en secuencia.

### Metadata de Capa

Cada capa contiene:

```sql
-- Layer ID: L005
-- Message: Add notifications system
-- Created: 2024-12-30 14:32:11
-- Author: developer@example.com (si está configurado)
-- Branch: main

-- Actual SQL changes
CREATE TABLE ...
```

## Validación de Commits

### Verificar Antes de Commit

```bash
# 1. Ver cambios
dbl diff

# 2. Verificar que se ve bien
# Si hay errores, corregir en sandbox

# 3. Commit solo cuando esté seguro
dbl commit -m "Mensaje"
```

### Validación Automática

```bash
# Validar capa después de crear
dbl commit -m "Add feature"
dbl validate --layers

# Si hay errores, la capa tiene problemas
```

## Integración con Control de Versiones

### Guardar en Git

```bash
# Después de commit
dbl commit -m "Add notifications"

# Agregar a Git
git add .dbl/layers/
git commit -m "Database: Add notifications system"
git push

# Tu equipo puede aplicar
git pull
dbl reset  # Reconstruir con nuevas capas
```

### Workflow de Equipo

```bash
# Developer 1
dbl commit -m "Add user profiles"
git push

# Developer 2
git pull
dbl reset  # Obtener cambios de Dev 1
dbl sandbox start
# ... su trabajo ...
dbl commit -m "Add comments"
git push
```

## Notas Importantes

!!! tip "Commits Atómicos"
    Haz commits pequeños y enfocados. Un commit = una funcionalidad.

!!! warning "No Editar Capas"
    Una vez creadas, no edites las capas manualmente. Crea nueva capa para correcciones.

!!! info "Mensajes Descriptivos"
    Usa mensajes claros. Tu equipo (y tú mismo en el futuro) lo agradecerá.

## Errores Comunes

### "No active sandbox"

```bash
# Necesitas un sandbox primero
dbl sandbox start
```

### "No changes detected"

```bash
# No hay cambios para guardar
dbl diff  # Verificar que hay cambios
```

### "Message required"

```bash
# Falta el mensaje
dbl commit -m "Tu mensaje aquí"
```

## Ejemplos Avanzados

### Commits Condicionales

```bash
#!/bin/bash
# commit-if-changes.sh

if dbl diff --summary | grep -q "Total: 0"; then
    echo "No changes to commit"
else
    dbl commit -m "Auto: $(date +%Y-%m-%d) changes"
fi
```

### Commits con Verificación

```bash
#!/bin/bash
# safe-commit.sh

# Mostrar cambios
echo "Changes to commit:"
dbl diff --summary

# Confirmar
read -p "Commit these changes? (y/n): " confirm

if [[ $confirm == "y" ]]; then
    read -p "Commit message: " msg
    dbl commit -m "$msg"
    echo "✓ Committed"
else
    echo "Cancelled"
fi
```

### Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validar que no hay sandbox sin commit
if dbl sandbox status 2>/dev/null | grep -q "Uncommitted"; then
    echo "Error: Tienes cambios sin commit en sandbox"
    echo "Ejecuta: dbl commit -m 'mensaje'"
    exit 1
fi
```

## Ver También

- [`dbl diff`](diff.md) - Ver cambios antes de commit
- [`dbl sandbox apply`](../sandbox/apply.md) - Aplicar commits
- [`dbl log`](../history/log.md) - Ver historial de commits
- [`dbl reset`](reset.md) - Reconstruir desde commits
- [Mejores Prácticas](../../guide/best-practices.md) - Guía de commits
