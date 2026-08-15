from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4, UUID # Maneja los identificadores unicos
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# Clases de "modelos.py"
from modelos import (
    ContratoCrear,
    ContratoModelo,
    EstadoContrato,
    MaquinaEstadosContrato
)
"""
Apartados que maneja la api actualmente
- Contratos NOTE: Por mejorar
"""
app = FastAPI(
    title = "API - Contratos Camiones",
    version = "0.0.1",
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
    id_transportista: str | None = None # Opcional
    id_camion: str | None = None # Opcional

# ======================
# Endpoints (Rutas Api)
# ======================

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
    except ValueError as error:
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


# patch: esta parte se utiliza cuando se modifica parte del contrato
@app.patch(
    "/contratos/{contrato.id}/estado",
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

    # Parseo de ids / NOTE: Modificar despues
    id_transportista_uuid = UUID(payload.id_transportista) if payload.id_transportista else None
    id_camion_uuid = UUID(payload.id_camion) if payload.id_camion else None

    # 2. Transición controlada por maquina de estados
    try:
        contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
            contrato= contrato,
            nuevo_estado= payload.nuevo_estado,
            id_transportista= id_transportista_uuid,
            id_camion= id_camion_uuid,
        )

        # Guardar cambio
        db_contratos[contrato_id] = contrato_actualizado
        return contrato_actualizado
    except ValueError as error:
        # Transiciones invalidas / datos faltantes
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= str(error),
        )





# Esta parte es lo mismo que ejecutar el comando en la terminal 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host= "127.0.0.1", port = 8000)