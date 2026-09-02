from fastapi import HTTPException, status
import hashlib
from domain.modelos_usuario import UsuarioCrear, UsuarioModelo
from dao.usuario_dao import UsuarioDAOMemoria

# Instancia global (en memoria) para acceder a los datos de los usuarios
usuario_dao = UsuarioDAOMemoria()

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
                detail="El email ya está registrado"
            )
        
        # Crear modelo de base de datos
        nuevo_usuario = UsuarioModelo(
            nombre=usuario_data.nombre,
            email=usuario_data.email,
            rol=usuario_data.rol,
            password_hash=hash_password(usuario_data.password)
        )
        
        # Guardar en la "base de datos"
        return usuario_dao.guardar(nuevo_usuario)
    
    @staticmethod
    def autenticar_usuario(email: str, password: str) -> UsuarioModelo:
        # Buscar al usuario por email
        usuario = usuario_dao.obt_por_email(email)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Credenciales inválidas"
            )
        
        # Verificar la contraseña
        if usuario.password_hash != hash_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Credenciales inválidas"
            )
            
        return usuario

