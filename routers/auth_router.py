from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


# Router para las funciones de autenticación
router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


# Datos que recibe el formulario de login
class LoginRequest(BaseModel):
    usuario: str
    password: str


# Usuarios de prueba
USUARIOS = {
    "admin": "1234",
    "transportista": "1234",
    "empresa": "1234"
}


# Endpoint para iniciar sesión
@router.post("/login")
async def login(datos: LoginRequest):

    # Verificar que el usuario exista
    if datos.usuario not in USUARIOS:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    # Verificar la contraseña
    if USUARIOS[datos.usuario] != datos.password:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    # Login correcto
    return {
        "mensaje": "Inicio de sesión exitoso",
        "usuario": datos.usuario
    }