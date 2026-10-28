"""Gestión de conexión, esquema y datos semilla para la base de datos SQLite.

Provee almacenamiento relacional persistente para usuarios, correos, perfiles
tributarios de dadores de carga y documentos de onboarding de transportistas
utilizando el módulo estándar ``sqlite3`` de Python.
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
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

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    rol TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'EN_REVISION',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol);

CREATE TABLE IF NOT EXISTS dadores_carga (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    rut_id_empresa TEXT NOT NULL,
    razon_social TEXT NOT NULL,
    direccion TEXT NOT NULL,
    correo_facturacion TEXT NOT NULL,
    estado_validacion TEXT NOT NULL DEFAULT 'PENDIENTE',
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dadores_user_id ON dadores_carga(user_id);
CREATE INDEX IF NOT EXISTS idx_dadores_rut ON dadores_carga(rut_id_empresa);

CREATE TABLE IF NOT EXISTS documentos_transportista (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tipo TEXT NOT NULL,
    archivo TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'PENDIENTE',
    created_at TEXT NOT NULL,
     UNIQUE(user_id, tipo),
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_documentos_user_id ON documentos_transportista(user_id);
CREATE INDEX IF NOT EXISTS idx_documentos_estado ON documentos_transportista(estado);
"""


def _hash_password(password: str) -> str:
    """Genera el hash SHA-256 de una contraseña en texto plano."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@contextmanager
def obtener_conexion(db_path: str | Path | None = None) -> Iterator[sqlite3.Connection]:
    """Context manager que entrega una conexión SQLite configurada con Row factory."""
    ruta = str(db_path or DEFAULT_DB_PATH)
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


def inicializar_bd(
    db_path: str | Path | None = None, cargar_semilla: bool = True
) -> None:
    """Crea las tablas en SQLite si no existen e inserta datos de prueba iniciales si está vacía."""
    with obtener_conexion(db_path) as conn:
        conn.executescript(SCHEMA_SQL)

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
