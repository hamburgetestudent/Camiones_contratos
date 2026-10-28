"""Tests unitarios dedicados a ServicioSubasta.adjudicar_subasta."""

from __future__ import annotations

from domain.maquina_estados import EstadoContrato
from domain.postulacion import EstadoPostulacion
from tests.subastas.base import BaseTestSubastas


class TestAdjudicarSubasta(BaseTestSubastas):
    """Pruebas dedicadas a la adjudicación de la oferta ganadora y descarte de las demás."""

    def test_adjudicacion_exitosa(self) -> None:
        carga = self.crear_carga_publicada()
        p_ganadora = self.subasta_service.postular_a_carga(
            self.crear_dto_postulacion(carga.id, transportista_id=self.transportista_id, precio_oferta=90000.0)
        )
        p_perdedora = self.subasta_service.postular_a_carga(
            self.crear_dto_postulacion(carga.id, transportista_id=self.transportista_2_id, precio_oferta=110000.0)
        )

        resultado = self.subasta_service.adjudicar_subasta(carga_id=carga.id, postulacion_id=p_ganadora.id)
        self.assertEqual(resultado.id, p_ganadora.id)
        self.assertEqual(resultado.estado, EstadoPostulacion.SELECCIONADA)

        # La otra debe quedar en RECHAZADA
        perdedora_actualizada = self.postulacion_dao.obtener_por_id(p_perdedora.id)
        self.assertEqual(perdedora_actualizada.estado, EstadoPostulacion.RECHAZADA)

        # La carga debe quedar en ADJUDICADO con transportista asignado
        carga_actualizada = self.contrato_dao.obtener_por_id(carga.id)
        self.assertEqual(carga_actualizada.estado, EstadoContrato.ADJUDICADO)
        self.assertEqual(carga_actualizada.id_transportista, self.transportista_id)

