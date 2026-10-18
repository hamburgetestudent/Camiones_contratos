-- Esquema SQLite para Gestión de Usuarios, Correos y Onboarding (KYC)
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

