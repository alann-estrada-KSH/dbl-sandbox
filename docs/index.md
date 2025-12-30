# DBL - Database Layering

![Version](https://img.shields.io/badge/version-0.0.1--alpha-blue) ![Status](https://img.shields.io/badge/status-experimental-orange) ![Python](https://img.shields.io/badge/python-3.8+-green) ![License](https://img.shields.io/badge/license-Apache%202.0-blue)

**Git-like version control for databases**

---

## What is DBL?

DBL (Database Layering) is a **version control system for databases**, similar to Git but designed specifically for database schema evolution.

### Key Capabilities

- **🌿 Branch your schema** - Work on multiple features in parallel
- **🔒 Sandbox testing** - Experiment safely without affecting your database
- **📦 Layer your changes** - Version control for all SQL migrations
- **✅ Validated migrations** - Built-in checks for safe changes
- **🔄 Reproducible rebuilds** - Deterministic database reconstruction

---

## Quick Start

```bash
# 1. Initialize project
dbl init

# 2. Create development sandbox
dbl sandbox start

# 3. Make your changes
# Use your favorite database client to modify schema

# 4. Save your changes
dbl commit -m "Add user_preferences table"

# 5. Apply to main database
dbl sandbox apply
```

---

## Core Features

### Safe Experimentation with Sandboxes

Work in an isolated **sandbox** - a temporary copy of your database where you can test changes without any risk to production or development databases.

### Complete Layer History

Every change is saved as a numbered **layer** (like Git commits), creating a complete, auditable history of your database evolution. View the history anytime with `dbl log`.

### Git-like Branching

Create **branches** for different features:

```bash
dbl branch create feature/authentication
dbl checkout feature/authentication
# ... make your changes ...
dbl checkout main
dbl merge feature/authentication
```

### Supported Databases

- ✅ **PostgreSQL** 11+
- ✅ **MySQL** 5.7+
- 🔄 **SQLite** (planned)
- 🚧 MariaDB (planned)

---

## Installation

### Prerequisites

---

## Installation

Install DBL with pip:

```bash
pip install dbl
```

Or clone from GitHub for development:

```bash
git clone https://github.com/alann-estrada-KSH/dbl-sandbox.git
cd dbl-sandbox
pip install -e .
```

---

## Learn More

### Getting Started

New to DBL? Start here:

- [Installation Guide](getting-started/installation.md) - Detailed setup instructions
- [Quick Start Tutorial](getting-started/quick-start.md) - Your first changes in 5 minutes
- [First Migration](getting-started/first-migration.md) - Complete step-by-step example

### Reference

Need help with a specific command?

- [All Commands](commands/index.md) - Complete command reference
- [Sandbox Management](commands/sandbox/start.md) - Work with sandboxes
- [Branching Guide](commands/branching/index.md) - Branch management

### Deep Dives

Learn architecture and patterns:

- [Architecture Overview](architecture/overview.md) - How DBL works
- [Supported Databases](architecture/engines.md) - PostgreSQL, MySQL, more
- [Best Practices](guide/best-practices.md) - Tips for teams and projects
- [Configuration](guide/configuration.md) - Advanced setup options

### Help & Resources

- [FAQ](reference/faq.md) - 40+ common questions answered
- [Troubleshooting](reference/troubleshooting.md) - Fix common issues
- [Changelog](changelog.md) - Version history and changes

---

## Common Workflows

### Adding a New Feature

```bash
# Create feature branch
dbl branch create feature/payments

# Switch to feature branch
dbl checkout feature/payments

# Create sandbox
dbl sandbox start

# Make schema changes using your DB client
# ... CREATE TABLE payments ...
# ... CREATE INDEX idx_payments ...

# Review changes
dbl diff

# Save changes
dbl commit -m "Add payments table with indexes"

# Apply to feature branch database
dbl sandbox apply

# Switch back to main
dbl checkout main

# Merge changes
dbl merge feature/payments
```

### Testing Migrations

```bash
# Test in a clean environment
dbl sandbox start

# Rebuild database from all layers
dbl reset

# Run your application tests
./run-tests.sh

# Verify schema matches expected
dbl validate

# Deploy when ready
dbl sandbox apply
```

---

## Why DBL?

### Unlike Raw SQL Scripts

- ✅ Version controlled with Git
- ✅ No manual migration ordering
- ✅ Safe sandbox testing
- ✅ Complete audit trail

### Unlike ORM Migrations (Alembic, Django)

- ✅ Database-agnostic (PostgreSQL, MySQL, SQLite)
- ✅ Pure SQL - no framework dependency
- ✅ Portable between projects
- ✅ Works with any programming language

### Unlike Migration Tools (Flyway, Liquibase)

- ✅ Git-like branching for parallel work
- ✅ Sandbox for safe testing
- ✅ Simple YAML configuration
- ✅ Easy to learn and use

---

## Contributing

We welcome contributions! Here are some ways to help:

- 🐛 [Report bugs](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)
- 💡 [Suggest features](https://github.com/alann-estrada-KSH/dbl-sandbox/discussions)
- 📚 [Improve documentation](https://github.com/alann-estrada-KSH/dbl-sandbox)
- 💻 [Submit code](https://github.com/alann-estrada-KSH/dbl-sandbox/pulls)

---

## License

DBL is licensed under **Apache 2.0**. See [LICENSE](../LICENSE) for details.

---

## Support

- 🐙 **GitHub**: [alann-estrada-KSH/dbl-sandbox](https://github.com/alann-estrada-KSH/dbl-sandbox)
- 📝 **Issues**: [Report a bug](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)
- 💬 **Discussions**: [Ask a question](https://github.com/alann-estrada-KSH/dbl-sandbox/discussions)

---

Made with ❤️ by [Alan Estrada](https://github.com/alann-estrada-KSH)
