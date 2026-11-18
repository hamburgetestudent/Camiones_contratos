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
            self.crear_dto_postulacion(
                carga.id, transportista_id=self.transportista_id, precio_oferta=90000.0
            )
        )
        p_perdedora = self.subasta_service.postular_a_carga(
            self.crear_dto_postulacion(
                carga.id,
                transportista_id=self.transportista_2_id,
                precio_oferta=110000.0,
            )
        )

        resultado = self.subasta_service.adjudicar_subasta(
            carga_id=carga.id, postulacion_id=p_ganadora.id
        )
        self.assertEqual(resultado.id, p_ganadora.id)
        self.assertEqual(resultado.estado, EstadoPostulacion.SELECCIONADA)

        # La otra debe quedar en RECHAZADA
        perdedora_actualizada = self.leer_postulacion_bd(carga.id, p_perdedora.id)
        self.assertEqual(perdedora_actualizada.estado, EstadoPostulacion.RECHAZADA)

        # La carga debe quedar en ADJUDICADO con transportista asignado
        carga_actualizada = self.leer_contrato_bd(carga.id)
        self.assertEqual(carga_actualizada.estado, EstadoContrato.ADJUDICADO)
        self.assertEqual(carga_actualizada.id_transportista, self.transportista_id)

    def test_regresion_adjudicar_con_transicion_invalida_no_deja_estado_a_medias(
        self,
    ) -> None:
        """Regresion (postcondicion todo o nada): si el contrato no puede pasar a
        ADJUDICADO, ninguna postulacion debe quedar SELECCIONADA ni RECHAZADA.
        """
        carga = self.crear_carga_publicada()
        p1 = self.subasta_service.postular_a_carga(
            self.crear_dto_postulacion(carga.id, transportista_id=self.transportista_id)
        )
        p2 = self.subasta_service.postular_a_carga(
            self.crear_dto_postulacion(
                carga.id, transportista_id=self.transportista_2_id
            )
        )
        # El contrato avanza a un estado desde el cual no se puede adjudicar
        self.forzar_estado_contrato(carga.id, EstadoContrato.EN_TRANSITO)

        with self.assertRaises(ValueError):
            self.subasta_service.adjudicar_subasta(carga.id, p1.id)

        for postulacion_id in (p1.id, p2.id):
            self.assertEqual(
                self.leer_postulacion_bd(carga.id, postulacion_id).estado,
                EstadoPostulacion.POSTULADA,
            )
        self.assertIsNone(self.leer_contrato_bd(carga.id).id_transportista)
