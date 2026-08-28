"""
Servicio de Negocio para el Motor de Postulaciones y Subastas.
"""

from typing import List, Optional
from uuid import UUID

from dao.base_dao import BD_DAO
from dao.postulacion_dao import PostulacionDAOInMemory
from domain.modelos import ContratoModelo
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from domain.postulacion import PostulacionCrear, PostulacionModelo, EstadoPostulacion


class SubastaService:
    """Orquesta la exploración de cargas, envío de ofertas y adjudicación de subastas."""

    def __init__(self, contrato_dao: BD_DAO[ContratoModelo, UUID], postulacion_dao: PostulacionDAOInMemory):
        self.contrato_dao = contrato_dao
        self.postulacion_dao = postulacion_dao

    def explorar_cargas(
        self,
        region: Optional[str] = None,
        tipo_carroceria: Optional[str] = None,
        distancia_max_km: Optional[float] = None,
    ) -> List[ContratoModelo]:
        """
        Retorna las cargas disponibles (en estado PUBLICADO, EN_SUBASTA o EN_POSTULACION)
        filtradas opcionalmente por región, tipo de carga/carrocería y distancia máxima simulada.
        """
        todos = self.contrato_dao.get_all()
        estados_disponibles = {
            EstadoContrato.PUBLICADO,
            EstadoContrato.EN_SUBASTA,
            EstadoContrato.EN_POSTULACION,
        }

        cargas_filtradas = [c for c in todos if c.estado in estados_disponibles]

        if region:
            region_lower = region.strip().lower()
            cargas_filtradas = [
                c for c in cargas_filtradas
                if region_lower in c.origen.lower() or region_lower in c.destino.lower()
            ]

        if tipo_carroceria:
            carroceria_lower = tipo_carroceria.strip().lower()
            cargas_filtradas = [
                c for c in cargas_filtradas
                if carroceria_lower in c.tipo_carga.value.lower()
            ]

        if distancia_max_km is not None and distancia_max_km > 0:
            # Simulación de cálculo de distancia aproximada
            cargas_filtradas = [
                c for c in cargas_filtradas
                if (c.peso_total * 0.1) <= distancia_max_km
            ]

        return cargas_filtradas

    def postular_a_carga(
        self,
        datos_postulacion: PostulacionCrear,
        onboarding_aprobado: bool = True,
    ) -> PostulacionModelo:
        """
        Permite a un transportista enviar una postulación para una carga activa.
        Validaciones:
        - Onboarding del transportista en estado APROBADO.
        - Tarifa mínima de $5.000 CLP.
        - Carga existente y no finalizada / asignada.
        """
        if not onboarding_aprobado:
            raise ValueError("El transportista debe tener su onboarding en estado 'APROBADO' para postular")

        contrato = self.contrato_dao.get_id(datos_postulacion.carga_id)
        if not contrato:
            raise ValueError(f"La carga/contrato con ID {datos_postulacion.carga_id} no existe")

        if contrato.estado in (EstadoContrato.ADJUDICADO, EstadoContrato.FINALIZADO, EstadoContrato.CANCELADO):
            raise ValueError(
                f"La carga se encuentra en estado '{contrato.estado.value}' y no acepta nuevas postulaciones"
            )

        nueva_postulacion = PostulacionModelo(**datos_postulacion.model_dump())
        self.postulacion_dao.save(nueva_postulacion)

        # Transición opcional del contrato a EN_POSTULACION si aún estaba en PUBLICADO o EN_SUBASTA
        if contrato.estado in (EstadoContrato.PUBLICADO, EstadoContrato.EN_SUBASTA):
            contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
                contrato_data=contrato,
                nuevo_estado=EstadoContrato.EN_POSTULACION,
            )
            self.contrato_dao.update(contrato.id, contrato_actualizado)

        return nueva_postulacion

    def adjudicar_subasta(
        self,
        carga_id: UUID,
        postulacion_id: UUID,
    ) -> PostulacionModelo:
        """
        El dador adjudica la oferta ganadora.
        - Pasa la postulación seleccionada a SELECCIONADA.
        - Rechaza las demás postulaciones de la carga.
        - Transiciona el contrato a ADJUDICADO asignando el transportista.
        """
        contrato = self.contrato_dao.get_id(carga_id)
        if not contrato:
            raise ValueError(f"La carga/contrato con ID {carga_id} no fue encontrada")

        if contrato.estado in (EstadoContrato.ADJUDICADO, EstadoContrato.FINALIZADO, EstadoContrato.CANCELADO):
            raise ValueError(f"El contrato ya fue adjudicado, finalizado o cancelado (Estado: {contrato.estado.value})")

        postulacion = self.postulacion_dao.get_id(postulacion_id)
        if not postulacion or postulacion.carga_id != carga_id:
            raise ValueError(f"La postulación con ID {postulacion_id} no pertenece al contrato indicado")

        # 1. Marcar postulación ganadora
        postulacion.estado = EstadoPostulacion.SELECCIONADA
        self.postulacion_dao.update(postulacion.id, postulacion)

        # 2. Rechazar el resto de postulaciones del mismo contrato
        self.postulacion_dao.rechazar_postulaciones(carga_id, postulacion.id)

        # 3. Transicionar contrato a ADJUDICADO y asignar transportista
        contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
            contrato_data=contrato,
            nuevo_estado=EstadoContrato.ADJUDICADO,
            id_transportista=postulacion.transportista_id,
        )
        self.contrato_dao.update(contrato.id, contrato_actualizado)

        return postulacion

    def listar_postulaciones_carga(self, carga_id: UUID) -> List[PostulacionModelo]:
        """Obtiene el listado de postulaciones enviadas para una carga."""
        return self.postulacion_dao.get_by_contrato(carga_id)
