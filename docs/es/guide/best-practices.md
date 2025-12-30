# Mejores Prácticas

Patrones y recomendaciones para usar DBL efectivamente en equipos y proyectos.

## Estrategia de Ramas

### Flujo Git-like

Usa patrón similar a Git Flow:

```
main (producción)
  ├─ develop (siguiente release)
  │   ├─ feature/auth
  │   ├─ feature/payments
  │   └─ feature/notifications
  └─ hotfix/urgent-bug
```

### Nombrado de Ramas

```bash
# ✅ Buenos nombres
dbl branch create feature/user-auth
dbl branch create feature/payment-integration
dbl branch create bugfix/null-pointer-error
dbl branch create hotfix/security-patch

# ❌ Malos nombres
dbl branch create work
dbl branch create test
dbl branch create stuff
```

## Gestión de Commits

### Commits Atómicos

Cada commit debe ser una unidad lógica de cambio:

```bash
# ✅ Bien: Commit por cambio lógico
dbl commit -m "Add user authentication table"
dbl commit -m "Add session management tables"
dbl commit -m "Add password reset functionality"

# ❌ Mal: Todo en un commit
dbl commit -m "Add auth, payments, notifications"
```

### Mensajes de Commit Claros

```bash
# ✅ Bueno
dbl commit -m "Add email verification for user registration"

# ✅ También bueno (con descripción)
dbl commit -m "Implement two-factor authentication"
dbl commit -m "
Add TOTP-based 2FA support

- Create totp_secrets table
- Add verification endpoint
- Add backup codes generation
"

# ❌ Malo
dbl commit -m "stuff"
dbl commit -m "fix"
```

## Seguridad en la Base de Datos

### Capas Separadas por Sensibilidad

```bash
# Crear capas separadas para datos sensibles
dbl sandbox start

# Capa 1: Estructuras
CREATE TABLE users (...);
dbl commit -m "Create user table structure"

# Capa 2: Datos de prueba (NO sensibles)
INSERT INTO users VALUES (...);
dbl commit -m "Add test users"

# Capa 3: Índices de rendimiento
CREATE INDEX idx_users_email ON users(email);
dbl commit -m "Add performance indexes"
```

### Nunca Commitear Datos Sensibles

```bash
# ❌ NUNCA hacer esto
INSERT INTO users VALUES ('admin', 'password123');
dbl commit -m "Add admin user"

# ✅ Usar variables o archivos externos
INSERT INTO users VALUES (?, ?);  -- Parámetros
dbl commit -m "Create user schema"
```

## Rendimiento

### Optimizar Migraciones Grandes

Para cambios que afectan muchos datos:

```bash
# Usar patrón expand-contract
# Semana 1: Expand (agregar)
dbl sandbox start
ALTER TABLE users ADD COLUMN email TEXT;
dbl commit -m "Expand: Add email column"
dbl sandbox apply

# Semana 2: Backfill (llenar datos)
dbl sandbox start
UPDATE users SET email = username || '@example.com';
dbl commit -m "Backfill: Populate email"
dbl sandbox apply

# Semana 3: Contract (aplicar constraints)
dbl sandbox start
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
dbl commit -m "Contract: Require email"
dbl sandbox apply
```

### Índices Selectivos

```sql
-- ✅ Bueno: Índices en columnas frecuentemente consultadas
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_author ON posts(author_id);

-- ❌ Malo: Índices innecesarios
CREATE INDEX idx_users_name_created ON users(name, created_at);
```

## Testing

### Validar Capas Regularmente

```bash
#!/bin/bash
# validate-schema.sh

# Recrear base de datos desde capas
dbl reset

# Ejecutar tests
pytest tests/database/

# Verificar integridad
dbl validate --check-schema
```

### Pruebas de Migración

```bash
# Crear ambiente de test
dbl --config test.yaml sandbox start

# Aplicar cambios
dbl --config test.yaml reset

# Ejecutar tests
pytest tests/migrations/

# Verificar rollback (para MySQL)
dbl --config test.yaml sandbox rollback
```

## Colaboración en Equipo

### Code Review de Cambios

```bash
# Developer abre PR con cambios
$ dbl log feature/auth

* L025 Add OAuth2 integration
* L024 Add password reset
* L023 Create user sessions table

# Reviewer examina cada capa
$ cat .dbl/layers/L025_*.sql
# Verificar SQL, performance, seguridad

# Approbar o pedir cambios
```

### Sincronización Entre Ramas

```bash
# Tu rama está atrás de main
$ dbl log main | wc -l
$ dbl log feature/auth | wc -l

# Actualizar feature desde main
$ dbl checkout main
$ dbl pull origin main
$ dbl checkout feature/auth
$ dbl merge main

# Ahora feature/auth incluye cambios de main
```

### Resolver Conflictos

```bash
# Intentar fusionar
$ dbl merge feature-payments
Error: Merge conflict
  Layer L020 modified in both branches

# Resolver manualmente
$ vim .dbl/layers/L020_*.sql
# Arreglar conflicto

# Marcar como resuelto
$ dbl merge --continue
```

## CI/CD Integration

### Pipeline de Validación

```yaml
# .github/workflows/db-validation.yml
name: Validate Database Changes

on:
  pull_request:
    paths:
      - '.dbl/layers/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Install DBL
        run: pip install dbl
        
      - name: Validate layers
        run: dbl validate --check-layers
        
      - name: Test schema reset
        run: dbl reset
        
      - name: Run tests
        run: pytest tests/database/
```

### Despliegue Progresivo

```bash
#!/bin/bash
# deploy-progressive.sh

LAYERS=$(dbl log --since "$LAST_DEPLOY" --oneline)
COUNT=$(echo "$LAYERS" | wc -l)

echo "Deploying $COUNT layers..."

# Desplegar a staging primero
dbl --env staging sandbox apply

# Esperar a validación
read -p "Proceed to production? [y/n]: " -n 1

if [[ $REPLY =~ ^[Yy]$ ]]; then
    dbl --env production sandbox apply
fi
```

## Mantenimiento

### Limpiar Ramas Antiguas

```bash
# Listar ramas
$ dbl branch --list

# Eliminar ramas mergeadas
$ dbl branch delete feature/old-auth
$ dbl branch delete bugfix/resolved-issue
```

### Archivar Cambios

```bash
# Backup de rama antes de eliminar
$ git checkout feature/old-feature
$ git bundle create feature-old.bundle
$ dbl branch delete feature/old-feature
```

## Documentación

### Documentar Cambios de Esquema

```bash
# Crear documento para cada feature
$ cat > SCHEMA_CHANGES.md << EOF
## Feature: OAuth2 Authentication (v2.2.0)

### Cambios de esquema:
- L025: Tabla oAuth_providers
- L026: Tabla user_oauth_tokens
- L027: Índices para búsqueda rápida

### Cambios de datos:
- Migración de passwords (L024)

### Breaking changes:
- Columna password_hash requerida

### Testing:
- Ver tests/auth/test_oauth.py

### Rollback:
- dbl reset --to L024
EOF
```

### README para Database

```markdown
# Database Schema

## Estructura

La base de datos consta de X tablas principales:
- users: Información de usuarios
- posts: Artículos publicados
- comments: Comentarios en posts

## Cambios Recientes

Ver [CHANGELOG.md](../CHANGELOG.md)

## Actualizar Schema

```bash
dbl sandbox start
dbl reset
```

## Validar

```bash
dbl validate
```
```

## Monitoreo

### Alertas de Cambios

```bash
#!/bin/bash
# monitor-schema.sh

LAST_LAYER=$(dbl log --oneline | head -1)
LAST_FILE="/tmp/dbl_last_layer"

if [ -f "$LAST_FILE" ]; then
    PREVIOUS=$(cat "$LAST_FILE")
    if [ "$LAST_LAYER" != "$PREVIOUS" ]; then
        echo "Schema changed: $LAST_LAYER" | \
        mail -s "DBL Alert" team@company.com
    fi
fi

echo "$LAST_LAYER" > "$LAST_FILE"
```

### Performance Tracking

```bash
#!/bin/bash
# track-performance.sh

echo "Layer,Duration" > migration-times.csv

for layer in .dbl/layers/*.sql; do
    START=$(date +%s%N)
    dbl reset
    END=$(date +%s%N)
    
    DURATION=$(( (END - START) / 1000000 ))
    LAYER=$(basename "$layer")
    
    echo "$LAYER,$DURATION" >> migration-times.csv
done
```

## Anti-patrones a Evitar

### ❌ No Hagas Esto

```bash
# Cambios ad-hoc sin capas
$ psql myapp -c "ALTER TABLE users DROP COLUMN email;"

# Datos hardcodeados
INSERT INTO config VALUES ('api_key', 'secret123');

# Commits demasiado grandes
dbl commit -m "Everything: add 50 features"

# Sin validación
# ... cambios sin probar ...
$ dbl sandbox apply

# Sin backups
dbl reset  # Sin backup previo

# Ramas sin sincronizar
$ dbl checkout old-branch
# (hace semanas sin actualizar)
```

## Próximos Pasos

- [Ramas](../commands/branching/index.md) - Gestión de ramas
- [Configuración](configuration.md) - Setups avanzados
- [Architecture](../architecture/overview.md) - Cómo funciona DBL
