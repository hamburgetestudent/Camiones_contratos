"""
Modulo DAO en memoria para Onboarding y Verificacion de Documentos (KYC).
"""

from typing import List, Optional, Dict
from uuid import UUID

from dao.base_dao import BaseDAO
from domain.modelos_onboarding import (
    DocumentoTransportista,
    DadorCarga,
    EstadoValidacion,
    TipoDocumento,
)


class OnboardingDAO:
    """Interfaz para operaciones DAO de onboarding."""
    pass

class DocumentoDAOInMemory(BaseDAO[DocumentoTransportista, UUID]):

    """Repositorio en memoria para los documentos de los transportistas."""

    def __init__(self) -> None:
        self._db: Dict[UUID, DocumentoTransportista] = {}

    def obt_por_id(self, entidad_id: UUID) -> Optional[DocumentoTransportista]:
        return self._db.get(entidad_id)

    def obt_todos(self) -> List[DocumentoTransportista]:
        return list(self._db.values())

    def guardar(self, entidad: DocumentoTransportista) -> DocumentoTransportista:
        self._db[entidad.id] = entidad
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: DocumentoTransportista) -> Optional[DocumentoTransportista]:
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

    # Alias de compatibilidad con BaseDAO
    get_id = obt_por_id
    get_all = obt_todos
    save = guardar
    update = actualizar
    delete = eliminar

    # --- Consultas especializadas ---


    def get_by_user_id(self, user_id: UUID) -> List[DocumentoTransportista]:
        """Obtiene todos los documentos cargados por un transportista."""
        return [doc for doc in self._db.values() if doc.user_id == user_id]

    def get_by_user_and_tipo(self, user_id: UUID, tipo: TipoDocumento) -> Optional[DocumentoTransportista]:
        """Obtiene el documento de un tipo específico para un transportista."""
        for doc in self._db.values():
            if doc.user_id == user_id and doc.tipo == tipo:
                return doc
        return None

    def get_pendientes(self) -> List[DocumentoTransportista]:
        """Obtiene todos los documentos en estado PENDIENTE."""
        return [doc for doc in self._db.values() if doc.estado == EstadoValidacion.PENDIENTE]


class DadorCargaDAOInMemory(BaseDAO[DadorCarga, UUID]):
    """Repositorio en memoria para los perfiles y datos de facturacion de dadores de carga."""

    def __init__(self) -> None:
        self._db: Dict[UUID, DadorCarga] = {}

    def obt_por_id(self, entidad_id: UUID) -> Optional[DadorCarga]:
        return self._db.get(entidad_id)

    def obt_todos(self) -> List[DadorCarga]:
        return list(self._db.values())

    def guardar(self, entidad: DadorCarga) -> DadorCarga:
        self._db[entidad.id] = entidad
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: DadorCarga) -> Optional[DadorCarga]:
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


    # --- Consultas especializadas ---


    def get_by_user_id(self, user_id: UUID) -> Optional[DadorCarga]:
        """Obtiene el perfil tributario de un dador de carga por su user_id."""
        for dador in self._db.values():
            if dador.user_id == user_id:
                return dador
        return None

    def get_by_rut(self, rut_id_empresa: str) -> Optional[DadorCarga]:
        """Obtiene el perfil dador por RUT o identificador de empresa."""
        rut_normalizado = rut_id_empresa.strip().upper().replace(".", "")
        for dador in self._db.values():
            if dador.rut_id_empresa.strip().upper().replace(".", "") == rut_normalizado:
                return dador
        return None

    def get_pendientes(self) -> List[DadorCarga]:
        """Obtiene todos los perfiles de dador de carga en estado PENDIENTE."""
        return [dador for dador in self._db.values() if dador.estado_validacion == EstadoValidacion.PENDIENTE]

    # Alias de compatibilidad
    get_id = obt_por_id
    get_all = obt_todos
    save = guardar
    update = actualizar
    delete = eliminar
