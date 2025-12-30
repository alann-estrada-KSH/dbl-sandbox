# Architecture Overview

Understanding how DBL works internally.

## Core Concepts

### 1. Layers

Layers are the fundamental unit of change in DBL.

```
┌─────────────────────────────────────┐
│ Layer (L005)                        │
├─────────────────────────────────────┤
│ ID: L005                            │
│ Message: "Add comments feature"     │
│ Timestamp: 2024-12-30 14:32:11      │
│ SQL: CREATE TABLE comments (...)    │
│ Branch: main                        │
└─────────────────────────────────────┘
```

**Properties:**
- **Sequential**: Numbered L001, L002, L003...
- **Immutable**: Once created, shouldn't be changed
- **Reproducible**: Can be replayed anytime
- **Portable**: Plain SQL files

### 2. State

DBL tracks database state in `.dbl/state.json`:

```json
{
  "database": "myapp",
  "engine": "postgres",
  "branch": "main",
  "last_layer": "L015",
  "active_sandbox": null,
  "created_at": "2024-12-28T10:00:00Z"
}
```

**Tracks:**
- Current database
- Active branch
- Last applied layer
- Sandbox status

### 3. Sandboxes

Sandboxes are temporary database copies:

```
┌──────────────┐         ┌──────────────────┐
│  Main DB     │         │  Sandbox DB      │
│  myapp       │ copy    │  myapp_sandbox   │
│              │────────>│                  │
│  (stable)    │         │  (experimental)  │
└──────────────┘         └──────────────────┘
```

**Features:**
- Isolated from main database
- Can be applied or discarded
- Automatically managed

### 4. Branches

Branches enable parallel development:

```
main:       L001 ─ L002 ─ L003 ─ L004
                      │
                      └─ L005 ─ L006  (feature-auth)
```

**Allows:**
- Independent feature development
- Team collaboration
- Experimental changes

## System Architecture

### Directory Structure

```
project/
├── dbl.yaml                    # Configuration
├── .dbl/                       # DBL metadata
│   ├── state.json             # Current state
│   ├── sandbox.json           # Active sandbox info
│   ├── layers/                # Committed changes
│   │   ├── L001_initial.sql
│   │   ├── L002_add_users.sql
│   │   └── L003_add_posts.sql
│   └── branches/              # Branch metadata
│       ├── main.json
│       └── feature-auth.json
└── migrations/                # Your app migrations (optional)
```

### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│                    DBL Core                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Config  │  │  State   │  │ Planner  │         │
│  │ Manager  │  │ Manager  │  │          │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │             │                │
│  ┌────┴─────────────┴─────────────┴─────┐         │
│  │         Layer Manager                 │         │
│  └────────────────┬──────────────────────┘         │
│                   │                                │
│  ┌────────────────┴──────────────────────┐         │
│  │        Database Engine                │         │
│  │  ┌──────────┐      ┌──────────┐       │         │
│  │  │PostgreSQL│      │  MySQL   │       │         │
│  │  │ Engine   │      │ Engine   │       │         │
│  │  └──────────┘      └──────────┘       │         │
│  └───────────────────────────────────────┘         │
│                                                     │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   Database    │
                  │   (Postgres/  │
                  │    MySQL)     │
                  └───────────────┘
```

## Workflow Diagrams

### Sandbox Workflow

```
┌──────────────────────────────────────────────────────┐
│                 Sandbox Lifecycle                     │
└──────────────────────────────────────────────────────┘

   [Start]
      │
      ▼
   dbl sandbox start
      │
      ├─ Create sandbox DB (copy main)
      ├─ Track in sandbox.json
      └─ Mark as active
      │
      ▼
   [Make Changes]
      │
      ├─ Direct SQL
      ├─ Application ORM
      └─ Manual edits
      │
      ▼
   dbl diff
      │
      └─ Compare sandbox vs main
      │
      ▼
   dbl commit
      │
      ├─ Generate SQL layer
      ├─ Save to .dbl/layers/
      └─ Update state
      │
      ▼
   Decision: Apply or Rollback?
      │
      ├─ Apply ──────────┐
      │   │              │
      │   ▼              │
      │ dbl sandbox apply│
      │   │              │
      │   ├─ Apply to    │
      │   │   main DB    │
      │   ├─ Drop sandbox│
      │   └─ Clean state │
      │                  │
      └─ Rollback ───────┤
          │              │
          ▼              │
      dbl sandbox rollback
          │              │
          └─ Drop sandbox│
                         │
                         ▼
                      [End]
```

### Reset Workflow

```
┌──────────────────────────────────────────────────────┐
│                 Reset Process                         │
└──────────────────────────────────────────────────────┘

   [Start]
      │
      ▼
   dbl reset
      │
      ├─ Confirm action
      └─ Backup recommended
      │
      ▼
   Drop Database
      │
      └─ DROP DATABASE myapp
      │
      ▼
   Create Database
      │
      └─ CREATE DATABASE myapp
      │
      ▼
   Replay Layers (in order)
      │
      ├─ L001 ─> Execute ─> ✓
      ├─ L002 ─> Execute ─> ✓
      ├─ L003 ─> Execute ─> ✓
      └─ ...
      │
      ▼
   Update State
      │
      └─ Mark layers as applied
      │
      ▼
   [Complete]
```

### Branch Workflow

```
┌──────────────────────────────────────────────────────┐
│                 Branch Lifecycle                      │
└──────────────────────────────────────────────────────┘

   main: L001 ─ L002 ─ L003
                   │
                   │ dbl branch feature-auth
                   │ dbl checkout feature-auth
                   │
                   ├─ feature-auth: L003 (base)
                   │                  │
                   │                  │ dbl commit
                   │                  │
                   │                  ├─ L004 (new)
                   │                  │
                   │                  │ dbl commit
                   │                  │
                   │                  └─ L005 (new)
                   │
                   │ main continues:
                   │
                   └─ L006 (different change)
                   
   Result:
   main:         L001 ─ L002 ─ L003 ─ L006
   feature-auth: L001 ─ L002 ─ L003 ─ L004 ─ L005
```

## Data Flow

### Diff Operation

```
┌──────────┐
│ Sandbox  │
│ Database │
└────┬─────┘
     │
     │ Read schema
     ▼
┌─────────────┐
│   Schema    │
│  Introspection│
│   (Sandbox)  │
└────┬────────┘
     │
     ├─────────────────┐
     │                 │
     ▼                 ▼
┌─────────┐       ┌─────────┐
│  Main   │       │ Sandbox │
│ Schema  │       │ Schema  │
└────┬────┘       └────┬────┘
     │                 │
     └────────┬────────┘
              │
              ▼
         ┌─────────┐
         │  Diff   │
         │ Engine  │
         └────┬────┘
              │
              ▼
         ┌─────────┐
         │  SQL    │
         │ Output  │
         └─────────┘
```

### Commit Operation

```
   [Changes in Sandbox]
         │
         ▼
   Run Diff ────> Generate SQL
         │
         ▼
   Create Layer File
         │
         ├─ Filename: L{N}_{message}.sql
         ├─ Content: SQL statements
         └─ Metadata: timestamp, branch
         │
         ▼
   Update State
         │
         └─ Increment layer counter
```

## Engine Abstraction

### Engine Interface

```python
class DatabaseEngine:
    """Base class for database engines"""
    
    def connect(self):
        """Establish database connection"""
        pass
    
    def get_schema(self, database):
        """Get current schema"""
        pass
    
    def diff_schemas(self, source, target):
        """Compare two schemas"""
        pass
    
    def apply_sql(self, sql):
        """Execute SQL"""
        pass
    
    def create_database(self, name):
        """Create new database"""
        pass
    
    def drop_database(self, name):
        """Drop database"""
        pass
```

### Engine Implementations

```python
PostgresEngine(DatabaseEngine):
    """PostgreSQL-specific implementation"""
    
    def get_schema(self, database):
        # Query pg_catalog
        # Extract tables, columns, indexes...
        return schema

MySQLEngine(DatabaseEngine):
    """MySQL-specific implementation"""
    
    def get_schema(self, database):
        # Query information_schema
        # Extract tables, columns, indexes...
        return schema
```

## State Management

### State Transitions

```
[Initialized] ──────────> [Clean]
                              │
                              │ sandbox start
                              ▼
                          [Sandbox Active]
                              │
                              ├─ apply ──> [Clean]
                              └─ rollback ─> [Clean]
```

### State File Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "database": {"type": "string"},
    "engine": {"enum": ["postgres", "mysql"]},
    "branch": {"type": "string"},
    "last_layer": {"type": "string", "pattern": "^L[0-9]{3}$"},
    "active_sandbox": {"type": ["string", "null"]},
    "created_at": {"type": "string", "format": "date-time"}
  },
  "required": ["database", "engine", "branch"]
}
```

## Performance Considerations

### Schema Introspection

- **Cached**: Schema queries are cached per command
- **Indexed**: Uses database catalog indexes
- **Selective**: Only queries needed metadata

### Layer Application

- **Transactional**: Each layer in a transaction
- **Sequential**: Applied in order
- **Idempotent**: Can be replayed safely

### Diff Generation

- **Optimized**: Only compares changed objects
- **Parallel**: Can diff multiple tables simultaneously
- **Minimal**: Generates minimal SQL

## Security Model

### Permissions Required

```sql
-- PostgreSQL
GRANT CONNECT ON DATABASE myapp TO dbuser;
GRANT CREATE ON DATABASE myapp TO dbuser;
GRANT ALL ON ALL TABLES IN SCHEMA public TO dbuser;

-- MySQL
GRANT ALL PRIVILEGES ON myapp.* TO 'dbuser'@'localhost';
GRANT CREATE ON *.* TO 'dbuser'@'localhost';
```

### Credential Management

- Never stores passwords in files
- Uses environment variables
- Supports external secret managers

## Extensibility

### Plugin System (Future)

```python
# Custom hook example
@dbl.hook('before_commit')
def validate_naming(layer):
    """Ensure tables follow naming convention"""
    for table in layer.tables:
        if not table.name.islower():
            raise ValueError(f"Table {table.name} must be lowercase")

@dbl.hook('after_apply')
def notify_team(layer):
    """Send Slack notification"""
    slack.send(f"Layer {layer.id} applied to production")
```

## See Also

- [Database Engines](engines.md) - Engine-specific details
- [Best Practices](../guide/best-practices.md) - Usage patterns
- [Configuration](../guide/configuration.md) - Config options
