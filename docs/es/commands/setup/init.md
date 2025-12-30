# dbl init

Inicializa un proyecto DBL en el directorio actual.

## Sinopsis

```bash
dbl init
```

## Descripción

El comando `init` configura DBL en tu proyecto creando los archivos de configuración necesarios y la estructura de directorios. Este es el primer comando que debes ejecutar al comenzar a usar DBL con una base de datos.

## Qué Hace

1. **Crea `dbl.yaml`**: El archivo de configuración principal que contiene los detalles de conexión a la base de datos y configuraciones
2. **Crea el directorio `.dbl/`**: Espacio de trabajo interno de DBL para almacenar:
   - `layers/`: Migraciones SQL con control de versiones
   - `manifest.json`: Metadatos de ramas y capas
   - `state.json`: Seguimiento del estado actual de la base de datos
   - `snapshot.sql`: Volcado base de datos de referencia
3. **Inicializa la rama `master`**: Crea la rama predeterminada en el manifest

## Ejemplo de Uso

```bash
# Navega a tu proyecto
cd mi-proyecto

# Inicializa DBL
dbl init

# Salida:
# ✓ Archivo de configuración dbl.yaml creado
# ✓ Estructura de directorio .dbl creada
# ✓ Rama master inicializada
```

## Qué Hacer Después de Init

Después de ejecutar `init`, necesitas:

1. **Editar `dbl.yaml`** con las credenciales de tu base de datos:
   ```yaml
   engine: postgres  # o mysql
   host: localhost
   port: 5432
   user: miusuario
   password: micontraseña
   database: mibasededatos
   ```

2. **Importar tu base de datos** (opcional):
   ```bash
   dbl import snapshot.sql
   ```

3. **Comenzar a trabajar** con sandboxes:
   ```bash
   dbl sandbox start
   ```

## Archivo de Configuración (dbl.yaml)

El `dbl.yaml` generado contiene:

```yaml
engine: postgres  # Motor de base de datos (postgres o mysql)

# Detalles de conexión
host: localhost
port: 5432
user: tu_usuario
password: tu_contraseña
database: tu_basededatos

# Opcional: Soporte para Docker
# container_name: mi_contenedor_postgres

# Opcional: Filtrado de tablas
ignore_tables: []   # Tablas a excluir del seguimiento
track_tables: []    # Solo rastrear estas tablas (si se establece)

# Opcional: Políticas de seguridad
policies:
  allow_data_loss: false  # Prevenir operaciones destructivas
  require_sandbox: true   # Forzar uso de sandbox

# Opcional: Reglas de validación
validate:
  strict: false              # Tratar advertencias como errores
  allow_orphaned: false      # Permitir backfill sin expand
  require_comments: false    # Requerir comentarios para fase contract
  detect_type_changes: true  # Advertir sobre cambios de tipo de columna
```

## Estructura de Directorios

Después de la inicialización:

```
mi-proyecto/
├── dbl.yaml              # Archivo de configuración
├── .dbl/                 # Espacio de trabajo DBL (añadir a .gitignore)
│   ├── layers/           # Capas de migración
│   │   └── manifest.json # Metadatos de ramas y capas
│   ├── snapshot.sql      # Línea base de la base de datos
│   ├── state.json        # Estado actual
│   └── sandbox.json      # Metadatos del sandbox (cuando está activo)
└── .gitignore            # (recomendado) Añadir .dbl/ aquí
```

## Notas Importantes

!!! warning "Seguridad"
    El archivo `dbl.yaml` contiene credenciales de base de datos. **Nunca lo subas al control de versiones** si contiene información sensible.

!!! tip "Control de Versiones"
    Añade `.dbl/` a tu `.gitignore`:
    ```bash
    echo ".dbl/" >> .gitignore
    ```
    
    Solo rastrea las capas de migración por separado si es necesario para la colaboración en equipo.

!!! info "Soporte Docker"
    Si usas Docker, descomenta y establece `container_name` en `dbl.yaml` para ejecutar comandos dentro del contenedor.

## Problemas Comunes

### Ya Inicializado

Si DBL ya está inicializado:
```
Error: dbl.yaml ya existe
```

**Solución**: Elimina el `dbl.yaml` existente y el directorio `.dbl/` si deseas reinicializar:
```bash
rm dbl.yaml
rm -rf .dbl/
dbl init
```

### Permiso Denegado

Si obtienes errores de permisos:
```
Error: Permiso denegado al crear .dbl/
```

**Solución**: Asegúrate de tener permisos de escritura en el directorio actual o ejecuta con los permisos apropiados.

## Próximos Pasos

Después de la inicialización:

1. [Configura tu conexión de base de datos](../../guide/configuration.md)
2. [Crea tu primer sandbox](../../sandbox/start.md)
3. [Haz tu primera migración](../../getting-started/first-migration.md)

## Ver También

- [Guía de Configuración](../../guide/configuration.md)
- [Tutorial de Inicio Rápido](../../getting-started/quick-start.md)
