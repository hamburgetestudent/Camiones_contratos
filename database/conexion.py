"""Conexion, esquema y datos semilla de la base de datos SQLite.

Es la unica puerta de entrada a la base de datos: los servicios abren su
conexion con ``obtener_conexion`` (o ``transaccion_exclusiva`` cuando deben
leer y escribir de forma atomica) y ejecutan su SQL directamente, sin capas
intermedias de acceso a datos.

El esquema vive en ``schema.sql`` y se aplica de forma perezosa e idempotente
la primera vez que se abre una conexion hacia una ruta dada, de modo que
importar un servicio nunca crea ni modifica archivos de base de datos.
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

# Ruta por defecto del archivo SQLite dentro de Camiones_contratos/
DEFAULT_DB_PATH = Path(
    os.getenv(
        "SQLITE_DB_PATH",
        str(Path(__file__).resolve().parent.parent / "camiones.db"),
    )
)

RUTA_ESQUEMA = Path(__file__).resolve().parent / "schema.sql"
SCHEMA_SQL = RUTA_ESQUEMA.read_text(encoding="utf-8")

# Rutas cuyo esquema ya fue aplicado en este proceso (evita repetir el script).
_esquemas_aplicados: set[str] = set()
_candado_esquema = threading.Lock()


def _hash_password(password: str) -> str:
    """Genera el hash SHA-256 de una contraseña en texto plano."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _asegurar_esquema(ruta: str) -> None:
    """Aplica ``schema.sql`` sobre ``ruta`` si aun no se hizo (o si el archivo desaparecio).

    Usa una conexion propia y de vida corta: asi las pragmas del script no se
    filtran a las conexiones de trabajo.
    """
    if ruta in _esquemas_aplicados and os.path.exists(ruta):
        return
    with _candado_esquema:
        conn = sqlite3.connect(ruta)
        try:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
        finally:
            conn.close()
        _esquemas_aplicados.add(ruta)


@contextmanager
def obtener_conexion(db_path: str | Path | None = None) -> Iterator[sqlite3.Connection]:
    """Entrega una conexion SQLite con ``Row`` factory dentro de una transaccion.

    Al salir del bloque sin error se hace ``commit``; ante una excepcion se hace
    ``rollback`` y se propaga. La ruta por defecto se resuelve en cada llamada,
    por lo que puede redirigirse (p. ej. en pruebas) cambiando ``DEFAULT_DB_PATH``.
    """
    ruta = str(db_path or DEFAULT_DB_PATH)
    _asegurar_esquema(ruta)
    conn = sqlite3.connect(ruta, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def transaccion_exclusiva(
    db_path: str | Path | None = None,
) -> Iterator[sqlite3.Connection]:
    """Como ``obtener_conexion`` pero reservando el derecho de escritura desde el inicio.

    Usar cuando una operacion lee un estado, valida y luego escribe: ningun otro
    escritor puede intercalarse entre la lectura y la escritura, y todos los
    cambios se confirman juntos o ninguno (postcondicion "todo o nada").
    """
    with obtener_conexion(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        yield conn


def inicializar_bd(
    db_path: str | Path | None = None, cargar_semilla: bool = True
) -> None:
    """Crea las tablas si no existen y, opcionalmente, carga los datos semilla iniciales."""
    _asegurar_esquema(str(db_path or DEFAULT_DB_PATH))

    if cargar_semilla:
        cargar_datos_semilla(db_path)


def cargar_datos_semilla(db_path: str | Path | None = None) -> None:
    """Inserta usuarios, correos, perfiles tributarios y documentos iniciales si no existen."""
    ahora_iso = datetime.now(UTC).isoformat()

    usuarios_iniciales = [
        (
            "00000000-0000-0000-0000-000000000001",
            "Administrador Backoffice",
            "admin@camiones.cl",
            "ADMIN_BACKOFFICE",
            _hash_password("admin123"),
            "APROBADO",
            ahora_iso,
        ),
        (
            "00000000-0000-0000-0000-000000000002",
            "Logística del Sur S.A.",
            "contacto@logisticasur.cl",
            "DADOR_CARGA",
            _hash_password("dador123"),
            "APROBADO",
            ahora_iso,
        ),
        (
            "00000000-0000-0000-0000-000000000003",
            "Agroexportadora Valle Central",
            "operaciones@vallecentral.cl",
            "DADOR_CARGA",
            _hash_password("valle123"),
            "EN_REVISION",
            ahora_iso,
        ),
        (
            "00000000-0000-0000-0000-000000000004",
            "Juan Pérez (Transportes Ruta Norte)",
            "juan.perez@rutanorte.cl",
            "TRANSPORTISTA",
            _hash_password("camion123"),
            "APROBADO",
            ahora_iso,
        ),
        (
            "00000000-0000-0000-0000-000000000005",
            "Carlos Soto",
            "carlos.soto@transporte.cl",
            "TRANSPORTISTA",
            _hash_password("carlos123"),
            "EN_REVISION",
            ahora_iso,
        ),
    ]

    dadores_iniciales = [
        (
            "10000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000002",
            "76123456-7",
            "Logística del Sur S.A.",
            "Av. Libertador Bernardo O'Higgins 1234, Santiago",
            "facturacion@logisticasur.cl",
            "APROBADO",
        ),
        (
            "10000000-0000-0000-0000-000000000002",
            "00000000-0000-0000-0000-000000000003",
            "77987654-K",
            "Agroexportadora Valle Central Ltda.",
            "Ruta 5 Sur Km 85, Rancagua",
            "pagos@vallecentral.cl",
            "PENDIENTE",
        ),
    ]

    documentos_iniciales = [
        # Transportista 1 (Juan Pérez) -> Todos los 5 documentos APROBADOS
        (
            "20000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000004",
            "LICENCIA_CONDUCIR",
            "docs/juan_perez/licencia_a5.pdf",
            "APROBADO",
            ahora_iso,
        ),
        (
            "20000000-0000-0000-0000-000000000002",
            "00000000-0000-0000-0000-000000000004",
            "PADRON_VEHICULO",
            "docs/juan_perez/padron_camion.pdf",
            "APROBADO",
            ahora_iso,
        ),
        (
            "20000000-0000-0000-0000-000000000003",
            "00000000-0000-0000-0000-000000000004",
            "REVISION_TECNICA",
            "docs/juan_perez/revision_tecnica.pdf",
            "APROBADO",
            ahora_iso,
        ),
        (
            "20000000-0000-0000-0000-000000000004",
            "00000000-0000-0000-0000-000000000004",
            "SEGURO_CARGA",
            "docs/juan_perez/seguro_carga.pdf",
            "APROBADO",
            ahora_iso,
        ),
        (
            "20000000-0000-0000-0000-000000000005",
            "00000000-0000-0000-0000-000000000004",
            "ANTECEDENTES",
            "docs/juan_perez/certificado_antecedentes.pdf",
            "APROBADO",
            ahora_iso,
        ),
        # Transportista 2 (Carlos Soto) -> Documentos en revisión (PENDIENTE)
        (
            "20000000-0000-0000-0000-000000000006",
            "00000000-0000-0000-0000-000000000005",
            "LICENCIA_CONDUCIR",
            "docs/carlos_soto/licencia.pdf",
            "PENDIENTE",
            ahora_iso,
        ),
        (
            "20000000-0000-0000-0000-000000000007",
            "00000000-0000-0000-0000-000000000005",
            "PADRON_VEHICULO",
            "docs/carlos_soto/padron.jpg",
            "PENDIENTE",
            ahora_iso,
        ),
    ]

    with obtener_conexion(db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) AS total FROM usuarios")
        total = cursor.fetchone()["total"]
        if total > 0:
            return

        conn.executemany(
            """
            INSERT OR IGNORE INTO usuarios (id, nombre, email, rol, password_hash, estado, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            usuarios_iniciales,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO dadores_carga (
                id, user_id, rut_id_empresa, razon_social, direccion, correo_facturacion, estado_validacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            dadores_iniciales,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO documentos_transportista (
                id, user_id, tipo, archivo, estado, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            documentos_iniciales,
        )
