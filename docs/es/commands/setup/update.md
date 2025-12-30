# dbl update

Actualizar DBL a la última versión.

## Sinopsis

```bash
dbl update
dbl update --version VERSION
dbl update --force
dbl update --check
```

## Descripción

Descarga e instala la última versión de DBL. Verifica GitHub para nuevas versiones y actualiza automáticamente si está disponible.

## Ejemplo de Uso

```bash
dbl update
```

**Salida:**
```
Checking for updates...
Current version: 2.1.0
Latest version: 2.2.0
New version available!

Downloading DBL 2.2.0...
✓ Downloaded successfully
Installing...
✓ Installation complete

Updated successfully!
DBL version 2.2.0

Run 'dbl help' for available commands.
```

## Opciones

### `--check`

Solo verificar actualizaciones sin instalar:

```bash
$ dbl update --check

Current version: 2.1.0
Latest version: 2.2.0
✓ New version available
```

### `--version VERSION`

Actualizar a versión específica:

```bash
$ dbl update --version 2.2.0
# Instala versión 2.2.0 específicamente
```

### `--force`

Forzar actualización incluso si versión es igual:

```bash
$ dbl update --force
# Reinstala versión actual
```

## Ejemplos Completos

### Actualización Automática

```bash
$ dbl update

Checking for updates...
✓ New version: 2.2.0
Downloading...
✓ Installed successfully
✓ DBL 2.2.0 ready
```

### Verificar y Actualizar Interactivo

```bash
$ dbl update --check

Current version: 2.1.0
Latest version: 2.2.0

Update now? [y/n]: y

Downloading...
✓ Installation complete
```

### Actualizar a Versión Específica

```bash
$ dbl update --version 2.1.5

Downloading DBL 2.1.5...
✓ Downloaded
Installing...
✓ Installed: DBL 2.1.5
```

### Volver a Versión Anterior

```bash
# Actualizar a versión específica anterior
$ dbl update --version 2.0.0

Downloading DBL 2.0.0...
✓ Installation complete
```

## Proceso de Actualización

### Paso a Paso

```
1. Verificar conexión internet
2. Consultar GitHub API para última versión
3. Comparar versiones
4. Si hay actualización disponible:
   a. Descargar archivo
   b. Instalar con pip
   c. Verificar instalación
   d. Mostrar cambios
```

### Verificación Post-Actualización

```bash
$ dbl update
... actualización completa ...

$ dbl version
DBL version 2.2.0 ✓

$ dbl help
... muestra ayuda ...
```

## Usar en Scripts

### Script de Actualización Automática

```bash
#!/bin/bash
# auto-update.sh

# Actualizar DBL si hay versión nueva
dbl update --check | grep -q "available" && {
    echo "Updating DBL..."
    dbl update
    echo "✓ Updated"
} || {
    echo "Already up to date"
}
```

### GitHub Actions

```yaml
name: Keep DBL Updated

on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Check for updates
        run: dbl update --check
        
      - name: Update if available
        run: dbl update
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test with Latest DBL

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Update DBL
        run: dbl update --force
        
      - name: Run tests
        run: pytest tests/
```

## Cambios en Nuevas Versiones

### v2.2.0 (Latest)

```bash
$ dbl update

Updated features:
  ✓ Improved performance
  ✓ New sandbox features
  ✓ Better error messages
  ✓ PostgreSQL 15 support

Breaking changes:
  - Cambiar configuración de X a Y
  - Ver docs/upgrade-2.2.md
```

### v2.1.0

```
✓ MySQL 8.0 support
✓ Auto-dependency installation
✓ New validation engine
```

### v2.0.0

```
✓ Major rewrite
✓ Ramas de feature (branching)
✓ Mejor rendimiento
```

## Política de Actualización

### Versioning

DBL usa Semantic Versioning:

```
2.1.3
│ │ └── Patch (bug fixes)
│ └──── Minor (new features)
└────── Major (breaking changes)
```

### Recomendaciones

```bash
# Patch updates: Siempre instalar
dbl update  # 2.1.2 → 2.1.3

# Minor updates: Generalmente seguro
dbl update  # 2.1.0 → 2.2.0

# Major updates: Revisar cambios primero
dbl update --check  # Leer notas de actualización
# Luego decidir actualizar
```

## Troubleshooting

### Falló la Descarga

**Error:**
```
Error: Failed to download
Network connection error
```

**Solución:**
```bash
# Reintentar
dbl update

# O instalar manualmente
pip install --upgrade dbl
```

### Permisos Insuficientes

**Error:**
```
Error: Permission denied
Cannot install to /usr/local/lib
```

**Solución:**
```bash
# Actualizar con permisos
sudo dbl update

# O usar virtualenv
source venv/bin/activate
dbl update
```

### Versión Corrupta

**Error:**
```
Error: Installation failed
DBL check failed
```

**Solución:**
```bash
# Desinstalar y reinstalar
pip uninstall dbl
pip install dbl

# Verificar
dbl version
```

### Ya Actualizada

**Output:**
```
Current version: 2.2.0
Latest version: 2.2.0
✓ Already up to date
```

No hay nada que hacer.

## Dependencias Automáticas

DBL automáticamente verifica e instala dependencias:

```bash
$ dbl update

Checking dependencies...
  PyYAML 6.0 ✓
  pydantic 1.10 ✓
  psycopg2 2.9 ✓
  mysql-connector-python 8.0 ✓

✓ All dependencies satisfied
```

Si falta algo:

```bash
✗ psycopg2 not found
Installing missing dependencies...
✓ psycopg2 installed
```

## Actualización en Producción

### Despliegue Seguro

```bash
#!/bin/bash
# deploy-dbl-update.sh

# 1. Verificar que versión está disponible
dbl update --check

# 2. Probar en staging
dbl update --version 2.2.0

# 3. Ejecutar tests
dbl reset
pytest tests/

# 4. Si todo OK, actualizar producción
ssh production 'dbl update --version 2.2.0'

# 5. Verificar
ssh production 'dbl version'
```

### Rollback

```bash
# Si algo sale mal, volver a versión anterior
dbl update --version 2.1.0

# Verificar
dbl version
```

## Monitoreo de Actualizaciones

### Verificación Regular

```bash
# Cron job para verificar diariamente
0 9 * * * dbl update --check >> /tmp/dbl-updates.log
```

### Notificaciones

```bash
#!/bin/bash
# notify-updates.sh

if dbl update --check | grep -q "available"; then
    echo "DBL update available" | mail -s "DBL Update" admin@company.com
fi
```

## Ver También

- [`dbl version`](version.md) - Ver versión actual
- [`dbl init`](init.md) - Inicializar proyecto
- [`dbl help`](help_cmd.md) - Ver ayuda
