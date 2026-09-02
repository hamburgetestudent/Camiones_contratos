from fastapi import APIRouter
from domain.modelos_usuario import UsuarioCrear, UsuarioModelo
from services.usuario_service import UsuarioService

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/registro", response_model=UsuarioModelo, summary="Registrar un nuevo usuario")
def registrar_usuario(usuario: UsuarioCrear):
    return UsuarioService.registrar_usuario(usuario)

