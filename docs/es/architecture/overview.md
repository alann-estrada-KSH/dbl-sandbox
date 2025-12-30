# Visión General de Arquitectura

Cómo funciona DBL internamente y conceptos clave.

## Modelo de Capas (Layers)

DBL ve tu base de datos como una serie de capas incrementales:

```
Capa L001: Esquema base
Capa L002: Tabla de usuarios
Capa L003: Tabla de posts
Capa L004: Tabla de comentarios
...
```

Cada capa:
- Es un archivo SQL autónomo
- Se puede ejecutar de forma independiente
- Construye sobre capas previas
- Es idempotente (se puede ejecutar múltiples veces)

### Construcción Desde Cero

Para reproducir la base de datos:

```bash
$ dbl reset

1. Ejecutar L001
   → Crea tabla users, posts
   
2. Ejecutar L002
   → Crea tabla comments
   
3. Ejecutar L003
   → Agrega índices
   
4. Ejecutar L004
   → Agrega constraints
```

## Flujo de Sandbox

El sandbox es tu área segura de trabajo:

```
Base de datos Principal
     ↓
   COPIA
     ↓
Base de datos Sandbox
     ↓
  Cambios aquí (seguro)
     ↓
  ¿Listo? Commit → Capas
     ↓
  Aplicar a Principal
```

### Proceso Detallado

```
1. dbl sandbox start
   → Copia esquema a sandbox_db
   
2. Hacer cambios
   → Ejecutar SQL en sandbox_db
   → Base principal intacta
   
3. dbl diff
   → Comparar sandbox vs main
   → Ver qué cambió
   
4. dbl commit
   → Guardar cambios como nueva capa
   
5. dbl sandbox apply
   → Ejecutar capa en base principal
   → Eliminar sandbox_db
```

## Almacenamiento de Estado

### Directorio .dbl

```
.dbl/
├── config.yaml         ← Configuración
├── state.json          ← Estado actual
├── sandbox.json        ← Metadata del sandbox
└── layers/
    ├── L001_initial_schema.sql
    ├── L002_add_users.sql
    ├── L003_add_posts.sql
    ...
```

### state.json

```json
{
  "version": "2.1.0",
  "database": "myapp",
  "engine": "postgres",
  "current_branch": "main",
  "latest_layer": "L015",
  "layers_applied": 15,
  "last_update": "2024-12-30T14:35:22Z"
}
```

## Gestión de Ramas

Las ramas permiten desarrollo paralelo:

```
main
├── L001 → L002 → L003 → ... → L015
└── feature/auth
    └── L001 → L002 → L003 → ... → L012 → L013 → L014
```

Cada rama tiene su propio historial de capas.

## Sincronización Entre Ambientes

```
Desarrollo
   ↓
Capas guardadas en .dbl/layers
   ↓
Staging (aplica capas)
   ↓
Producción (aplica capas)
```

Mismo código de migración en todos los ambientes.

## Conceptos Clave

### Idempotencia

Cada capa debe poderse ejecutar múltiples veces sin error:

```sql
-- ✅ Idempotente
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY
);

-- ❌ No idempotente
CREATE TABLE users (
    id SERIAL PRIMARY KEY
);  -- Error si tabla existe
```

### Declarativo vs Imperativo

DBL favorece cambios declarativos:

```sql
-- ✅ Declarativo (DBL lo prefiere)
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id)
);

-- ❌ Imperativo (evitar)
DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'comments') THEN
        CREATE TABLE comments ...
    END IF;
END $$;
```

### Atomicidad

Cada capa debe ser una transacción:

```sql
BEGIN;
    CREATE TABLE notifications (...);
    CREATE INDEX idx_notifications (...);
    INSERT INTO config VALUES (...);
COMMIT;
```

Si algo falla, nada se aplica.

## Flujo de Desarrollo

```
1. Clone del repo
   → Obtiene .dbl/layers/

2. dbl reset
   → Reconstruye base desde capas

3. dbl sandbox start
   → Área segura para cambios

4. Hacer cambios
   → Experimentar sin riesgos

5. dbl commit
   → Guardar cambios

6. dbl sandbox apply
   → Aplicar a base principal

7. git commit
   → Guardar capas en Git

8. git push
   → Compartir con equipo
```

## Comparación con Alternativas

### vs Raw SQL Scripts

```
Raw SQL:
- ❌ Difícil de reproducir
- ❌ Sin versionado
- ❌ Sin rollback seguro
- ❌ Sin debugging

DBL:
- ✅ Reproducible
- ✅ Versionado con Git
- ✅ Sandbox seguro
- ✅ Debugging claro
```

### vs Migraciones ORM (Sequelize, Alembic)

```
ORM Migrations:
- ✅ Integrado con código
- ❌ Código específico por lenguaje
- ❌ Acoplado a ORM

DBL:
- ✅ SQL puro, agnóstico de lenguaje
- ✅ Independiente de código
- ✅ Funciona con cualquier framework
```

## Próximos Pasos

- [Engines soportados](engines.md)
- [Guía de configuración](../guide/configuration.md)
- [Mejores prácticas](../guide/best-practices.md)
