import hashlib
from uuid import UUID

from fastapi import HTTPException, status

from dao.usuario_dao import UsuarioDAO, UsuarioDAOSQLite
from domain.modelos_login import CredencialesLogin, RespuestaLogin
from domain.modelos_onboarding import CrearPerfilDadorDTO
from domain.modelos_usuario import (
    UsuarioCrear,
    UsuarioModelo,
)
from services.onboarding_service import onboarding_service_instancia
from services.respuesta_login import construir_respuesta_login


def hash_password(password: str) -> str:
    # Hasheo simple para demostración (idealmente usar passlib y bcrypt)
    return hashlib.sha256(password.encode()).hexdigest()


class UsuarioService:
    # Almacen persistente (base por defecto resuelta en cada llamada).
    # Sustituible por inyeccion: ``UsuarioService.dao = UsuarioDAOSQLite(ruta)``.
    dao: UsuarioDAO = UsuarioDAOSQLite()

    @staticmethod
    def registrar_usuario(usuario_data: UsuarioCrear) -> UsuarioModelo:
        """Registra un usuario nuevo y, si corresponde, sus datos de onboarding.

        Precondiciones:
            - ``usuario_data`` cumple las validaciones de ``UsuarioCrear`` (email valido,
              rol permitido, password de al menos 6 caracteres).
            - El email no esta registrado previamente.

        Postcondiciones:
            - El usuario queda persistido con ``password_hash`` (nunca la clave en claro).
            - Si se enviaron documentos o perfil tributario, quedan cargados en PENDIENTE.

        Raises:
            HTTPException: 400 si el email ya existe.
        """
        # Comprobar unicidad del email y guardar en una sola transaccion (evita
        # que dos registros simultaneos con el mismo email pasen la comprobacion).
        with UsuarioService.dao.transaccion() as conn:
            # El correo sigue vinculado a su titular tras una baja lógica.
            if UsuarioService.dao.existe_email(conn, usuario_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado",
                )

            nuevo_usuario = UsuarioModelo(
                nombre=usuario_data.nombre,
                email=usuario_data.email,
                rol=usuario_data.rol,
                password_hash=hash_password(usuario_data.password),
            )
            usuario_guardado = UsuarioService.dao.guardar(conn, nuevo_usuario)

        # Si adjuntó documentos de transportista en el registro, persistirlos en SQLite
        if usuario_data.documentos:
            for doc in usuario_data.documentos:
                onboarding_service_instancia.cargar_documento(
                    user_id=usuario_guardado.id,
                    tipo=doc.tipo,
                    archivo=doc.archivo,
                )

        # Si adjuntó perfil tributario de dador de carga en el registro, persistirlo en SQLite
        if isinstance(usuario_data.perfil_tributario, CrearPerfilDadorDTO):
            onboarding_service_instancia.registrar_o_actualizar_perfil_dador(
                user_id=usuario_guardado.id,
                rut_id_empresa=usuario_data.perfil_tributario.rut_id_empresa,
                datos_facturacion=usuario_data.perfil_tributario.datos_facturacion,
            )

        return usuario_guardado

    @staticmethod
    def listar_usuarios() -> list[UsuarioModelo]:
        """Lista todos los usuarios almacenados en SQLite."""
        with UsuarioService.dao.conexion() as conn:
            return UsuarioService.dao.obtener_todos(conn)

    @staticmethod
    def obtener_usuario(usuario_id: UUID) -> UsuarioModelo:
        """Obtiene un usuario por su UUID desde SQLite."""
        with UsuarioService.dao.conexion() as conn:
            usuario = UsuarioService.dao.obtener_por_id(conn, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        return usuario

    @staticmethod
    def autenticar_usuario(email: str, password: str) -> UsuarioModelo:
        """Verifica la existencia del usuario y la validez de su contrasena."""
        if not email or not email.strip() or not password or not password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correo electrónico y contraseña requeridos",
            )

        with UsuarioService.dao.conexion() as conn:
            usuario = UsuarioService.dao.obtener_por_email(conn, email.strip())
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        if usuario.password_hash != hash_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        return usuario

    @staticmethod
    def iniciar_sesion(credenciales: CredencialesLogin) -> RespuestaLogin:
        """Autentica las credenciales del usuario y emite credencial de acceso OAuth2 Bearer."""
        email = credenciales.usuario.strip() if credenciales.usuario else ""
        password = credenciales.obtener_password_texto()

        if not email and not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico y la contraseña son campos obligatorios.",
            )
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico es un campo obligatorio.",
            )
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña es un campo obligatorio.",
            )

        usuario = UsuarioService.autenticar_usuario(email, password)
        return construir_respuesta_login(usuario)


class ValidadorUsuario:
    """Adaptador que cumple con ValidadorCredenciales delegando la verificación a UsuarioService."""

    def validar(self, usuario: str, password: str) -> bool:
        try:
            UsuarioService.autenticar_usuario(usuario, password)
            return True
        except HTTPException:
            return False

    def obtener_datos_usuario(self, usuario: str) -> UsuarioModelo | None:
        """Obtiene los datos del usuario autenticado por su email."""
        with UsuarioService.dao.conexion() as conn:
            return UsuarioService.dao.obtener_por_email(conn, usuario)
