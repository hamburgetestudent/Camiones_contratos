"""Pruebas del cierre por expiracion sobre una base SQLite aislada."""

import unittest
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.db.conexion import obtener_conexion
from app.modules.contratos.maquina_estados import EstadoContrato
from app.modules.contratos.models import ContratoModelo
from app.modules.subastas.models import PostulacionCrear
from tests.subastas.base import BaseTestSubastas


class TestSubastaExpiracion(BaseTestSubastas):
    def setUp(self) -> None:
        super().setUp()
        self.ahora = datetime.now(UTC)

    def _fijar_cierre(self, contrato_id: UUID, cierre: datetime) -> None:
        # Simula el paso del tiempo sin sobrescribir el estado de las ofertas.
        with obtener_conexion(self.db_path) as conn:
            conn.execute(
                "UPDATE contratos SET f_cierre_postulaciones = ? WHERE id = ?",
                (cierre.isoformat(), str(contrato_id)),
            )

    def _crear_contrato(self, f_cierre: datetime) -> ContratoModelo:
        contrato = self.crear_carga_publicada()
        self._fijar_cierre(contrato.id, f_cierre)
        return contrato

    def test_postular_a_carga_vigente_exitosa(self) -> None:
        """Una postulacion dentro del plazo vigente debe aceptarse correctamente."""
        cierre_futuro = self.ahora + timedelta(hours=2)
        contrato = self._crear_contrato(f_cierre=cierre_futuro)

        datos = PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=uuid4(),
            precio_oferta=80000.0,
            tiempo_entrega_horas=4.0,
            comentario="Oferta valida",
        )

        postulacion = self.subasta_service.postular_a_carga(datos, onboarding_aprobado=True)
        self.assertIsNotNone(postulacion.id)

        # El contrato pasa automaticamente a EN_POSTULACION
        contrato_actualizado = self.leer_contrato_bd(contrato.id)
        self.assertIsNotNone(contrato_actualizado)
        assert contrato_actualizado is not None
        self.assertEqual(contrato_actualizado.estado, EstadoContrato.EN_POSTULACION)

    def test_postular_a_carga_expirada_sin_ofertas_declara_desierta_y_cancela(self) -> None:
        """Si la subasta expiro y no tiene ofertas, se declara desierta y transiciona a CANCELADO."""
        cierre_pasado = self.ahora - timedelta(minutes=10)
        contrato = self._crear_contrato(f_cierre=cierre_pasado)

        datos = PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=uuid4(),
            precio_oferta=80000.0,
            tiempo_entrega_horas=4.0,
            comentario="Oferta fuera de plazo",
        )

        with self.assertRaises(ValueError) as ctx:
            self.subasta_service.postular_a_carga(datos, onboarding_aprobado=True)

        self.assertIn("desierta", str(ctx.exception).lower())

        contrato_actualizado = self.leer_contrato_bd(contrato.id)
        self.assertIsNotNone(contrato_actualizado)
        assert contrato_actualizado is not None
        self.assertEqual(contrato_actualizado.estado, EstadoContrato.CANCELADO)

    def test_postular_a_carga_expirada_con_ofertas_previas_declara_cerrada(self) -> None:
        """Si la subasta expiro pero ya cuenta con ofertas previas, se declara cerrada."""
        cierre_futuro = self.ahora + timedelta(hours=1)
        contrato = self._crear_contrato(f_cierre=cierre_futuro)

        # 1. Postulacion valida dentro del plazo
        datos_1 = PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=uuid4(),
            precio_oferta=90000.0,
            tiempo_entrega_horas=5.0,
            comentario="Primera oferta valida",
        )
        self.subasta_service.postular_a_carga(datos_1, onboarding_aprobado=True)

        # 2. Simulamos el paso del tiempo cambiando f_cierre_postulaciones al pasado
        self._fijar_cierre(contrato.id, self.ahora - timedelta(minutes=5))

        # 3. Nueva postulacion fuera de plazo
        datos_2 = PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=uuid4(),
            precio_oferta=85000.0,
            tiempo_entrega_horas=4.5,
            comentario="Segunda oferta fuera de plazo",
        )
        with self.assertRaises(ValueError) as ctx:
            self.subasta_service.postular_a_carga(datos_2, onboarding_aprobado=True)

        self.assertIn("cerrada", str(ctx.exception).lower())

        # El contrato se mantiene en EN_POSTULACION (no cancelado) para permitir adjudicacion
        contrato_actualizado = self.leer_contrato_bd(contrato.id)
        self.assertIsNotNone(contrato_actualizado)
        assert contrato_actualizado is not None
        self.assertEqual(contrato_actualizado.estado, EstadoContrato.EN_POSTULACION)

    def test_verificar_expiracion_subasta_helper(self) -> None:
        """Comprueba el metodo auxiliar verificar_expiracion_subasta."""
        cierre_futuro = self.ahora + timedelta(hours=2)
        c_vigente = self._crear_contrato(f_cierre=cierre_futuro)
        self.assertEqual(self.subasta_service.verificar_expiracion_subasta(c_vigente.id), "VIGENTE")

        cierre_pasado = self.ahora - timedelta(hours=1)
        c_desierta = self._crear_contrato(f_cierre=cierre_pasado)
        self.assertEqual(self.subasta_service.verificar_expiracion_subasta(c_desierta.id), "DESIERTA")
        c_desierta_actualizado = self.leer_contrato_bd(c_desierta.id)
        self.assertIsNotNone(c_desierta_actualizado)
        assert c_desierta_actualizado is not None
        self.assertEqual(c_desierta_actualizado.estado, EstadoContrato.CANCELADO)

    def test_adjudicacion_permitida_despues_de_cierre_con_postulaciones(self) -> None:
        """Una vez cerrada la recepcion de ofertas, el dador puede adjudicar exitosamente."""
        cierre = self.ahora + timedelta(hours=1)
        contrato = self._crear_contrato(f_cierre=cierre)

        transp_id = uuid4()
        postulacion = self.subasta_service.postular_a_carga(
            PostulacionCrear(
                carga_id=contrato.id,
                transportista_id=transp_id,
                precio_oferta=75000.0,
                tiempo_entrega_horas=3.0,
                comentario="Oferta para adjudicacion",
            ),
            onboarding_aprobado=True,
        )

        # La subasta expira
        self._fijar_cierre(contrato.id, self.ahora - timedelta(minutes=10))

        # Adjudicar funciona correctamente
        adjudicada = self.subasta_service.adjudicar_subasta(contrato.id, postulacion.id)
        self.assertEqual(adjudicada.id, postulacion.id)

        contrato_final = self.leer_contrato_bd(contrato.id)
        self.assertIsNotNone(contrato_final)
        assert contrato_final is not None
        self.assertEqual(contrato_final.estado, EstadoContrato.ADJUDICADO)
        self.assertEqual(contrato_final.id_transportista, transp_id)


if __name__ == "__main__":
    unittest.main()
