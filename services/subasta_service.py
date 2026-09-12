"""Servicio de negocio para el Motor de Postulaciones y Subastas."""

from uuid import UUID

from dao.contrato_dao import ContratoDAO
from dao.postulacion_dao import PostulacionDAO
from domain.auditoria import AccionAuditoria, EntidadAuditable
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from domain.modelos import ContratoModelo
from domain.postulacion import EstadoPostulacion, PostulacionCrear, PostulacionModelo
from domain.reglas import ReglasNegocio
from services.auditoria_service import ServicioAuditoria

ESTADOS_CARGA_DISPONIBLES: set[EstadoContrato] = {
    EstadoContrato.PUBLICADO,
    EstadoContrato.EN_SUBASTA,
    EstadoContrato.EN_POSTULACION,
}

ESTADOS_NO_POSTULABLES: set[EstadoContrato] = {
    EstadoContrato.ADJUDICADO,
    EstadoContrato.FINALIZADO,
    EstadoContrato.CANCELADO,
}


def estimar_distancia_entre_puntos(origen: str, destino: str) -> float:
    """Calcula una distancia estimada en km entre origen y destino en ausencia de distancia explicita.

    Args:
        origen (str): Comuna o ciudad de salida del transporte.
        destino (str): Comuna o ciudad de llegada del transporte.

    Returns:
        float: Distancia estimada en kilometros (0.0 si origen y destino coinciden, o 150.0 km de media interurbana).
    """
    if origen.strip().lower() == destino.strip().lower():
        return 0.0
    return 150.0


class ServicioSubasta:
    """Orquesta la exploracion de cargas, envio de ofertas y adjudicacion de subastas."""

    def __init__(
        self,
        contrato_dao: ContratoDAO,
        postulacion_dao: PostulacionDAO,
        auditoria_service: ServicioAuditoria | None = None,
    ) -> None:
        """Inicializa el servicio inyectando los DAOs de contratos y postulaciones.

        Args:
            contrato_dao (ContratoDAO): Capa de acceso a datos para contratos de carga.
            postulacion_dao (PostulacionDAO): Capa de acceso a datos para ofertas/postulaciones.
        """
        self.contrato_dao = contrato_dao
        self.postulacion_dao = postulacion_dao
        self.auditoria_service = auditoria_service

    def explorar_cargas(
        self,
        region: str | None = None,
        tipo_carroceria: str | None = None,
        distancia_max_km: float | None = None,
    ) -> list[ContratoModelo]:
        """Retorna las cargas disponibles para postulacion aplicando filtros opcionales.

        Filtra contratos en estados PUBLICADO, EN_SUBASTA o EN_POSTULACION según
        los criterios de búsqueda proporcionados por el transportista.

        Args:
            region (Optional[str], optional): Texto para filtrar por origen o destino. Defaults to None.
            tipo_carroceria (Optional[str], optional): Tipo de carga o carroceria requerida. Defaults to None.
            distancia_max_km (Optional[float], optional): Distancia maxima de la ruta en kilometros. Defaults to None.

        Returns:
            List[ContratoModelo]: Lista de contratos que cumplen con todos los filtros activos.
        """
        todos = self.contrato_dao.obtener_todos()
        cargas = [c for c in todos if c.estado in ESTADOS_CARGA_DISPONIBLES]

        if region and region.strip():
            filtro_region = region.strip().lower()
            cargas = [c for c in cargas if filtro_region in c.origen.lower() or filtro_region in c.destino.lower()]

        if tipo_carroceria and tipo_carroceria.strip():
            filtro_carroceria = tipo_carroceria.strip().lower()
            cargas = [c for c in cargas if filtro_carroceria in c.tipo_carga.value.lower()]

        if distancia_max_km is not None and distancia_max_km > 0:

            def _resolver_distancia(contrato: ContratoModelo) -> float:
                if contrato.distancia_km is not None:
                    return contrato.distancia_km
                return estimar_distancia_entre_puntos(contrato.origen, contrato.destino)

            cargas = [c for c in cargas if _resolver_distancia(c) <= distancia_max_km]

        return cargas

    def postular_a_carga(
        self,
        datos_postulacion: PostulacionCrear,
        onboarding_aprobado: bool = True,
    ) -> PostulacionModelo:
        """Registra la postulacion de un transportista para una carga activa tras validar las reglas de negocio.

        Valida que el transportista cuente con onboarding aprobado, que la carga exista y que se
        encuentre en un estado que admita nuevas ofertas. Si la carga estaba en PUBLICADO o EN_SUBASTA,
        se transiciona automaticamente a EN_POSTULACION.

        Args:
            datos_postulacion (PostulacionCrear): Esquema con ID de carga, transportista, camion y tarifa ofertada.
            onboarding_aprobado (bool, optional): Estado de verificacion de antecedentes/flota. Defaults to True.

        Returns:
            PostulacionModelo: Entidad de postulacion persistida con estado PENDIENTE.

        Raises:
            ValueError: Si el onboarding no esta aprobado, si el contrato no existe o si no admite ofertas.
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
        if self.auditoria_service:
            self.auditoria_service.registrar_evento(
                transporte_id=contrato.id,
                entidad=EntidadAuditable.OFERTA,
                entidad_id=nueva_postulacion.id,
                accion=AccionAuditoria.OFERTA_CREADA,
                actor_id=nueva_postulacion.transportista_id,
                datos=nueva_postulacion.model_dump(mode="json"),
                bases_aplicadas=ReglasNegocio.obtener_configuracion(),
                informacion_utilizada={
                    "estado_contrato_al_postular": contrato.estado.value,
                    "onboarding_aprobado": onboarding_aprobado,
                },
            )

        # Transicion automatica a EN_POSTULACION si la carga estaba en PUBLICADO o EN_SUBASTA
        if contrato.estado in (EstadoContrato.PUBLICADO, EstadoContrato.EN_SUBASTA):
            estado_anterior = contrato.estado
            contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
                contrato_data=contrato,
                nuevo_estado=EstadoContrato.EN_POSTULACION,
            )
            self.contrato_dao.actualizar(contrato.id, contrato_actualizado)
            if self.auditoria_service:
                self.auditoria_service.registrar_evento(
                    transporte_id=contrato.id,
                    entidad=EntidadAuditable.CONTRATO,
                    entidad_id=contrato.id,
                    accion=AccionAuditoria.ESTADO_CONTRATO_CAMBIADO,
                    actor_id=nueva_postulacion.transportista_id,
                    datos=contrato_actualizado.model_dump(mode="json"),
                    bases_aplicadas=ReglasNegocio.obtener_configuracion(),
                    informacion_utilizada={
                        "estado_anterior": estado_anterior.value,
                        "estado_nuevo": EstadoContrato.EN_POSTULACION.value,
                        "motivo": "Primera oferta recibida",
                        "oferta_id": str(nueva_postulacion.id),
                    },
                )

        return nueva_postulacion

    def adjudicar_subasta(
        self,
        carga_id: UUID,
        postulacion_id: UUID,
        revisado_por: UUID | None = None,
    ) -> PostulacionModelo:
        """Adjudica una subasta: selecciona la oferta ganadora, rechaza las demas y adjudica el contrato.

        Cambia el estado de la postulacion a SELECCIONADA, rechaza atomica y formalmente las demas postulaciones
        competidoras del contrato, y transiciona el estado del contrato a ADJUDICADO asignando el transportista.

        Args:
            carga_id (UUID): Identificador unico del contrato/carga subastada.
            postulacion_id (UUID): Identificador unico de la oferta seleccionada por el dador de carga.
            revisado_por (UUID | None): Usuario que reviso las ofertas y tomo la decision.

        Returns:
            PostulacionModelo: La oferta adjudicada actualizada en estado SELECCIONADA.

        Raises:
            ValueError: Si el contrato o postulacion no existen, si ya esta cerrado, o si la oferta no
                corresponde al contrato.
        """
        contrato = self.contrato_dao.obtener_por_id(carga_id)
        if not contrato:
            raise ValueError(f"La carga/contrato con ID {carga_id} no fue encontrada")

        if contrato.estado in ESTADOS_NO_POSTULABLES:
            raise ValueError(f"El contrato ya fue adjudicado, finalizado o cancelado (Estado: {contrato.estado.value})")

        postulacion = self.postulacion_dao.obtener_por_id(postulacion_id)
        if not postulacion or postulacion.carga_id != carga_id:
            raise ValueError(f"La postulacion con ID {postulacion_id} no pertenece al contrato indicado")

        revisor_id = revisado_por or contrato.id_empresa_generadora
        estado_anterior = contrato.estado
        ofertas_consideradas = [
            oferta.model_dump(mode="json") for oferta in self.postulacion_dao.obtener_por_contrato(carga_id)
        ]

        # 1. Marcar postulacion como SELECCIONADA
        postulacion.estado = EstadoPostulacion.SELECCIONADA
        self.postulacion_dao.actualizar(postulacion.id, postulacion)

        # 2. Rechazar postulaciones competidoras
        postulaciones_rechazadas = self.postulacion_dao.rechazar_postulaciones(carga_id, postulacion.id)

        # 3. Transicionar contrato a ADJUDICADO y asignar transportista
        contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
            contrato_data=contrato,
            nuevo_estado=EstadoContrato.ADJUDICADO,
            id_transportista=postulacion.transportista_id,
        )
        self.contrato_dao.actualizar(contrato.id, contrato_actualizado)

        if self.auditoria_service:
            bases_aplicadas = ReglasNegocio.obtener_configuracion()
            contexto_revision = {
                "ofertas_consideradas": ofertas_consideradas,
                "oferta_seleccionada_id": str(postulacion.id),
            }
            self.auditoria_service.registrar_evento(
                transporte_id=carga_id,
                entidad=EntidadAuditable.OFERTA,
                entidad_id=postulacion.id,
                accion=AccionAuditoria.OFERTA_ESTADO_CAMBIADO,
                actor_id=revisor_id,
                datos=postulacion.model_dump(mode="json"),
                bases_aplicadas=bases_aplicadas,
                informacion_utilizada=contexto_revision,
            )
            self.auditoria_service.registrar_evento(
                transporte_id=carga_id,
                entidad=EntidadAuditable.REVISION,
                entidad_id=postulacion.id,
                accion=AccionAuditoria.OFERTA_REVISADA,
                actor_id=revisor_id,
                datos={
                    "resultado": EstadoPostulacion.SELECCIONADA.value,
                    "oferta_revisada_id": str(postulacion.id),
                },
                bases_aplicadas=bases_aplicadas,
                informacion_utilizada=contexto_revision,
            )
            for oferta_rechazada in postulaciones_rechazadas:
                self.auditoria_service.registrar_evento(
                    transporte_id=carga_id,
                    entidad=EntidadAuditable.OFERTA,
                    entidad_id=oferta_rechazada.id,
                    accion=AccionAuditoria.OFERTA_ESTADO_CAMBIADO,
                    actor_id=revisor_id,
                    datos=oferta_rechazada.model_dump(mode="json"),
                    bases_aplicadas=bases_aplicadas,
                    informacion_utilizada={
                        "motivo": "Oferta no seleccionada en la adjudicacion",
                        "oferta_ganadora_id": str(postulacion.id),
                    },
                )
            self.auditoria_service.registrar_evento(
                transporte_id=carga_id,
                entidad=EntidadAuditable.CONTRATO,
                entidad_id=carga_id,
                accion=AccionAuditoria.ESTADO_CONTRATO_CAMBIADO,
                actor_id=revisor_id,
                datos=contrato_actualizado.model_dump(mode="json"),
                bases_aplicadas=bases_aplicadas,
                informacion_utilizada={
                    "estado_anterior": estado_anterior.value,
                    "estado_nuevo": EstadoContrato.ADJUDICADO.value,
                    "oferta_ganadora_id": str(postulacion.id),
                },
            )
            self.auditoria_service.registrar_evento(
                transporte_id=carga_id,
                entidad=EntidadAuditable.DECISION,
                entidad_id=postulacion.id,
                accion=AccionAuditoria.ADJUDICACION_REALIZADA,
                actor_id=revisor_id,
                datos={
                    "oferta_ganadora_id": str(postulacion.id),
                    "transportista_id": str(postulacion.transportista_id),
                    "estado_contrato": contrato_actualizado.estado.value,
                },
                bases_aplicadas=bases_aplicadas,
                informacion_utilizada=contexto_revision,
            )

        return postulacion

    def listar_postulaciones_carga(self, carga_id: UUID) -> list[PostulacionModelo]:
        """Retorna todas las postulaciones asociadas a una carga especifica.

        Args:
            carga_id (UUID): Identificador del contrato del que se consultan las ofertas.

        Returns:
            List[PostulacionModelo]: Listado cronologico de postulaciones recibidas.
        """
        return self.postulacion_dao.obtener_por_contrato(carga_id)


# Alias para retrocompatibilidad
SubastaService = ServicioSubasta
