"""Tests unitarios dedicados a ServicioSubasta.postular_a_carga."""

from __future__ import annotations

from uuid import uuid4
from domain.maquina_estados import EstadoContrato
from domain.postulacion import EstadoPostulacion
from tests.subastas.base import BaseTestSubastas


class TestPostularACarga(BaseTestSubastas):
    """Pruebas dedicadas al envío y validación de postulaciones/ofertas."""

    def test_postulacion_exitosa(self) -> None:
        carga = self.crear_carga_publicada()
        dto = self.crear_dto_postulacion(carga_id=carga.id)

        postulacion = self.subasta_service.postular_a_carga(dto, onboarding_aprobado=True)
        self.assertEqual(postulacion.carga_id, carga.id)
        self.assertEqual(postulacion.transportista_id, self.transportista_id)
        self.assertEqual(postulacion.estado, EstadoPostulacion.POSTULADA)

        # La carga debe transicionar a EN_POSTULACION si estaba en PUBLICADO
        carga_actualizada = self.contrato_dao.obtener_por_id(carga.id)
        self.assertEqual(carga_actualizada.estado, EstadoContrato.EN_POSTULACION)

    def test_rechazo_transportista_sin_onboarding(self) -> None:
        carga = self.crear_carga_publicada()
        dto = self.crear_dto_postulacion(carga_id=carga.id)

        with self.assertRaises(ValueError) as ctx:
            self.subasta_service.postular_a_carga(dto, onboarding_aprobado=False)
        self.assertIn("onboarding", str(ctx.exception).lower())

    def test_rechazo_carga_inexistente(self) -> None:
        dto = self.crear_dto_postulacion(carga_id=uuid4())
        with self.assertRaises(ValueError) as ctx:
            self.subasta_service.postular_a_carga(dto, onboarding_aprobado=True)
        self.assertIn("no existe", str(ctx.exception).lower())

    def test_rechazo_carga_no_postulable(self) -> None:
        carga = self.crear_carga_publicada(estado=EstadoContrato.CANCELADO)
        dto = self.crear_dto_postulacion(carga_id=carga.id)

        with self.assertRaises(ValueError) as ctx:
            self.subasta_service.postular_a_carga(dto, onboarding_aprobado=True)
        self.assertIn("no acepta", str(ctx.exception).lower())
