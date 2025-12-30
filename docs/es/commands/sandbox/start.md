# dbl sandbox start

Crear un sandbox temporal para desarrollo seguro.

## Sinopsis

```bash
dbl sandbox start
```

## Descripción

Crea una copia temporal de tu base de datos donde puedes experimentar libremente sin afectar la base principal. El sandbox es una base de datos completamente funcional con el mismo esquema que tu base principal.

## Qué Hace

1. **Copia esquema**: Duplica estructura de la base principal
2. **Crea base sandbox**: Genera `{database}_sandbox`
3. **Rastrea estado**: Marca sandbox como activo
4. **Preserva original**: Base principal permanece intacta

## Ejemplo de Uso

```bash
dbl sandbox start
```

**Salida:**
```
Creating sandbox for database 'myapp'...
✓ Copied schema from myapp
✓ Sandbox database created: myapp_sandbox
✓ Sandbox is now active

You can now make changes safely in the sandbox.
Connection: myapp_sandbox
```

## Usar el Sandbox

### Conectar al Sandbox

El sandbox es una base de datos real que puedes usar con cualquier herramienta:

=== "PostgreSQL"
    ```bash
    # psql
    psql -d myapp_sandbox
    
    # Aplicación
    DATABASE_URL=postgresql://user:pass@localhost/myapp_sandbox
    ```

=== "MySQL"
    ```bash
    # mysql
    mysql -u user -p myapp_sandbox
    
    # Aplicación
    DATABASE_URL=mysql://user:pass@localhost/myapp_sandbox
    ```

### Hacer Cambios

```sql
-- Agregar nueva tabla
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agregar índice
CREATE INDEX idx_notifications_user ON notifications(user_id);

-- Modificar tabla existente
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
```

## Ejemplo Completo

### Agregar Sistema de Notificaciones

```bash
# 1. Crear sandbox
$ dbl sandbox start
✓ Sandbox: myapp_sandbox

# 2. Conectar y hacer cambios
$ psql -d myapp_sandbox << EOF
-- Tabla de notificaciones
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para rendimiento
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read) 
WHERE read = false;

-- Tabla de preferencias de notificación
CREATE TABLE notification_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    email_enabled BOOLEAN DEFAULT true,
    push_enabled BOOLEAN DEFAULT true,
    sms_enabled BOOLEAN DEFAULT false
);
EOF

# 3. Verificar cambios
$ dbl diff
+ CREATE TABLE notifications (...)
+ CREATE TABLE notification_preferences (...)
+ CREATE INDEX idx_notifications_user ...

# 4. Probar con tu aplicación
$ DATABASE=myapp_sandbox npm test

# 5. Si funciona, guardar
$ dbl commit -m "Add notification system"
✓ Layer L008 created

# 6. Aplicar a principal
$ dbl sandbox apply
✓ Applied to myapp
```

## Características del Sandbox

### Aislamiento Completo

```
Base Principal (myapp)     Sandbox (myapp_sandbox)
├── users                  ├── users (copia)
├── posts                  ├── posts (copia)
└── comments               ├── comments (copia)
                          └── notifications (¡NUEVO!)

Cambios en sandbox → No afectan principal
```

### Múltiples Cambios

Puedes hacer múltiples commits en un sandbox:

```bash
# Sandbox activo
dbl sandbox start

# Cambio 1
psql -d myapp_sandbox -c "CREATE TABLE tags (...);"
dbl commit -m "Add tags table"

# Cambio 2
psql -d myapp_sandbox -c "CREATE TABLE post_tags (...);"
dbl commit -m "Add post-tag relationship"

# Cambio 3
psql -d myapp_sandbox -c "CREATE INDEX idx_post_tags (...);"
dbl commit -m "Add indexes for tags"

# Aplicar todos los cambios
dbl sandbox apply
```

## Casos de Uso

### Desarrollo de Feature

```bash
# Nueva feature: sistema de comentarios
dbl sandbox start

# Implementar tablas
psql -d myapp_sandbox << EOF
CREATE TABLE comments (...);
CREATE TABLE comment_votes (...);
EOF

# Probar con aplicación
npm test

# Si funciona, guardar
dbl commit -m "Add comment system"
dbl sandbox apply
```

### Experimentación

```bash
# Probar un nuevo índice
dbl sandbox start
psql -d myapp_sandbox -c "CREATE INDEX idx_new ON users(email);"

# Medir rendimiento
psql -d myapp_sandbox -c "EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';"

# Si mejora, guardar
dbl commit -m "Add email index for performance"
dbl sandbox apply

# Si no, descartar
dbl sandbox rollback
```

### Refactorización

```bash
# Renombrar columnas
dbl sandbox start

psql -d myapp_sandbox << EOF
ALTER TABLE users RENAME COLUMN name TO full_name;
ALTER TABLE posts RENAME COLUMN body TO content;
EOF

# Actualizar aplicación para usar nuevos nombres
# Probar...

# Si todo funciona
dbl commit -m "Refactor: rename columns for clarity"
dbl sandbox apply
```

## Estado del Sandbox

### Verificar Sandbox Activo

```bash
dbl sandbox status
```

**Salida:**
```
Active Sandbox: myapp_sandbox
Base Database: myapp
Created: 2024-12-30 10:23:15

Uncommitted Changes:
  + 2 tables added
  + 3 indexes added

Status: Ready to commit
```

### Información del Sandbox

```bash
# Ver base de datos sandbox
psql -l | grep sandbox

# o en MySQL
mysql -e "SHOW DATABASES LIKE '%sandbox%';"
```

## Notas Importantes

!!! warning "Un Sandbox a la Vez"
    Solo puedes tener un sandbox activo por base de datos.

!!! tip "Prueba Libremente"
    El sandbox es desechable. Experimenta sin miedo.

!!! info "Datos No Copiados"
    Solo se copia el esquema, no los datos. Esto hace que sea rápido.

## Limitaciones

### Solo Esquema

```bash
# Sandbox copia:
✓ Tablas
✓ Columnas
✓ Índices
✓ Constraints
✓ Views
✓ Funciones
✓ Triggers

# Sandbox NO copia:
✗ Datos de filas
✗ Secuencias (valores se resetean)
✗ Permisos específicos de usuarios
```

### Solución: Seed Data

```bash
# Después de crear sandbox
dbl sandbox start

# Cargar datos de prueba
psql -d myapp_sandbox -f test/fixtures/seed_data.sql
```

## Errores Comunes

### "Sandbox already exists"

```bash
# Ya tienes un sandbox activo
$ dbl sandbox start
Error: Sandbox 'myapp_sandbox' already exists

# Soluciones:
# 1. Aplicar sandbox existente
dbl sandbox apply

# 2. O descartarlo
dbl sandbox rollback

# 3. Luego crear nuevo
dbl sandbox start
```

### "Database connection failed"

```bash
# Verificar conexión
psql -d myapp  # o mysql

# Revisar dbl.yaml
cat dbl.yaml
```

### "Permission denied"

```sql
-- PostgreSQL: Otorgar permisos
ALTER USER myuser WITH CREATEDB;

-- MySQL: Otorgar permisos
GRANT ALL PRIVILEGES ON *.* TO 'myuser'@'localhost';
```

## Integración con Herramientas

### Con ORMs

```python
# Django settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'myapp_sandbox'),
        # ...
    }
}
```

```javascript
// Node.js / Sequelize
const sequelize = new Sequelize(
  process.env.DB_NAME || 'myapp_sandbox',
  // ...
);
```

### Con Testing

```bash
#!/bin/bash
# test-migrations.sh

# Crear sandbox para tests
dbl sandbox start

# Ejecutar migraciones
dbl reset

# Correr tests
npm test

# Limpiar
dbl sandbox rollback
```

### En CI/CD

```yaml
# .github/workflows/test.yml
- name: Test database changes
  run: |
    dbl sandbox start
    dbl reset
    npm test
    dbl sandbox rollback
```

## Siguientes Pasos

Después de crear un sandbox:

1. [Ver cambios](../changes/diff.md) - `dbl diff`
2. [Guardar cambios](../changes/commit.md) - `dbl commit`
3. [Aplicar a principal](apply.md) - `dbl sandbox apply`
4. [Descartar cambios](rollback.md) - `dbl sandbox rollback`

## Ver También

- [`dbl sandbox status`](status.md) - Estado del sandbox
- [`dbl sandbox apply`](apply.md) - Aplicar cambios
- [`dbl sandbox rollback`](rollback.md) - Descartar cambios
- [`dbl diff`](../changes/diff.md) - Ver diferencias
- [Mejores Prácticas](../../guide/best-practices.md) - Patrones de uso
