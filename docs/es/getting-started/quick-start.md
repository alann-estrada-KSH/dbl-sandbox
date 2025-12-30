# Inicio Rápido

Aprende los fundamentos de DBL en 10 minutos.

## Prerrequisitos

- DBL instalado ([Guía de Instalación](installation.md))
- Base de datos PostgreSQL o MySQL corriendo
- Conocimientos básicos de SQL

## Paso 1: Crear una Base de Datos

```bash
# PostgreSQL
createdb myapp

# MySQL
mysql -u root -e "CREATE DATABASE myapp;"
```

## Paso 2: Configurar DBL

Crea `dbl.yaml` en tu proyecto:

```yaml
database:
  name: myapp
  engine: postgres  # o 'mysql'
  host: localhost
  port: 5432        # o 3306 para MySQL
  user: tu_usuario
  password: ${DB_PASSWORD}
```

Exporta tu contraseña:

```bash
export DB_PASSWORD="tu_password"
```

## Paso 3: Inicializar DBL

```bash
dbl init
```

**Salida:**
```
Initializing DBL for database 'myapp'...
✓ Configuration validated
✓ Database connection successful
✓ DBL initialized

Your database is ready for version control!
```

## Paso 4: Crear un Sandbox

Un sandbox es una copia temporal de tu base de datos donde puedes experimentar sin riesgos.

```bash
dbl sandbox start
```

**Salida:**
```
Creating sandbox for 'myapp'...
✓ Sandbox database created: myapp_sandbox
✓ Sandbox is active

You can now make changes in the sandbox.
```

## Paso 5: Hacer Cambios

Crea una tabla en el sandbox:

=== "PostgreSQL"
    ```bash
    psql -d myapp_sandbox -c "
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    "
    ```

=== "MySQL"
    ```bash
    mysql -u tu_usuario -p myapp_sandbox -e "
    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    "
    ```

## Paso 6: Ver los Cambios

```bash
dbl diff
```

**Salida:**
```sql
-- Changes in sandbox (not yet committed)

+ CREATE TABLE users (
+     id SERIAL PRIMARY KEY,
+     username VARCHAR(50) UNIQUE NOT NULL,
+     email VARCHAR(255) UNIQUE NOT NULL,
+     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+ );

Summary:
  + 1 table added (users)
  + 2 indexes added (users_pkey, users_username_key)
  + 1 constraint added
```

## Paso 7: Guardar los Cambios

Guarda los cambios como una "capa" (layer):

```bash
dbl commit -m "Add users table"
```

**Salida:**
```
Creating layer from sandbox changes...
✓ Layer L001 created: Add users table
✓ Layer saved to .dbl/layers/L001_add_users_table.sql

Your changes are now committed.
```

## Paso 8: Aplicar al Proyecto Principal

Aplica los cambios a tu base de datos principal:

```bash
dbl sandbox apply
```

**Salida:**
```
Applying sandbox changes to main database...
  → Executing layer L001
✓ Changes applied successfully
✓ Sandbox database dropped
✓ Sandbox metadata cleared

Your main database (myapp) now includes all sandbox changes.
```

## ¡Felicitaciones! 🎉

Has completado tu primera migración con DBL. Ahora sabes cómo:

- ✅ Inicializar DBL en un proyecto
- ✅ Crear un sandbox para cambios seguros
- ✅ Ver diferencias entre sandbox y principal
- ✅ Guardar cambios como capas
- ✅ Aplicar cambios al proyecto principal

## Flujo de Trabajo Completo

Resumen del flujo que acabas de usar:

```bash
# 1. Inicializar
dbl init

# 2. Crear sandbox
dbl sandbox start

# 3. Hacer cambios en sandbox
psql -d myapp_sandbox  # o mysql

# 4. Ver cambios
dbl diff

# 5. Guardar cambios
dbl commit -m "Descripción"

# 6. Aplicar a principal
dbl sandbox apply
```

## Verificar el Resultado

```bash
# Verificar que la tabla existe en la base principal
psql -d myapp -c "\dt"
# o
mysql -u tu_usuario -p myapp -e "SHOW TABLES;"
```

**Salida:**
```
         List of relations
 Schema |  Name  | Type  | Owner
--------+--------+-------+-------
 public | users  | table | dbuser
```

## Ver Historial

```bash
dbl log
```

**Salida:**
```
* L001 - Add users table
  Date: 2024-12-30 10:15:33
  Branch: main
  
  Created users table with basic fields for authentication.
```

## Experimentar con Cambios

Puedes probar cambios sin afectar la base principal:

```bash
# Crear otro sandbox
dbl sandbox start

# Probar algo
psql -d myapp_sandbox -c "
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
"

# Ver cambios
dbl diff

# Si no te gusta, descarta todo
dbl sandbox rollback

# El sandbox se elimina, la base principal no se toca
```

## Conceptos Clave

### Sandbox
- Copia temporal de tu base de datos
- Lugar seguro para experimentar
- Puedes aplicar o descartar cambios

### Capas (Layers)
- Cambios guardados en archivos SQL
- Numeradas secuencialmente (L001, L002, ...)
- Se pueden reproducir en cualquier orden

### Estados
```
Main DB ──> Sandbox ──> Commit ──> Apply ──> Main DB actualizada
(estable)   (temporal)  (guardar)  (aplicar)  (con cambios)
```

## Comandos Esenciales

| Comando | Propósito |
|---------|-----------|
| `dbl init` | Inicializar DBL |
| `dbl sandbox start` | Crear sandbox |
| `dbl diff` | Ver cambios |
| `dbl commit -m "msg"` | Guardar cambios |
| `dbl sandbox apply` | Aplicar a principal |
| `dbl sandbox rollback` | Descartar sandbox |
| `dbl log` | Ver historial |
| `dbl reset` | Reconstruir desde capas |

## Ejemplo: Agregar Más Tablas

Ahora que entiendes el flujo, agrega más tablas:

```bash
# Sandbox
dbl sandbox start

# Posts table
psql -d myapp_sandbox << EOF
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_user_id ON posts(user_id);
EOF

# Commit
dbl commit -m "Add posts table with user relationship"

# Apply
dbl sandbox apply

# Verificar historial
dbl log
```

**Salida de `dbl log`:**
```
* L002 - Add posts table with user relationship
  Date: 2024-12-30 10:25:11
  
* L001 - Add users table
  Date: 2024-12-30 10:15:33
```

## Trabajar en Equipo

Comparte tus cambios con el equipo:

```bash
# Guardar capas en Git
git add .dbl/
git commit -m "Database: Add users and posts tables"
git push

# Tu equipo puede aplicar los cambios
git pull
dbl reset  # Reconstruye desde las capas
```

## Solución Rápida de Problemas

### "No active sandbox"

```bash
# Necesitas crear un sandbox primero
dbl sandbox start
```

### "Uncommitted changes detected"

```bash
# Guarda los cambios primero
dbl commit -m "Descripción de cambios"
```

### Error de conexión

```bash
# Verifica la conexión
psql -d myapp  # o mysql

# Revisa dbl.yaml
cat dbl.yaml
```

## Próximos Pasos

Ahora que dominas lo básico:

1. [Tu Primera Migración](first-migration.md) - Ejemplo más detallado
2. [Comandos](../commands/index.md) - Referencia completa
3. [Mejores Prácticas](../guide/best-practices.md) - Patrones recomendados
4. [Configuración](../guide/configuration.md) - Opciones avanzadas

## Ver También

- [Instalación](installation.md)
- [Comandos de Sandbox](../commands/sandbox/start.md)
- [FAQ](../reference/faq.md)
