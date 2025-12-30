# Resumen de Comandos

DBL proporciona un conjunto completo de comandos organizados por funcionalidad. Esta guía te ayudará a entender qué hace cada comando y cuándo usarlo.

## Categorías de Comandos

### 🔧 Comandos de Configuración
Comandos para inicializar y mantener tu instalación de DBL.

| Comando | Descripción |
|---------|-------------|
| [`dbl init`](setup/init.md) | Inicializar DBL en tu proyecto |
| [`dbl version`](setup/version.md) | Mostrar información de versión de DBL |
| [`dbl update`](setup/update.md) | Verificar e instalar actualizaciones de DBL |

### 🏖️ Comandos de Sandbox
Entorno de pruebas seguro para cambios en la base de datos.

| Comando | Descripción |
|---------|-------------|
| [`dbl sandbox start`](sandbox/start.md) | Crear una base de datos sandbox aislada |
| [`dbl sandbox apply`](sandbox/apply.md) | Aplicar cambios del sandbox a la DB principal |
| [`dbl sandbox rollback`](sandbox/rollback.md) | Descartar todos los cambios del sandbox |
| [`dbl sandbox status`](sandbox/status.md) | Verificar estado del sandbox |

### 📝 Gestión de Cambios
Comandos para rastrear y confirmar cambios en la base de datos.

| Comando | Descripción |
|---------|-------------|
| [`dbl diff`](changes/diff.md) | Mostrar cambios en sandbox vs línea base |
| [`dbl commit`](changes/commit.md) | Guardar cambios como una capa versionada |
| [`dbl reset`](changes/reset.md) | Reconstruir base de datos desde capas |

### 🌿 Ramificación
Ramificación tipo Git para desarrollo paralelo.

| Comando | Descripción |
|---------|-------------|
| [`dbl branch`](../commands/branching/branch.md) | Listar, crear o eliminar ramas |
| [`dbl checkout`](../commands/branching/checkout.md) | Cambiar a una rama diferente |
| [`dbl merge`](../commands/branching/merge.md) | Fusionar cambios de otra rama |
| [`dbl pull`](../commands/branching/pull.md) | Traer cambios de otra rama |
| [`dbl rebase`](../commands/branching/rebase.md) | Rebasar rama actual sobre otra |

### 📜 Historial e Inspección
Ver y validar tu historial de base de datos.

| Comando | Descripción |
|---------|-------------|
| [`dbl log`](../commands/history/log.md) | Ver historial de capas |
| [`dbl rev-parse`](../commands/history/rev-parse.md) | Resolver referencias (HEAD, ramas) |
| [`dbl validate`](../commands/history/validate.md) | Validar patrones de migración |

## Referencia Rápida

### Flujos de Trabajo Comunes

**Flujo básico:**
```bash
dbl sandbox start      # Crear sandbox
# Hacer cambios en la base de datos...
dbl diff              # Revisar cambios
dbl commit -m "msg"   # Guardar cambios
dbl sandbox apply     # Aplicar a DB principal
```

**Flujo de ramas:**
```bash
dbl branch feature-x  # Crear rama
dbl checkout feature-x # Cambiar a rama
# Trabajar en la funcionalidad...
dbl checkout master   # Volver a master
dbl merge feature-x   # Fusionar cambios
```

**Revisar historial:**
```bash
dbl log               # Historial completo
dbl log --oneline     # Vista compacta
dbl log -n 5          # Últimas 5 capas
```

## Patrones de Sintaxis de Comandos

DBL sigue patrones consistentes en todos los comandos:

- **Banderas**: Opciones que comienzan con `-` o `--`
- **Argumentos**: Parámetros requeridos u opcionales
- **Subcomandos**: Comandos con acciones (ej., `sandbox start`)

### Ejemplos:
```bash
dbl comando [opciones] [argumentos]
dbl comando subcomando [opciones]
dbl comando --bandera valor argumento
```

## Obtener Ayuda

Para ayuda detallada sobre cualquier comando:
```bash
dbl help
dbl <comando> --help
```

## Próximos Pasos

- [Tutorial de Inicio Rápido](../getting-started/quick-start.md)
- [Mejores Prácticas](../guide/best-practices.md)
- [Guía de Configuración](../guide/configuration.md)

## Glosario

**Capa (Layer)**: Un conjunto versionado de cambios SQL  
**Sandbox**: Base de datos temporal para pruebas seguras  
**Rama (Branch)**: Línea paralela de desarrollo de esquema  
**Manifest**: Registro de ramas, capas e historial  
**HEAD**: Referencia a la capa actual  
**Baseline**: Estado de referencia para detección de cambios
