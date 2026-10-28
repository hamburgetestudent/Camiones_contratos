"""Tests unitarios dedicados a la función estimar_distancia_entre_puntos."""

from __future__ import annotations

from services.subasta_service import estimar_distancia_entre_puntos
from tests.subastas.base import BaseTestSubastas


class TestEstimarDistancia(BaseTestSubastas):
    """Pruebas dedicadas exclusivamente al cálculo de distancias estimadas."""

    def test_distancia_cero_si_mismo_origen_y_destino(self) -> None:
        self.assertEqual(estimar_distancia_entre_puntos("SANTIAGO", "santiago"), 0.0)
        self.assertEqual(estimar_distancia_entre_puntos(" Valparaiso ", "valparaiso"), 0.0)

    def test_distancia_estimada_por_defecto_si_ciudades_distintas(self) -> None:
        self.assertEqual(estimar_distancia_entre_puntos("SANTIAGO", "CONCEPCION"), 150.0)
