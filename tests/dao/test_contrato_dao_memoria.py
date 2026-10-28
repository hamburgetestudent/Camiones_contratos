"""Tests unitarios dedicados a ContratoDAOMemoria y PostulacionDAOMemoria."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4
from dao.contrato_dao import ContratoDAOMemoria
from dao.postulacion_dao import PostulacionDAOMemoria
from domain.maquina_estados import EstadoContrato
from domain.modelos import ContratoModelo, TipoCarga
from domain.postulacion import EstadoPostulacion, PostulacionModelo
from tests.dao.base import BaseTestDAO


class TestContratoDAOMemoria(BaseTestDAO):
    """Pruebas dedicadas a las operaciones de almacenamiento de contratos y postulaciones en memoria."""

    def setUp(self) -> None:
        super().setUp()
        self.contrato_dao = ContratoDAOMemoria()
        self.postulacion_dao = PostulacionDAOMemoria()

    def test_guardar_y_obtener_contrato(self) -> None:
        ahora = datetime.now(UTC)
        contrato = ContratoModelo(
            id=uuid4(),
            id_empresa_generadora=uuid4(),
            origen="SANTIAGO",
            destino="VALPARAISO",
            f_cierre_postulaciones=ahora + timedelta(hours=3),
            f_estimada_salida=ahora + timedelta(hours=5),
            f_estimada_llegada=ahora + timedelta(hours=10),
            input_camionKG=10000.0,
            tipo_carga=TipoCarga.GENERAL,
            peso_total=5000.0,
            monto_neto=100000.0,
            monto_iva=19000.0,
            monto_total=119000.0,
            estado=EstadoContrato.BORRADOR,
        )
        guardado = self.contrato_dao.guardar(contrato)
        self.assertEqual(guardado.id, contrato.id)

        recuperado = self.contrato_dao.obtener_por_id(contrato.id)
        self.assertIsNotNone(recuperado)
        self.assertEqual(len(self.contrato_dao.obtener_todos()), 1)

    def test_guardar_y_listar_postulaciones_por_carga(self) -> None:
        carga_id = uuid4()
        post1 = PostulacionModelo(
            id=uuid4(),
            carga_id=carga_id,
            transportista_id=uuid4(),
            precio_oferta=60000.0,
            tiempo_entrega_horas=8.0,
            estado=EstadoPostulacion.POSTULADA,
        )
        post2 = PostulacionModelo(
            id=uuid4(),
            carga_id=carga_id,
            transportista_id=uuid4(),
            precio_oferta=55000.0,
            tiempo_entrega_horas=7.0,
            estado=EstadoPostulacion.POSTULADA,
        )
        self.postulacion_dao.guardar(post1)
        self.postulacion_dao.guardar(post2)

        postulaciones = self.postulacion_dao.obtener_por_contrato(carga_id)
        self.assertEqual(len(postulaciones), 2)
