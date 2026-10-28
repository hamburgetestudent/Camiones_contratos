"""Tests unitarios dedicados a ServicioSubasta.explorar_cargas."""

from __future__ import annotations

from domain.maquina_estados import EstadoContrato
from domain.modelos import TipoCarga
from tests.subastas.base import BaseTestSubastas


class TestExplorarCargas(BaseTestSubastas):
    """Pruebas dedicadas a la exploración de cargas con filtros de región, carrocería y distancia."""

    def test_explorar_cargas_solo_estados_disponibles(self) -> None:
        c1 = self.crear_carga_publicada(estado=EstadoContrato.PUBLICADO)
        c2 = self.crear_carga_publicada(estado=EstadoContrato.EN_SUBASTA)
        c3 = self.crear_carga_publicada(estado=EstadoContrato.EN_POSTULACION)
        # Estados no disponibles
        self.crear_carga_publicada(estado=EstadoContrato.ADJUDICADO)
        self.crear_carga_publicada(estado=EstadoContrato.CANCELADO)

        cargas = self.subasta_service.explorar_cargas()
        self.assertEqual(len(cargas), 3)
        ids = {c.id for c in cargas}
        self.assertEqual(ids, {c1.id, c2.id, c3.id})

    def test_filtro_por_region(self) -> None:
        c_stgo = self.crear_carga_publicada(origen="SANTIAGO", destino="RANCAGUA")
        self.crear_carga_publicada(origen="ANTOFAGASTA", destino="CALAMA")

        resultados = self.subasta_service.explorar_cargas(region="Santiago")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].id, c_stgo.id)

    def test_filtro_por_tipo_carroceria(self) -> None:
        c_refri = self.crear_carga_publicada(tipo_carga=TipoCarga.REFRIGERADA)
        self.crear_carga_publicada(tipo_carga=TipoCarga.GENERAL)

        resultados = self.subasta_service.explorar_cargas(tipo_carroceria="refrigerada")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].id, c_refri.id)

    def test_filtro_por_distancia_maxima(self) -> None:
        c_corta = self.crear_carga_publicada(distancia_km=80.0)
        self.crear_carga_publicada(distancia_km=300.0)

        resultados = self.subasta_service.explorar_cargas(distancia_max_km=100.0)
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].id, c_corta.id)

