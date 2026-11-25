"""Tests unitarios de la persistencia de contratos y postulaciones en SQLite."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from database.conexion import obtener_conexion
from domain.maquina_estados import EstadoContrato
from domain.modelos import ContratoModelo, Moneda, TipoCarga
from domain.postulacion import EstadoPostulacion, PostulacionCrear
from services.contrato_service import (
    actualizar_contrato,
    buscar_contrato,
    buscar_todos_los_contratos,
    guardar_contrato,
)
from services.subasta_service import ServicioSubasta
from tests.persistencia.base import BaseTestPersistencia


def _contrato(**cambios) -> ContratoModelo:
    ahora = datetime.now(UTC)
    datos = {
        "id": uuid4(),
        "id_empresa_generadora": uuid4(),
        "origen": "SANTIAGO",
        "destino": "VALPARAISO",
        "f_cierre_postulaciones": ahora + timedelta(hours=3),
        "f_estimada_salida": ahora + timedelta(hours=5),
        "f_estimada_llegada": ahora + timedelta(hours=10),
        "input_camionKG": 10000.0,
        "tipo_carga": TipoCarga.GENERAL,
        "peso_total": 5000.0,
        "monto_neto": 100000.0,
        "monto_iva": 19000.0,
        "monto_total": 119000.0,
        "estado": EstadoContrato.BORRADOR,
    }
    datos.update(cambios)
    return ContratoModelo(**datos)


class TestPersistenciaContratos(BaseTestPersistencia):
    """Pruebas dedicadas a guardar y recuperar contratos desde SQLite."""

    def _guardar(self, contrato: ContratoModelo) -> ContratoModelo:
        with obtener_conexion(self.db_path) as conn:
            return guardar_contrato(conn, contrato)

    def _buscar(self, contrato_id):
        with obtener_conexion(self.db_path) as conn:
            return buscar_contrato(conn, contrato_id)

    def test_guardar_y_obtener_contrato(self) -> None:
        contrato = _contrato()
        guardado = self._guardar(contrato)
        self.assertEqual(guardado.id, contrato.id)

        recuperado = self._buscar(contrato.id)
        self.assertIsNotNone(recuperado)
        with obtener_conexion(self.db_path) as conn:
            self.assertEqual(len(buscar_todos_los_contratos(conn)), 1)

    def test_ciclo_completo_conserva_todos_los_campos(self) -> None:
        contrato = _contrato(
            tipo_carga=TipoCarga.PELIGROSA,
            numero_onu="UN1234",
            volumen_m3=33.5,
            distancia_km=120.5,
            req_embalaje="Embalaje reforzado homologado",
            requiere_termo=True,
            req_blindaje=True,
            moneda=Moneda.CLP,
            estado=EstadoContrato.ADJUDICADO,
            id_transportista=uuid4(),
            id_camion=uuid4(),
            fecha_publicacion=datetime.now(UTC),
        )
        self._guardar(contrato)

        recuperado = self._buscar(contrato.id)
        assert recuperado is not None
        self.assertEqual(recuperado.model_dump(), contrato.model_dump())

    def test_campos_opcionales_vacios_se_recuperan_como_none(self) -> None:
        contrato = _contrato()
        self._guardar(contrato)
        recuperado = self._buscar(contrato.id)
        assert recuperado is not None
        self.assertIsNone(recuperado.volumen_m3)
        self.assertIsNone(recuperado.distancia_km)
        self.assertIsNone(recuperado.numero_onu)
        self.assertIsNone(recuperado.id_transportista)
        self.assertIsNone(recuperado.id_camion)
        self.assertIsNone(recuperado.fecha_publicacion)
        self.assertFalse(recuperado.requiere_termo)

    def test_obtener_inexistente_retorna_none(self) -> None:
        self.assertIsNone(self._buscar(uuid4()))

    def test_listar_en_orden_de_insercion(self) -> None:
        primero = self._guardar(_contrato(origen="ARICA", destino="IQUIQUE"))
        segundo = self._guardar(_contrato(origen="TEMUCO", destino="OSORNO"))
        tercero = self._guardar(_contrato(origen="CALAMA", destino="COPIAPO"))

        with obtener_conexion(self.db_path) as conn:
            ids = [c.id for c in buscar_todos_los_contratos(conn)]
        self.assertEqual(ids, [primero.id, segundo.id, tercero.id])

    def test_guardar_mismo_id_actualiza_en_lugar_de_duplicar(self) -> None:
        contrato = _contrato()
        self._guardar(contrato)
        contrato.estado = EstadoContrato.CANCELADO
        self._guardar(contrato)

        with obtener_conexion(self.db_path) as conn:
            todos = buscar_todos_los_contratos(conn)
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].estado, EstadoContrato.CANCELADO)

    def test_actualizar_contrato_existente_y_inexistente(self) -> None:
        contrato = self._guardar(_contrato())
        contrato.estado = EstadoContrato.PUBLICADO
        with obtener_conexion(self.db_path) as conn:
            self.assertIsNotNone(actualizar_contrato(conn, contrato.id, contrato))
            self.assertIsNone(actualizar_contrato(conn, uuid4(), contrato))
        recuperado = self._buscar(contrato.id)
        assert recuperado is not None
        self.assertEqual(recuperado.estado, EstadoContrato.PUBLICADO)

    def test_contrato_con_fechas_ya_vencidas_se_puede_leer(self) -> None:
        """Los datos persistidos no se revalidan: un contrato antiguo no debe romper la lectura."""
        contrato = self._guardar(_contrato())
        pasado = (datetime.now(UTC) - timedelta(days=30)).isoformat()
        with obtener_conexion(self.db_path) as conn:
            conn.execute(
                "UPDATE contratos SET f_estimada_salida = ?, f_cierre_postulaciones = ? WHERE id = ?",
                (pasado, pasado, str(contrato.id)),
            )
        recuperado = self._buscar(contrato.id)
        self.assertIsNotNone(recuperado)

    def test_datos_quedan_realmente_en_la_tabla_contratos(self) -> None:
        contrato = self._guardar(_contrato(origen="  santiago  "))
        filas = self.consultar("SELECT id, origen, estado, monto_total FROM contratos")
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["id"], str(contrato.id))
        self.assertEqual(filas[0]["origen"], "SANTIAGO")  # normalizado por el modelo
        self.assertEqual(filas[0]["estado"], "BORRADOR")
        self.assertEqual(filas[0]["monto_total"], 119000.0)


class TestPersistenciaPostulaciones(BaseTestPersistencia):
    """Pruebas dedicadas a la persistencia de postulaciones a traves de ServicioSubasta."""

    def setUp(self) -> None:
        super().setUp()
        self.servicio = ServicioSubasta(db_path=self.db_path)
        with obtener_conexion(self.db_path) as conn:
            self.carga = guardar_contrato(
                conn, _contrato(estado=EstadoContrato.PUBLICADO)
            )

    def _postular(self, precio: float, comentario: str | None = None):
        return self.servicio.postular_a_carga(
            PostulacionCrear(
                carga_id=self.carga.id,
                transportista_id=uuid4(),
                precio_oferta=precio,
                tiempo_entrega_horas=8.0,
                comentario=comentario,
            )
        )

    def test_guardar_y_listar_postulaciones_por_carga(self) -> None:
        post1 = self._postular(60000.0, comentario="Con termo")
        post2 = self._postular(55000.0)

        postulaciones = self.servicio.listar_postulaciones_carga(self.carga.id)
        self.assertEqual([p.id for p in postulaciones], [post1.id, post2.id])
        self.assertEqual(postulaciones[0].comentario, "Con termo")
        self.assertIsNone(postulaciones[1].comentario)
        self.assertEqual(postulaciones[0].precio_oferta, 60000.0)
        self.assertEqual(postulaciones[0].estado, EstadoPostulacion.POSTULADA)

    def test_postulaciones_de_otra_carga_no_se_mezclan(self) -> None:
        self._postular(60000.0)
        self.assertEqual(self.servicio.listar_postulaciones_carga(uuid4()), [])

    def test_datos_quedan_realmente_en_la_tabla_postulaciones(self) -> None:
        post = self._postular(70000.0)
        filas = self.consultar(
            "SELECT carga_id, precio_oferta, estado FROM postulaciones WHERE id = ?",
            (str(post.id),),
        )
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["carga_id"], str(self.carga.id))
        self.assertEqual(filas[0]["precio_oferta"], 70000.0)
        self.assertEqual(filas[0]["estado"], "POSTULADA")
