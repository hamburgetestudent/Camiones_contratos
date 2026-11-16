"""Base DRY para pruebas de Usuarios y Autenticación."""

from __future__ import annotations

from uuid import UUID, uuid4

from database.conexion import obtener_conexion
from domain.modelos_onboarding import (
    CargarDocumentoDTO,
    CrearPerfilDadorDTO,
    DatosFacturacion,
    TipoDocumento,
)
from domain.modelos_usuario import (
    EstadoUsuario,
    RolUsuario,
    UsuarioCrear,
    UsuarioModelo,
)
from services.onboarding_service import OnboardingService
from services.usuario_service import (
    buscar_usuario_por_id,
    guardar_usuario,
    hash_password,
)
from tests.base import BaseTestCase


class BaseTestUsuarios(BaseTestCase):
    """Clase base DRY para pruebas de usuarios y autenticación.

    Hereda de tests.base.BaseTestCase y provee aislamiento
    completo de usuarios sobre una base SQLite temporal (la ruta por defecto
    queda redirigida a ella, por lo que ``UsuarioService`` y el singleton de
    onboarding operan sobre la misma base aislada).
    """

    def setUp(self) -> None:
        super().setUp()
        self.db_path = self.preparar_bd_aislada()
        self.onboarding_service = OnboardingService(db_path=self.db_path)

        self.password_comun = "passwordSegura123"
        self.hash_comun = hash_password(self.password_comun)

        # Semilla transportista
        self.usuario_transportista = UsuarioModelo(
            id=uuid4(),
            nombre="Juan Chofer",
            email="juan.chofer@transporte.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password_hash=self.hash_comun,
            estado=EstadoUsuario.APROBADO,
        )
        self.guardar_usuario_bd(self.usuario_transportista)

        # Semilla dador de carga
        self.usuario_dador = UsuarioModelo(
            id=uuid4(),
            nombre="Marcela Gerente",
            email="marcela@empresa.cl",
            rol=RolUsuario.DADOR_CARGA,
            password_hash=self.hash_comun,
            estado=EstadoUsuario.APROBADO,
        )
        self.guardar_usuario_bd(self.usuario_dador)

        # Semilla admin
        self.usuario_admin = UsuarioModelo(
            id=uuid4(),
            nombre="Carlos Admin",
            email="admin@plataforma.cl",
            rol=RolUsuario.ADMIN_BACKOFFICE,
            password_hash=self.hash_comun,
            estado=EstadoUsuario.APROBADO,
        )
        self.guardar_usuario_bd(self.usuario_admin)

    def guardar_usuario_bd(self, usuario: UsuarioModelo) -> UsuarioModelo:
        """Persiste un usuario directamente en SQLite (datos semilla del test)."""
        with obtener_conexion(self.db_path) as conn:
            return guardar_usuario(conn, usuario)

    def leer_usuario_bd(self, usuario_id: UUID) -> UsuarioModelo | None:
        """Lee un usuario directamente de SQLite (verifica persistencia real)."""
        with obtener_conexion(self.db_path) as conn:
            return buscar_usuario_por_id(conn, usuario_id)

    def crear_dto_transportista_valido(
        self,
        email: str = "nuevo.chofer@transporte.cl",
        nombre: str = "Nuevo Conductor",
    ) -> UsuarioCrear:
        """Helper DRY para crear un payload válido de transportista con sus 5 documentos."""
        documentos = [
            CargarDocumentoDTO(
                tipo=TipoDocumento.LICENCIA_CONDUCIR, archivo="docs/lic.pdf"
            ),
            CargarDocumentoDTO(
                tipo=TipoDocumento.PADRON_VEHICULO, archivo="docs/pad.jpg"
            ),
            CargarDocumentoDTO(
                tipo=TipoDocumento.REVISION_TECNICA, archivo="docs/rev.jpeg"
            ),
            CargarDocumentoDTO(tipo=TipoDocumento.SEGURO_CARGA, archivo="docs/seg.png"),
            CargarDocumentoDTO(tipo=TipoDocumento.ANTECEDENTES, archivo="docs/ant.pdf"),
        ]
        return UsuarioCrear(
            nombre=nombre,
            email=email,
            rol=RolUsuario.TRANSPORTISTA,
            password=self.password_comun,
            documentos=documentos,
        )

    def crear_dto_dador_valido(
        self,
        email: str = "nuevo.dador@empresa.cl",
        nombre: str = "Nuevo Dador",
        rut: str = "76.123.456-0",
    ) -> UsuarioCrear:
        """Helper DRY para crear un payload válido de dador con su perfil tributario."""
        perfil = CrearPerfilDadorDTO(
            rut_id_empresa=rut,
            datos_facturacion=DatosFacturacion(
                razon_social="Distribuciones Central SpA",
                direccion="Av. Providencia 1234",
                correo_facturacion=email,
            ),
        )
        return UsuarioCrear(
            nombre=nombre,
            email=email,
            rol=RolUsuario.DADOR_CARGA,
            password=self.password_comun,
            perfil_tributario=perfil,
        )
