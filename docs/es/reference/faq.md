# FAQ

Preguntas frecuentes sobre DBL.

## General

### ¿Qué es DBL?

DBL (Database Layering) es una herramienta de control de versiones para bases de datos, similar a Git pero para esquemas de bases de datos.

### ¿Necesito Git?

No es obligatorio pero se recomienda. DBL puede trabajar solo, pero Git ayuda con colaboración y auditoría.

### ¿Funciona con mi base de datos?

DBL soporta:
- ✅ PostgreSQL 11+
- ✅ MySQL 5.7+
- 🔄 MariaDB (próximamente)
- 🔄 SQLite (en desarrollo)

### ¿Es gratuito?

Sí, DBL es open source bajo licencia Apache 2.0.

## Instalación

### ¿Cómo instalo DBL?

```bash
pip install dbl
```

Requiere Python 3.7+.

### ¿Tengo que instalar dependencias de BD?

No. DBL los instala automáticamente si faltan:
- `psycopg2` para PostgreSQL
- `mysql-connector-python` para MySQL

### ¿Qué versión de Python?

Python 3.7 o mayor. Probado en 3.7, 3.8, 3.9, 3.10, 3.11.

## Configuración

### ¿Dónde va el archivo de configuración?

El archivo `dbl.yaml` va en la raíz del proyecto:

```
mi-proyecto/
├── dbl.yaml      ← Aquí
├── .dbl/
├── README.md
└── ...
```

### ¿Puedo tener múltiples archivos de config?

Sí:

```bash
dbl --config production.yaml init
dbl --config staging.yaml reset
dbl --config development.yaml sandbox start
```

### ¿Cómo protejo mis credenciales?

Usa variables de ambiente:

```yaml
engine: postgres
database:
  host: ${DB_HOST}
  user: ${DB_USER}
  password: ${DB_PASSWORD}
```

```bash
export DB_HOST=prod.example.com
export DB_USER=admin
export DB_PASSWORD=secret
dbl init
```

## Sandbox

### ¿Qué es el sandbox?

Una copia temporal de tu base de datos donde experimentar cambios sin afectar la principal.

### ¿El sandbox copia datos?

Solo el esquema (estructura). No los datos de producción por defecto.

Para incluir datos:

```bash
dbl sandbox start --copy-data
```

### ¿Dónde se crea el sandbox?

En el mismo servidor/motor, con nombre `{database}_sandbox`.

Ejemplo:
- Principal: `myapp`
- Sandbox: `myapp_sandbox`

### ¿Cuánto espacio ocupa?

Igual al esquema de la BD principal. Si copias datos, igual a la BD completa.

### ¿Puedo ejecutar múltiples sandboxes?

Por el momento, un sandbox activo por rama. Se pueden crear en diferentes ramas simultáneamente.

## Commits y Capas

### ¿Cuándo debo hacer commit?

Después de completar un cambio lógico:

```bash
dbl commit -m "Add user authentication"
dbl commit -m "Optimize search indexes"
dbl commit -m "Add payment processing"
```

### ¿Puedo deshacer un commit?

Sí, de varias formas:

```bash
# Rollback del sandbox (cambios sin guardar)
dbl sandbox rollback

# Resetear base a punto anterior
dbl reset  # Reconstruir desde capas

# Eliminar capa (avanzado)
rm .dbl/layers/L015_*.sql
```

### ¿Qué tamaño deben tener las capas?

Preferiblemente pequeñas y lógicas. Una tabla, un índice, una migración de datos.

No:
```
L001 - Crear 50 tablas, 100 índices, cargar datos
```

Mejor:
```
L001 - Crear tabla users
L002 - Crear tabla posts
L003 - Crear índices en users
```

## Ramas

### ¿Cuándo debo crear rama?

Cuando trabajas en feature que toma tiempo o querés aislar del trabajo principal.

```bash
dbl branch create feature/payment
dbl checkout feature/payment
# ... desarrollo ...
dbl checkout main
dbl merge feature/payment
```

### ¿Puedo eliminar rama?

Sí, después de fusionar:

```bash
dbl branch delete feature/payment
```

### ¿Qué pasa si tengo cambios sin fusionar?

DBL te avisa. Debes fusionar o descartar antes de continuar.

## Validación

### ¿Por qué validar?

Para asegurar que:
- Todas las capas funcionan
- Esquema está limpio
- No hay problemas antes de deploy

```bash
dbl validate --check-layers
```

### ¿Qué hace exactamente?

Verifica:
- ✅ Sintaxis SQL correcta
- ✅ Capas pueden ejecutarse
- ✅ No hay conflictos
- ✅ Integridad referencial

### ¿Cuándo debo validar?

Frecuentemente, especialmente:
- Antes de Push a Git
- Antes de deploy a Staging
- Antes de deploy a Producción

## Performance

### ¿Cuánto tarda un reset?

Depende de tamaño de BD:
- Pequeña (100MB): <1 segundo
- Mediana (1GB): 5-10 segundos
- Grande (10GB+): 1-5 minutos

### ¿Cómo optimizar resets?

- Usar índices apropiados
- Evitar datos enormes en migrations
- Usar patrón expand-contract para cambios grandes

### ¿Pueden afectar commits el rendimiento?

No. Los commits solo guardan SQL, no afectan performance.

## Producción

### ¿Es DBL para producción?

Sí, pero con cuidado:

```bash
# NUNCA en producción sin backup
pg_dump myapp > backup.sql
dbl sandbox apply
```

### ¿Cómo es el flujo a producción?

```
1. Desarrollo: dbl sandbox apply en dev
2. Testing: dbl reset en ambiente test
3. Staging: dbl sandbox apply en staging
4. Producción: dbl sandbox apply en producción (con backup)
```

### ¿Puede causar downtime?

Algunas operaciones pueden bloquear tablas brevemente. Planifica en horarios de bajo uso.

### ¿Hay rollback?

No automático. Por eso:
1. Hacer backup antes
2. Testear en staging
3. Aplicar en ventana de mantenimiento

## Seguridad

### ¿Se guardan passwords?

No en capas. Las capas contienen SQL, no credenciales.

**Malo:**
```sql
INSERT INTO admins VALUES ('admin', 'password123');
```

**Bueno:**
```sql
-- Password viene de SQL script separado
-- O variable de ambiente
```

### ¿Puedo ocultar cambios sensibles?

Usar archivos separados:

```bash
# En .gitignore
echo "secrets.sql" >> .gitignore

# Aplicar por separado
dbl sandbox start
psql -d myapp_sandbox < secrets.sql
dbl commit -m "Run secrets migration"
```

### ¿Quién puede ver el historial de cambios?

Toda persona con acceso a `.dbl/layers/`. Es recomendable:

```bash
chmod 600 .dbl/config.yaml
chmod 700 .dbl/layers/
```

## Troubleshooting

### ¿Dbl no encuentra la BD?

Verifica configuración:

```bash
dbl --verbose init
# Muestra detalles de conexión
```

### ¿Sandbox no se elimina?

Limpiar manualmente:

```bash
psql -c "DROP DATABASE myapp_sandbox;"
rm .dbl/sandbox.json
```

### ¿Merge tiene conflictos?

Ver archivo de conflicto y resolver:

```bash
# DBL indica qué archivo tiene conflicto
# Editar manualmente
vim .dbl/layers/L020_*.sql

# Marcar como resuelto
dbl merge --continue
```

## Integración

### ¿Funciona con Docker?

Sí:

```dockerfile
FROM python:3.9
RUN pip install dbl
RUN dbl init
RUN dbl reset
```

### ¿Funciona con CI/CD?

Sí, perfecto para pipelines:

```yaml
- name: Test migrations
  run: dbl reset && pytest tests/
```

### ¿Funciona con ORMs?

Sí. DBL maneja esquema, ORM maneja datos:

```bash
# DBL: cambios de esquema
dbl sandbox start
# ... cambios BD ...
dbl commit -m "Add users table"
dbl sandbox apply

# ORM: migración de datos
# ... código ORM ...
```

## Comparaciones

### DBL vs Flyway

```
Flyway:
- ✅ Java-centric
- ❌ SQL sin versionado
- ❌ Sin sandbox

DBL:
- ✅ Language-agnostic
- ✅ SQL con versionado Git
- ✅ Sandbox para seguridad
```

### DBL vs Liquibase

```
Liquibase:
- ✅ Muy flexible
- ❌ Complejo de aprender
- ❌ XML/YAML en lugar de SQL

DBL:
- ✅ Simple: puro SQL
- ✅ Fácil de aprender
- ✅ Git-like familiar
```

### DBL vs ORM Migrations

```
ORM (Alembic, Django):
- ✅ Integrado
- ❌ Acoplado a framework
- ❌ Lenguaje específico

DBL:
- ✅ Independiente
- ✅ Cualquier framework
- ✅ SQL puro
```

## Próximos Pasos

- [Guía de inicio](../getting-started/installation.md)
- [Troubleshooting](troubleshooting.md)
- [Contact us](https://github.com/dbl-project)
