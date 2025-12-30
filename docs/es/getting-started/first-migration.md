# Tu Primera Migración

Tutorial completo para crear tu primera migración real con DBL.

## Escenario

Estás construyendo un blog y necesitas:
- Sistema de usuarios
- Publicaciones (posts)
- Comentarios
- Sistema de etiquetas (tags)

Crearemos estas tablas paso a paso usando DBL.

## Prerrequisitos

- DBL instalado e inicializado
- Base de datos creada
- Archivo `dbl.yaml` configurado

Si aún no lo has hecho:

```bash
# Crear base de datos
createdb blog_db

# Configurar DBL
cat > dbl.yaml << EOF
database:
  name: blog_db
  engine: postgres
  host: localhost
  port: 5432
  user: tu_usuario
  password: \${DB_PASSWORD}
EOF

# Inicializar
dbl init
```

## Paso 1: Crear Tabla de Usuarios

### Iniciar Sandbox

```bash
dbl sandbox start
```

**Salida:**
```
✓ Sandbox created: blog_db_sandbox
```

### Diseñar la Tabla

Crea `migrations/001_users.sql` (solo para referencia):

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    bio TEXT,
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsquedas comunes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Ejecutar en Sandbox

```bash
psql -d blog_db_sandbox -f migrations/001_users.sql
```

### Verificar Cambios

```bash
dbl diff
```

**Salida:**
```sql
+ CREATE TABLE users (
+     id SERIAL PRIMARY KEY,
+     username VARCHAR(50) UNIQUE NOT NULL,
+     email VARCHAR(255) UNIQUE NOT NULL,
+     ...
+ );

+ CREATE INDEX idx_users_username ON users(username);
+ CREATE INDEX idx_users_email ON users(email);
+ CREATE INDEX idx_users_active ON users(is_active);

+ CREATE FUNCTION update_updated_at_column() ...
+ CREATE TRIGGER update_users_updated_at ...

Summary:
  + 1 table added (users)
  + 5 indexes added
  + 1 function added
  + 1 trigger added
```

### Guardar como Capa

```bash
dbl commit -m "Add users table with authentication fields"
```

**Salida:**
```
✓ Layer L001 created: Add users table with authentication fields
✓ Layer saved to .dbl/layers/L001_add_users_table.sql
```

## Paso 2: Crear Tabla de Posts

### Diseñar Posts

```sql
-- migrations/002_posts.sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    featured_image VARCHAR(500),
    status VARCHAR(20) DEFAULT 'draft' 
        CHECK (status IN ('draft', 'published', 'archived')),
    published_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para rendimiento
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_slug ON posts(slug);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_published ON posts(published_at);

-- Trigger para updated_at
CREATE TRIGGER update_posts_updated_at 
    BEFORE UPDATE ON posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Aplicar en Sandbox

```bash
psql -d blog_db_sandbox -f migrations/002_posts.sql
```

### Ver y Guardar

```bash
dbl diff
dbl commit -m "Add posts table with status and publishing features"
```

## Paso 3: Crear Tabla de Comentarios

### Diseñar Comentarios

```sql
-- migrations/003_comments.sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_comments_post ON comments(post_id);
CREATE INDEX idx_comments_author ON comments(author_id);
CREATE INDEX idx_comments_parent ON comments(parent_id);
CREATE INDEX idx_comments_approved ON comments(is_approved);

-- Trigger
CREATE TRIGGER update_comments_updated_at 
    BEFORE UPDATE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Aplicar

```bash
psql -d blog_db_sandbox -f migrations/003_comments.sql
dbl commit -m "Add comments table with nested comment support"
```

## Paso 4: Sistema de Etiquetas

### Diseñar Tags y Relación

```sql
-- migrations/004_tags.sql

-- Tabla de etiquetas
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Relación muchos-a-muchos entre posts y tags
CREATE TABLE post_tags (
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, tag_id)
);

-- Índices
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_tags_slug ON tags(slug);
CREATE INDEX idx_post_tags_post ON post_tags(post_id);
CREATE INDEX idx_post_tags_tag ON post_tags(tag_id);
```

### Aplicar

```bash
psql -d blog_db_sandbox -f migrations/004_tags.sql
dbl commit -m "Add tags system with many-to-many relationship"
```

## Paso 5: Revisar Historial

```bash
dbl log
```

**Salida:**
```
* L004 - Add tags system with many-to-many relationship
  Date: 2024-12-30 11:05:22
  
* L003 - Add comments table with nested comment support
  Date: 2024-12-30 11:00:15
  
* L002 - Add posts table with status and publishing features
  Date: 2024-12-30 10:55:33
  
* L001 - Add users table with authentication fields
  Date: 2024-12-30 10:50:11
```

## Paso 6: Aplicar Todo a la Base Principal

```bash
dbl sandbox apply
```

**Salida:**
```
Applying sandbox changes to main database (blog_db)...
  → Executing L001
  → Executing L002
  → Executing L003
  → Executing L004
✓ All changes applied successfully

Summary:
  Database: blog_db
  Layers applied: 4
  Tables added: 6 (users, posts, comments, tags, post_tags)
  Indexes added: 15
  Functions added: 1
  Triggers added: 3
```

## Paso 7: Verificar el Resultado

```bash
psql -d blog_db -c "\dt"
```

**Salida:**
```
             List of relations
 Schema |    Name    | Type  |  Owner
--------+------------+-------+---------
 public | comments   | table | dbuser
 public | post_tags  | table | dbuser
 public | posts      | table | dbuser
 public | tags       | table | dbuser
 public | users      | table | dbuser
```

## Paso 8: Probar con Datos

### Insertar Datos de Prueba

```sql
-- Crear un usuario
INSERT INTO users (username, email, password_hash, first_name, last_name)
VALUES ('johndoe', 'john@example.com', 'hashed_password', 'John', 'Doe')
RETURNING id;

-- Crear un post (usa el ID del usuario)
INSERT INTO posts (author_id, title, slug, content, status, published_at)
VALUES (1, 'Mi Primer Post', 'mi-primer-post', 
        'Este es el contenido de mi primer post.', 
        'published', CURRENT_TIMESTAMP)
RETURNING id;

-- Crear tags
INSERT INTO tags (name, slug) VALUES 
    ('Tutorial', 'tutorial'),
    ('DBL', 'dbl'),
    ('PostgreSQL', 'postgresql');

-- Asociar tags al post
INSERT INTO post_tags (post_id, tag_id) VALUES (1, 1), (1, 2), (1, 3);

-- Agregar comentario
INSERT INTO comments (post_id, author_id, content, is_approved)
VALUES (1, 1, '¡Gran post!', true);
```

### Ejecutar

```bash
psql -d blog_db << EOF
-- Insertar todos los datos de prueba aquí
EOF
```

### Consultar Datos

```sql
-- Ver posts con autor y cantidad de comentarios
SELECT 
    p.title,
    u.username as author,
    COUNT(c.id) as comment_count,
    p.published_at
FROM posts p
JOIN users u ON p.author_id = u.id
LEFT JOIN comments c ON p.id = c.post_id
GROUP BY p.id, u.username
ORDER BY p.published_at DESC;
```

## Paso 9: Agregar Mejora (Nueva Capa)

Agreguemos una tabla de "me gusta" para posts:

```bash
# Nuevo sandbox
dbl sandbox start

# Crear likes table
psql -d blog_db_sandbox << EOF
CREATE TABLE post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);

CREATE INDEX idx_post_likes_post ON post_likes(post_id);
CREATE INDEX idx_post_likes_user ON post_likes(user_id);
EOF

# Ver cambios
dbl diff

# Commit
dbl commit -m "Add post likes functionality"

# Apply
dbl sandbox apply
```

## Paso 10: Verificar Integridad

```bash
dbl validate
```

**Salida:**
```
Validating DBL repository...

✓ Configuration (dbl.yaml)
✓ State file (.dbl/state.json)
✓ Layer files (5 layers)
✓ SQL syntax
✓ Database schema
✓ Foreign key relationships

All checks passed! Repository is healthy.
```

## Estructura Final

```
blog_db
├── users (usuarios)
├── posts (publicaciones)
│   └── author_id → users.id
├── comments (comentarios)
│   ├── post_id → posts.id
│   ├── author_id → users.id
│   └── parent_id → comments.id (comentarios anidados)
├── tags (etiquetas)
├── post_tags (relación posts-tags)
│   ├── post_id → posts.id
│   └── tag_id → tags.id
└── post_likes (me gusta)
    ├── post_id → posts.id
    └── user_id → users.id
```

## Reconstruir desde Cero

Puedes reconstruir toda la base de datos desde las capas:

```bash
# Reconstruir
dbl reset

# Verifica que todo se creó correctamente
psql -d blog_db -c "\dt"
```

**DBL reproduce todas las capas:**
```
Dropping database blog_db...
Creating database blog_db...
Replaying layers:
  → L001 ✓
  → L002 ✓
  → L003 ✓
  → L004 ✓
  → L005 ✓
  
✓ Reset complete
```

## Lecciones Aprendidas

### ✅ Buenas Prácticas Aplicadas

1. **Índices apropiados**: Creamos índices en claves foráneas y campos de búsqueda
2. **Constraints**: Usamos CHECK constraints para validar datos
3. **Cascadas**: ON DELETE CASCADE para mantener integridad referencial
4. **Triggers**: Actualización automática de timestamps
5. **Commits descriptivos**: Mensajes claros de cada capa

### 📝 Estructura de Capas

```
.dbl/layers/
├── L001_add_users_table.sql
├── L002_add_posts_table.sql
├── L003_add_comments_table.sql
├── L004_add_tags_system.sql
└── L005_add_post_likes.sql
```

### 🔄 Flujo de Trabajo

```
sandbox start → cambios → diff → commit → apply
     ↓           ↓         ↓       ↓        ↓
   seguro    experimenta  revisa guarda  aplica
```

## Trabajo en Equipo

Comparte con tu equipo:

```bash
# Guardar en Git
git add .dbl/ dbl.yaml
git commit -m "Initial blog database schema"
git push

# Tu equipo puede aplicar
git pull
dbl reset  # Recrea desde capas
```

## Próximos Pasos

Has completado tu primera migración real. Ahora:

1. [Aprende más comandos](../commands/index.md)
2. [Usa branches](../commands/branching/index.md) para desarrollo paralelo
3. [Mejores prácticas](../guide/best-practices.md) para proyectos grandes
4. [CI/CD](../guide/best-practices.md#cicd-integration) para automatización

## Ver También

- [Inicio Rápido](quick-start.md)
- [Comandos de Sandbox](../commands/sandbox/start.md)
- [Guía de Configuración](../guide/configuration.md)
- [Mejores Prácticas](../guide/best-practices.md)
