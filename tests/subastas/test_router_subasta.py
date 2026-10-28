"""Tests para los endpoints de routers/subasta_router.py."""

from __future__ import annotations

from routers.subasta_router import (
    SolicitudAdjudicacion,
    adjudicar_subasta,
    explorar_cargas,
    listar_postulaciones_carga,
    postular_a_carga,
)
from tests.subastas.base import BaseTestSubastas


class TestRouterSubasta(BaseTestSubastas):
    """Pruebas dedicadas a las funciones endpoint de routers/subasta_router.py."""

    def test_explorar_postular_y_adjudicar_via_router(self) -> None:
        carga = self.crear_carga_publicada()

        # 1. Explorar cargas
        disponibles = explorar_cargas(subasta_service=self.subasta_service)
        self.assertEqual(len(disponibles), 1)

        # 2. Postular
        dto = self.crear_dto_postulacion(carga_id=carga.id)
        postulacion = postular_a_carga(datos=dto, subasta_service=self.subasta_service, onboarding_aprobado=True)
        self.assertEqual(postulacion.carga_id, carga.id)

        # 3. Listar postulaciones
        lista = listar_postulaciones_carga(carga_id=carga.id, subasta_service=self.subasta_service)
        self.assertEqual(len(lista), 1)

        # 4. Adjudicar
        payload = SolicitudAdjudicacion(carga_id=carga.id, postulacion_id=postulacion.id)
        adjudicada = adjudicar_subasta(payload=payload, subasta_service=self.subasta_service)
        self.assertEqual(adjudicada.id, postulacion.id)

