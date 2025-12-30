# Introducción a DBL

**Database Layering** - Control de versiones para bases de datos.

## ¿Qué es DBL?

DBL es una herramienta que trata cambios de esquema en base de datos como código:

- Versionarlos con Git
- Trabajar en ramas
- Revisar cambios antes de aplicar
- Mantener historial completo

## Por Qué Usar DBL?

### Seguridad
Todos los cambios pasan por sandbox primero. Nunca afectas la base principal por accidente.

### Trazabilidad
Cada cambio tiene:
- Quién lo hizo
- Cuándo lo hizo
- Por qué (mensaje de commit)

### Reproducibilidad
Reproducir exactamente el esquema en cualquier momento:
```bash
dbl reset  # Reconstruir desde capas
```

### Colaboración
Múltiples developers trabajando en paralelo sin conflictos:
```bash
dbl branch create feature/auth
dbl branch create feature/payments
```

## Conceptos Principales

### Capas (Layers)
Cada cambio se guarda como una "capa" SQL:
```
L001: CREATE TABLE users
L002: CREATE TABLE posts
L003: ADD COLUMN email TO users
```

### Sandbox
Tu área privada de trabajo. Cambios se quedan aquí hasta que estés listo:
```bash
dbl sandbox start
# Trabajar libremente
dbl sandbox apply  # Cuando esté listo
```

### Commit
Guardar cambios como capa permanente:
```bash
dbl commit -m "Add email verification"
```

### Ramas
Trabajo independiente en features:
```bash
dbl branch create feature/auth
dbl checkout feature/auth
```

## Flujo Básico

```
1. Crear sandbox → Espacio seguro
2. Hacer cambios → SQL normal
3. dbl commit → Guardar como capa
4. dbl sandbox apply → Aplicar a base principal
5. git commit → Guardar en Git
6. git push → Compartir con equipo
```

## Próximos Pasos

- [Instalación](getting-started/installation.md)
- [Quick Start](getting-started/quick-start.md)
- [First Migration](getting-started/first-migration.md)
- [Todos los comandos](commands/index.md)

---

Comencemos: [Instalar DBL →](getting-started/installation.md)
