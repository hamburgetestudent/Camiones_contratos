"""Modulo DAO en memoria para Onboarding y Verificacion de Documentos (KYC)."""

from uuid import UUID

from dao.base_dao import BaseDAO
from domain.modelos_onboarding import (
    DadorCarga,
    DocumentoTransportista,
    EstadoValidacion,
    TipoDocumento,
)


class DocumentoDAOInMemory(BaseDAO[DocumentoTransportista, UUID]):
    """Repositorio en memoria para los documentos de los transportistas."""

    def __init__(self) -> None:
        self._db: dict[UUID, DocumentoTransportista] = {}

    def obtener_por_id(self, entidad_id: UUID) -> DocumentoTransportista | None:
        return self._db.get(entidad_id)

    def obtener_todos(self) -> list[DocumentoTransportista]:
        return list(self._db.values())

    def guardar(self, entidad: DocumentoTransportista) -> DocumentoTransportista:
        self._db[entidad.id] = entidad
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: DocumentoTransportista) -> DocumentoTransportista | None:
        if entidad_id in self._db:
            self._db[entidad_id] = entidad
            return entidad
        return None

    def eliminar(self, entidad_id: UUID) -> bool:
        if entidad_id in self._db:
            del self._db[entidad_id]
            return True
        return False

    def existe(self, entidad_id: UUID) -> bool:
        return entidad_id in self._db

    def get_by_user_id(self, user_id: UUID) -> list[DocumentoTransportista]:
        """Obtiene todos los documentos cargados por un transportista."""
        return [doc for doc in self._db.values() if doc.user_id == user_id]

    def get_by_user_and_tipo(self, user_id: UUID, tipo: TipoDocumento) -> DocumentoTransportista | None:
        """Obtiene el documento de un tipo específico para un transportista."""
        for doc in self._db.values():
            if doc.user_id == user_id and doc.tipo == tipo:
                return doc
        return None

    def get_pendientes(self) -> list[DocumentoTransportista]:
        """Obtiene todos los documentos en estado PENDIENTE."""
        return [doc for doc in self._db.values() if doc.estado == EstadoValidacion.PENDIENTE]

    # Alias en ingles y nombres previos
    get_id = obtener_por_id
    obt_por_id = obtener_por_id
    get_all = obtener_todos
    obt_todos = obtener_todos
    save = guardar
    update = actualizar
    delete = eliminar


class DadorCargaDAOInMemory(BaseDAO[DadorCarga, UUID]):
    """Repositorio en memoria para los perfiles y datos de facturacion de dadores de carga."""

    def __init__(self) -> None:
        self._db: dict[UUID, DadorCarga] = {}

    def obtener_por_id(self, entidad_id: UUID) -> DadorCarga | None:
        return self._db.get(entidad_id)

    def obtener_todos(self) -> list[DadorCarga]:
        return list(self._db.values())

    def guardar(self, entidad: DadorCarga) -> DadorCarga:
        self._db[entidad.id] = entidad
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: DadorCarga) -> DadorCarga | None:
        if entidad_id in self._db:
            self._db[entidad_id] = entidad
            return entidad
        return None

    def eliminar(self, entidad_id: UUID) -> bool:
        if entidad_id in self._db:
            del self._db[entidad_id]
            return True
        return False

    def existe(self, entidad_id: UUID) -> bool:
        return entidad_id in self._db

    def get_by_user_id(self, user_id: UUID) -> DadorCarga | None:
        """Obtiene el perfil tributario de un dador de carga por su user_id."""
        for dador in self._db.values():
            if dador.user_id == user_id:
                return dador
        return None

    def get_by_rut(self, rut_id_empresa: str) -> DadorCarga | None:
        """Obtiene el perfil dador por RUT o identificador de empresa."""
        rut_normalizado = rut_id_empresa.strip().upper().replace(".", "")
        for dador in self._db.values():
            if dador.rut_id_empresa.strip().upper().replace(".", "") == rut_normalizado:
                return dador
        return None

    def get_pendientes(self) -> list[DadorCarga]:
        """Obtiene todos los perfiles de dador de carga en estado PENDIENTE."""
        return [dador for dador in self._db.values() if dador.estado_validacion == EstadoValidacion.PENDIENTE]

    # Alias en ingles y nombres previos
    get_id = obtener_por_id
    obt_por_id = obtener_por_id
    get_all = obtener_todos
    obt_todos = obtener_todos
    save = guardar
    update = actualizar
    delete = eliminar
