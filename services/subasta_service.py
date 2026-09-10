"""Servicio de negocio para el Motor de Postulaciones y Subastas."""

from uuid import UUID

from dao.contrato_dao import ContratoDAO
from dao.postulacion_dao import PostulacionDAO
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from domain.modelos import ContratoModelo
from domain.postulacion import EstadoPostulacion, PostulacionCrear, PostulacionModelo

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

    def __init__(self, contrato_dao: ContratoDAO, postulacion_dao: PostulacionDAO) -> None:
        """Inicializa el servicio inyectando los DAOs de contratos y postulaciones.

        Args:
            contrato_dao (ContratoDAO): Capa de acceso a datos para contratos de carga.
            postulacion_dao (PostulacionDAO): Capa de acceso a datos para ofertas/postulaciones.
        """
        self.contrato_dao = contrato_dao
        self.postulacion_dao = postulacion_dao

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
        """Adjudica una subasta: selecciona la oferta ganadora, rechaza las demas y adjudica el contrato.

        Cambia el estado de la postulacion a SELECCIONADA, rechaza atomica y formalmente las demas postulaciones
        competidoras del contrato, y transiciona el estado del contrato a ADJUDICADO asignando el transportista.

        Args:
            carga_id (UUID): Identificador unico del contrato/carga subastada.
            postulacion_id (UUID): Identificador unico de la oferta seleccionada por el dador de carga.

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
