-- Esquema SQLite del proyecto (fuente unica, cargada por database/conexion.py).
-- Todas las sentencias son idempotentes (IF NOT EXISTS): se pueden ejecutar
-- sobre una base nueva o sobre una existente sin perder datos.
--
-- Convenciones de almacenamiento:
--   * UUID            -> TEXT (formato canonico con guiones)
--   * Fechas y horas  -> TEXT en ISO 8601 (con zona horaria)
--   * Booleanos       -> INTEGER (0 / 1)
--   * Enumeraciones   -> TEXT con el valor del enum del dominio

PRAGMA foreign_keys = ON;

-- 1. Tabla de Usuarios y Credenciales
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

-- 2. Tabla de Perfiles Tributarios y Correos de Facturación (Dadores de Carga)
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

-- 3. Tabla de Documentos de Habilitación (Transportistas)
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

-- 4. Tabla de Contratos de Carga (ciclo de vida gestionado por MaquinaEstadosContrato)
CREATE TABLE IF NOT EXISTS contratos (
    id TEXT PRIMARY KEY,
    id_empresa_generadora TEXT NOT NULL,
    origen TEXT NOT NULL,
    destino TEXT NOT NULL,
    f_estimada_salida TEXT NOT NULL,
    f_estimada_llegada TEXT NOT NULL,
    f_cierre_postulaciones TEXT NOT NULL,
    input_camion_kg REAL NOT NULL,
    tipo_carga TEXT NOT NULL,
    peso_total REAL NOT NULL,
    volumen_m3 REAL,
    distancia_km REAL,
    requiere_termo INTEGER NOT NULL DEFAULT 0,
    numero_onu TEXT,
    req_embalaje TEXT,
    req_blindaje INTEGER NOT NULL DEFAULT 0,
    moneda TEXT NOT NULL DEFAULT 'CLP',
    monto_neto REAL NOT NULL,
    monto_iva REAL NOT NULL,
    monto_total REAL NOT NULL,
    estado TEXT NOT NULL DEFAULT 'BORRADOR',
    id_transportista TEXT,
    id_camion TEXT,
    fecha_publicacion TEXT
);

CREATE INDEX IF NOT EXISTS idx_contratos_estado ON contratos(estado);
CREATE INDEX IF NOT EXISTS idx_contratos_empresa ON contratos(id_empresa_generadora);

-- 5. Tabla de Postulaciones (ofertas de transportistas sobre una carga)
CREATE TABLE IF NOT EXISTS postulaciones (
    id TEXT PRIMARY KEY,
    carga_id TEXT NOT NULL,
    transportista_id TEXT NOT NULL,
    precio_oferta REAL NOT NULL,
    tiempo_entrega_horas REAL NOT NULL,
    comentario TEXT,
    estado TEXT NOT NULL DEFAULT 'POSTULADA',
    creado_en TEXT NOT NULL,
    FOREIGN KEY (carga_id) REFERENCES contratos(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_postulaciones_carga ON postulaciones(carga_id);
CREATE INDEX IF NOT EXISTS idx_postulaciones_transportista ON postulaciones(transportista_id);
