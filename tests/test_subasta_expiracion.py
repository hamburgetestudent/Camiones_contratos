"""Pruebas unitarias para el cierre automatico por expiracion de subastas."""

from datetime import UTC, datetime, timedelta
import unittest
from uuid import UUID, uuid4

from dao.contrato_dao import ContratoDAOMemoria
from dao.postulacion_dao import PostulacionDAOMemoria
from domain.maquina_estados import EstadoContrato
from domain.modelos import ContratoModelo, Moneda, TipoCarga
from domain.postulacion import PostulacionCrear
from services.subasta_service import ServicioSubasta


class TestSubastaExpiracion(unittest.TestCase):
    """Conjunto de pruebas para expiracion de subastas en postular_a_carga."""

    def setUp(self) -> None:
        self.contrato_dao = ContratoDAOMemoria()
        self.postulacion_dao = PostulacionDAOMemoria()
        self.servicio = ServicioSubasta(
            contrato_dao=self.contrato_dao,
            postulacion_dao=self.postulacion_dao,
        )

        self.ahora = datetime.now(UTC)
        self.salida = self.ahora + timedelta(hours=5)
        self.llegada = self.ahora + timedelta(hours=10)

    def _crear_contrato(
        self,
        f_cierre: datetime,
        estado: EstadoContrato = EstadoContrato.PUBLICADO,
        origen: str = "Santiago",
        destino: str = "Valparaiso",
        peso_total: float = 5000.0,
        input_camionKG: float = 10000.0,
        tipo_carga: TipoCarga = TipoCarga.GENERAL,
        monto_neto: float = 100000.0,
        id_empresa_generadora: UUID | None = None,
        volumen_m3: float | None = 30.0,
        distancia_km: float | None = 120.0,
        requiere_termo: bool = False,
        numero_onu: str | None = None,
        req_embalaje: str | None = None,
        req_blindaje: bool = False,
        moneda: Moneda = Moneda.CLP,
    ) -> ContratoModelo:
        monto_iva = round(monto_neto * 0.19, 2)
        monto_total = round(monto_neto + monto_iva, 2)
        contrato = ContratoModelo(
            id=uuid4(),
            id_empresa_generadora=id_empresa_generadora or uuid4(),
            origen=origen,
            destino=destino,
            f_estimada_salida=self.salida,
            f_estimada_llegada=self.llegada,
            f_cierre_postulaciones=f_cierre,
            input_camionKG=input_camionKG,
            tipo_carga=tipo_carga,
            peso_total=peso_total,
            volumen_m3=volumen_m3,
            distancia_km=distancia_km,
            requiere_termo=requiere_termo,
            numero_onu=numero_onu,
            req_embalaje=req_embalaje,
            req_blindaje=req_blindaje,
            moneda=moneda,
            monto_neto=monto_neto,
            monto_iva=monto_iva,
            monto_total=monto_total,
            estado=estado,
            id_transportista=None,
            id_camion=None,
            fecha_publicacion=self.ahora if estado in (EstadoContrato.PUBLICADO, EstadoContrato.EN_SUBASTA, EstadoContrato.EN_POSTULACION) else None,
        )
        self.contrato_dao.guardar(contrato)
        return contrato

    def test_postular_a_carga_vigente_exitosa(self) -> None:
        """Una postulacion dentro del plazo vigente debe aceptarse correctamente."""
        cierre_futuro = self.ahora + timedelta(hours=2)
        contrato = self._crear_contrato(f_cierre=cierre_futuro, estado=EstadoContrato.PUBLICADO)

        datos = PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=uuid4(),
            precio_oferta=80000.0,
            tiempo_entrega_horas=4.0,
            comentario="Oferta valida",
        )

        postulacion = self.servicio.postular_a_carga(datos, onboarding_aprobado=True)
        self.assertIsNotNone(postulacion.id)

        # El contrato pasa automaticamente a EN_POSTULACION
        contrato_actualizado = self.contrato_dao.obtener_por_id(contrato.id)
        self.assertIsNotNone(contrato_actualizado)
        assert contrato_actualizado is not None
        self.assertEqual(contrato_actualizado.estado, EstadoContrato.EN_POSTULACION)

    def test_postular_a_carga_expirada_sin_ofertas_declara_desierta_y_cancela(self) -> None:
        """Si la subasta expiro y no tiene ofertas, se declara desierta y transiciona a CANCELADO."""
        cierre_pasado = self.ahora - timedelta(minutes=10)
        contrato = self._crear_contrato(f_cierre=cierre_pasado, estado=EstadoContrato.PUBLICADO)

        datos = PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=uuid4(),
            precio_oferta=80000.0,
            tiempo_entrega_horas=4.0,
            comentario="Oferta fuera de plazo",
        )

        with self.assertRaises(ValueError) as ctx:
            self.servicio.postular_a_carga(datos, onboarding_aprobado=True)

        self.assertIn("desierta", str(ctx.exception).lower())

        contrato_actualizado = self.contrato_dao.obtener_por_id(contrato.id)
        self.assertIsNotNone(contrato_actualizado)
        assert contrato_actualizado is not None
        self.assertEqual(contrato_actualizado.estado, EstadoContrato.CANCELADO)

    def test_postular_a_carga_expirada_con_ofertas_previas_declara_cerrada(self) -> None:
        """Si la subasta expiro pero ya cuenta con ofertas previas, se declara cerrada."""
        cierre_futuro = self.ahora + timedelta(hours=1)
        contrato = self._crear_contrato(f_cierre=cierre_futuro, estado=EstadoContrato.PUBLICADO)

        # 1. Postulacion valida dentro del plazo
        datos_1 = PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=uuid4(),
            precio_oferta=90000.0,
            tiempo_entrega_horas=5.0,
            comentario="Primera oferta valida",
        )
        self.servicio.postular_a_carga(datos_1, onboarding_aprobado=True)

        # 2. Simulamos el paso del tiempo cambiando f_cierre_postulaciones al pasado
        contrato.f_cierre_postulaciones = self.ahora - timedelta(minutes=5)
        self.contrato_dao.actualizar(contrato.id, contrato)

        # 3. Nueva postulacion fuera de plazo
        datos_2 = PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=uuid4(),
            precio_oferta=85000.0,
            tiempo_entrega_horas=4.5,
            comentario="Segunda oferta fuera de plazo",
        )
        with self.assertRaises(ValueError) as ctx:
            self.servicio.postular_a_carga(datos_2, onboarding_aprobado=True)

        self.assertIn("cerrada", str(ctx.exception).lower())

        # El contrato se mantiene en EN_POSTULACION (no cancelado) para permitir adjudicacion
        contrato_actualizado = self.contrato_dao.obtener_por_id(contrato.id)
        self.assertIsNotNone(contrato_actualizado)
        assert contrato_actualizado is not None
        self.assertEqual(contrato_actualizado.estado, EstadoContrato.EN_POSTULACION)

    def test_verificar_expiracion_subasta_helper(self) -> None:
        """Comprueba el metodo auxiliar verificar_expiracion_subasta."""
        cierre_futuro = self.ahora + timedelta(hours=2)
        c_vigente = self._crear_contrato(f_cierre=cierre_futuro)
        self.assertEqual(self.servicio.verificar_expiracion_subasta(c_vigente.id), "VIGENTE")

        cierre_pasado = self.ahora - timedelta(hours=1)
        c_desierta = self._crear_contrato(f_cierre=cierre_pasado)
        self.assertEqual(self.servicio.verificar_expiracion_subasta(c_desierta.id), "DESIERTA")
        c_desierta_actualizado = self.contrato_dao.obtener_por_id(c_desierta.id)
        self.assertIsNotNone(c_desierta_actualizado)
        assert c_desierta_actualizado is not None
        self.assertEqual(c_desierta_actualizado.estado, EstadoContrato.CANCELADO)

    def test_adjudicacion_permitida_despues_de_cierre_con_postulaciones(self) -> None:
        """Una vez cerrada la recepcion de ofertas, el dador puede adjudicar exitosamente."""
        cierre = self.ahora + timedelta(hours=1)
        contrato = self._crear_contrato(f_cierre=cierre)

        transp_id = uuid4()
        postulacion = self.servicio.postular_a_carga(
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
        contrato.f_cierre_postulaciones = self.ahora - timedelta(minutes=10)
        self.contrato_dao.actualizar(contrato.id, contrato)

        # Adjudicar funciona correctamente
        adjudicada = self.servicio.adjudicar_subasta(contrato.id, postulacion.id)
        self.assertEqual(adjudicada.id, postulacion.id)

        contrato_final = self.contrato_dao.obtener_por_id(contrato.id)
        self.assertIsNotNone(contrato_final)
        assert contrato_final is not None
        self.assertEqual(contrato_final.estado, EstadoContrato.ADJUDICADO)
        self.assertEqual(contrato_final.id_transportista, transp_id)


if __name__ == "__main__":
    unittest.main()