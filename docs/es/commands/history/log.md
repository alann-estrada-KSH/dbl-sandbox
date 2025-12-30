# dbl log

Ver el historial de capas y cambios del database.

## Sinopsis

```bash
dbl log
dbl log [--branch BRANCH]
dbl log [--limit N]
dbl log [--oneline]
```

## Descripción

Muestra el historial de todas las capas creadas, incluyendo quién hizo el cambio, cuándo, y qué se modificó. Similar a `git log` pero para tu base de datos.

## Ejemplo de Uso

```bash
dbl log
```

**Salida:**
```
commit L015 (HEAD -> main)
Author: Ana García <ana@company.com>
Date:   2024-12-30 14:35:22 +0000

    Add webhook notification system

commit L014
Author: Carlos López <carlos@company.com>
Date:   2024-12-30 10:22:41 +0000

    Add rate limiting to API

commit L013
Author: Ana García <ana@company.com>
Date:   2024-12-29 16:18:33 +0000

    Add user notifications table

commit L012
...
```

## Opciones

### `--oneline`

Formato compacto:

```bash
$ dbl log --oneline

L015 - Add webhook notification system
L014 - Add rate limiting to API
L013 - Add user notifications table
L012 - Add comments feature
L011 - Add post reactions
```

### `--limit N`

Ver solo últimas N capas:

```bash
$ dbl log --limit 5

# Muestra las 5 capas más recientes
```

### `--branch BRANCH`

Ver log de rama específica:

```bash
$ dbl log --branch feature-auth

# Muestra historial de feature-auth
```

### `--author AUTHOR`

Filtrar por autor:

```bash
$ dbl log --author "Ana García"

# Muestra solo cambios de Ana
```

### `--since DATE`

Cambios después de fecha:

```bash
$ dbl log --since "2024-12-20"

# Cambios desde 20 de diciembre
```

## Ejemplos Completos

### Ver Historial Completo

```bash
$ dbl log

* L015 Add webhook system (Ana, 14:35)
* L014 Add rate limiting (Carlos, 10:22)
* L013 Add notifications (Ana, 16:18)
* L012 Add comments (Carlos, 09:45)
* L011 Add reactions (Ana, 08:30)
```

### Buscar Cambio Específico

```bash
# Quién agregó una feature?
$ dbl log | grep -i "email"

* L008 Add email verification (Ana, 2024-12-25 11:22)

# Detalles de esa capa
$ cat .dbl/layers/L008_*.sql
```

### Ver Cambios de Usuario

```bash
$ dbl log --author "Ana García"

* L015 Add webhook system
* L013 Add notifications
* L011 Add reactions
* L009 Add user preferences
* L007 Add authentication
```

### Últimas N Capas

```bash
$ dbl log --limit 3 --oneline

* L015 Add webhook notification system
* L014 Add rate limiting to API
* L013 Add user notifications table
```

### Historial de Rama

```bash
$ dbl log --branch feature-auth

* L010 Add OAuth2 integration (feature-auth)
* L009 Add social login (feature-auth)
* L008 Add password reset (feature-auth)

$ dbl log --branch main

* L007 Add authentication (main)
* L006 Add users table (main)
```

## Interpretar Salida

### Componentes

```
commit L015                              ← ID de capa
Author: Ana García <ana@company.com>     ← Quién hizo cambio
Date:   2024-12-30 14:35:22 +0000        ← Cuándo
                                          ← Blank line
    Add webhook notification system      ← Mensaje de commit
```

### Estados de Rama

```
commit L015 (HEAD -> main)  ← HEAD en main
commit L014 (feature-auth)  ← HEAD en feature-auth
commit L013                 ← Sin rama específica
```

## Casos de Uso

### Auditoría

```bash
# Quién cambió qué?
$ dbl log --author "carlos@company.com" --since "2024-12-01"

L020 - Fix migration script (2024-12-15)
L019 - Add payment processing (2024-12-10)
L018 - Fix indexing strategy (2024-12-05)
```

### Debugging

```bash
# Cuándo se rompió?
$ dbl log --oneline | head -20

# Capa reciente que podría ser el problema
L025 - Refactor user roles

# Ver qué cambió en L025
$ cat .dbl/layers/L025_*.sql
```

### Release Notes

```bash
#!/bin/bash
# generate-release-notes.sh

LAST_TAG=$(git describe --tags --abbrev=0)
LAST_COMMIT=$(git rev-list -n 1 $LAST_TAG)

echo "# Changes in this release"
dbl log --since "$LAST_COMMIT"
```

### Comparación de Ramas

```bash
# Diferencias entre ramas
$ dbl log --branch main | wc -l
42 cambios en main

$ dbl log --branch staging | wc -l
38 cambios en staging

# staging necesita 4 capas de main
```

## Integración con Scripts

### Python

```python
import subprocess
import json

# Obtener log
result = subprocess.run(['dbl', 'log', '--oneline'], 
                       capture_output=True, text=True)

layers = []
for line in result.stdout.strip().split('\n'):
    layer_id, message = line.split(' - ', 1)
    layers.append({'id': layer_id, 'message': message})

print(f"Total layers: {len(layers)}")
```

### Bash

```bash
#!/bin/bash
# get-last-author.sh

LAST_AUTHOR=$(dbl log --oneline | head -1 | awk '{print $NF}')
echo "Last change by: $LAST_AUTHOR"
```

## Formatos de Salida

### Compacto (--oneline)

```
L025 - Add webhook endpoints
L024 - Fix user profile bug
L023 - Optimize queries
```

### Detallado (default)

```
commit L025
Author: Ana García <ana@company.com>
Date:   2024-12-30 16:45:22 +0000

    Add webhook endpoints
    
    - POST /webhooks
    - GET /webhooks/:id
    - DELETE /webhooks/:id
```

### Solo mensajes

```bash
$ dbl log --format="%s"

Add webhook endpoints
Fix user profile bug
Optimize queries
```

## Mejores Prácticas de Mensajes

### ❌ Mensajes Malos

```
L025 - stuff
L026 - fixes
L027 - update
```

### ✅ Mensajes Buenos

```
L025 - Add webhook notification system

L026 - Fix user profile update query N+1 problem

L027 - Optimize user dashboard query with materialized view
```

### Formato Estándar

```
<tipo>: <descripción breve>

<descripción detallada>

<cambios>
- Agregar tabla X
- Modificar columna Y
- Crear índice Z
```

## Ejemplos de Búsqueda

### Encontrar Feature

```bash
# Dónde está la feature de comentarios?
$ dbl log | grep -i comment

L012 - Add comments feature
L008 - Create comments table
```

### Cronología de Feature

```bash
# Historia completa de una feature
$ dbl log --oneline | grep -i "payment"

L030 - Add webhook for payment confirmations
L029 - Add payment method storage
L028 - Add payment processing endpoint
L027 - Create payments table
```

### Cambios en Rango de Fechas

```bash
$ dbl log --since "2024-12-01" --until "2024-12-15"

# Todas las capas entre esas fechas
```

## Comparar con Git

| Aspecto | Git Log | DBL Log |
|---------|---------|---------|
| Qué | Cambios en código | Cambios en esquema DB |
| Historial | Commits de código | Capas de DB |
| Trazabilidad | Por desarrollador | Por quién, cuándo, qué |
| Reproducibilidad | Checkout a commit | Reset a capa específica |

## Próximos Pasos

Después de revisar log:

- **Inspeccionar capa**: `cat .dbl/layers/L015_*.sql`
- **Resetear a punto**: `dbl reset` y luego crear desde ahí
- **Comparar ramas**: `dbl log --branch feature-xyz`
- **Ver cambios**: `dbl diff` de cambios sin guardar

## Ver También

- [`dbl diff`](diff.md) - Ver cambios detallados
- [`dbl commit`](commit.md) - Crear nuevas capas
- [`dbl reset`](reset.md) - Reconstruir desde capas
- [`dbl branch`](../branching/index.md) - Gestionar ramas
