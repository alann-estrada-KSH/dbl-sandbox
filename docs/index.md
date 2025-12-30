# DBL - Database Layering

<div align="center">

![Version](https://img.shields.io/badge/version-0.0.1--alpha-blue)
![Status](https://img.shields.io/badge/status-experimental-orange)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Git-like version control for databases**

[Getting Started](getting-started.md) · [Commands](commands.md) · [Architecture](architecture.md) · [Changelog](changelog.md)

</div>

---

## What is DBL?

DBL (Database Layering) is a **lightweight CLI tool** that brings Git-like workflows to database schema evolution:

- 🌿 **Branch your schema** - Work on multiple features in parallel
- 🔒 **Sandbox experiments** - Test changes without breaking your database
- 📦 **Layer your changes** - Version control for SQL migrations
- ✅ **Validate patterns** - Automated checks for safe migrations
- 🔄 **Replay changes** - Deterministic database rebuilds

---

## Quick Start

```bash
# Initialize project
dbl init

# Create sandbox
dbl sandbox start

# Make your changes in your database...

# Commit changes
dbl commit -m "Add user_preferences table"

# Apply changes
dbl sandbox apply
```

---

## Key Features

### 🛡️ Safe Experimentation
Work in a **sandbox mode** that clones your database, allowing you to test changes without risk.

### 📚 Layer History
Every change is saved as a **layer** (like a git commit), creating a complete history of your database evolution.

### 🌿 Branching
Create **branches** to work on different features simultaneously, just like git branches.

### 🔍 Smart Validation
Automatically detects risky operations:
- Uncommented DROP statements
- Missing backfill operations
- Type changes without data migration
- Mixed schema/data changes

### 🔄 Three-Phase Migrations
Follows best practices with:
1. **Expand** - Add new structures (safe)
2. **Backfill** - Migrate data (optional)
3. **Contract** - Remove old structures (careful)

---

## Supported Databases

- ✅ PostgreSQL (9.6+)
- ✅ MySQL (5.7+)
- 🚧 SQLite (planned)
- 🚧 MariaDB (planned)

---

## Installation

### Prerequisites

- Python 3.8+
- Database CLI tools:
  - PostgreSQL: `psql`, `pg_dump`
  - MySQL: `mysql`, `mysqldump`

### Install

```bash
# Clone repository
git clone https://github.com/alann-estrada-KSH/dbl-sandbox.git
cd dbl-sandbox

# Install dependencies
pip install pyyaml

# Make executable (Unix/Linux/Mac)
chmod +x dbl.py

# Run
./dbl.py version
```

---

## Documentation

- [Getting Started Guide](getting-started.md)
- [Command Reference](commands.md)
- [Architecture Overview](architecture.md)
- [Migration Patterns](patterns.md)
- [Best Practices](best-practices.md)
- [Changelog](changelog.md)

---

## Example Workflow

```bash
# 1. Initialize project
dbl init

# 2. Import existing database
dbl import snapshot.sql

# 3. Create feature branch
dbl branch feature/add-auth

# 4. Start sandbox
dbl sandbox start

# 5. Make schema changes in your database
# ... use your favorite DB client ...

# 6. Review changes
dbl diff

# 7. Commit layer
dbl commit -m "Add authentication tables"

# 8. Apply changes
dbl sandbox apply

# 9. Merge to master
dbl checkout master
dbl merge feature/add-auth
```

---

## Comparison with Other Tools

| Feature | DBL | Flyway | Liquibase | Rails Migrations |
|---------|-----|--------|-----------|------------------|
| Git-like branching | ✅ | ❌ | ❌ | ❌ |
| Sandbox testing | ✅ | ❌ | ❌ | ❌ |
| Schema inspection | ✅ | ❌ | ✅ | ✅ |
| Migration validation | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Production-ready | ❌ | ✅ | ✅ | ✅ |

**Note**: DBL complements, doesn't replace production migration tools.

---

## Warnings ⚠️

This is **alpha software**. Use only in development:

- ⚠️ Can drop databases and delete data
- ⚠️ Generates SQL that may be destructive
- ⚠️ Not suitable for production deployments
- ⚠️ Always backup before using

---

## Contributing

Contributions are welcome! Please read our [Contributing Guide](contributing.md).

---

## License

MIT License - see [LICENSE](../LICENSE) for details.

---

## Roadmap

### v0.1.0 (Next)
- [ ] SQLite support
- [ ] Migration squashing
- [ ] Diff visualization
- [ ] Config validation

### v0.2.0
- [ ] Remote sync (git-like push/pull)
- [ ] Team collaboration features
- [ ] Migration testing framework

### v1.0.0
- [ ] Production hardening
- [ ] Full documentation
- [ ] CI/CD integration examples

---

## Community

- 📝 [Report Issues](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)
- 💬 [Discussions](https://github.com/alann-estrada-KSH/dbl-sandbox/discussions)
- 🐦 Follow updates: [@alann-estrada-KSH](https://github.com/alann-estrada-KSH)

---

<div align="center">

**Made with ❤️ by [Alan Estrada](https://github.com/alann-estrada-KSH)**

</div>
