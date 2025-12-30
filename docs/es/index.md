# DBL - Database Layering

![Versión](https://img.shields.io/badge/versi%C3%B3n-0.0.1--alpha-blue) ![Estado](https://img.shields.io/badge/estado-experimental-orange) ![Python](https://img.shields.io/badge/python-3.8+-green) ![Licencia](https://img.shields.io/badge/licencia-Apache%202.0-blue)

**Control de versiones tipo Git para bases de datos**

---

## ¿Qué es DBL?

DBL (Database Layering) es un **sistema de control de versiones para bases de datos**, similar a Git pero diseñado específicamente para la evolución del esquema de bases de datos.

### Capacidades Clave

- **🌿 Ramifica tu esquema** - Trabaja en múltiples features en paralelo
- **🔒 Pruebas en sandbox** - Experimenta sin afectar tu base de datos
- **📦 Capas de cambios** - Control de versiones para todas tus migraciones SQL
- **✅ Migraciones validadas** - Controles integrados para cambios seguros
- **🔄 Reconstrucciones reproducibles** - Reconstrucción determinista de BD

---

## Inicio Rápido

```bash
# 1. Inicializa proyecto
dbl init

# 2. Crea sandbox de desarrollo
dbl sandbox start

# 3. Realiza tus cambios
# Usa tu cliente de BD favorito para modificar el esquema

# 4. Guarda tus cambios
dbl commit -m "Agregar tabla user_preferences"

# 5. Aplica a la base de datos principal
dbl sandbox apply
```

---

## Características Principales

### Experimentación Segura con Sandboxes

Trabaja en un **sandbox** aislado - una copia temporal de tu base de datos donde puedes probar cambios sin riesgo alguno a producción o desarrollo.

### Historial Completo de Capas

Cada cambio se guarda como una **capa** numerada (como commits de Git), creando un historial completo y auditable de la evolución de tu base de datos. Ver el historial en cualquier momento con `dbl log`.

### Ramificación tipo Git

Crea **ramas** para diferentes features:

```bash
dbl branch create feature/authentication
dbl checkout feature/authentication
# ... realiza tus cambios ...
dbl checkout main
dbl merge feature/authentication
```

### Bases de Datos Soportadas

- ✅ **PostgreSQL** 11+
- ✅ **MySQL** 5.7+
- 🔄 **SQLite** (planeado)

---

## Instalación

Instala DBL con pip:

```bash
pip install dbl
```

O clona desde GitHub para desarrollo:

```bash
git clone https://github.com/alann-estrada-KSH/dbl-sandbox.git
cd dbl-sandbox
pip install -e .
```

---

## Aprende Más

### Comienza Aquí

¿Nuevo en DBL? Comienza aquí:

- [Guía de Instalación](getting-started/installation.md) - Instrucciones de setup detalladas
- [Tutorial Rápido](getting-started/quick-start.md) - Tus primeros cambios en 5 minutos
- [Primera Migración](getting-started/first-migration.md) - Ejemplo completo paso a paso

### Referencia

¿Necesitas ayuda con un comando específico?

- [Todos los Comandos](commands/index.md) - Referencia completa de comandos
- [Gestión de Sandbox](commands/sandbox/start.md) - Trabaja con sandboxes
- [Guía de Ramas](commands/branching/index.md) - Gestión de ramas

### Análisis Profundos

Aprende arquitectura y patrones:

- [Visión General de Arquitectura](architecture/overview.md) - Cómo funciona DBL
- [Bases de Datos Soportadas](architecture/engines.md) - PostgreSQL, MySQL, más
- [Mejores Prácticas](guide/best-practices.md) - Consejos para equipos y proyectos
- [Configuración](guide/configuration.md) - Opciones de setup avanzado

### Ayuda y Recursos

- [FAQ](reference/faq.md) - 40+ preguntas frecuentes respondidas
- [Solución de Problemas](reference/troubleshooting.md) - Resuelve problemas comunes
- [Changelog](changelog.md) - Historial de versiones y cambios

---

## Flujos de Trabajo Comunes

### Agregando una Nueva Feature

```bash
# Crea rama de feature
dbl branch create feature/payments

# Cambia a rama de feature
dbl checkout feature/payments

# Crea sandbox
dbl sandbox start

# Realiza cambios de esquema usando tu cliente de BD
# ... CREATE TABLE payments ...
# ... CREATE INDEX idx_payments ...

# Revisa cambios
dbl diff

# Guarda cambios
dbl commit -m "Agregar tabla de pagos con índices"

# Aplica a la BD de la rama de feature
dbl sandbox apply

# Vuelve a main
dbl checkout main

# Fusiona cambios
dbl merge feature/payments
```

### Testeando Migraciones

```bash
# Prueba en un ambiente limpio
dbl sandbox start

# Reconstruye BD desde todas las capas
dbl reset

# Ejecuta tus tests de aplicación
./run-tests.sh

# Verifica que el esquema coincida
dbl validate

# Despliega cuando esté listo
dbl sandbox apply
```

---

## ¿Por Qué DBL?

### A Diferencia de Scripts SQL Raw

- ✅ Versionado con Git
- ✅ Sin ordenamiento manual de migraciones
- ✅ Pruebas seguras en sandbox
- ✅ Auditoría completa

### A Diferencia de Migraciones de ORM (Alembic, Django)

- ✅ Agnóstico de BD (PostgreSQL, MySQL, SQLite)
- ✅ SQL puro - sin dependencia de framework
- ✅ Portable entre proyectos
- ✅ Funciona con cualquier lenguaje de programación

### A Diferencia de Herramientas de Migración (Flyway, Liquibase)

- ✅ Ramificación tipo Git para trabajo paralelo
- ✅ Sandbox para pruebas seguras
- ✅ Configuración YAML simple
- ✅ Fácil de aprender y usar

---

## Contribuir

¡Bienvenidas las contribuciones! Aquí hay formas de ayudar:

- 🐛 [Reportar bugs](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)
- 💡 [Sugerir features](https://github.com/alann-estrada-KSH/dbl-sandbox/discussions)
- 📚 [Mejorar documentación](https://github.com/alann-estrada-KSH/dbl-sandbox)
- 💻 [Enviar código](https://github.com/alann-estrada-KSH/dbl-sandbox/pulls)

---

## Licencia

DBL está licenciado bajo **Apache 2.0**. Ver [LICENSE](../LICENSE) para detalles.

---

## Soporte

- 🐙 **GitHub**: [alann-estrada-KSH/dbl-sandbox](https://github.com/alann-estrada-KSH/dbl-sandbox)
- 📝 **Issues**: [Reporta un bug](https://github.com/alann-estrada-KSH/dbl-sandbox/issues)
- 💬 **Discussions**: [Haz una pregunta](https://github.com/alann-estrada-KSH/dbl-sandbox/discussions)

---

Hecho con ❤️ por [Alan Estrada](https://github.com/alann-estrada-KSH)
