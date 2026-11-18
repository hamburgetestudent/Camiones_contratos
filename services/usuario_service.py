
import hashlib
from uuid import UUID

from fastapi import HTTPException, status

from dao.usuario_dao import UsuarioDAOSQLite
from domain.modelos_login import CredencialesLogin, RespuestaLogin
from domain.modelos_onboarding import CrearPerfilDadorDTO
from domain.modelos_usuario import UsuarioCrear, UsuarioModelo
from services.onboarding_service import onboarding_service_instancia

# TD-01: Se importa el componente reutilizable de autenticación.
# Antes, este servicio construía directamente el token y la respuesta.
# Ahora delega esa responsabilidad para evitar lógica duplicada.
from services.respuesta_login import construir_respuesta_login


# Instancia global respaldada por SQLite para acceder a los datos de los usuarios
usuario_dao = UsuarioDAOSQLite()


def hash_password(password: str) -> str:
    # Hasheo simple para demostración (idealmente usar passlib y bcrypt)
    return hashlib.sha256(password.encode()).hexdigest()


class UsuarioService:
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
        # persistirlos en SQLite.
        if usuario_data.documentos:
            for doc in usuario_data.documentos:
                onboarding_service_instancia.cargar_documento(
                    user_id=usuario_guardado.id,
                    tipo=doc.tipo,
                    archivo=doc.archivo,
                )

        # Si adjuntó perfil tributario de dador de carga en el registro, persistirlo en SQLite
        # persistirlo en SQLite.
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
        """Autentica las credenciales y devuelve una respuesta OAuth2 Bearer.

        TD-01:
        Se conserva la validación original de credenciales.
        La construcción del token y de la respuesta se delega
        al componente compartido services/respuesta_login.py.
        """
        email = credenciales.usuario.strip() if credenciales.usuario else ""
        password = credenciales.obtener_password_texto()

        # Validaciones originales: no modificar códigos ni mensajes.
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

        # Se conserva el mecanismo original de autenticación.
        usuario = UsuarioService.autenticar_usuario(email, password)

        # ============================================================
        # TD-01: REFACTORIZACIÓN DE AUTENTICACIÓN
        #
        # ANTES:
        # Este servicio convertía el rol y el estado del usuario,
        # preparaba los datos del token y construía RespuestaLogin.
        #
        # AHORA:
        # Se utiliza un componente compartido que concentra
        # esas operaciones para evitar su duplicación.
        #
        # IMPORTANTE:
        # Se mantiene usuario.email como identificador de respuesta
        # para conservar el comportamiento del endpoint /auth/login.
        #
        # Clases aplicadas:
        # 3.1 - Refactorización sistemática.
        # 3.2 - Eliminación de duplicación y deuda técnica.
        # 3.3 - Reutilización de componentes.
        # ============================================================
        return construir_respuesta_login(
            datos_usuario=usuario,
            usuario_solicitado=usuario.email,
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
