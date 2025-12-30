# DBL - Database Layering

## Project Structure

The project is now organized in a modular way to improve maintainability:

```
dbl-sandbox/
├── dbl.py                  # Main entry point
├── dbl/                    # Main package
│   ├── __init__.py        # Package metadata
│   ├── constants.py       # Constants and configurations
│   ├── errors.py          # Custom exceptions
│   ├── utils.py           # Utility functions
│   ├── manifest.py        # Manifest management
│   ├── config.py          # Configuration management
│   ├── state.py           # Database state management
│   ├── planner.py         # Migration SQL generator
│   ├── engines/           # Database engines
│   │   ├── __init__.py
│   │   ├── base.py        # Abstract base class
│   │   ├── postgres.py    # PostgreSQL implementation
│   │   └── mysql.py       # MySQL implementation
│   └── commands/          # CLI commands
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

## Architecture

### Separation of Concerns

1. **constants.py**: All constants, paths, and colors
2. **errors.py**: Custom exceptions
3. **utils.py**: Auxiliary functions (log, run_command, confirm_action)
4. **manifest.py**: Branch and layer management
5. **config.py**: Configuration loading and engine factory
6. **state.py**: Database state comparison
7. **planner.py**: Intelligent SQL generation

### Engines (DB Abstraction)

- **base.py**: Abstract `DBEngine` class with common interface
- **postgres.py**: PostgreSQL-specific implementation
- **mysql.py**: MySQL-specific implementation

Each engine implements:
- Database CRUD operations
- Schema inspection (AST)
- Dialect-specific SQL generation
- Structure and data dump

### Commands (CLI Commands)

Each command in its own module for:
- Better code navigation
- Easier unit testing
- Lower coupling
- Logic reuse

## Advantages of the New Structure

1. **Maintainability**: Each module has a clear responsibility
2. **Scalability**: Easy to add new engines or commands
3. **Testing**: Each module can be tested independently
4. **Readability**: More organized and understandable code
5. **Reuse**: Modular reusable components

## Migration from Monolithic dbl.py

The original monolithic `dbl.py` file has been split into:
- 13 core modules
- 3 engines
- 10 separate commands

**Total**: From 1 file of ~1000 lines to 26 modular files.

## Usage

The usage is identical to before:

```bash
python dbl.py init
python dbl.py sandbox start
python dbl.py commit -m "my change"
# etc.
```

## Development

To add a new command:

1. Create file in `dbl/commands/new_cmd.py`
2. Implement `cmd_new(args)` function
3. Import in `dbl/commands/__init__.py`
4. Add parser in `dbl.py` main()

To add a new engine:

1. Create file in `dbl/engines/new_engine.py`
2. Inherit from `DBEngine` and implement abstract methods
3. Import in `dbl/engines/__init__.py`
4. Add factory in `dbl/config.py`
