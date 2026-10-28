"""Tests unitarios dedicados a ServicioSubasta.listar_postulaciones_carga."""

from __future__ import annotations

from tests.subastas.base import BaseTestSubastas


class TestListarPostulaciones(BaseTestSubastas):
    """Pruebas dedicadas al listado de ofertas asociadas a una carga."""

    def test_listar_postulaciones_carga_vacia(self) -> None:
        carga = self.crear_carga_publicada()
        self.assertEqual(self.subasta_service.listar_postulaciones_carga(carga.id), [])

    def test_listar_multiples_postulaciones(self) -> None:
        carga = self.crear_carga_publicada()
        p1 = self.subasta_service.postular_a_carga(
            self.crear_dto_postulacion(carga.id, transportista_id=self.transportista_id, precio_oferta=100000.0)
        )
        p2 = self.subasta_service.postular_a_carga(
            self.crear_dto_postulacion(carga.id, transportista_id=self.transportista_2_id, precio_oferta=95000.0)
        )

        lista = self.subasta_service.listar_postulaciones_carga(carga.id)
        self.assertEqual(len(lista), 2)
        ids = {p.id for p in lista}
        self.assertEqual(ids, {p1.id, p2.id})

