import hashlib
from uuid import UUID

from fastapi import HTTPException, status

from dao.usuario_dao import UsuarioDAOSQLite
from domain.modelos_login import CredencialesLogin, RespuestaLogin
from domain.modelos_onboarding import CrearPerfilDadorDTO
from domain.modelos_usuario import UsuarioCrear, UsuarioModelo
from services.onboarding_service import onboarding_service_instancia
from services.security import crear_token_acceso

# Instancia global respaldada por SQLite para acceder a los datos de los usuarios
usuario_dao = UsuarioDAOSQLite()


def hash_password(password: str) -> str:
    # Hasheo simple para demostración (idealmente usar passlib y bcrypt)
    return hashlib.sha256(password.encode()).hexdigest()


class UsuarioService:
    @staticmethod
    def registrar_usuario(usuario_data: UsuarioCrear) -> UsuarioModelo:
        # Validar si el email ya existe utilizando obt_por_email
        usuario_existente = usuario_dao.obt_por_email(usuario_data.email)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado",
            )

        # Crear modelo de base de datos
        nuevo_usuario = UsuarioModelo(
            nombre=usuario_data.nombre,
            email=usuario_data.email,
            rol=usuario_data.rol,
            password_hash=hash_password(usuario_data.password),
        )

        # Guardar en la base de datos SQLite
        usuario_guardado = usuario_dao.guardar(nuevo_usuario)

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
        return usuario_dao.obtener_todos()

    @staticmethod
    def obtener_usuario(usuario_id: UUID) -> UsuarioModelo:
        """Obtiene un usuario por su UUID desde SQLite."""
        usuario = usuario_dao.obtener_por_id(usuario_id)
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

        usuario = usuario_dao.obt_por_email(email.strip())
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
        rol_valor = (
            usuario.rol.value if hasattr(usuario.rol, "value") else str(usuario.rol)
        )
        estado_valor = (
            usuario.estado.value
            if hasattr(usuario.estado, "value")
            else str(usuario.estado)
        )

        access_token = crear_token_acceso(
            {
                "sub": str(usuario.id),
                "email": usuario.email,
                "rol": rol_valor,
            }
        )

        return RespuestaLogin(
            access_token=access_token,
            token_type="bearer",
            rol=rol_valor,
            mensaje="Inicio de sesión exitoso",
            usuario=usuario.email,
            id=str(usuario.id),
            nombre=usuario.nombre,
            email=usuario.email,
            estado=estado_valor,
        )


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
        return usuario_dao.obt_por_email(usuario)
