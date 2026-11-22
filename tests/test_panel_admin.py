"""Pruebas de integración del panel usando SQLite temporal y HTTP real."""

import json
import socket
import sqlite3
import threading
import time
from contextlib import closing
from datetime import UTC, datetime, timedelta
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import UUID, uuid4

import uvicorn

from database.conexion import inicializar_bd, obtener_conexion
from domain.maquina_estados import EstadoContrato
from main import app
from services import admin_service
from services.usuario_service import UsuarioService
from tests.subastas.base import BaseTestSubastas


class TestPanelAdmin(BaseTestSubastas):
    def setUp(self):
        super().setUp()
        inicializar_bd(self.db_path)
        self.actor = UsuarioService.obtener_usuario(UUID(int=1))

    def test_baja_solo_si_sigue_publicado_y_conserva_relaciones(self):
        for estado in EstadoContrato:
            contrato = self.crear_carga_publicada()
            self.forzar_estado_contrato(contrato.id, estado)
            with self.subTest(estado=estado):
                _, causa = admin_service.eliminar(
                    "contrato", contrato.id, self.actor, "Duplicado", True
                )
                self.assertEqual(causa is None, estado == EstadoContrato.PUBLICADO)
                with obtener_conexion() as conn:
                    fila = conn.execute(
                        "SELECT estado, eliminado FROM contratos WHERE id=?",
                        (str(contrato.id),),
                    ).fetchone()
                    self.assertEqual(tuple(fila), (estado.value, int(causa is None)))
                (evento,) = admin_service.historial(elemento_id=contrato.id)
                self.assertEqual(
                    evento["resultado"], "Rechazado" if causa else "Completado"
                )
                self.assertEqual(evento["administrador_id"], str(self.actor.id))

    def test_carga_eliminada_sale_de_subastas_pero_conserva_ofertas(self):
        carga = self.crear_carga_publicada()
        oferta = self.subasta_service.postular_a_carga(
            self.crear_dto_postulacion(carga.id)
        )
        # Fixture histórica: publicación con una oferta ya almacenada.
        self.forzar_estado_contrato(carga.id, EstadoContrato.PUBLICADO)
        admin_service.eliminar("contrato", carga.id, self.actor, "Duplicada", True)
        self.assertFalse(self.subasta_service.explorar_cargas())
        with self.assertRaises(ValueError):
            self.subasta_service.postular_a_carga(self.crear_dto_postulacion(carga.id))
        with self.assertRaises(ValueError):
            self.subasta_service.adjudicar_subasta(carga.id, oferta.id)
        inicializar_bd(self.db_path)
        with closing(sqlite3.connect(self.db_path)) as conn:
            self.assertEqual(
                conn.execute("SELECT id FROM postulaciones").fetchone()[0],
                str(oferta.id),
            )
        self.assertEqual(admin_service.listar_elementos("contrato"), [])
        self.assertEqual(
            admin_service.listar_elementos("contrato", True)[0]["eliminado"], 1
        )
        self.assertEqual(admin_service.resumen()["acciones"], 1)

    def test_fallo_de_auditoria_revierte_la_baja(self):
        contrato = self.crear_carga_publicada()
        with obtener_conexion() as conn:
            conn.execute("""CREATE TRIGGER impedir_registro BEFORE INSERT ON acciones_admin
                            BEGIN SELECT RAISE(ABORT, 'fallo simulado'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            admin_service.eliminar(
                "contrato", contrato.id, self.actor, "Duplicado", True
            )
        self.assertIsNotNone(self.leer_contrato_bd(contrato.id))
        self.assertFalse(admin_service.historial())

    def test_filtros_actividad_y_reintento(self):
        contrato = self.crear_carga_publicada()
        for motivo, confirmar in [
            (" ", True),
            ("Duplicada", False),
            ("Duplicada", True),
            ("Reintento", True),
        ]:
            admin_service.eliminar(
                "contrato", contrato.id, self.actor, motivo, confirmar
            )
        for _ in range(10):
            admin_service.eliminar(
                "cuenta", uuid4(), self.actor, "Cuenta inexistente", True
            )
        resumen = admin_service.resumen()
        self.assertEqual(
            (resumen["publicados"], resumen["activas"], resumen["acciones"]), (0, 5, 1)
        )
        self.assertEqual(resumen["recientes"], admin_service.historial()[:10])
        hoy = datetime.now(UTC).date()
        filtrado = admin_service.historial(
            hoy,
            hoy,
            self.actor.nombre,
            "eliminar_contrato",
            "Completado",
            "contrato",
            contrato.id,
        )
        self.assertEqual(len(filtrado), 1)
        self.assertFalse(admin_service.historial(hasta=hoy - timedelta(days=1)))
        self.assertEqual(
            len(
                admin_service.historial(resultado="Rechazado", elemento_id=contrato.id)
            ),
            3,
        )

    def test_http_permisos_revocacion_y_cierre_de_sesion(self):
        with closing(socket.socket()) as puerto:
            puerto.bind(("127.0.0.1", 0))
            base = f"http://127.0.0.1:{puerto.getsockname()[1]}"
            servidor = uvicorn.Server(
                uvicorn.Config(app, log_level="error", access_log=False)
            )
            hilo = threading.Thread(
                target=servidor.run, kwargs={"sockets": [puerto]}, daemon=True
            )
            hilo.start()
            try:
                for _ in range(100):
                    if servidor.started:
                        break
                    time.sleep(0.02)
                self.assertTrue(servidor.started)

                def solicitar(ruta, token=None, datos=None):
                    cabeceras = {"Content-Type": "application/json"}
                    if token:
                        cabeceras["Authorization"] = "Bearer " + token
                    req = Request(
                        base + ruta,
                        headers=cabeceras,
                        data=json.dumps(datos).encode() if datos is not None else None,
                    )
                    try:
                        with urlopen(req, timeout=3) as resp:
                            return resp.status, json.loads(resp.read() or b"null")
                    except HTTPError as error:
                        with error:
                            return error.code, json.load(error)

                def login(email, clave):
                    return solicitar(
                        "/auth/login", datos={"email": email, "password": clave}
                    )

                usuario = login("juan.perez@rutanorte.cl", "camion123")[1]
                token = usuario["access_token"]
                admin = login("admin@camiones.cl", "admin123")[1]["access_token"]
                self.assertEqual(solicitar("/admin/resumen")[0], 401)
                self.assertEqual(solicitar("/admin/historial", token)[0], 403)
                ruta = "/admin/elementos/cuenta/" + usuario["id"] + "/eliminar"
                self.assertEqual(
                    solicitar(ruta, token, {"motivo": "Prueba", "confirmado": True})[0],
                    403,
                )
                (intento,) = solicitar("/admin/historial", admin)[1]
                self.assertEqual(
                    (intento["resultado"], intento["administrador_id"]),
                    ("Rechazado", usuario["id"]),
                )
                self.assertIsNone(intento["anterior"])
                self.assertEqual(
                    solicitar(
                        ruta, admin, {"motivo": "Baja solicitada", "confirmado": True}
                    )[0],
                    200,
                )
                self.assertEqual(solicitar("/contratos", token)[0], 401)
                self.assertEqual(login("juan.perez@rutanorte.cl", "camion123")[0], 401)
                self.assertEqual(solicitar("/admin/resumen", admin)[1]["activas"], 4)
                self.assertEqual(solicitar("/auth/logout", admin, {})[0], 204)
                self.assertEqual(solicitar("/admin/resumen", admin)[0], 401)
            finally:
                servidor.should_exit = True
                hilo.join(5)
