"""Tests unitarios dedicados a validaciones Pydantic y máquina de estados de Postulación."""

from __future__ import annotations

from uuid import uuid4
from pydantic import ValidationError
from domain.postulacion import (
    EstadoPostulacion,
    MaquinaEstadoPostulacion,
    PostulacionCrear,
    TARIFA_MINIMA_POSTULACION_CLP,
)
from tests.subastas.base import BaseTestSubastas


class TestModelosPostulacion(BaseTestSubastas):
    """Pruebas dedicadas a las reglas de negocio de esquemas de postulación."""

    def test_tarifa_minima_postulacion(self) -> None:
        # Menor a 5000 CLP debe fallar
        with self.assertRaises(ValidationError):
            PostulacionCrear(
                carga_id=uuid4(),
                transportista_id=uuid4(),
                precio_oferta=4999.0,
                tiempo_entrega_horas=5.0,
            )

        # 5000 CLP exactos debe ser admitido
        dto = PostulacionCrear(
            carga_id=uuid4(),
            transportista_id=uuid4(),
            precio_oferta=TARIFA_MINIMA_POSTULACION_CLP,
            tiempo_entrega_horas=5.0,
        )
        self.assertEqual(dto.precio_oferta, 5000.0)

    def test_transiciones_maquina_postulacion(self) -> None:
        self.assertTrue(MaquinaEstadoPostulacion.validar_transicion(EstadoPostulacion.POSTULADA, EstadoPostulacion.SELECCIONADA))
        self.assertTrue(MaquinaEstadoPostulacion.validar_transicion(EstadoPostulacion.POSTULADA, EstadoPostulacion.RECHAZADA))
        self.assertFalse(MaquinaEstadoPostulacion.validar_transicion(EstadoPostulacion.BORRADOR, EstadoPostulacion.SELECCIONADA))

