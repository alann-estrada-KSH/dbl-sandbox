# Instalación

Guía para instalar DBL en tu sistema.

## Requisitos Previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- PostgreSQL 9.6+ o MySQL 5.7+
- Git (recomendado)

## Instalación Rápida

```bash
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```

## Verificar Instalación

```bash
dbl version
```

**Salida esperada:**
```
DBL (Database Layering) v0.0.1-alpha
Repository: https://github.com/alann-estrada-KSH/dbl-sandbox
```

## Métodos de Instalación

### Desde GitHub (Recomendado)

```bash
# Última versión
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git

# Versión específica (cuando esté disponible)
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git@v0.1.0
```

### Instalación de Usuario

Si no tienes permisos de administrador:

```bash
pip install --user git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```

Luego agrega al PATH:

```bash
# Linux/macOS (agregar a ~/.bashrc o ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Windows (ejecutar en PowerShell como Admin)
$env:Path += ";$env:LOCALAPPDATA\Programs\Python\Python3X\Scripts"
```

### Instalación en Entorno Virtual

```bash
# Crear entorno virtual
python -m venv dbl-env

# Activar entorno
# Linux/macOS:
source dbl-env/bin/activate
# Windows:
dbl-env\Scripts\activate

# Instalar DBL
pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git

# Verificar
dbl version
```

## Instalación de Base de Datos

### PostgreSQL

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### macOS

```bash
brew install postgresql
brew services start postgresql
```

#### Windows

Descarga el instalador desde [postgresql.org](https://www.postgresql.org/download/windows/)

#### Verificar

```bash
psql --version
```

### MySQL

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

#### macOS

```bash
brew install mysql
brew services start mysql
```

#### Windows

Descarga el instalador desde [mysql.com](https://dev.mysql.com/downloads/installer/)

#### Verificar

```bash
mysql --version
```

## Configuración Inicial de Base de Datos

### PostgreSQL

```bash
# Cambiar a usuario postgres
sudo -u postgres psql

# Crear usuario y base de datos
CREATE USER dbuser WITH PASSWORD 'tu_password';
CREATE DATABASE myapp OWNER dbuser;
GRANT ALL PRIVILEGES ON DATABASE myapp TO dbuser;

# Salir
\q
```

### MySQL

```bash
# Conectar como root
sudo mysql

# Crear usuario y base de datos
CREATE USER 'dbuser'@'localhost' IDENTIFIED BY 'tu_password';
CREATE DATABASE myapp;
GRANT ALL PRIVILEGES ON myapp.* TO 'dbuser'@'localhost';
FLUSH PRIVILEGES;

# Salir
EXIT;
```

## Verificar Conexión

### PostgreSQL

```bash
psql -h localhost -U dbuser -d myapp
```

### MySQL

```bash
mysql -h localhost -u dbuser -p myapp
```

## Actualizar DBL

```bash
# Método automático
dbl update

# O manualmente
pip install --upgrade git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
```

## Desinstalar

```bash
pip uninstall dbl
```

## Instalación para Desarrollo

Si quieres contribuir a DBL:

```bash
# Clonar repositorio
git clone https://github.com/alann-estrada-KSH/dbl-sandbox.git
cd dbl-sandbox

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate  # Windows

# Instalar en modo desarrollo
pip install -e .

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
```

## Instalación con Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instalar DBL
RUN pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git

# Verificar instalación
RUN dbl version

WORKDIR /app
CMD ["dbl"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: dbuser
      POSTGRES_PASSWORD: dbpass
      POSTGRES_DB: myapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  dbl:
    build: .
    depends_on:
      - postgres
    environment:
      DB_HOST: postgres
      DB_USER: dbuser
      DB_PASSWORD: dbpass
      DB_NAME: myapp
    volumes:
      - .:/app

volumes:
  postgres_data:
```

## Integración CI/CD

### GitHub Actions

```yaml
name: DBL Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install DBL
        run: |
          pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
      
      - name: Verify installation
        run: dbl version
      
      - name: Run tests
        run: |
          dbl init
          dbl reset
```

### GitLab CI

```yaml
stages:
  - test

test_dbl:
  stage: test
  image: python:3.11
  
  services:
    - postgres:14
  
  variables:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    POSTGRES_DB: testdb
  
  before_script:
    - pip install git+https://github.com/alann-estrada-KSH/dbl-sandbox.git
    - dbl version
  
  script:
    - dbl init
    - dbl reset
```

## Solución de Problemas

### Comando `dbl` no encontrado

```bash
# Verificar instalación
pip list | grep dbl

# Agregar al PATH
export PATH="$HOME/.local/bin:$PATH"

# O usar como módulo
python -m dbl version
```

### Error de permisos

```bash
# Instalar como usuario
pip install --user git+https://github.com/...

# O usar sudo (Linux/macOS)
sudo pip install git+https://github.com/...
```

### Falta PyYAML

```bash
# Instalar manualmente
pip install PyYAML

# O usar actualización de DBL
dbl update
```

### Error de conexión a base de datos

1. Verificar que la base de datos esté corriendo
2. Revisar credenciales en `dbl.yaml`
3. Probar conexión manualmente con `psql` o `mysql`

## Próximos Pasos

Después de instalar DBL:

1. [Inicio Rápido](quick-start.md) - Tutorial de 10 minutos
2. [Tu Primera Migración](first-migration.md) - Ejemplo práctico
3. [Configuración](../guide/configuration.md) - Configurar DBL

## Ver También

- [Inicio Rápido](quick-start.md)
- [Guía de Configuración](../guide/configuration.md)
- [Preguntas Frecuentes](../reference/faq.md)
- [Solución de Problemas](../reference/troubleshooting.md)
