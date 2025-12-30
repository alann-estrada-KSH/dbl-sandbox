# DBL - Database Layering

## Estructura del Proyecto

El proyecto ahora está organizado de forma modular para mejorar la mantenibilidad:

```
dbl-sandbox/
├── dbl.py                  # Entry point principal
├── dbl/                    # Paquete principal
│   ├── __init__.py        # Metadata del paquete
│   ├── constants.py       # Constantes y configuraciones
│   ├── errors.py          # Excepciones personalizadas
│   ├── utils.py           # Funciones utilitarias
│   ├── manifest.py        # Gestión de manifiestos
│   ├── config.py          # Gestión de configuración
│   ├── state.py           # Gestión de estado de BD
│   ├── planner.py         # Generador de SQL de migración
│   ├── engines/           # Motores de base de datos
│   │   ├── __init__.py
│   │   ├── base.py        # Clase abstracta base
│   │   ├── postgres.py    # Implementación PostgreSQL
│   │   └── mysql.py       # Implementación MySQL
│   └── commands/          # Comandos CLI
│       ├── __init__.py
│       ├── help_cmd.py    # help, version
│       ├── init.py        # init, import
│       ├── sandbox.py     # sandbox (start/apply/rollback/status)
│       ├── diff.py        # diff
│       ├── commit.py      # commit
│       ├── branch.py      # branch, checkout, merge, pull
│       ├── log.py         # log, rev-parse
│       ├── reset.py       # reset
│       ├── rebase.py      # rebase
│       └── validate.py    # validate
```

## Arquitectura

### Separación de Responsabilidades

1. **constants.py**: Todas las constantes, paths y colores
2. **errors.py**: Excepciones personalizadas
3. **utils.py**: Funciones auxiliares (log, run_command, confirm_action)
4. **manifest.py**: Gestión de branches y layers
5. **config.py**: Carga de configuración y factory de engines
6. **state.py**: Comparación de estado de BD
7. **planner.py**: Generación inteligente de SQL

### Engines (Abstracción de BD)

- **base.py**: Clase abstracta `DBEngine` con interfaz común
- **postgres.py**: Implementación específica para PostgreSQL
- **mysql.py**: Implementación específica para MySQL

Cada engine implementa:
- Operaciones CRUD de BD
- Inspección de schema (AST)
- Generación de SQL dialect-specific
- Dump de estructura y datos

### Commands (Comandos CLI)

Cada comando en su propio módulo para:
- Mejor navegación del código
- Testing unitario más fácil
- Menor acoplamiento
- Reutilización de lógica

## Ventajas de la Nueva Estructura

1. **Mantenibilidad**: Cada módulo tiene una responsabilidad clara
2. **Escalabilidad**: Fácil agregar nuevos engines o comandos
3. **Testing**: Cada módulo se puede testear independientemente
4. **Legibilidad**: Código más organizado y fácil de entender
5. **Reutilización**: Componentes modulares reutilizables

## Migración desde dbl.py monolítico

El archivo `dbl.py` monolítico original se ha dividido en:
- 13 módulos core
- 3 engines
- 10 comandos separados

**Total**: De 1 archivo de ~1000 líneas a 26 archivos modulares.

## Uso

El uso es idéntico al anterior:

```bash
python dbl.py init
python dbl.py sandbox start
python dbl.py commit -m "mi cambio"
# etc.
```

## Desarrollo

Para agregar un nuevo comando:

1. Crear archivo en `dbl/commands/nuevo_cmd.py`
2. Implementar función `cmd_nuevo(args)`
3. Importar en `dbl/commands/__init__.py`
4. Agregar parser en `dbl.py` main()

Para agregar un nuevo engine:

1. Crear archivo en `dbl/engines/nuevo_engine.py`
2. Heredar de `DBEngine` e implementar métodos abstractos
3. Importar en `dbl/engines/__init__.py`
4. Agregar factory en `dbl/config.py`
