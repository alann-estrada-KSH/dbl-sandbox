# dbl sandbox rollback

Descartar todos los cambios del sandbox y eliminar el sandbox.

## Sinopsis

```bash
dbl sandbox rollback
```

## Descripción

Elimina la base de datos sandbox y todos los cambios no guardados, dejando tu base de datos principal intacta. Es una forma segura de descartar cambios experimentales.

## Qué Hace

1. **Elimina sandbox** - Remueve `{database}_sandbox`
2. **Limpia metadata** - Elimina archivos de rastreo
3. **Reinicia estado** - Marca que no hay sandbox activo

## Ejemplo de Uso

```bash
# Crear sandbox y hacer cambios
dbl sandbox start
psql -d myapp_sandbox -c "CREATE TABLE test (id INT);"

# Decidir que no quieres estos cambios
dbl sandbox rollback
```

**Salida:**
```
Rolling back sandbox changes...
✓ Dropped sandbox database (myapp_sandbox)
✓ Cleared sandbox metadata
✓ No active sandbox

Your main database (myapp) remains unchanged.
```

## Cuándo Usar

### ✅ Usa Rollback Cuando:

- **Experimentas**: Probaste algo que no funcionó
- **Pruebas**: Querías ver el efecto de cambios
- **Errores**: Cometiste errores que quieres descartar
- **Cambio de dirección**: Decidiste un enfoque diferente

### ❌ No Uses Cuando:

- **Quieres guardar cambios**: Usa `dbl sandbox apply` en su lugar
- **Parcialmente hecho**: Guarda primero lo que funciona con commit
- **Ya aplicado**: No puedes rollback después de `sandbox apply`

## Ejemplos Completos

### Experimento Fallido

```bash
# 1. Empezar a experimentar
$ dbl sandbox start
✓ Sandbox: myapp_sandbox

# 2. Probar algo
$ psql -d myapp_sandbox
myapp_sandbox=# DROP TABLE users CASCADE;
DROP TABLE
myapp_sandbox=# -- ¡Oops, no quería hacer eso!

# 3. Rollback
$ dbl sandbox rollback
✓ Sandbox dropped
✓ Base principal sin cambios

# 4. Empezar fresco
$ dbl sandbox start
✓ New clean sandbox created
```

### Múltiples Rollbacks

```bash
# Probar enfoque 1
$ dbl sandbox start
# Hacer cambios...
$ dbl diff
# No me gusta
$ dbl sandbox rollback

# Probar enfoque 2
$ dbl sandbox start
# Hacer cambios diferentes...
$ dbl diff
# Tampoco me gusta
$ dbl sandbox rollback

# Probar enfoque 3
$ dbl sandbox start
# ¡Finalmente funcionó!
$ dbl commit -m "Final approach"
$ dbl sandbox apply
```

### Guardar Algunos, Descartar Otros

```bash
# Hacer varios cambios
$ dbl sandbox start

# Cambio 1: Bueno
$ psql -d myapp_sandbox -c "CREATE TABLE comments (...);"
$ dbl commit -m "Add comments table"

# Cambio 2: Bueno
$ psql -d myapp_sandbox -c "CREATE INDEX idx_comments_post (...);"
$ dbl commit -m "Add comments index"

# Cambio 3: Mala idea
$ psql -d myapp_sandbox -c "DROP TABLE users;"
# ¡No hacer commit de esto!

# Rollback para descartar cambios no guardados
$ dbl sandbox rollback

# Los cambios anteriores están guardados en capas
# Puedes aplicarlos después en nuevo sandbox
```

## Qué Se Elimina

### Eliminado:
- ❌ Sandbox database (`myapp_sandbox`)
- ❌ Cambios sin guardar
- ❌ Metadata del sandbox (`.dbl/sandbox.json`)

### Preservado:
- ✅ Base principal (sin cambios)
- ✅ Capas guardadas (`.dbl/layers/`)
- ✅ Historial de ramas
- ✅ Todo trabajo anterior

## Comparación con Apply

| Aspecto | Rollback | Apply |
|---------|----------|-------|
| Sandbox DB | Eliminada | Eliminada |
| Cambios | Descartados | Aplicados a principal |
| Base Principal | Sin cambios | Actualizada |
| Usar cuando | No quiero cambios | Quiero cambios |

## Características de Seguridad

### Confirmación

Por defecto, DBL puede pedir confirmación:

```bash
$ dbl sandbox rollback
Warning: This will discard all sandbox changes.
Are you sure? (y/n): y
✓ Sandbox rolled back
```

### Sin Deshacer

!!! danger "Eliminación Permanente"
    Después de rollback, cambios del sandbox se pierden **permanentemente**. No hay deshacer.

!!! tip "Guardar Primero"
    Si tienes dudas, guarda cambios con commit antes de rollback. Siempre puedes crear nuevo sandbox sin aplicar esos commits.

## Patrones de Workflow

### Experimento Rápido

```bash
# Prueba rápida
dbl sandbox start
# Probar algo...
dbl sandbox rollback  # Descartar
```

### Desarrollo Iterativo

```bash
# Loop hasta estar satisfecho
while true; do
    dbl sandbox start
    # Hacer cambios...
    dbl diff
    read -p "¿Guardar? (y/n): " keep
    if [ "$keep" = "y" ]; then
        dbl commit -m "Cambios"
        dbl sandbox apply
        break
    else
        dbl sandbox rollback
    fi
done
```

### Exploración de Features

```bash
# Probar feature en sandbox
dbl branch feature-xyz
dbl checkout feature-xyz
dbl sandbox start

# Explorar implementación
# ... hacer cambios ...

# No está listo
dbl sandbox rollback

# Más tarde, intentar de nuevo
dbl sandbox start
# ... mejor implementación ...
dbl commit -m "Feature XYZ"
dbl sandbox apply
```

## Manejo de Errores

### Sin Sandbox Activo

**Error:**
```
Error: No active sandbox found
```

**Solución:**
- No hay nada que rollback
- Estado ya está limpio

### Sandbox ya Eliminado

**Error:**
```
Error: Sandbox database not found
```

**Solución:**
```bash
# Limpiar metadata
rm .dbl/sandbox.json
```

### Problemas de Permisos

**Error:**
```
Error: Permission denied to drop database
```

**Solución:**
```sql
-- Otorgar permiso de drop
ALTER USER myuser WITH CREATEDB;
```

## Notas Importantes

!!! warning "Cambios sin Guardar Perdidos"
    Solo se pierden cambios **sin guardar**. Las capas guardadas están seguras.

!!! info "Base Principal Segura"
    Tu base principal nunca se ve afectada por rollback.

!!! tip "Sin Limpieza Manual"
    DBL limpia automáticamente todos los artefactos del sandbox.

## Después de Rollback

### Verificar Estado

```bash
$ dbl sandbox status
No active sandbox
```

### Empezar de Nuevo

```bash
$ dbl sandbox start
✓ New sandbox created
```

### Revisar Capas Guardadas

```bash
# Los cambios guardados están seguros
$ dbl log
* L005 - Add comments feature
* L004 - Add indexes
...
```

## Integración CI/CD

### Auto-rollback en Fallo

```yaml
# .github/workflows/test.yml
name: Test Migrations

on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test migrations
        run: |
          dbl sandbox start
          dbl reset || dbl sandbox rollback
          
      - name: Cleanup on failure
        if: failure()
        run: dbl sandbox rollback
```

### Script de Limpieza

```bash
#!/bin/bash
# cleanup.sh

# Siempre rollback al final
trap "dbl sandbox rollback 2>/dev/null" EXIT

# Ejecutar tests
dbl sandbox start
./run-migrations.sh
./run-tests.sh
```

## Comparación con Reset

| Comando | Propósito | Alcance |
|---------|-----------|---------|
| `rollback` | Descartar sandbox | Solo sandbox |
| `reset` | Reconstruir desde capas | Base principal |

```bash
# Rollback: descartar cambios del sandbox
dbl sandbox rollback

# Reset: reconstruir base principal desde capas
dbl reset
```

## Mejores Prácticas

1. **Usa rollback libremente** - No tengas miedo de descartar experimentos
2. **Guarda lo bueno** - Commit antes de descartar el resto
3. **Usa ramas** - Aísla experimentos en ramas de feature
4. **Documenta por qué** - Anota por qué hiciste rollback para el equipo

## Próximos Pasos

Después de rollback:

- [Crear nuevo sandbox](start.md) e intentar de nuevo
- [Revisar capas guardadas](../history/log.md)
- [Cambiar ramas](../branching/index.md) para probar enfoque diferente
- [Resetear base](../changes/reset.md) para probar replay de capas

## Ver También

- [`dbl sandbox start`](start.md) - Crear sandbox
- [`dbl sandbox apply`](apply.md) - Aplicar cambios
- [`dbl sandbox status`](status.md) - Ver estado del sandbox
- [`dbl commit`](../changes/commit.md) - Guardar cambios antes de rollback
