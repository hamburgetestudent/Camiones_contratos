# Pendientes para Producción en Vercel (Persistencia y Backend)

Este archivo documenta el apartado **3. Persistencia y Backend** del plan de despliegue en Vercel que queda pendiente de definir e implementar antes de pasar a producción real.

---

## 1. Base de Datos (`database/conexion.py` y `services/*.py`)

Actualmente, todo el backend utiliza `sqlite3` apuntando por defecto a `camiones.db` en la raíz del repositorio (`SQLITE_DB_PATH`). En Vercel Serverless Functions, el directorio del despliegue es de solo lectura (`/var/task`) y `/tmp` es efímero.

### Opciones pendientes de decisión:
* **Opción A — Producción con PostgreSQL (Recomendado):**
  * Configurar una base de datos PostgreSQL externa (Neon, Supabase o Vercel Postgres) mediante la variable de entorno `DATABASE_URL`.
  * Adaptar `database/conexion.py` (y las consultas SQL en `services/*.py` que usan placeholders `?` y `BEGIN IMMEDIATE` de SQLite) para soportar PostgreSQL con `psycopg2` o `sqlalchemy`, manteniendo SQLite para desarrollo local y pruebas.
* **Opción B — Modo Demo rápido en `/tmp`:**
  * Detectar `os.getenv("VERCEL")` en `database/conexion.py` para usar `/tmp/camiones.db`.
  * Garantizar que `cargar_datos_semilla()` se ejecute automáticamente si la tabla `usuarios` está vacía en la primera conexión (ya que `lifespan` en serverless no garantiza persistencia entre *cold starts*).
  * *Limitación:* Los datos se pierden cada vez que se recicla la instancia serverless y no se comparten entre instancias concurrentes.

---

## 2. Limpieza de Dependencias (`requirements.txt`)

* Eliminar entradas duplicadas (`coverage>=7.0.0`, `python-dotenv>=1.0.0`).
* Mover herramientas de desarrollo y testing (`ruff>=0.8.0`, `coverage>=7.0.0`) a un archivo `requirements-dev.txt` para reducir el tamaño del bundle Python en Vercel (límite de 250 MB descomprimido).

---

## 3. Variables de Entorno en Vercel

* Configurar `JWT_SECRET_KEY` en el panel de Vercel (actualmente `services/security.py` usa una clave por defecto de desarrollo).
* Restringir `allow_origins` en `main.py` al dominio final de Vercel en producción.
