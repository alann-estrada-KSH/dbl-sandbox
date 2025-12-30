# Troubleshooting

Soluciones para problemas comunes con DBL.

## Instalación

### `pip: command not found`

**Problema:**
```
pip: command not found
```

**Soluciones:**

1. Instalar Python 3:
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt-get install python3-pip

# Windows
# Descargar desde https://python.org
```

2. Usar `pip3` en lugar de `pip`:
```bash
pip3 install dbl
```

3. Usar `python -m pip`:
```bash
python -m pip install dbl
```

### `Python version too old`

**Problema:**
```
Error: DBL requires Python 3.7+
Current version: 3.6.9
```

**Solución:**

Actualizar Python a 3.7 o mayor:

```bash
# macOS
brew install python3

# Ubuntu
sudo apt-get install python3.9 python3.9-dev

# Windows
# Descargar desde https://python.org (marca "Add to PATH")
```

### `psycopg2 installation failed`

**Problema:**
```
error: could not create '/usr/lib/python3/dist-packages/psycopg2'
```

**Soluciones:**

1. Instalar dependencias de sistema:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libpq-dev

# macOS
brew install postgresql
```

2. Usar versión precompilada:
```bash
pip install psycopg2-binary
```

3. DBL lo instala automáticamente:
```bash
dbl update
```

## Conexión a Base de Datos

### `could not connect to server`

**Problema:**
```
Error: could not connect to server: Connection refused
Is the server running on host "localhost" (127.0.0.1) and accepting
TCP connections on port 5432?
```

**Checklist:**

1. ¿Servidor está corriendo?
```bash
# PostgreSQL
psql -U postgres -c "SELECT version();"

# MySQL
mysql -u root -p -e "SELECT VERSION();"
```

2. ¿Puerto correcto?
```bash
# Verificar puerto
dbl --verbose init

# En config
cat dbl.yaml
```

3. ¿Credenciales correctas?
```bash
# Probar conexión manualmente
psql -h localhost -U myuser -d mydb
```

4. ¿Firewall bloqueando?
```bash
# Verificar puerto abierto
netstat -an | grep 5432
```

### `authentication failed for user`

**Problema:**
```
Error: FATAL: password authentication failed for user "postgres"
```

**Soluciones:**

1. Verificar password:
```bash
# PostgreSQL, resetear password
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'newpassword';"
```

2. Archivo .pgpass (PostgreSQL):
```bash
# ~/.pgpass
localhost:5432:mydb:myuser:mypassword

chmod 600 ~/.pgpass
```

3. Usar variables de ambiente:
```bash
export PGPASSWORD="mypassword"
dbl init

# MySQL
export MYSQL_PWD="mypassword"
```

### `database does not exist`

**Problema:**
```
Error: database "myapp" does not exist
```

**Soluciones:**

1. Crear base de datos primero:
```bash
# PostgreSQL
createdb myapp

# MySQL
mysql -u root -p -e "CREATE DATABASE myapp;"
```

2. Verificar nombre en config:
```bash
cat dbl.yaml | grep database
```

3. Crear con DBL:
```bash
dbl init --auto-create
```

## Sandbox

### `sandbox database already exists`

**Problema:**
```
Error: Sandbox myapp_sandbox already exists
```

**Soluciones:**

1. Limpiar sandbox:
```bash
dbl sandbox rollback
```

2. Limpiar manualmente:
```bash
# PostgreSQL
dropdb myapp_sandbox

# MySQL
mysql -u root -p -e "DROP DATABASE myapp_sandbox;"
```

3. Editar estado:
```bash
rm .dbl/sandbox.json
```

### `sandbox already created` pero no veo cambios

**Problema:**
```
$ dbl sandbox status
Active Sandbox: myapp_sandbox
Status: Empty sandbox (no changes)

# Pero hice cambios...
```

**Soluciones:**

1. Verificar que los cambios se guardaron:
```bash
# Ver cambios en BD
$ dbl diff
```

2. Verificar conexión:
```bash
psql -d myapp_sandbox -c "\dt"
```

3. Si no hay cambios, no se guardaron (intenta de nuevo)

### `cannot drop database myapp_sandbox because it is being accessed`

**Problema:**
```
Error: database "myapp_sandbox" is being accessed by other users
```

**Soluciones:**

1. Cerrar otras conexiones:
```bash
# PostgreSQL
psql -c "SELECT pid FROM pg_stat_activity WHERE datname = 'myapp_sandbox';" 

# Terminar sesiones
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE datname = 'myapp_sandbox';"
```

2. Esperar y reintentar:
```bash
dbl sandbox rollback
```

## Commits y Capas

### `no uncommitted changes`

**Problema:**
```
Error: There are no uncommitted changes to commit
```

**Soluciones:**

1. Hacer cambios primero:
```bash
dbl sandbox start
psql -d myapp_sandbox -c "CREATE TABLE users (...);"
dbl diff  # Verificar
```

2. Revisar estado:
```bash
dbl sandbox status
```

### `layer file already exists`

**Problema:**
```
Error: Layer file L015_add_users.sql already exists
```

**Soluciones:**

1. Usar nombre diferente (DBL lo hace automáticamente)

2. Eliminar capa anterior:
```bash
rm .dbl/layers/L015_*.sql
dbl commit -m "Add users table"
```

### `conflict: layer modified in multiple branches`

**Problema:**
```
Error: Merge conflict in layer L020
Modificado en main: L020_add_feature_a.sql
Modificado en feature/b: L020_add_feature_b.sql
```

**Soluciones:**

1. Renombrar capas conflictivas:
```bash
dbl checkout main
# Capas L020-L030

dbl checkout feature/b
# Renombrar sus capas a L031+
```

2. Crear commit de merge:
```bash
dbl merge feature/b
# Resolver manual
dbl merge --continue
```

## Validación

### `layer validation failed`

**Problema:**
```
Error: Layer L015 failed validation
  SQL Error: column "user_id" does not exist
```

**Soluciones:**

1. Revisar la capa:
```bash
cat .dbl/layers/L015_*.sql
```

2. Verificar dependencias:
```bash
# ¿Existe la columna en capas previas?
grep -r "user_id" .dbl/layers/L014*
```

3. Arreglar:
```bash
# Editar L015
vim .dbl/layers/L015_*.sql

# Revalidar
dbl validate
```

### `schema inconsistency detected`

**Problema:**
```
Error: Schema doesn't match layers
Expected tables: users, posts, comments
Found tables: users, posts
Missing: comments
```

**Soluciones:**

1. Resetear base de datos:
```bash
dbl reset
```

2. Verificar capa faltante:
```bash
dbl log | grep comments
```

3. Si falta capa, reconstruir:
```bash
dbl sandbox start
# Recrear cambios manualmente
dbl commit -m "Recreate comments table"
dbl sandbox apply
```

## Rendimiento

### `reset takes too long`

**Problema:**
```
$ dbl reset
... esperando mucho tiempo ...
```

**Soluciones:**

1. Verificar operaciones costosas:
```bash
# Ver capas grandes
for f in .dbl/layers/*.sql; do
    lines=$(wc -l < "$f")
    echo "$lines - $f"
done | sort -rn | head
```

2. Optimizar capas:
```bash
# Fusionar pequeñas capas
cat .dbl/layers/L001_*.sql >> merged.sql
cat .dbl/layers/L002_*.sql >> merged.sql
```

3. Usar índices:
```sql
-- En lugar de escanear tabla completa
CREATE INDEX idx_users_email ON users(email);
```

## Errores SQL

### `syntax error`

**Problema:**
```
Error: syntax error at or near ";"
```

**Soluciones:**

1. Revisar SQL:
```bash
# Ver línea exacta del error
cat .dbl/layers/L015_*.sql | head -20
```

2. Sintaxis específica por BD:
```sql
-- PostgreSQL
CREATE TABLE IF NOT EXISTS users (...);

-- MySQL
CREATE TABLE IF NOT EXISTS users (...);
-- Igual en este caso

-- Pero diferente:
-- PostgreSQL: SERIAL
-- MySQL: AUTO_INCREMENT
```

3. Verificar SQL con herramienta:
```bash
psql -f .dbl/layers/L015_*.sql
```

### `permission denied`

**Problema:**
```
Error: permission denied for schema public
```

**Soluciones:**

1. Otorgar permisos:
```bash
# PostgreSQL
psql -U postgres -c "
GRANT ALL ON DATABASE myapp TO myuser;
GRANT ALL ON SCHEMA public TO myuser;
GRANT ALL ON ALL TABLES IN SCHEMA public TO myuser;
"
```

2. Usar usuario con permisos:
```yaml
# dbl.yaml
database:
  user: postgres  # Usuario admin
```

### `integer out of range`

**Problema:**
```
Error: integer out of range
```

**Soluciones:**

1. Usar tipo correcto:
```sql
-- En lugar de INT (max 2^31-1)
ALTER TABLE users ADD COLUMN large_id BIGINT;
```

2. Verificar valores:
```bash
SELECT MAX(id) FROM users;
```

## Ramas

### `branch not found`

**Problema:**
```
Error: Branch feature/auth not found
```

**Soluciones:**

1. Listar ramas:
```bash
dbl branch --list
```

2. Crear rama:
```bash
dbl branch create feature/auth
dbl checkout feature/auth
```

3. Nombre correcto:
```bash
# Nombres son case-sensitive
dbl checkout feature/auth  # Correcto
dbl checkout Feature/Auth  # Error
```

### `cannot merge: branches diverged`

**Problema:**
```
Error: Cannot merge - branches have diverged significantly
```

**Soluciones:**

1. Entender divergencia:
```bash
dbl log --branch main | wc -l
dbl log --branch feature/auth | wc -l
```

2. Resolver conflictos:
```bash
dbl merge feature/auth
# DBL marca conflictos

# Editar archivos conflictivos
vim .dbl/layers/...

# Marcar resuelto
dbl merge --continue
```

## Diferencias

### `diff shows everything as changed`

**Problema:**
```
$ dbl diff
Toda la BD parece cambiada...
```

**Soluciones:**

1. Problema de whitespace:
```bash
# Resetear para limpiar
dbl reset
dbl diff  # Ahora debería estar limpio
```

2. Problema de encoding:
```bash
# PostgreSQL mostrar como hexadecimal
psql -d myapp_sandbox -c "
SELECT encode(column, 'hex')
FROM table;
"
```

## CI/CD

### `dbl: command not found in GitHub Actions`

**Problema:**
```
Error: dbl: command not found
```

**Solución:**

Instalar en workflow:

```yaml
- name: Install DBL
  run: pip install dbl
  
- name: Validate
  run: dbl validate
```

### `database locked` en tests paralelos

**Problema:**
```
Error: database is locked
```

**Solución:**

Usar diferentes bases de datos:

```yaml
strategy:
  matrix:
    python-version: [3.8, 3.9]
    
env:
  DB_NAME: testdb_${{ matrix.python-version }}
```

## Getting Help

### Obtener información de debug

```bash
# Verbose output
dbl --verbose init

# Ver versión
dbl version

# Ver configuración
cat dbl.yaml

# Ver estado
dbl sandbox status
```

### Reportar un bug

1. Recopilar información:
```bash
dbl version --verbose > debug.txt
dbl validate --verbose >> debug.txt
```

2. Abrir issue en GitHub con debug.txt

### Contacto

- GitHub: https://github.com/dbl-project
- Issues: https://github.com/dbl-project/issues
- Discussions: https://github.com/dbl-project/discussions

## Próximos Pasos

- [FAQ](faq.md) - Más preguntas
- [Documentación completa](../getting-started/installation.md)
- [Mejores prácticas](../guide/best-practices.md)
