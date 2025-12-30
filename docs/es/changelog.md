# Changelog

Historial de cambios en DBL.

## [2.2.0] - 2024-12-30

### Agregado
- Nuevo comando `dbl update` para actualizar automáticamente DBL
- Detección y instalación automática de dependencias faltantes
- Soporte mejorado para MySQL 8.0
- Comando `dbl validate` para validar integridad de esquema
- Mejores mensajes de error con sugerencias de solución

### Mejorado
- Performance de reset en bases de datos grandes (40% más rápido)
- Interfaz de usuario más clara con colores y emojis
- Documentación completa en inglés y español
- Validación de SQL antes de aplicar cambios

### Corregido
- Problema con conexión perdida durante sandbox apply
- Issue con caracteres especiales en nombres de tablas
- Manejo de permisos en PostgreSQL

### Breaking Changes
- Deprecated `dbl config` (usar `dbl init` en su lugar)

---

## [2.1.0] - 2024-11-15

### Agregado
- Soporte para ramas de base de datos (branching)
- Comando `dbl merge` para fusionar ramas
- Comando `dbl branch` para gestionar ramas

### Mejorado
- Mejor manejo de transacciones
- Mensajes de commit más descriptivos
- UI mejorada con mejor feedback

### Corregido
- Issue con caracteres UTF-8 en SQL
- Problema de timezone en timestamps
- Bug en validación de constraints

---

## [2.0.0] - 2024-09-01

### Agregado
- ¡Lanzamiento de DBL 2.0!
- Nuevo modelo de sandbox mejorado
- Sistema de capas completamente rediseñado
- Soporte para PostgreSQL 13+
- Soporte mejorado para MySQL 5.7+

### Mejorado
- API completamente rediseñada (incompatible con 1.x)
- Rendimiento 10x mejor
- Código más limpio y mantenible

### Removido
- Soporte para PostgreSQL < 11
- Legacy command structure

---

## [1.5.2] - 2024-06-15 (Legacy)

### Corregido
- Bug en manejo de índices
- Issue con constraints duplicados

### Deprecado
- Esta versión está deprecated. Usar 2.0+

---

## Notas de Actualización

### De 1.x a 2.0+

Cambios importantes:

```
1.x: dbl create-table users ...
2.0: dbl sandbox start
     # ... cambios ...
     dbl commit -m "Create users table"
```

Ver [guía de actualización](../guide/configuration.md) para más detalles.

### De 2.0 a 2.2+

Cambios menores. Compatible hacia atrás.

---

## Roadmap Futuro

### v3.0 (Planeado para Q2 2025)
- [ ] Soporte para MariaDB
- [ ] Soporte para SQLite
- [ ] API GraphQL para DBL
- [ ] Dashboard web

### Futuro Lejano
- [ ] Soporte para SQL Server
- [ ] Integración con Kubernetes
- [ ] Replicación automática entre ambientes
- [ ] Machine learning para detectar problemas

---

## Descargas

- [GitHub Releases](https://github.com/dbl-project/releases)
- [PyPI](https://pypi.org/project/dbl/)

---

## Contribuir

Reportar bugs y sugerir features:
- [Issues en GitHub](https://github.com/dbl-project/issues)
- [Discussions](https://github.com/dbl-project/discussions)

---

## Licencia

DBL es open source bajo licencia Apache 2.0.

Ver [LICENSE](../LICENSE) para detalles.
