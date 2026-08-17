from typing import Dict, List
from uuid import uuid4, UUID # Maneja los identificadores unicos
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ValidationError

# Clases de "modelos.py"
from modelos import (
    ContratoCrear,
    ContratoModelo,
    EstadoContrato,
    MaquinaEstadosContrato,
    ReglasNegocio
)
"""
Apartados que maneja la api actualmente
- Contratos NOTE: Por mejorar
"""
app = FastAPI(
    title = "API - Contratos Camiones",
    version = "0.0.3",
    description= "Backend centralizado, ciclo de vida de contratos"
)

# Esta parte del codigo puede ser remplazada por un motor de BD, pero no es necesario todavia, como menciono el profesor
db_contratos: dict[UUID, ContratoModelo] = {}

# =========================
# DTO (Data Transfer Object) para cambio de estado
# =========================

# Estos son los datos finales que maneja el frontend
class SolicitudCambioEstado(BaseModel):
    nuevo_estado: EstadoContrato # Obligatorio
    id_transportista: UUID | None = None # Opcional
    id_camion: UUID | None = None # Opcional

class ActualizarConfiguracionNegocio(BaseModel):
    iva_porcentaje: float | None = None
    tolerancia_max: float | None = None
    anticipacion_min_h: int | None = None

# ======================
# Endpoint de configuracion de negocio
# ======================

@app.get(
    "/configuracion",
    summary= "Obtener las reglas de negocio actuales",
    tags= ["Configuración"],
)
def get_configuracion():
    return {
        "iva_porcentaje": ReglasNegocio.IVA_PORCENTAJE,
        "tolerancia_max": ReglasNegocio.TOLERANCIA_MAX,
        "anticipacion_min_h": ReglasNegocio.ANTICIPACION_MIN_H,
    }

@app.patch(
        "/configuracion",
        summary="Modificar las reglas de negocio en ejecución",
        tags=["Configuración"],
)
def actualizar_configuracion(payload: ActualizarConfiguracionNegocio):
    if payload.iva_porcentaje is not None:
        if not (0 <= payload.iva_porcentaje <= 1):
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail= "El porcentaje del IVA debe estar entre 0 y 1"
            )
        ReglasNegocio.IVA_PORCENTAJE = payload.iva_porcentaje

    if payload.tolerancia_max is not None:
        if payload.tolerancia_max < 0:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail= "La tolerancia financiera no puede ser negativa",
            )
        ReglasNegocio.TOLERANCIA_MAX = payload.tolerancia_max

    if payload.anticipacion_min_h is not None:
        if payload.anticipacion_min_h < 0:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail = "La anticipación minima no puede ser negativa"
            )
        ReglasNegocio.ANTICIPACION_MIN_H = payload.anticipacion_min_h

    return get_configuracion()

# =======================
# Endpoints de contratos
# =======================

@app.post(
    "/contratos",
    response_model= ContratoModelo,
    status_code= status.HTTP_201_CREATED,
    summary= "Crear un nuevo contrato (Borrador)"
)
def crear_contrato(datos_contrato: ContratoCrear):
    """
    Se crea un contrato ("Con las validaciones logicas tambien")
    """

    try:
        # Se validan los campos
        nuevo_contrato = ContratoModelo(**datos_contrato.model_dump())

        # Guarda en la BD
        db_contratos[nuevo_contrato.id] = nuevo_contrato
        return nuevo_contrato
    except (ValueError, ValidationError) as error:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail = f"Error en validacion de contrato: {str(error)}"
        )

@app.get(
    "/contratos/{contrato_id}",
    response_model= ContratoModelo,
    summary= "Obtener un contrato por ID",
)
def obtener_contrato(contrato_id : UUID):
    """ Se recupera los detalles de un contrato existente """
    if contrato_id not in db_contratos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "El contrato no existe",
        )
    return db_contratos[contrato_id]

@app.get (
        "/contratos",
        response_model= List[ContratoModelo],
        summary= "Listar todos los contratos registrados"
)
def listar_contratos():
    # Retorna TODOS los contratos
    return list(db_contratos.values())

@app.patch(
    "/contratos/{contrato_id}/estado",
    response_model= ContratoModelo,
    summary= "Transicion de estado del contrato",
)
def cambiar_estado_contrato(contrato_id: UUID, payload: SolicitudCambioEstado):
    """
    Aplica la maquina de estados para mover el contrato de un estado a otro, especificamente en
    modelos.py en def nuevo_estado
    """

    # 1. Verificacion de existencia
    if contrato_id not in db_contratos:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "El contrato solicitado no existe"
        )

    contrato = db_contratos[contrato_id]

    # 2. Transición controlada por maquina de estados
    try:
        contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
            contrato= contrato,
            nuevo_estado= payload.nuevo_estado,
            id_transportista= payload.id_transportista,
            id_camion= payload.id_camion,
        )

        # Guardar cambio
        db_contratos[contrato_id] = contrato_actualizado
        return contrato_actualizado
    except (ValueError, ValidationError) as error:
        # Transiciones invalidas / datos faltantes
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= str(error),
        )

# Esta parte es lo mismo que ejecutar el comando en la terminal 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host= "127.0.0.1", port = 8000)