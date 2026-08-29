"""
Servicio de negocio para el Motor de Postulaciones y Subastas.
"""

from typing import List, Optional, Set
from uuid import UUID

from dao.contrato_dao import ContratoDAO
from dao.postulacion_dao import PostulacionDAO
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from domain.modelos import ContratoModelo
from domain.postulacion import EstadoPostulacion, PostulacionCrear, PostulacionModelo

ESTADOS_CARGA_DISPONIBLES: Set[EstadoContrato] = {
    EstadoContrato.PUBLICADO,
    EstadoContrato.EN_SUBASTA,
    EstadoContrato.EN_POSTULACION,
}

ESTADOS_NO_POSTULABLES: Set[EstadoContrato] = {
    EstadoContrato.ADJUDICADO,
    EstadoContrato.FINALIZADO,
    EstadoContrato.CANCELADO,
}


class ServicioSubasta:
    """Orquesta la exploracion de cargas, envio de ofertas y adjudicacion de subastas."""

    def __init__(self, contrato_dao: ContratoDAO, postulacion_dao: PostulacionDAO) -> None:
        self.contrato_dao = contrato_dao
        self.postulacion_dao = postulacion_dao

    def explorar_cargas(
        self,
        region: Optional[str] = None,
        tipo_carroceria: Optional[str] = None,
        distancia_max_km: Optional[float] = None,
    ) -> List[ContratoModelo]:
        """
        Retorna las cargas disponibles para postulacion aplicando filtros opcionales.
        """
        todos = self.contrato_dao.obtener_todos()
        cargas = [c for c in todos if c.estado in ESTADOS_CARGA_DISPONIBLES]

        if region and region.strip():
            filtro_region = region.strip().lower()
            cargas = [
                c for c in cargas
                if filtro_region in c.origen.lower() or filtro_region in c.destino.lower()
            ]

        if tipo_carroceria and tipo_carroceria.strip():
            filtro_carroceria = tipo_carroceria.strip().lower()
            cargas = [
                c for c in cargas
                if filtro_carroceria in c.tipo_carga.value.lower()
            ]

        if distancia_max_km is not None and distancia_max_km > 0:
            cargas = [
                c for c in cargas
                if (c.peso_total * 0.1) <= distancia_max_km
            ]

        return cargas

    def postular_a_carga(
        self,
        datos_postulacion: PostulacionCrear,
        onboarding_aprobado: bool = True,
    ) -> PostulacionModelo:
        """
        Registra la postulacion de un transportista para una carga activa tras validar las reglas de negocio.
        """
        if not onboarding_aprobado:
            raise ValueError("El transportista debe tener su onboarding en estado 'APROBADO' para postular")

        contrato = self.contrato_dao.obtener_por_id(datos_postulacion.carga_id)
        if not contrato:
            raise ValueError(f"La carga/contrato con ID {datos_postulacion.carga_id} no existe")

        if contrato.estado in ESTADOS_NO_POSTULABLES:
            raise ValueError(
                f"La carga se encuentra en estado '{contrato.estado.value}' y no acepta nuevas postulaciones"
            )

        nueva_postulacion = PostulacionModelo(**datos_postulacion.model_dump())
        self.postulacion_dao.guardar(nueva_postulacion)

        # Transicion automatica a EN_POSTULACION si la carga estaba en PUBLICADO o EN_SUBASTA
        if contrato.estado in (EstadoContrato.PUBLICADO, EstadoContrato.EN_SUBASTA):
            contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
                contrato_data=contrato,
                nuevo_estado=EstadoContrato.EN_POSTULACION,
            )
            self.contrato_dao.actualizar(contrato.id, contrato_actualizado)

        return nueva_postulacion

    def adjudicar_subasta(
        self,
        carga_id: UUID,
        postulacion_id: UUID,
    ) -> PostulacionModelo:
        """
        Adjudica una subasta: selecciona la oferta ganadora, rechaza las demas y adjudica el contrato.
        """
        contrato = self.contrato_dao.obtener_por_id(carga_id)
        if not contrato:
            raise ValueError(f"La carga/contrato con ID {carga_id} no fue encontrada")

        if contrato.estado in ESTADOS_NO_POSTULABLES:
            raise ValueError(f"El contrato ya fue adjudicado, finalizado o cancelado (Estado: {contrato.estado.value})")

        postulacion = self.postulacion_dao.obtener_por_id(postulacion_id)
        if not postulacion or postulacion.carga_id != carga_id:
            raise ValueError(f"La postulacion con ID {postulacion_id} no pertenece al contrato indicado")

        # 1. Marcar postulacion como SELECCIONADA
        postulacion.estado = EstadoPostulacion.SELECCIONADA
        self.postulacion_dao.actualizar(postulacion.id, postulacion)

        # 2. Rechazar postulaciones competidoras
        self.postulacion_dao.rechazar_postulaciones(carga_id, postulacion.id)

        # 3. Transicionar contrato a ADJUDICADO y asignar transportista
        contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
            contrato_data=contrato,
            nuevo_estado=EstadoContrato.ADJUDICADO,
            id_transportista=postulacion.transportista_id,
        )
        self.contrato_dao.actualizar(contrato.id, contrato_actualizado)

        return postulacion

    def listar_postulaciones_carga(self, carga_id: UUID) -> List[PostulacionModelo]:
        """Retorna todas las postulaciones asociadas a una carga."""
        return self.postulacion_dao.obtener_por_contrato(carga_id)


# Alias para retrocompatibilidad
SubastaService = ServicioSubasta
