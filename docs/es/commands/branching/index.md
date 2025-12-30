# Ramas

Gestionar ramas de base de datos para desarrollo paralelo.

## Descripción

Las ramas permiten que múltiples desarrolladores trabajen en cambios independientes sin interferir entre sí. Cada rama tiene su propio historial de capas y puede fusionarse cuando está lista.

## Conceptos Clave

### Rama Principal (Main)

La rama `main` es tu fuente de verdad. Contiene todas las capas aprobadas y estables. Directamente conectada a tu base de datos de producción.

```bash
$ dbl branch
* main
  feature-auth
  feature-payments
```

### Ramas de Feature

Crea ramas para trabajar en features aisladamente:

```bash
# Crear rama
$ dbl branch create feature-comments
✓ Created branch: feature-comments

# Cambiar a rama
$ dbl checkout feature-comments
```

## Flujo de Trabajo

### Crear Feature

```bash
# 1. Crear rama desde main
$ dbl branch create feature-auth
✓ Branch feature-auth created

# 2. Cambiar a rama
$ dbl checkout feature-auth

# 3. Hacer cambios
$ dbl sandbox start
# ... crear tablas ...
$ dbl commit -m "Add authentication tables"
$ dbl sandbox apply

# 4. Fusionar cuando lista
$ dbl checkout main
$ dbl merge feature-auth
```

## Comandos Relacionados

- [`dbl branch`](../commands/branching/index.md) - Listar/crear ramas
- [`dbl checkout`](../commands/branching/index.md) - Cambiar rama
- [`dbl merge`](../commands/branching/index.md) - Fusionar ramas

## Mejores Prácticas

- **Rama por feature**: Una rama por feature aislada
- **Nombres descriptivos**: `feature-auth`, no `work`
- **Sincronizar con main**: Actualizar main regularmente
- **PR antes de fusionar**: Revisar cambios antes de merge

## Próximos Pasos

- [Crear rama](../commands/branching/index.md)
- [Revisar ramas](../commands/branching/index.md)
- [Fusionar cambios](../commands/branching/index.md)
