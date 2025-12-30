# dbl version

Mostrar la versión de DBL instalada y verificar actualizaciones disponibles.

## Sinopsis

```bash
dbl version
dbl version --check
dbl version --verbose
```

## Descripción

Muestra la versión actual de DBL instalada en tu sistema. También puede verificar si hay versiones más nuevas disponibles.

## Ejemplo de Uso

```bash
dbl version
```

**Salida:**
```
DBL version 2.1.0
Python 3.9.13
PostgreSQL driver: psycopg2 2.9.5
MySQL driver: mysql-connector-python 8.0.33
```

## Opciones

### `--check`

Verificar si hay actualizaciones disponibles:

```bash
$ dbl version --check

DBL version 2.1.0
Latest version: 2.2.0
✓ New version available!

To update: dbl update
```

### `--verbose`

Información detallada:

```bash
$ dbl version --verbose

DBL version 2.1.0
Installed: /usr/local/lib/python3.9/site-packages/dbl
Python version: 3.9.13
Python location: /usr/local/bin/python3.9

Database Drivers:
  PostgreSQL: psycopg2 2.9.5 ✓
  MySQL: mysql-connector-python 8.0.33 ✓

Configuration:
  Home: ~/.dbl
  Config file: ~/.dbl/config.yaml
  Default engine: postgres
```

## Ejemplos Completos

### Verificar Instalación

```bash
$ dbl version
DBL version 2.1.0

# Instalado correctamente
```

### Verificar Actualizaciones

```bash
$ dbl version --check
DBL version 2.1.0
Latest version: 2.2.0
✓ New version available!

# Usar dbl update para instalar
```

### Información Detallada

```bash
$ dbl version --verbose

DBL version 2.1.0
Installed at: /opt/homebrew/lib/python3.9/site-packages/dbl/

Python:
  Version: 3.9.13
  Location: /opt/homebrew/bin/python3.9

Drivers:
  PostgreSQL: psycopg2 2.9.5 ✓
  MySQL: mysql-connector-python 8.0.33 ✓

Dependencies:
  PyYAML: 6.0 ✓
  pydantic: 1.10.2 ✓
```

## Casos de Uso

### CI/CD Pipelines

```bash
#!/bin/bash
# verify-dbl.sh

# Verificar que DBL está instalado
dbl version || {
    echo "DBL not installed!"
    exit 1
}

# Verificar versión mínima
CURRENT=$(dbl version | grep -oP '(?<=version )\d+\.\d+\.\d+')
REQUIRED="2.0.0"

if [ $(printf '%s\n' "$REQUIRED" "$CURRENT" | sort -V | head -n1) = "$REQUIRED" ]; then
    echo "✓ DBL version OK ($CURRENT >= $REQUIRED)"
else
    echo "✗ DBL too old ($CURRENT < $REQUIRED)"
    exit 1
fi
```

### Script de Onboarding

```bash
#!/bin/bash
# setup-dev-env.sh

echo "Verifying DBL installation..."
dbl version --verbose

echo ""
echo "Checking for updates..."
dbl version --check

echo ""
read -p "Update now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    dbl update
fi
```

### Comparación entre Ambientes

```bash
echo "=== Development ==="
dbl version

echo ""
echo "=== Staging ==="
ssh staging "dbl version"

echo ""
echo "=== Production ==="
ssh production "dbl version"
```

## Integración con Scripts

### Python

```python
import subprocess

# Obtener versión
result = subprocess.run(['dbl', 'version'], 
                       capture_output=True, text=True)
print(result.stdout)

# Verificar si necesita actualización
result = subprocess.run(['dbl', 'version', '--check'],
                       capture_output=True, text=True)
if 'New version available' in result.stdout:
    print("Update available!")
```

### Shell

```bash
#!/bin/bash
# check-version.sh

VERSION=$(dbl version | grep -oP '(?<=version )\d+\.\d+\.\d+')
echo "DBL version: $VERSION"

# Parsear versión
MAJOR=$(echo $VERSION | cut -d. -f1)
MINOR=$(echo $VERSION | cut -d. -f2)

echo "Major: $MAJOR, Minor: $MINOR"
```

## Salida por Versión

### V2.x (Actual)

```
DBL version 2.1.0
Python 3.9.13
PostgreSQL driver: psycopg2 2.9.5
MySQL driver: mysql-connector-python 8.0.33
```

### V1.x (Legacy)

```
DBL version 1.5.2
Python 3.7.10
```

## Relacionado

### Actualización

```bash
# Ver versiones disponibles
dbl version --check

# Actualizar a última
dbl update

# Actualizar a versión específica
dbl update --version 2.2.0
```

### Información de Sistema

```bash
$ python3 --version
Python 3.9.13

$ psql --version
psql (PostgreSQL) 13.8

$ mysql --version
mysql Ver 8.0.33
```

## Notas Importantes

!!! info "Sin Conexión"
    `dbl version` funciona sin conexión. `dbl version --check` requiere internet.

!!! tip "Actualización Regular"
    Mantener DBL actualizado para nuevas features y seguridad. Ejecutar `dbl version --check` regularmente.

## Troubleshooting

### Comando No Encontrado

```
Error: command not found: dbl
```

**Solución:**
```bash
# Reinstalar DBL
pip install --upgrade dbl

# O si se instaló con otra herramienta
brew upgrade dbl  # macOS
```

### Versión Antigua

Si tienes versión vieja:

```bash
$ dbl version
DBL version 1.5.2

# Actualizar
$ pip install --upgrade dbl
$ dbl version
DBL version 2.1.0
```

## Ver También

- [`dbl update`](update.md) - Actualizar DBL
- [`dbl init`](init.md) - Inicializar nuevo proyecto
- [`dbl help`](help_cmd.md) - Ver ayuda
