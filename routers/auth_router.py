from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from domain.modelos_usuario import UsuarioCrear, UsuarioModelo
from services.usuario_service import UsuarioService

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/registro", response_model=UsuarioModelo, summary="Registrar un nuevo usuario")
def registrar_usuario(usuario: UsuarioCrear):
    return UsuarioService.registrar_usuario(usuario)

@router.post("/login", summary="Autenticación de usuario")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm recibe 'username' (que usaremos como email) y 'password'
    usuario = UsuarioService.autenticar_usuario(form_data.username, form_data.password)
    
    # En una app real aquí se generaría un token JWT
    return {
        "access_token": usuario.email, 
        "token_type": "bearer", 
        "rol": usuario.rol
    }

