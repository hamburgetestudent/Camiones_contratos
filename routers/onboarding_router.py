"""
Router HTTP para el flujo de Onboarding y Verificacion de Documentacion (KYC / Fleet Compliance).
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Header, HTTPException, status

from domain.modelos_onboarding import (
    DocumentoTransportista,
    CargarDocumentoDTO,
    ValidarDocumentoDTO,
    EstadoOnboardingTransportistaDTO,
    DadorCarga,
    CrearPerfilDadorDTO,
    ValidarPerfilDadorDTO,
)
from services.onboarding_service import onboarding_service_instancia

router = APIRouter(prefix="/onboarding", tags=["Onboarding & KYC"])


# =========================================
# Endpoints Transportista
# =========================================

@router.post(
    "/transportista/documentos",
    response_model=DocumentoTransportista,
    status_code=status.HTTP_201_CREATED,
    summary="Cargar documento de transportista",
)
def cargar_documento_transportista(
    payload: CargarDocumentoDTO,
    x_user_id: UUID = Header(..., alias="X-User-Id", description="UUID del transportista"),
):
    """Permite al transportista cargar o actualizar un documento para verificación."""
    return onboarding_service_instancia.cargar_documento(
        user_id=x_user_id,
        tipo=payload.tipo,
        archivo=payload.archivo,
    )


@router.get(
    "/transportista/documentos",
    response_model=List[DocumentoTransportista],
    summary="Listar documentos del transportista",
)
def listar_documentos_transportista(
    x_user_id: UUID = Header(..., alias="X-User-Id", description="UUID del transportista"),
):
    """Retorna la lista de documentos cargados por el transportista identificado en el header."""
    return onboarding_service_instancia.listar_documentos_transportista(user_id=x_user_id)


@router.get(
    "/transportista/estado",
    response_model=EstadoOnboardingTransportistaDTO,
    summary="Consultar estado global de onboarding del transportista",
)
def consultar_estado_transportista(
    x_user_id: UUID = Header(..., alias="X-User-Id", description="UUID del transportista"),
):
    """Calcula y retorna el estado global (APROBADO, PENDIENTE o RECHAZADO) del transportista."""
    return onboarding_service_instancia.obtener_estado_transportista(user_id=x_user_id)


# =========================================
# Endpoints Dador de Carga
# =========================================

@router.post(
    "/dador/perfil",
    response_model=DadorCarga,
    status_code=status.HTTP_200_OK,
    summary="Registrar o actualizar perfil tributario del dador de carga",
)
def registrar_perfil_dador(
    payload: CrearPerfilDadorDTO,
    x_user_id: UUID = Header(..., alias="X-User-Id", description="UUID del dador de carga"),
):
    """Registra los datos de facturación e ID de empresa del dador de carga."""
    return onboarding_service_instancia.registrar_o_actualizar_perfil_dador(
        user_id=x_user_id,
        rut_id_empresa=payload.rut_id_empresa,
        datos_facturacion=payload.datos_facturacion,
    )


@router.get(
    "/dador/perfil",
    response_model=DadorCarga,
    summary="Obtener perfil tributario del dador de carga",
)
def obtener_perfil_dador(
    x_user_id: UUID = Header(..., alias="X-User-Id", description="UUID del dador de carga"),
):
    """Obtiene los datos tributarios y el estado_validacion actual del dador de carga."""
    perfil = onboarding_service_instancia.obtener_perfil_dador(user_id=x_user_id)
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontro perfil de dador de carga para el usuario {x_user_id}",
        )
    return perfil


# =========================================
# Endpoints Backoffice / Admin
# =========================================

@router.get(
    "/admin/documentos",
    response_model=List[DocumentoTransportista],
    summary="Listar documentos de transportistas pendientes de revisión",
)
def listar_documentos_pendientes_admin():
    """Listado para administradores de todos los documentos pendientes de validación."""
    return onboarding_service_instancia.listar_documentos_pendientes_admin()


@router.patch(
    "/admin/documentos/{documento_id}/validar",
    response_model=DocumentoTransportista,
    summary="Aprobar o rechazar un documento de transportista",
)
def validar_documento_admin(documento_id: UUID, payload: ValidarDocumentoDTO):
    """Aprobación o rechazo administrativo de un documento individual."""
    try:
        return onboarding_service_instancia.validar_documento(
            documento_id=documento_id,
            nuevo_estado=payload.estado,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.get(
    "/admin/dadores",
    response_model=List[DadorCarga],
    summary="Listar dadores de carga pendientes de validación tributaria",
)
def listar_dadores_pendientes_admin():
    """Listado para administradores de todos los dadores pendientes de validación."""
    return onboarding_service_instancia.listar_dadores_pendientes_admin()


@router.patch(
    "/admin/dadores/{dador_id}/validar",
    response_model=DadorCarga,
    summary="Aprobar o rechazar perfil de dador de carga",
)
def validar_dador_admin(dador_id: UUID, payload: ValidarPerfilDadorDTO):
    """Aprobación o rechazo administrativo del perfil tributario de un dador de carga."""
    try:
        return onboarding_service_instancia.validar_dador(
            dador_id=dador_id,
            nuevo_estado=payload.estado_validacion,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

