# dbl sandbox status

Revisar el estado actual del sandbox.

## Sinopsis

```bash
dbl sandbox status
```

## Descripción

Muestra información del sandbox activo, incluyendo cambios sin guardar, capas pendientes, y detalles de la base sandbox.

## Ejemplo de Uso

```bash
dbl sandbox status
```

**Salida:**
```
Active Sandbox: myapp_sandbox
Base Database: myapp
Created: 2024-12-30 10:23:15
Branch: feature-auth

Uncommitted Changes:
  + 1 table added (user_sessions)
  + 2 columns added
  ~ 1 table modified

Committed Layers (not yet applied):
  L012 - Add user preferences (2024-12-30 10:45:22)
  L013 - Add session tracking (2024-12-30 11:02:05)

Status: Ready to apply (2 layers pending)

Next steps:
  - Review changes: dbl diff
  - Commit changes: dbl commit -m "message"
  - Apply to main: dbl sandbox apply
  - Discard sandbox: dbl sandbox rollback
```

## Secciones de Salida

### Información del Sandbox

```
Active Sandbox: myapp_sandbox
Base Database: myapp
Created: 2024-12-30 10:23:15
Branch: feature-auth
```

Muestra:
- **Nombre del sandbox**: Nombre de la BD temporal
- **Base original**: BD original
- **Creado**: Cuándo se creó el sandbox
- **Rama**: Rama actual de DBL

### Cambios Sin Guardar

```
Uncommitted Changes:
  + 3 tables added
  + 5 columns added
  ~ 2 tables modified
  - 1 table dropped
```

Resumen de diff antes de hacer commit.

### Capas Guardadas

```
Committed Layers (not yet applied):
  L015 - Add notifications (2024-12-30 14:32:11)
  L016 - Add indexes (2024-12-30 14:35:28)
```

Capas creadas pero no aplicadas a base principal.

### Resumen de Estado

```
Status: Ready to apply (2 layers pending)
```

Estados posibles:
- `Clean` - Sin cambios
- `Uncommitted changes` - Cambios sin guardar
- `Ready to apply` - Commits listos para base principal
- `Empty sandbox` - Sin cambios hechos

## Cuando No Hay Sandbox

```bash
$ dbl sandbox status
No active sandbox

Your main database: myapp
Last applied layer: L014
Current branch: main

To start a sandbox: dbl sandbox start
```

## Ejemplos Completos

### Durante Desarrollo

```bash
# Iniciar sandbox
$ dbl sandbox start
✓ Sandbox: myapp_sandbox

# Revisar estado (vacío)
$ dbl sandbox status
Active Sandbox: myapp_sandbox
Status: Empty sandbox (no changes)

# Hacer cambios
$ psql -d myapp_sandbox -c "CREATE TABLE comments (id SERIAL);"

# Revisar estado (sin guardar)
$ dbl sandbox status
Active Sandbox: myapp_sandbox
Uncommitted Changes:
  + 1 table added (comments)
Status: Uncommitted changes

# Guardar
$ dbl commit -m "Add comments"

# Revisar estado (listo)
$ dbl sandbox status
Active Sandbox: myapp_sandbox
Committed Layers (not yet applied):
  L008 - Add comments (2024-12-30 15:12:33)
Status: Ready to apply (1 layer pending)

# Aplicar
$ dbl sandbox apply

# Revisar estado (no hay sandbox)
$ dbl sandbox status
No active sandbox
```

### Múltiples Commits

```bash
$ dbl sandbox status

Active Sandbox: blog_sandbox
Base Database: blog

Uncommitted Changes:
  + 1 table added (comments)
  ~ 1 table modified (posts)

Committed Layers (not yet applied):
  L020 - Add user profiles (2024-12-30 09:15:33)
  L021 - Add social login (2024-12-30 10:22:41)
  L022 - Add rate limiting (2024-12-30 11:45:19)

Status: Ready to apply (3 layers pending)
Uncommitted: 2 changes

Next steps:
  1. Commit remaining changes: dbl commit -m "Add comments"
  2. Apply all layers: dbl sandbox apply
  3. Or rollback everything: dbl sandbox rollback
```

## Casos de Uso

### Antes de Commit

```bash
# Revisar qué necesita guardarse
$ dbl sandbox status
Uncommitted Changes:
  + 3 tables added
  
$ dbl diff  # Ver detalles
$ dbl commit -m "Add feature X"
```

### Antes de Aplicar

```bash
# Revisar qué se aplicará
$ dbl sandbox status
Committed Layers (not yet applied):
  L015 - Add notifications
  L016 - Add webhooks
  
# Revisar cada capa
$ cat .dbl/layers/L015_*.sql
$ cat .dbl/layers/L016_*.sql

# Aplicar
$ dbl sandbox apply
```

### Verificaciones en CI/CD

```bash
# Verificar que sandbox está limpio antes de fusionar
$ dbl sandbox status
if [ "$?" -ne 0 ]; then
    echo "Sandbox has uncommitted changes!"
    exit 1
fi
```

### Coordinación de Equipo

```bash
# Compartir estado con equipo
$ dbl sandbox status > sandbox-status.txt
$ cat sandbox-status.txt

Active Sandbox: myapp_sandbox
Committed Layers (not yet applied):
  L030 - Add payment system (hace 3 horas)
  L031 - Add webhooks (hace 1 hora)
  
# El equipo sabe qué se está desarrollando
```

## Indicadores de Estado

### Estado Limpio

```
Status: Clean
```
- Sin cambios sin guardar
- Sin capas pendientes
- Seguro cerrar sandbox o cambiar ramas

### Trabajo Sin Guardar

```
Status: Uncommitted changes
```
- Cambios no guardados
- Deberías hacer commit o descartar antes de aplicar

### Listo para Aplicar

```
Status: Ready to apply (N layers pending)
```
- Tiene capas guardadas
- Puede aplicar a base principal
- Puede tener cambios sin guardar también

### Estado Mixto

```
Status: Ready to apply (2 layers pending)
Uncommitted: 1 table added
```
- Tiene cambios guardados y sin guardar
- Puede aplicar capas guardadas
- Cambios sin guardar permanecen en sandbox

## Ejemplos de Integración

### Git Hook

```bash
#!/bin/bash
# .git/hooks/pre-push

# Asegurar que sandbox está aplicado antes de push
STATUS=$(dbl sandbox status)

if echo "$STATUS" | grep -q "Active Sandbox"; then
    echo "Error: Active sandbox detected"
    echo "Apply or rollback sandbox before pushing"
    exit 1
fi
```

### Script de Monitoreo

```bash
#!/bin/bash
# monitor-sandbox.sh

while true; do
    clear
    echo "=== Sandbox Status ==="
    dbl sandbox status
    echo ""
    echo "Press Ctrl+C to exit"
    sleep 5
done
```

### Estado API

```python
# get_sandbox_status.py
import subprocess
import json

result = subprocess.run(['dbl', 'sandbox', 'status'], 
                       capture_output=True, text=True)

if result.returncode == 0:
    print(f"Status: {result.stdout}")
else:
    print("No active sandbox")
```

## Notas Importantes

!!! info "Solo Lectura"
    El comando status solo lee estado, nunca modifica nada.

!!! tip "Verifica Frecuentemente"
    Ejecuta `dbl sandbox status` frecuentemente durante desarrollo para rastrear progreso.

!!! warning "Metadata vs Realidad"
    Status muestra la vista de DBL. Si algo parece mal, verifica manualmente con herramientas DB.

## Ver También

- [`dbl diff`](../changes/diff.md) - Ver cambios detallados
- [`dbl commit`](../changes/commit.md) - Guardar cambios
- [`dbl sandbox apply`](apply.md) - Aplicar sandbox
- [`dbl sandbox rollback`](rollback.md) - Descartar sandbox
- [`dbl log`](../history/log.md) - Ver historial de capas
