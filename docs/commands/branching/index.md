# Branching

Learn how to use branches in DBL to manage parallel development.

## Overview

DBL branches work like Git branches but for database schemas. They allow multiple developers to work on different features simultaneously without conflicts.

## Quick Reference

```bash
# Create branch
dbl branch feature-auth

# Switch branches
dbl checkout feature-auth

# List branches
dbl branch

# Merge branches (future)
dbl merge feature-auth
```

## Branch Concepts

### What is a Branch?

A branch is an independent line of development:

```
main:     L001 → L002 → L003 → L004
                    ↓
feature:           L003 → L005 → L006
```

- Each branch has its own layer sequence
- Branches share common history
- Changes in one branch don't affect others

### When to Branch

✅ **Use branches for:**
- New features
- Experimental changes
- Hotfixes
- Multiple parallel developments

❌ **Don't branch for:**
- Quick fixes (use sandbox instead)
- Single-person projects (maybe)
- Linear development

## Branch Workflow

### Basic Workflow

```bash
# 1. Create feature branch
$ dbl branch feature-comments
$ dbl checkout feature-comments

# 2. Make changes
$ dbl sandbox start
# ... make changes ...
$ dbl commit -m "Add comments table"

# 3. Continue working
$ dbl commit -m "Add comment indexes"

# 4. Switch back to main
$ dbl checkout main

# 5. Merge (manual for now)
# Copy layers from feature branch
```

### Team Workflow

```bash
# Developer 1: Works on auth
$ dbl branch feature-auth
$ dbl checkout feature-auth
# ... work on authentication ...

# Developer 2: Works on payments (parallel)
$ dbl branch feature-payments
$ dbl checkout feature-payments
# ... work on payments ...

# Both can work independently!
```

## Branch Operations

### Create Branch

```bash
# Create from current point
$ dbl branch feature-name

# Create and switch
$ dbl branch feature-name
$ dbl checkout feature-name
```

### Switch Branches

```bash
# Switch to existing branch
$ dbl checkout feature-auth

# Your database and layers change to that branch's state
```

### List Branches

```bash
$ dbl branch

  main
* feature-auth
  feature-payments
  
(* = current branch)
```

### Delete Branch

```bash
# Delete merged branch
$ dbl branch -d feature-auth

# Force delete
$ dbl branch -D feature-auth
```

## Examples

### Feature Development

```bash
# Start feature
$ dbl branch feature-notifications
$ dbl checkout feature-notifications

# Build feature
$ dbl sandbox start
$ psql -d myapp_sandbox << EOF
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    message TEXT,
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF

$ dbl commit -m "Add notifications table"

# Add more
$ psql -d myapp_sandbox << EOF
CREATE INDEX idx_notifications_user 
ON notifications(user_id);
EOF

$ dbl commit -m "Add notifications indexes"

# Feature complete
$ dbl log
* L006 - Add notifications indexes
* L005 - Add notifications table
* L004 - Add comments (from main)
```

### Parallel Features

```bash
# Feature 1: Authentication
$ dbl branch feature-auth
$ dbl checkout feature-auth
$ dbl sandbox start
# ... add auth tables ...
$ dbl commit -m "Add authentication"

# Switch to Feature 2: Profiles
$ dbl checkout main
$ dbl branch feature-profiles
$ dbl checkout feature-profiles
$ dbl sandbox start
# ... add profile tables ...
$ dbl commit -m "Add user profiles"

# Both features developed independently!
```

### Hotfix Workflow

```bash
# Critical bug in production
$ dbl checkout main

# Create hotfix branch
$ dbl branch hotfix-user-constraint
$ dbl checkout hotfix-user-constraint

# Fix issue
$ dbl sandbox start
$ psql -d myapp_sandbox -c "
ALTER TABLE users 
ADD CONSTRAINT unique_email UNIQUE(email);
"
$ dbl commit -m "hotfix: Add unique email constraint"
$ dbl sandbox apply

# Deploy immediately
$ dbl checkout main
# Merge hotfix (manual for now)
```

## Branch Strategy

### Gitflow-style

```
main (production)
  ├── develop (staging)
  │   ├── feature-auth
  │   ├── feature-payments
  │   └── feature-notifications
  └── hotfix-critical-bug
```

### Trunk-based

```
main (always deployable)
  ├── feature-short-lived-1
  └── feature-short-lived-2
```

### Feature Branches

```
main
  ├── feature/user-management
  ├── feature/reporting
  └── feature/api-v2
```

## Merging Branches

### Manual Merge (Current)

```bash
# From feature branch
$ dbl checkout feature-auth
$ dbl log --oneline
L008 Add OAuth
L007 Add 2FA
L006 Add sessions

# Copy layers to main
$ cp .dbl/layers/L007_* ../main-layers/
$ cp .dbl/layers/L008_* ../main-layers/

# Switch to main
$ dbl checkout main
$ mv ../main-layers/* .dbl/layers/
$ dbl reset  # Replay with new layers
```

### Auto-merge (Future)

```bash
# Planned feature
$ dbl checkout main
$ dbl merge feature-auth

Merging feature-auth into main...
  → L007 Add 2FA
  → L008 Add OAuth
✓ Merged successfully
```

## Conflicts

### Detecting Conflicts

```bash
# When branches modify same tables
$ dbl merge feature-auth
⚠ Conflict detected:
  Both branches modified table 'users'
  
  main: Added column 'last_login'
  feature-auth: Added column 'auth_token'
  
Resolve manually and commit.
```

### Resolving Conflicts

```bash
# 1. Review both changes
$ dbl diff main
$ dbl diff feature-auth

# 2. Manually create unified layer
$ nano .dbl/layers/L009_merge_auth.sql
-- Add both columns
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
ALTER TABLE users ADD COLUMN auth_token TEXT;

# 3. Commit merge
$ dbl commit -m "Merge: Add login tracking and auth"
```

## Best Practices

### Naming Branches

```bash
# Good names
feature-user-authentication
hotfix-email-validation
experiment-new-indexes

# Bad names
branch1
test
temp
```

### Branch Lifetime

- **Feature branches**: Days to weeks
- **Hotfix branches**: Hours to days
- **Experiment branches**: Delete after evaluation
- **Long-lived branches**: Avoid (causes conflicts)

### Keep Branches Updated

```bash
# Regularly sync with main
$ dbl checkout feature-auth
$ dbl merge main  # (future)

# Or manual rebase
$ dbl reset --from main
```

## Advanced Usage

### Branch Per Developer

```bash
# Alice
$ dbl branch alice/feature-auth
$ dbl checkout alice/feature-auth

# Bob
$ dbl branch bob/feature-payments
$ dbl checkout bob/feature-payments
```

### Release Branches

```bash
# Create release branch
$ dbl branch release-v1.5
$ dbl checkout release-v1.5

# Only critical fixes go here
$ dbl commit -m "Release: Version 1.5.0"
```

### Experiment Branches

```bash
# Try something risky
$ dbl branch experiment-new-schema
$ dbl checkout experiment-new-schema

# If it works, merge
# If not, delete
$ dbl branch -D experiment-new-schema
```

## State Management

### Branch State

Each branch tracks:
- Layer sequence
- Last applied layer
- Sandbox state
- Branch metadata

```bash
# View branch info
$ cat .dbl/branches/feature-auth.json
{
  "name": "feature-auth",
  "base": "main",
  "created": "2024-12-30T10:00:00Z",
  "layers": ["L001", "L002", "L007", "L008"]
}
```

### Switching Impact

When switching branches:
1. Database state may change
2. Active sandboxes are preserved
3. Uncommitted changes carry over (⚠️ be careful)

## See Also

- [dbl branch](branch.md) - Create and list branches
- [dbl checkout](checkout.md) - Switch branches
- [Best Practices](../../guide/best-practices.md) - Branching strategies
