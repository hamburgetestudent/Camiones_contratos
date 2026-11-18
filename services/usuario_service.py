import hashlib
import sqlite3
from uuid import UUID

from fastapi import HTTPException, status

from database.conexion import obtener_conexion, transaccion_exclusiva
from domain.modelos_login import CredencialesLogin, RespuestaLogin
from domain.modelos_onboarding import CrearPerfilDadorDTO
from domain.modelos_usuario import (
    EstadoUsuario,
    RolUsuario,
    UsuarioCrear,
    UsuarioModelo,
)
from services.onboarding_service import onboarding_service_instancia
from services.security import crear_token_acceso

# ---------------------------------------------------------------------------
# SQL: tabla ``usuarios`` (usa la base de datos por defecto de database.conexion)
# ---------------------------------------------------------------------------

_SELECT_USUARIO = "SELECT id, nombre, email, rol, password_hash, estado FROM usuarios"


def _fila_a_usuario(fila: sqlite3.Row) -> UsuarioModelo:
    """Convierte una fila de SQLite en una instancia de UsuarioModelo."""
    return UsuarioModelo(
        id=UUID(fila["id"]),
        nombre=fila["nombre"],
        email=fila["email"],
        rol=RolUsuario(fila["rol"]),
        password_hash=fila["password_hash"],
        estado=EstadoUsuario(fila["estado"]),
    )


def buscar_usuario_por_id(
    conn: sqlite3.Connection, usuario_id: UUID
) -> UsuarioModelo | None:
    """Obtiene un usuario por su UUID, o None si no existe."""
    fila = conn.execute(
        f"{_SELECT_USUARIO} WHERE id = ?", (str(usuario_id),)
    ).fetchone()
    return _fila_a_usuario(fila) if fila else None


def buscar_usuario_por_email(
    conn: sqlite3.Connection, email: str
) -> UsuarioModelo | None:
    """Busca un usuario por correo (insensible a mayusculas y espacios extremos)."""
    fila = conn.execute(
        f"{_SELECT_USUARIO} WHERE lower(trim(email)) = ?", (email.strip().lower(),)
    ).fetchone()
    return _fila_a_usuario(fila) if fila else None


def buscar_todos_los_usuarios(conn: sqlite3.Connection) -> list[UsuarioModelo]:
    """Retorna todos los usuarios en orden de creacion."""
    filas = conn.execute(
        f"{_SELECT_USUARIO} ORDER BY created_at ASC, rowid ASC"
    ).fetchall()
    return [_fila_a_usuario(fila) for fila in filas]


def guardar_usuario(conn: sqlite3.Connection, usuario: UsuarioModelo) -> UsuarioModelo:
    """Inserta el usuario o, si su ID ya existe, actualiza sus campos. El correo se guarda en minusculas."""
    conn.execute(
        """
        INSERT INTO usuarios (id, nombre, email, rol, password_hash, estado)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            nombre = excluded.nombre,
            email = excluded.email,
            rol = excluded.rol,
            password_hash = excluded.password_hash,
            estado = excluded.estado
        """,
        (
            str(usuario.id),
            usuario.nombre,
            usuario.email.strip().lower(),
            RolUsuario(usuario.rol).value,
            usuario.password_hash,
            EstadoUsuario(usuario.estado).value,
        ),
    )
    return usuario


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
        # Comprobar unicidad del email y guardar en una sola transaccion (evita
        # que dos registros simultaneos con el mismo email pasen la comprobacion).
        with transaccion_exclusiva() as conn:
            if buscar_usuario_por_email(conn, usuario_data.email):
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
            usuario_guardado = guardar_usuario(conn, nuevo_usuario)

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
        with obtener_conexion() as conn:
            return buscar_todos_los_usuarios(conn)

    @staticmethod
    def obtener_usuario(usuario_id: UUID) -> UsuarioModelo:
        """Obtiene un usuario por su UUID desde SQLite."""
        with obtener_conexion() as conn:
            usuario = buscar_usuario_por_id(conn, usuario_id)
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

        with obtener_conexion() as conn:
            usuario = buscar_usuario_por_email(conn, email.strip())
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
        with obtener_conexion() as conn:
            return buscar_usuario_por_email(conn, usuario)
