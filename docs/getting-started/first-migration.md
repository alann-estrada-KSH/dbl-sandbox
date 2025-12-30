# Your First Migration

Learn migration best practices by building a real-world example.

## Scenario

You're building a blog application and need to add:
1. A `posts` table
2. A `comments` table with foreign key
3. An index for performance

We'll use DBL's migration phases to do this safely.

---

## Migration Phases

DBL supports three optional phases:

| Phase | Purpose | Risk | When to Use |
|-------|---------|------|-------------|
| **expand** | Add things | ✅ Low | New tables, columns |
| **backfill** | Update data | ⚠️ Medium | Populate new columns |
| **contract** | Remove things | ❌ High | Drop columns, constraints |

!!! tip "Best Practice"
    Always add before you remove. Use expand → backfill → contract pattern.

---

## Step 1: Initialize

```bash
# Create project
mkdir blog-app
cd blog-app

# Initialize DBL
dbl init

# Configure database
nano dbl.yaml  # Add your DB credentials
```

---

## Step 2: Start Sandbox

```bash
dbl sandbox start
```

---

## Step 3: Create Posts Table (Expand Phase)

Connect to your sandbox database and run:

```sql
-- Create posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    author_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index for performance
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_status ON posts(status);
```

**Review changes:**
```bash
dbl diff
```

**Commit:**
```bash
dbl commit -m "Add posts table with indexes"
```

---

## Step 4: Add Comments Table (Expand Phase)

```sql
-- Create comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_content CHECK (length(content) > 0)
);

-- Performance indexes
CREATE INDEX idx_comments_post ON comments(post_id);
CREATE INDEX idx_comments_user ON comments(user_id);
```

**Commit:**
```bash
dbl commit -m "Add comments table with foreign keys"
```

---

## Step 5: Apply to Main Database

```bash
dbl sandbox apply
```

---

## Step 6: Add Sample Data (Optional)

For the backfill phase example:

```bash
dbl sandbox start
```

```sql
-- Add sample posts
INSERT INTO posts (title, content, author_id, status) VALUES
    ('Hello World', 'My first blog post!', 1, 'published'),
    ('DBL is Awesome', 'Learning database migrations...', 1, 'draft');

-- Add sample comments
INSERT INTO comments (post_id, user_id, content) VALUES
    (1, 2, 'Great first post!'),
    (1, 3, 'Welcome to blogging!');
```

**Commit with data:**
```bash
dbl commit -m "Add sample blog data" --with-data
```

!!! warning "Data Commits"
    Use `--with-data` flag to include INSERT/UPDATE statements. This is opt-in for safety.

```bash
dbl sandbox apply
```

---

## Step 7: View Your History

```bash
dbl log
```

**Output:**
```
* L003 - Add sample blog data
         2025-12-30 11:15:22
         Branch: master

* L002 - Add comments table with foreign keys
         2025-12-30 11:10:15
         Branch: master

* L001 - Add posts table with indexes
         2025-12-30 11:05:30
         Branch: master
```

---

## Advanced: Add a New Column

Let's add a `view_count` column to posts using the expand → backfill → contract pattern.

### Migration 1: Expand (Add Column)

```bash
dbl sandbox start
```

```sql
-- Add new column (nullable at first)
ALTER TABLE posts 
  ADD COLUMN view_count INTEGER;
```

```bash
dbl commit -m "expand: Add view_count column"
dbl sandbox apply
```

### Migration 2: Backfill (Populate Data)

```bash
dbl sandbox start
```

```sql
-- Set default values for existing rows
UPDATE posts 
SET view_count = 0 
WHERE view_count IS NULL;
```

```bash
dbl commit -m "backfill: Initialize view_count to 0" --with-data
dbl sandbox apply
```

### Migration 3: Contract (Add Constraint)

```bash
dbl sandbox start
```

```sql
-- Now make it NOT NULL and add default
ALTER TABLE posts 
  ALTER COLUMN view_count SET NOT NULL,
  ALTER COLUMN view_count SET DEFAULT 0;
```

```bash
dbl commit -m "contract: Make view_count NOT NULL"
dbl sandbox apply
```

!!! success "Zero-Downtime Pattern"
    This expand → backfill → contract pattern allows zero-downtime deployments in production.

---

## Validate Your Migrations

DBL can validate migration patterns:

```bash
dbl validate
```

**Output:**
```
Validating layers on branch: master

✓ L001: expand phase (safe)
✓ L002: expand phase (safe)
✓ L003: backfill phase (data changes)
✓ L004: expand phase (safe)
✓ L005: backfill phase (data changes)
⚠ L006: contract phase (review required)

Validation complete: 0 errors, 1 warning
```

---

## Branching Example

Work on a feature in isolation:

```bash
# Create feature branch
dbl branch add-tags

# Switch to it
dbl checkout add-tags

# Work on feature
dbl sandbox start
```

```sql
-- Add tags support
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);
```

```bash
dbl commit -m "Add tags support"
dbl sandbox apply

# Merge back to master
dbl checkout master
dbl merge add-tags
```

---

## Reset and Rebuild

Rebuild your entire database from layers:

```bash
# This drops and recreates your database
dbl reset

# All layers are replayed in order
# Your database is now identical to layer history
```

!!! danger "Destructive Operation"
    `dbl reset` DROPS your database. Always have backups!

---

## Configuration Tips

Add to your `dbl.yaml`:

```yaml
# Track specific tables
track_tables:
  - posts
  - comments
  - tags
  - post_tags

# Ignore system tables
ignore_tables:
  - sessions
  - cache

# Validation rules
validate:
  strict: false               # Warnings don't fail
  detect_type_changes: true   # Warn on type changes
  require_comments: true      # Require comments for contract phase
```

---

## Testing Your Migrations

Create a test workflow:

```bash
#!/bin/bash
# test-migrations.sh

# Start fresh
dbl reset

# Verify schema
psql -d your_database -c "\dt"  # List tables

# Run app tests
pytest tests/

# If tests pass, migration is good!
```

---

## CI/CD Integration

Use DBL in your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Check for DB changes
  run: |
    dbl diff
    if [ $? -eq 1 ]; then
      echo "Schema changes detected but not committed!"
      exit 1
    fi
```

---

## Real-World Example: E-commerce

Complete example with orders, products, and inventory:

```bash
# Branch for feature
dbl branch order-system
dbl checkout order-system
dbl sandbox start
```

```sql
-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- Indexes
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
```

```bash
dbl commit -m "Add order management system"
dbl sandbox apply
```

---

## Best Practices Summary

1. ✅ **Always use sandboxes** - Never modify main DB directly
2. ✅ **Review with diff** - Always check what will be committed
3. ✅ **Descriptive messages** - Write clear commit messages
4. ✅ **Use branches** - Isolate feature work
5. ✅ **Follow phases** - expand → backfill → contract
6. ✅ **Add indexes** - Include performance considerations
7. ✅ **Validate regularly** - Run `dbl validate` often
8. ✅ **Test migrations** - Use `dbl reset` to test replaying

---

## Common Pitfalls

❌ **Don't:**
- Skip sandbox for "quick changes"
- Commit without reviewing diff
- Use contract phase without expand first
- Forget indexes on foreign keys
- Mix schema and data in one commit

✅ **Do:**
- Always work in sandbox
- Review every diff carefully
- Add things before removing
- Index appropriately
- Separate schema and data commits

---

## Next Steps

- 📖 [Best Practices Guide](../guide/best-practices.md)
- 🎯 [Migration Patterns](../guide/patterns.md)
- ⚙️ [Configuration Reference](../guide/configuration.md)
- 🌿 [Branching Strategies](../commands/branching/branch.md)

---

## Need Help?

- [Troubleshooting Guide](../guide/troubleshooting.md)
- [FAQ](../reference/faq.md)
- [GitHub Issues](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)
