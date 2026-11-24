"""Servicio de negocio para el Motor de Postulaciones y Subastas.

La persistencia se delega en ``ContratoDAO`` y ``PostulacionDAO`` inyectados
(por defecto sus implementaciones SQLite). Las operaciones que leen, validan y
escriben (postular, adjudicar) se ejecutan en una unica transaccion exclusiva.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from dao.contrato_dao import ContratoDAO, ContratoDAOSQLite
from dao.postulacion_dao import PostulacionDAO, PostulacionDAOSQLite
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

    def __init__(
        self,
        db_path: str | Path | None = None,
        contrato_dao: ContratoDAO | None = None,
        postulacion_dao: PostulacionDAO | None = None,
    ) -> None:
        """Inicializa el servicio con sus almacenes persistentes.

        Args:
            db_path (str | Path | None, optional): Archivo SQLite para los DAO que no se
                inyecten. Si es None se usa ``DEFAULT_DB_PATH``. Defaults to None.
            contrato_dao (ContratoDAO | None, optional): Almacen de contratos.
            postulacion_dao (PostulacionDAO | None, optional): Almacen de postulaciones.
                Ambos DAO deben apuntar a la misma base para compartir transaccion.
        """
        self._contratos: ContratoDAO = contrato_dao or ContratoDAOSQLite(db_path)
        self._postulaciones: PostulacionDAO = postulacion_dao or PostulacionDAOSQLite(
            db_path
        )

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
        with self._contratos.conexion() as conn:
            todos = self._contratos.obtener_todos(conn)
        cargas = [c for c in todos if c.estado in ESTADOS_CARGA_DISPONIBLES]

        if region and region.strip():
            filtro_region = region.strip().lower()
            cargas = [
                c
                for c in cargas
                if filtro_region in c.origen.lower()
                or filtro_region in c.destino.lower()
            ]

        if tipo_carroceria and tipo_carroceria.strip():
            filtro_carroceria = tipo_carroceria.strip().lower()
            cargas = [
                c for c in cargas if filtro_carroceria in c.tipo_carga.value.lower()
            ]

        if distancia_max_km is not None and distancia_max_km > 0:

            def _resolver_distancia(contrato: ContratoModelo) -> float:
                if contrato.distancia_km is not None:
                    return contrato.distancia_km
                return estimar_distancia_entre_puntos(contrato.origen, contrato.destino)

            cargas = [c for c in cargas if _resolver_distancia(c) <= distancia_max_km]

        return cargas

    def _evaluar_plazo(self, conn: sqlite3.Connection, contrato: ContratoModelo) -> str:
        if datetime.now(UTC) <= contrato.f_cierre_postulaciones:
            return "VIGENTE"
        if self._postulaciones.existe_para_contrato(conn, contrato.id):
            return "CERRADA"
        if contrato.estado in ESTADOS_CARGA_DISPONIBLES:
            cancelado = MaquinaEstadosContrato.cambiar_estado(
                contrato_data=contrato, nuevo_estado=EstadoContrato.CANCELADO
            )
            self._contratos.actualizar(conn, contrato.id, cancelado)
        return "DESIERTA"

    def verificar_expiracion_subasta(self, carga_id: UUID) -> str:
        """Evalua el plazo y persiste el cierre de una subasta desierta."""
        with self._contratos.transaccion() as conn:
            contrato = self._contratos.obtener_por_id(conn, carga_id)
            if contrato is None:
                raise ValueError(f"La carga/contrato con ID {carga_id} no existe")
            return self._evaluar_plazo(conn, contrato)

    def postular_a_carga(
        self,
        datos_postulacion: PostulacionCrear,
        onboarding_aprobado: bool = True,
    ) -> PostulacionModelo:
        """Registra la postulacion de un transportista para una carga activa tras validar las reglas de negocio.

        Valida que el transportista cuente con onboarding aprobado, que la carga exista, que se
        encuentre en un estado que admita nuevas ofertas y que no haya expirado la fecha límite de
        postulación (f_cierre_postulaciones). Si expiró, la subasta se declara desierta (si no hubo
        postulaciones previas) o cerrada (si ya contaba con ofertas). Si la carga estaba en
        PUBLICADO o EN_SUBASTA y es válida, se transiciona automáticamente a EN_POSTULACION.

        Args:
            datos_postulacion (PostulacionCrear): Esquema con ID de carga, transportista, camion y tarifa ofertada.
            onboarding_aprobado (bool, optional): Estado de verificacion de antecedentes/flota. Defaults to True.

        Returns:
            PostulacionModelo: Entidad de postulacion persistida con estado POSTULADA.

        Raises:
            ValueError: Si el onboarding no esta aprobado, si el contrato no existe, si no admite ofertas
                o si el plazo para postular ha expirado (cerrada o desierta).
        """
        if not onboarding_aprobado:
            raise ValueError(
                "El transportista debe tener su onboarding en estado 'APROBADO' para postular"
            )

        # Lectura, validacion y escrituras en una sola transaccion: si algo falla,
        # no queda una postulacion guardada con el contrato sin transicionar.
        with self._contratos.transaccion() as conn:
            contrato = self._contratos.obtener_por_id(conn, datos_postulacion.carga_id)
            if not contrato:
                raise ValueError(
                    f"La carga/contrato con ID {datos_postulacion.carga_id} no existe"
                )

            # Precondicion: solo cargas visibles para el transportista admiten ofertas
            # (un BORRADOR o un contrato en transito tampoco deben recibirlas).
            if contrato.estado not in ESTADOS_CARGA_DISPONIBLES:
                raise ValueError(
                    f"La carga se encuentra en estado '{contrato.estado.value}' y no acepta nuevas postulaciones"
                )

            plazo = self._evaluar_plazo(conn, contrato)
            if plazo == "VIGENTE":
                nueva_postulacion = PostulacionModelo(**datos_postulacion.model_dump())
                self._postulaciones.guardar(conn, nueva_postulacion)

                # Transicion automatica a EN_POSTULACION si la carga estaba en PUBLICADO o EN_SUBASTA
                if contrato.estado in (
                    EstadoContrato.PUBLICADO,
                    EstadoContrato.EN_SUBASTA,
                ):
                    contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
                        contrato_data=contrato,
                        nuevo_estado=EstadoContrato.EN_POSTULACION,
                    )
                    self._contratos.actualizar(conn, contrato.id, contrato_actualizado)

                return nueva_postulacion

        # El rechazo se comunica despues del commit para conservar el cierre sin ofertas.
        raise ValueError(
            f"La subasta esta {plazo.lower()} y no admite nuevas postulaciones"
        )

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
        # Toda la operacion es una unica transaccion: o se aplican los tres cambios
        # (postulacion ganadora, competidoras y contrato) o no se aplica ninguno.
        with self._contratos.transaccion() as conn:
            contrato = self._contratos.obtener_por_id(conn, carga_id)
            if not contrato:
                raise ValueError(
                    f"La carga/contrato con ID {carga_id} no fue encontrada"
                )

            if contrato.estado in ESTADOS_NO_POSTULABLES:
                raise ValueError(
                    f"El contrato ya fue adjudicado, finalizado o cancelado (Estado: {contrato.estado.value})"
                )

            postulacion = self._postulaciones.obtener_por_id(conn, postulacion_id)
            if not postulacion or postulacion.carga_id != carga_id:
                raise ValueError(
                    f"La postulacion con ID {postulacion_id} no pertenece al contrato indicado"
                )

            # Precondicion: validar la transicion ANTES de escribir nada, para que la
            # postcondicion "todo o nada" se cumpla (evita ofertas SELECCIONADA con
            # un contrato que sigue en BORRADOR, EN_TRANSITO, etc.).
            if not MaquinaEstadosContrato.validar_transicion(
                contrato.estado, EstadoContrato.ADJUDICADO
            ):
                raise ValueError(
                    "Transicion de estado no permitida, no se puede pasar de "
                    f"{contrato.estado.value} a {EstadoContrato.ADJUDICADO.value}"
                )

            # 1. Marcar postulacion como SELECCIONADA
            postulacion.estado = EstadoPostulacion.SELECCIONADA
            self._postulaciones.actualizar_estado(
                conn, postulacion.id, postulacion.estado
            )

            # 2. Rechazar postulaciones competidoras
            self._postulaciones.rechazar_competidoras(conn, carga_id, postulacion.id)

            # 3. Transicionar contrato a ADJUDICADO y asignar transportista
            contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
                contrato_data=contrato,
                nuevo_estado=EstadoContrato.ADJUDICADO,
                id_transportista=postulacion.transportista_id,
            )
            self._contratos.actualizar(conn, contrato.id, contrato_actualizado)

        return postulacion

    def listar_postulaciones_carga(self, carga_id: UUID) -> list[PostulacionModelo]:
        """Retorna todas las postulaciones asociadas a una carga especifica.

        Args:
            carga_id (UUID): Identificador del contrato del que se consultan las ofertas.

        Returns:
            List[PostulacionModelo]: Listado cronologico de postulaciones recibidas.
        """
        with self._contratos.conexion() as conn:
            if not self._contratos.obtener_por_id(conn, carga_id):
                return []
            return self._postulaciones.obtener_por_contrato(conn, carga_id)


# Alias para retrocompatibilidad
SubastaService = ServicioSubasta
