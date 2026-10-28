"""Base DRY para pruebas de Subastas y Postulaciones."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4
from dao.contrato_dao import ContratoDAOMemoria
from dao.postulacion_dao import PostulacionDAOMemoria
from domain.maquina_estados import EstadoContrato
from domain.modelos import ContratoModelo, Moneda, TipoCarga
from domain.postulacion import EstadoPostulacion, PostulacionCrear, PostulacionModelo
from services.subasta_service import ServicioSubasta
from tests.base import BaseTestCase


class BaseTestSubastas(BaseTestCase):
    """Clase base DRY para pruebas del motor de subastas.
    
    Hereda de tests.base.BaseTestCase y provee aislamiento
    completo de persistencia, DAOs en memoria y creadores de cargas de prueba.
    """

    def setUp(self) -> None:
        super().setUp()
        self.contrato_dao = ContratoDAOMemoria()
        self.postulacion_dao = PostulacionDAOMemoria()
        self.subasta_service = ServicioSubasta(
            contrato_dao=self.contrato_dao,
            postulacion_dao=self.postulacion_dao,
        )

        self.transportista_id = uuid4()
        self.transportista_2_id = uuid4()
        self.empresa_id = uuid4()

    def crear_carga_publicada(
        self,
        origen: str = "SANTIAGO",
        destino: str = "VALPARAISO",
        tipo_carga: TipoCarga = TipoCarga.GENERAL,
        estado: EstadoContrato = EstadoContrato.PUBLICADO,
        distancia_km: float | None = 120.0,
    ) -> ContratoModelo:
        """Helper DRY para crear y persistir una carga en subasta/postulación."""
        ahora = datetime.now(UTC)
        requiere_termo = (tipo_carga == TipoCarga.REFRIGERADA)
        contrato = ContratoModelo(
            id=uuid4(),
            id_empresa_generadora=self.empresa_id,
            origen=origen,
            destino=destino,
            f_cierre_postulaciones=ahora + timedelta(hours=2),
            f_estimada_salida=ahora + timedelta(hours=4),
            f_estimada_llegada=ahora + timedelta(hours=8),
            input_camionKG=15000.0,
            tipo_carga=tipo_carga,
            peso_total=8000.0,
            distancia_km=distancia_km,
            requiere_termo=requiere_termo,
            moneda=Moneda.CLP,
            monto_neto=200000.0,
            monto_iva=38000.0,
            monto_total=238000.0,
            estado=estado,
        )
        return self.contrato_dao.guardar(contrato)

    def crear_dto_postulacion(
        self,
        carga_id: UUID,
        transportista_id: UUID | None = None,
        precio_oferta: float = 180000.0,
        tiempo_entrega_horas: float = 6.0,
        comentario: str | None = "Camión con termo disponible",
    ) -> PostulacionCrear:
        """Helper DRY para instanciar postulaciones válidas."""
        return PostulacionCrear(
            carga_id=carga_id,
            transportista_id=transportista_id or self.transportista_id,
            precio_oferta=precio_oferta,
            tiempo_entrega_horas=tiempo_entrega_horas,
            comentario=comentario,
        )
