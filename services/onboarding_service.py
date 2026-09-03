"""
Servicio de Negocio para el modulo de Onboarding y Verificacion de Documentacion (KYC / Fleet Compliance).
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from dao.onboarding_dao import DocumentoDAOInMemory, DadorCargaDAOInMemory
from domain.modelos_onboarding import (
    DocumentoTransportista,
    DadorCarga,
    DatosFacturacion,
    EstadoValidacion,
    TipoDocumento,
    EstadoOnboardingTransportistaDTO,
)


DOCUMENTOS_REQUERIDOS_TRANSPORTISTA = [
    TipoDocumento.LICENCIA_CONDUCIR,
    TipoDocumento.PADRON_VEHICULO,
    TipoDocumento.REVISION_TECNICA,
    TipoDocumento.SEGURO_CARGA,
    TipoDocumento.ANTECEDENTES,
]


class OnboardingService:
    """Servicio que implementa las reglas de negocio de onboarding y validacion documental."""

    def __init__(
        self,
        documento_dao: Optional[DocumentoDAOInMemory] = None,
        dador_dao: Optional[DadorCargaDAOInMemory] = None,
    ) -> None:
        self.documento_dao = documento_dao or DocumentoDAOInMemory()
        self.dador_dao = dador_dao or DadorCargaDAOInMemory()

    # =========================================
    # Operaciones del Transportista
    # =========================================

    def cargar_documento(self, user_id: UUID, tipo: TipoDocumento, archivo: str) -> DocumentoTransportista:
        """
        Carga o actualiza un documento para el transportista.
        Si ya existe un documento del mismo tipo, se actualiza el archivo y se reinicia a PENDIENTE.
        """
        existente = self.documento_dao.get_by_user_and_tipo(user_id, tipo)
        if existente:
            existente.archivo = archivo
            existente.estado = EstadoValidacion.PENDIENTE
            existente.created_at = datetime.now(timezone.utc)
            self.documento_dao.update(existente.id, existente)
            return existente

        nuevo_doc = DocumentoTransportista(
            user_id=user_id,
            tipo=tipo,
            archivo=archivo,
            estado=EstadoValidacion.PENDIENTE,
        )
        return self.documento_dao.save(nuevo_doc)

    def listar_documentos_transportista(self, user_id: UUID) -> List[DocumentoTransportista]:
        """Obtiene la lista de todos los documentos cargados por el transportista."""
        return self.documento_dao.get_by_user_id(user_id)

    def obtener_estado_transportista(self, user_id: UUID) -> EstadoOnboardingTransportistaDTO:
        """
        Calcula el estado global de onboarding del transportista:
        - APROBADO: Si y solo si los 5 documentos requeridos existen y estan todos APROBADOS.
        - RECHAZADO: Si al menos un documento cargado esta RECHAZADO.
        - PENDIENTE: En cualquier otro caso (faltan documentos o estan en revision).
        """
        documentos = self.documento_dao.get_by_user_id(user_id)
        docs_por_tipo = {doc.tipo: doc for doc in documentos}

        # Verificar si alguno esta rechazado
        tiene_rechazados = any(doc.estado == EstadoValidacion.RECHAZADO for doc in documentos)

        # Verificar si todos los requeridos existen y estan aprobados
        todos_cargados = all(tipo in docs_por_tipo for tipo in DOCUMENTOS_REQUERIDOS_TRANSPORTISTA)
        todos_aprobados = todos_cargados and all(
            docs_por_tipo[tipo].estado == EstadoValidacion.APROBADO
            for tipo in DOCUMENTOS_REQUERIDOS_TRANSPORTISTA
        )

        if tiene_rechazados:
            estado_global = EstadoValidacion.RECHAZADO
        elif todos_aprobados:
            estado_global = EstadoValidacion.APROBADO
        else:
            estado_global = EstadoValidacion.PENDIENTE

        faltantes = [tipo for tipo in DOCUMENTOS_REQUERIDOS_TRANSPORTISTA if tipo not in docs_por_tipo]

        return EstadoOnboardingTransportistaDTO(
            user_id=user_id,
            estado_global=estado_global,
            documentos_requeridos=DOCUMENTOS_REQUERIDOS_TRANSPORTISTA,
            documentos_cargados=documentos,
            faltantes=faltantes,
        )

    def es_transportista_aprobado(self, user_id: UUID) -> bool:
        """Verifica si el transportista tiene su onboarding completado y aprobado."""
        estado_dto = self.obtener_estado_transportista(user_id)
        return estado_dto.estado_global == EstadoValidacion.APROBADO

    # =========================================
    # Operaciones del Dador de Carga
    # =========================================

    def registrar_o_actualizar_perfil_dador(
        self,
        user_id: UUID,
        rut_id_empresa: str,
        datos_facturacion: DatosFacturacion,
    ) -> DadorCarga:
        """Registra o actualiza los datos tributarios del dador de carga, reiniciando validacion a PENDIENTE."""
        existente = self.dador_dao.get_by_user_id(user_id)
        if existente:
            existente.rut_id_empresa = rut_id_empresa
            existente.datos_facturacion = datos_facturacion
            existente.estado_validacion = EstadoValidacion.PENDIENTE
            self.dador_dao.update(existente.id, existente)
            return existente

        nuevo_perfil = DadorCarga(
            user_id=user_id,
            rut_id_empresa=rut_id_empresa,
            datos_facturacion=datos_facturacion,
            estado_validacion=EstadoValidacion.PENDIENTE,
        )
        return self.dador_dao.save(nuevo_perfil)

    def obtener_perfil_dador(self, user_id: UUID) -> Optional[DadorCarga]:
        """Obtiene el perfil del dador de carga por su UUID de usuario."""
        return self.dador_dao.get_by_user_id(user_id)

    def es_dador_aprobado(self, user_id: UUID) -> bool:
        """Verifica si el dador de carga cuenta con su validacion tributaria APROBADA."""
        perfil = self.dador_dao.get_by_user_id(user_id)
        if not perfil:
            return False
        return perfil.estado_validacion == EstadoValidacion.APROBADO

    # =========================================
    # Operaciones de Backoffice / Admin
    # =========================================

    def listar_documentos_pendientes_admin(self) -> List[DocumentoTransportista]:
        """Lista todos los documentos de transportistas pendientes de revision."""
        return self.documento_dao.get_pendientes()

    def validar_documento(self, documento_id: UUID, nuevo_estado: EstadoValidacion) -> DocumentoTransportista:
        """Aprueba o rechaza un documento especifico."""
        doc = self.documento_dao.get_id(documento_id)
        if not doc:
            raise ValueError(f"No se encontro el documento con ID {documento_id}")

        if nuevo_estado not in (EstadoValidacion.APROBADO, EstadoValidacion.RECHAZADO):
            raise ValueError("El estado de validacion debe ser APROBADO o RECHAZADO")

        doc.estado = nuevo_estado
        self.documento_dao.update(documento_id, doc)
        return doc

    def listar_dadores_pendientes_admin(self) -> List[DadorCarga]:
        """Lista todos los dadores de carga pendientes de validacion tributaria."""
        return self.dador_dao.get_pendientes()

    def validar_dador(self, dador_id: UUID, nuevo_estado: EstadoValidacion) -> DadorCarga:
        """Aprueba o rechaza el perfil tributario de un dador de carga."""
        dador = self.dador_dao.get_id(dador_id)
        if not dador:
            raise ValueError(f"No se encontro el perfil dador con ID {dador_id}")

        if nuevo_estado not in (EstadoValidacion.APROBADO, EstadoValidacion.RECHAZADO):
            raise ValueError("El estado de validacion debe ser APROBADO o RECHAZADO")

        dador.estado_validacion = nuevo_estado
        self.dador_dao.update(dador_id, dador)
        return dador


# Instancia singleton del servicio y DAOs
documento_dao_instancia = DocumentoDAOInMemory()
dador_dao_instancia = DadorCargaDAOInMemory()
onboarding_service_instancia = OnboardingService(
    documento_dao=documento_dao_instancia,
    dador_dao=dador_dao_instancia,
)

