"""Servicio de negocio para el Motor de Postulaciones y Subastas.

Persiste directamente en SQLite (tablas ``postulaciones`` y ``contratos``)
mediante ``database.conexion``. Las operaciones que leen, validan y escriben
(postular, adjudicar) se ejecutan en una unica transaccion exclusiva.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import UUID

from database.conexion import obtener_conexion, transaccion_exclusiva
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from domain.modelos import ContratoModelo
from domain.postulacion import EstadoPostulacion, PostulacionCrear, PostulacionModelo
from services.contrato_service import (
    actualizar_contrato,
    buscar_contrato,
    buscar_todos_los_contratos,
)

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


# ---------------------------------------------------------------------------
# SQL: tabla ``postulaciones``
# ---------------------------------------------------------------------------

_SELECT_POSTULACION = (
    "SELECT id, carga_id, transportista_id, precio_oferta, tiempo_entrega_horas, "
    "comentario, estado, creado_en FROM postulaciones"
)


def _fila_a_postulacion(fila: sqlite3.Row) -> PostulacionModelo:
    """Reconstruye una postulacion ya validada al momento de crearse (sin revalidar)."""
    return PostulacionModelo.model_construct(
        id=UUID(fila["id"]),
        carga_id=UUID(fila["carga_id"]),
        transportista_id=UUID(fila["transportista_id"]),
        precio_oferta=fila["precio_oferta"],
        tiempo_entrega_horas=fila["tiempo_entrega_horas"],
        comentario=fila["comentario"],
        estado=EstadoPostulacion(fila["estado"]),
        creado_en=datetime.fromisoformat(fila["creado_en"]),
    )


def _insertar_postulacion(
    conn: sqlite3.Connection, postulacion: PostulacionModelo
) -> PostulacionModelo:
    conn.execute(
        """
        INSERT INTO postulaciones (
            id, carga_id, transportista_id, precio_oferta, tiempo_entrega_horas,
            comentario, estado, creado_en
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(postulacion.id),
            str(postulacion.carga_id),
            str(postulacion.transportista_id),
            postulacion.precio_oferta,
            postulacion.tiempo_entrega_horas,
            postulacion.comentario,
            EstadoPostulacion(postulacion.estado).value,
            postulacion.creado_en.isoformat(),
        ),
    )
    return postulacion


def _buscar_postulacion(
    conn: sqlite3.Connection, postulacion_id: UUID
) -> PostulacionModelo | None:
    fila = conn.execute(
        f"{_SELECT_POSTULACION} WHERE id = ?", (str(postulacion_id),)
    ).fetchone()
    return _fila_a_postulacion(fila) if fila else None


def _buscar_postulaciones_por_contrato(
    conn: sqlite3.Connection, contrato_id: UUID
) -> list[PostulacionModelo]:
    filas = conn.execute(
        f"{_SELECT_POSTULACION} WHERE carga_id = ? ORDER BY rowid",
        (str(contrato_id),),
    ).fetchall()
    return [_fila_a_postulacion(fila) for fila in filas]


def _actualizar_estado_postulacion(
    conn: sqlite3.Connection, postulacion: PostulacionModelo
) -> None:
    conn.execute(
        "UPDATE postulaciones SET estado = ? WHERE id = ?",
        (EstadoPostulacion(postulacion.estado).value, str(postulacion.id)),
    )


def _rechazar_postulaciones_competidoras(
    conn: sqlite3.Connection, contrato_id: UUID, ganadora_id: UUID
) -> None:
    """Marca como RECHAZADA toda postulacion del contrato excepto la ganadora."""
    conn.execute(
        """
        UPDATE postulaciones SET estado = ?
        WHERE carga_id = ? AND id != ? AND estado != ?
        """,
        (
            EstadoPostulacion.RECHAZADA.value,
            str(contrato_id),
            str(ganadora_id),
            EstadoPostulacion.RECHAZADA.value,
        ),
    )


class ServicioSubasta:
    """Orquesta la exploracion de cargas, envio de ofertas y adjudicacion de subastas."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        """Inicializa el servicio sobre una base de datos SQLite.

        Args:
            db_path (str | Path | None, optional): Archivo SQLite a usar. Si es None se
                usa ``DEFAULT_DB_PATH``. Defaults to None.
        """
        self._db_path = db_path

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
        with obtener_conexion(self._db_path) as conn:
            todos = buscar_todos_los_contratos(conn)
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
            PostulacionModelo: Entidad de postulacion persistida con estado POSTULADA.

        Raises:
            ValueError: Si el onboarding no esta aprobado, si el contrato no existe o si no admite ofertas.
        """
        if not onboarding_aprobado:
            raise ValueError(
                "El transportista debe tener su onboarding en estado 'APROBADO' para postular"
            )

        # Lectura, validacion y escrituras en una sola transaccion: si algo falla,
        # no queda una postulacion guardada con el contrato sin transicionar.
        with transaccion_exclusiva(self._db_path) as conn:
            contrato = buscar_contrato(conn, datos_postulacion.carga_id)
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

            nueva_postulacion = PostulacionModelo(**datos_postulacion.model_dump())
            _insertar_postulacion(conn, nueva_postulacion)

            # Transicion automatica a EN_POSTULACION si la carga estaba en PUBLICADO o EN_SUBASTA
            if contrato.estado in (EstadoContrato.PUBLICADO, EstadoContrato.EN_SUBASTA):
                contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
                    contrato_data=contrato,
                    nuevo_estado=EstadoContrato.EN_POSTULACION,
                )
                actualizar_contrato(conn, contrato.id, contrato_actualizado)

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
        # Toda la operacion es una unica transaccion: o se aplican los tres cambios
        # (postulacion ganadora, competidoras y contrato) o no se aplica ninguno.
        with transaccion_exclusiva(self._db_path) as conn:
            contrato = buscar_contrato(conn, carga_id)
            if not contrato:
                raise ValueError(
                    f"La carga/contrato con ID {carga_id} no fue encontrada"
                )

            if contrato.estado in ESTADOS_NO_POSTULABLES:
                raise ValueError(
                    f"El contrato ya fue adjudicado, finalizado o cancelado (Estado: {contrato.estado.value})"
                )

            postulacion = _buscar_postulacion(conn, postulacion_id)
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
            _actualizar_estado_postulacion(conn, postulacion)

            # 2. Rechazar postulaciones competidoras
            _rechazar_postulaciones_competidoras(conn, carga_id, postulacion.id)

            # 3. Transicionar contrato a ADJUDICADO y asignar transportista
            contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
                contrato_data=contrato,
                nuevo_estado=EstadoContrato.ADJUDICADO,
                id_transportista=postulacion.transportista_id,
            )
            actualizar_contrato(conn, contrato.id, contrato_actualizado)

        return postulacion

    def listar_postulaciones_carga(self, carga_id: UUID) -> list[PostulacionModelo]:
        """Retorna todas las postulaciones asociadas a una carga especifica.

        Args:
            carga_id (UUID): Identificador del contrato del que se consultan las ofertas.

        Returns:
            List[PostulacionModelo]: Listado cronologico de postulaciones recibidas.
        """
        with obtener_conexion(self._db_path) as conn:
            return _buscar_postulaciones_por_contrato(conn, carga_id)


# Alias para retrocompatibilidad
SubastaService = ServicioSubasta
