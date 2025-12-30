# Bienvenido a DBL

**Database Layering** - Control de versiones para tu base de datos.

## ¿Qué es DBL?

DBL te permite versionar cambios de esquema en base de datos como lo haces con Git:

```bash
# Cambiar tabla
dbl sandbox start
ALTER TABLE users ADD COLUMN email TEXT;

# Guardar cambios
dbl commit -m "Add email column"

# Aplicar a base de datos
dbl sandbox apply
```

## Características Clave

- ✅ **Sandbox seguro**: Experimentar sin riesgos
- ✅ **Control de versiones**: Historial de todos los cambios
- ✅ **Ramas**: Desarrollo paralelo de features
- ✅ **Multiplataforma**: PostgreSQL, MySQL
- ✅ **Simple**: SQL puro, sin complicaciones

## Comenzar

### 1. Instalar

```bash
pip install dbl
```

### 2. Inicializar Proyecto

```bash
dbl init
```

### 3. Hacer Cambios

```bash
dbl sandbox start
# ... cambios en BD ...
dbl commit -m "Mi primer cambio"
dbl sandbox apply
```

## Documentación

- [Instalación](getting-started/installation.md)
- [Quick Start](getting-started/quick-start.md)
- [Comandos](commands/index.md)
- [FAQ](reference/faq.md)

## Comparación Rápida

| Aspecto | DBL | SQL Scripts | Migraciones ORM |
|---------|-----|------------|-----------------|
| Lenguaje | SQL puro | SQL | Lenguaje específico |
| Versionado | ✅ Git | ❌ Manual | ✅ Limitado |
| Sandbox | ✅ Seguro | ❌ Riesgo | ⚠️ Parcial |
| Ramas | ✅ Soportado | ❌ No | ⚠️ Complejo |
| Agnóstico | ✅ Sí | ✅ Sí | ❌ No |

## Ejemplo de Flujo

```bash
# 1. Crear rama para feature
dbl branch create feature/payments

# 2. Cambiar a rama
dbl checkout feature/payments

# 3. Crear sandbox
dbl sandbox start

# 4. Hacer cambios
psql -d myapp_sandbox -c "CREATE TABLE payments (...);"

# 5. Ver cambios
dbl diff

# 6. Guardar cambios
dbl commit -m "Add payments table"

# 7. Aplicar a base
dbl sandbox apply

# 8. Fusionar a main
dbl checkout main
dbl merge feature/payments

# 9. Listo!
dbl log
```

## Soportado

- **PostgreSQL**: 11+
- **MySQL**: 5.7+
- **Python**: 3.7+

## Próximos Pasos

1. [Instalar DBL](getting-started/installation.md)
2. [Primer cambio](getting-started/first-migration.md)
3. [Ver todos los comandos](commands/index.md)
4. [Mejores prácticas](guide/best-practices.md)

## Comunidad

- [GitHub](https://github.com/dbl-project)
- [Issues](https://github.com/dbl-project/issues)
- [Discussions](https://github.com/dbl-project/discussions)

## Licencia

Apache 2.0

---

¿Preguntas? [Ver FAQ](reference/faq.md) o [Troubleshooting](reference/troubleshooting.md).
