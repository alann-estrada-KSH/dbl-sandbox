# Changelog

All notable changes to DBL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Auto-update command**: `dbl update` to check and install latest version from GitHub
  - Interactive mode with release notes preview
  - Auto-confirm option with `-y` flag
  - Automatic installation via pip
  - Version comparison (ignores alpha/beta suffixes for compatibility)
  - Automatic dependency checking and installation
- **Package distribution support**:
  - `setup.py` for pip installation
  - `pyproject.toml` for modern Python packaging
  - `requirements.txt` for dependency management
  - `MANIFEST.in` for distribution file inclusion
  - Entry point for `dbl` command after pip install
  - Support for `python -m dbl` execution
- **Dependency management**:
  - Automatic detection of missing dependencies (PyYAML)
  - Auto-install option for missing dependencies
  - Clear error messages with installation instructions

### Changed
- **Installation process**: Now supports `pip install git+https://...` for easy installation
- **Documentation**: Expanded installation guide with multiple installation methods
- **Troubleshooting**: Added comprehensive troubleshooting section in README

### Planned
- SQLite engine support
- Migration squashing command
- Visual diff tool
- Config file validation

---

## [0.0.1-alpha] - 2025-12-30

### 🎉 Initial Release

#### Added
- **Core Functionality**
  - Basic CLI with argparse
  - Git-like command structure (init, commit, branch, checkout, etc.)
  - PostgreSQL engine implementation
  - MySQL engine implementation
  
- **Sandbox Mode**
  - Safe experimentation with shadow databases
  - `sandbox start` - Create isolated environment
  - `sandbox apply` - Confirm changes
  - `sandbox rollback` - Discard changes
  - `sandbox status` - Check current state

- **Layer Management**
  - Commit schema changes as layers
  - Layer history tracking
  - Migration SQL generation with phases (expand/backfill/contract)
  - Editor integration for manual SQL review

- **Branching System**
  - Create branches for parallel development
  - Switch between branches with `checkout`
  - Merge branches
  - Pull changes from other branches
  - Branch metadata tracking (parent, creation date)

- **Database Operations**
  - Schema inspection (AST generation)
  - Table structure analysis
  - Data hash tracking for change detection
  - Smart cloning (template-based or pg_dump fallback)

- **Validation**
  - Phase validation (expand/backfill/contract)
  - Detection of risky operations:
    - Uncommented DROP statements
    - Type changes
    - Missing backfill operations
    - Mixed data/schema changes
  - Configurable validation rules
  - Non-blocking warnings

- **Advanced Commands**
  - `diff` - Detect database changes
  - `log` - View layer history
  - `rebase` - Rebase branches (git-style)
  - `rev-parse` - Resolve references
  - `reset` - Rebuild database from layers
  - `validate` - Check migration patterns

- **Configuration**
  - YAML-based configuration (`dbl.yaml`)
  - Engine selection (postgres/mysql)
  - Docker container support
  - Table tracking configuration
  - Policy settings (drop protection)

#### Architecture
- **Modular Structure** (26 files)
  - Separated engines into pluggable architecture
  - Command modules for each CLI operation
  - Core services (config, state, planner, manifest)
  - Utility functions and error handling

- **Database Abstraction**
  - `DBEngine` abstract base class
  - Dialect-specific SQL generation
  - Inspector pattern for schema introspection
  - Pluggable engine system

#### Documentation
- README with quick start guide
- Architecture documentation (ARCHITECTURE.md)
- Visual structure diagrams (STRUCTURE.md)
- Inline code documentation

#### Known Issues
- ⚠️ Alpha quality - not production ready
- ⚠️ Limited error recovery
- ⚠️ No remote sync capability
- ⚠️ Basic conflict resolution
- ⚠️ Windows path handling may need adjustment

#### Breaking Changes
- N/A (initial release)

---

## Version Naming Convention

DBL follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0) - Incompatible API changes
- **MINOR** version (0.X.0) - New functionality (backwards compatible)
- **PATCH** version (0.0.X) - Bug fixes (backwards compatible)

### Pre-release Tags
- **alpha** - Early testing, unstable, expect breaking changes
- **beta** - Feature complete, stabilizing, minor breaking changes possible
- **rc** (release candidate) - Final testing before stable release

### Examples
- `0.0.1-alpha` - Initial alpha release
- `0.1.0-beta.1` - First beta of v0.1
- `0.1.0-rc.1` - Release candidate
- `0.1.0` - Stable release
- `1.0.0` - Production-ready

---

## Contributing

See changes you'd like to make? Check out our [Contributing Guide](contributing.md)!

---

## Links

- [Homepage](https://alann-estrada-ksh.github.io/dbl-sandbox/)
- [GitHub Repository](https://github.com/alann-estrada-KSH/dbl-sandbox)
- [Issue Tracker](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)
