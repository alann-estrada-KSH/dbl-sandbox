# Configuración

Guía completa de configuración de DBL a través del archivo `dbl.yaml`.

## Archivo de Configuración

DBL usa `dbl.yaml` para toda su configuración. Este archivo debe estar en la raíz de tu proyecto.

### Configuración Mínima

```yaml
database:
  name: myapp
  engine: postgres  # o 'mysql'
  host: localhost
  port: 5432       # o 3306 para MySQL
  user: dbuser
  password: ${DB_PASSWORD}
```

### Configuración Completa

```yaml
# Configuración de base de datos
database:
  name: myapp
  engine: postgres
  host: localhost
  port: 5432
  user: dbuser
  password: ${DB_PASSWORD}
  
  # Opciones del motor
  options:
    sslmode: require
    connect_timeout: 10
    application_name: dbl

# Configuración de DBL
dbl:
  # Directorio para layers
  layers_dir: .dbl/layers
  
  # Rama por defecto
  default_branch: main
  
  # Prefijo para sandbox
  sandbox_prefix: sandbox_
  
  # Validación
  validation:
    strict: false
    check_syntax: true

# Logging
logging:
  level: info  # debug, info, warning, error
  file: .dbl/dbl.log
```

## Configuración de Base de Datos

### Campos Requeridos

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `name` | Nombre de la base de datos | `myapp` |
| `engine` | Motor de BD | `postgres`, `mysql` |
| `host` | Host de la BD | `localhost` |
| `port` | Puerto | `5432`, `3306` |
| `user` | Usuario de BD | `dbuser` |
| `password` | Contraseña | `${DB_PASSWORD}` |

### Variables de Entorno

Usa variables de entorno para credenciales sensibles:

```yaml
database:
  name: ${DB_NAME}
  user: ${DB_USER}
  password: ${DB_PASSWORD}
  host: ${DB_HOST:-localhost}  # valor por defecto
  port: ${DB_PORT:-5432}
```

```bash
# Exportar variables
export DB_NAME=myapp
export DB_USER=dbuser
export DB_PASSWORD=secreto
```

### PostgreSQL

```yaml
database:
  name: myapp
  engine: postgres
  host: localhost
  port: 5432
  user: postgres
  password: ${DB_PASSWORD}
  
  # Opciones específicas de PostgreSQL
  options:
    sslmode: require
    sslrootcert: /path/to/ca.crt
    connect_timeout: 10
    application_name: dbl
    
    # Pool de conexiones
    pool_size: 10
    max_overflow: 20
```

### MySQL

```yaml
database:
  name: myapp
  engine: mysql
  host: localhost
  port: 3306
  user: root
  password: ${DB_PASSWORD}
  
  # Opciones específicas de MySQL
  options:
    charset: utf8mb4
    ssl_ca: /path/to/ca.pem
    connect_timeout: 10
    
    # Pool de conexiones
    pool_size: 10
    pool_recycle: 3600
```

## Configuración por Entorno

### Desarrollo

```yaml
# dbl.dev.yaml
database:
  name: myapp_dev
  host: localhost
  user: dev_user
  password: ${DEV_PASSWORD}
  
dbl:
  validation:
    strict: false
  
logging:
  level: debug
```

### Staging

```yaml
# dbl.staging.yaml
database:
  name: myapp_staging
  host: staging-db.example.com
  user: staging_user
  password: ${STAGING_PASSWORD}
  
  options:
    sslmode: require
    
dbl:
  validation:
    strict: true
    
logging:
  level: info
```

### Producción

```yaml
# dbl.production.yaml
database:
  name: myapp_production
  host: prod-db.example.com
  user: prod_user
  password: ${PROD_PASSWORD}
  
  options:
    sslmode: require
    connect_timeout: 30
    
dbl:
  validation:
    strict: true
    check_syntax: true
    
logging:
  level: warning
  file: /var/log/dbl/production.log
```

### Usar Configuración Específica

```bash
# Desarrollo (por defecto: dbl.yaml)
dbl sandbox start

# Staging
dbl --config dbl.staging.yaml sandbox start

# Producción
dbl --config dbl.production.yaml sandbox apply
```

## Configuración de DBL

### Directorios

```yaml
dbl:
  # Directorio base
  base_dir: .dbl
  
  # Subdirectorios
  layers_dir: .dbl/layers
  branches_dir: .dbl/branches
  temp_dir: .dbl/temp
```

### Ramas

```yaml
dbl:
  # Rama por defecto
  default_branch: main
  
  # Prefijo para ramas de feature
  feature_prefix: feature/
  
  # Prefijo para hotfixes
  hotfix_prefix: hotfix/
```

### Sandbox

```yaml
dbl:
  # Prefijo de nombre para sandboxes
  sandbox_prefix: sandbox_
  
  # Sufijo de nombre
  sandbox_suffix: _dev
  
  # Resultado: myapp_sandbox_dev
```

### Validación

```yaml
dbl:
  validation:
    # Modo estricto
    strict: false
    
    # Validar sintaxis SQL
    check_syntax: true
    
    # Validar nombres de tablas
    table_naming: snake_case  # snake_case, camelCase
    
    # Validar nombres de columnas
    column_naming: snake_case
    
    # Requerir comentarios
    require_comments: false
```

## Logging

### Configuración de Logs

```yaml
logging:
  # Nivel: debug, info, warning, error
  level: info
  
  # Archivo de log
  file: .dbl/dbl.log
  
  # Formato
  format: "[{timestamp}] {level}: {message}"
  
  # Rotación
  rotation:
    max_size: 10485760  # 10MB
    backup_count: 5
```

### Niveles de Log

| Nivel | Descripción | Uso |
|-------|-------------|-----|
| `debug` | Información detallada | Desarrollo |
| `info` | Información general | Producción |
| `warning` | Advertencias | Producción |
| `error` | Solo errores | Producción crítica |

## Configuración Avanzada

### Hooks (Futuro)

```yaml
hooks:
  # Antes de commit
  pre_commit:
    - validate_naming
    - check_migrations
    
  # Después de apply
  post_apply:
    - notify_team
    - update_docs
```

### Plantillas

```yaml
templates:
  # Plantilla de layer
  layer_header: |
    -- Layer: {layer_id}
    -- Message: {message}
    -- Date: {date}
    -- Author: {author}
    
  # Plantilla de commit
  commit_message: |
    Database: {message}
    
    Layer: {layer_id}
    Tables: {tables}
```

### Exclusiones

```yaml
dbl:
  # Ignorar tablas
  ignore_tables:
    - django_migrations
    - django_session
    - _temp_*
    
  # Ignorar esquemas
  ignore_schemas:
    - information_schema
    - pg_catalog
```

## Configuración de Testing

```yaml
# dbl.test.yaml
database:
  name: myapp_test
  host: localhost
  user: test_user
  password: test_password
  
dbl:
  # Limpiar después de tests
  auto_cleanup: true
  
  # Seed data
  seed_data: tests/fixtures/seed.sql
```

## Múltiples Bases de Datos

```yaml
# Configuración principal
database:
  name: myapp
  # ... config ...

# Bases adicionales
databases:
  analytics:
    name: myapp_analytics
    host: analytics-db.example.com
    # ... config ...
    
  cache:
    name: myapp_cache
    engine: mysql
    # ... config ...
```

```bash
# Usar base específica
dbl --database analytics sandbox start
```

## Variables y Secretos

### Archivo .env

```bash
# .env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=dbuser
DB_PASSWORD=secreto
```

```yaml
# dbl.yaml
database:
  name: ${DB_NAME}
  host: ${DB_HOST}
  port: ${DB_PORT}
  user: ${DB_USER}
  password: ${DB_PASSWORD}
```

### Gestores de Secretos

#### AWS Secrets Manager

```yaml
database:
  password: ${AWS_SECRET:myapp/db/password}
```

#### HashiCorp Vault

```yaml
database:
  password: ${VAULT:secret/myapp/db#password}
```

## Validación de Configuración

```bash
# Validar configuración
dbl validate --config

# Ver configuración actual
dbl config show

# Probar conexión
dbl config test
```

## Mejores Prácticas

### 1. No Commitear Contraseñas

```yaml
# ✅ Correcto
password: ${DB_PASSWORD}

# ❌ Incorrecto
password: mi_password_secreta
```

### 2. Usar Archivos por Entorno

```
project/
├── dbl.yaml           # Desarrollo
├── dbl.staging.yaml   # Staging
└── dbl.production.yaml # Producción
```

### 3. Versionado en Git

```gitignore
# .gitignore
dbl.yaml           # No commitear desarrollo
dbl.*.local.yaml   # Configuraciones locales
.env               # Variables de entorno

# Sí commitear
dbl.*.yaml.example # Ejemplos
dbl.production.yaml # Producción (sin secretos)
```

### 4. Documentar Configuración

```yaml
# dbl.yaml.example
database:
  name: myapp
  engine: postgres  # o 'mysql'
  host: localhost
  port: 5432
  user: dbuser
  password: ${DB_PASSWORD}  # Configurar en .env
```

## Ejemplo Completo

```yaml
# dbl.yaml - Configuración completa
database:
  # Conexión
  name: ${DB_NAME:-myapp}
  engine: postgres
  host: ${DB_HOST:-localhost}
  port: ${DB_PORT:-5432}
  user: ${DB_USER:-dbuser}
  password: ${DB_PASSWORD}
  
  # Opciones
  options:
    sslmode: ${DB_SSLMODE:-prefer}
    connect_timeout: 10
    application_name: dbl
    pool_size: 10

# Configuración DBL
dbl:
  # Directorios
  base_dir: .dbl
  layers_dir: .dbl/layers
  
  # Ramas
  default_branch: main
  
  # Sandbox
  sandbox_prefix: ""
  sandbox_suffix: _sandbox
  
  # Validación
  validation:
    strict: false
    check_syntax: true
    table_naming: snake_case
    
  # Ignorar
  ignore_tables:
    - _*
    - temp_*

# Logging
logging:
  level: ${LOG_LEVEL:-info}
  file: .dbl/dbl.log
  format: "[{timestamp}] {level}: {message}"
```

## Ver También

- [Inicio Rápido](../getting-started/quick-start.md)
- [Mejores Prácticas](best-practices.md)
- [Motores de BD](../architecture/engines.md)
- [FAQ](../reference/faq.md)
