"""Ejecuta el flujo integrado completo contra una base SQLite temporal y registra cada paso.

Uso (desde la raíz, con el entorno virtual activo)::

    python scripts/verificar_flujo_integrado.py

Corre tres casos sobre la API real (FastAPI + SQLite, sin simulaciones de servicios):
  1. Datos válidos: registro, login, contrato, publicación, postulación y adjudicación.
  2. Datos inválidos: se comprueba la respuesta de validación y que la base no cambie.
  3. Recurso ausente: contrato/carga inexistente y archivo de base de datos eliminado.

Termina con código 0 si todos los resultados obtenidos coinciden con los esperados.
No toca ``camiones.db``: usa un directorio temporal.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

_TMP = tempfile.TemporaryDirectory()
RUTA_BD = Path(_TMP.name) / "integracion.db"
os.environ["SQLITE_DB_PATH"] = str(RUTA_BD)

from fastapi.testclient import TestClient  # noqa: E402

from database.conexion import inicializar_bd  # noqa: E402
from main import app  # noqa: E402

REGISTRO: list[tuple[str, str, str, bool]] = []


def comprobar(paso: str, esperado: str, obtenido: str, ok: bool) -> None:
    REGISTRO.append((paso, esperado, obtenido, ok))
    print(f"[{'OK' if ok else 'FALLO'}] {paso}\n      esperado: {esperado}\n      obtenido: {obtenido}")


def contar(tabla: str) -> int:
    with closing(sqlite3.connect(RUTA_BD)) as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]  # noqa: S608


def id_usuario(email: str) -> str:
    with closing(sqlite3.connect(RUTA_BD)) as conn:
        return conn.execute("SELECT id FROM usuarios WHERE email=?", (email,)).fetchone()[0]


def contrato_json(**cambios) -> dict:
    ahora = datetime.now(UTC)
    base = {
        "id_empresa_generadora": id_usuario("contacto@logisticasur.cl"),
        "origen": "SANTIAGO",
        "destino": "CONCEPCION",
        "f_cierre_postulaciones": (ahora + timedelta(hours=3)).isoformat(),
        "f_estimada_salida": (ahora + timedelta(hours=6)).isoformat(),
        "f_estimada_llegada": (ahora + timedelta(hours=14)).isoformat(),
        "input_camionKG": 10000,
        "tipo_carga": "GENERAL",
        "peso_total": 5000,
        "distancia_km": 500,
        "moneda": "CLP",
        "monto_neto": 100000,
        "monto_iva": 19000,
        "monto_total": 119000,
    }
    base.update(cambios)
    return base


def login(cliente: TestClient, email: str, password: str) -> dict:
    r = cliente.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"} if r.status_code == 200 else {}


def caso_1_datos_validos(c: TestClient) -> None:
    print("\n== Caso 1: datos válidos ==")
    r = c.post("/auth/registro", json={"nombre": "Ana Prueba", "email": "ana@empresa.cl", "rol": "DADOR_CARGA", "password": "clave123"})
    comprobar("1.1 POST /auth/registro (correo válido)", "201", str(r.status_code), r.status_code == 201)
    h_dador = login(c, "contacto@logisticasur.cl", "dador123")
    comprobar("1.2 POST /auth/login (dador aprobado)", "200 + token Bearer", "token emitido" if h_dador else "sin token", bool(h_dador))
    r = c.post("/contratos", json=contrato_json(), headers=h_dador)
    ok = r.status_code == 201 and r.json().get("estado") == "BORRADOR"
    comprobar("1.3 POST /contratos", "201, estado BORRADOR", f"{r.status_code}, {r.json().get('estado')}", ok)
    cid = r.json()["id"]
    r = c.patch(f"/contratos/{cid}/estado", json={"nuevo_estado": "PUBLICADO"}, headers=h_dador)
    comprobar("1.4 PATCH estado → PUBLICADO", "200, PUBLICADO", f"{r.status_code}, {r.json().get('estado')}", r.status_code == 200 and r.json().get("estado") == "PUBLICADO")
    r = c.get("/subastas/cargas", headers=h_dador)
    visible = any(x["id"] == cid for x in r.json())
    comprobar("1.5 GET /subastas/cargas", "la carga aparece publicada", "aparece" if visible else "no aparece", visible)
    h_trans = login(c, "juan.perez@rutanorte.cl", "camion123")
    r = c.post("/subastas/postular", json={"carga_id": cid, "transportista_id": id_usuario("juan.perez@rutanorte.cl"), "precio_oferta": 110000, "tiempo_entrega_horas": 8}, headers=h_trans)
    comprobar("1.6 POST /subastas/postular", "201, POSTULADA", f"{r.status_code}, {r.json().get('estado')}", r.status_code == 201 and r.json().get("estado") == "POSTULADA")
    pid = r.json()["id"]
    r = c.post("/subastas/adjudicar", json={"carga_id": cid, "postulacion_id": pid}, headers=h_dador)
    comprobar("1.7 POST /subastas/adjudicar", "200, postulación SELECCIONADA", f"{r.status_code}, {r.json().get('estado')}", r.status_code == 200 and r.json().get("estado") == "SELECCIONADA")
    r = c.get(f"/contratos/{cid}", headers=h_dador)
    comprobar("1.8 GET /contratos/{id}", "ADJUDICADO", str(r.json().get("estado")), r.json().get("estado") == "ADJUDICADO")


def caso_2_datos_invalidos(c: TestClient) -> None:
    print("\n== Caso 2: datos inválidos ==")
    h_dador = login(c, "contacto@logisticasur.cl", "dador123")
    antes_u, antes_c = contar("usuarios"), contar("contratos")
    r = c.post("/auth/registro", json={"nombre": "Ana", "email": "ana@@empresa.cl", "rol": "DADOR_CARGA", "password": "clave123"})
    comprobar("2.1 POST /auth/registro (correo ana@@empresa.cl)", "422", str(r.status_code), r.status_code == 422)
    r = c.post("/contratos", json=contrato_json(monto_total=500000), headers=h_dador)
    comprobar("2.2 POST /contratos (neto + IVA ≠ total)", "400/422", str(r.status_code), r.status_code in (400, 422))
    r = c.post("/contratos", json=contrato_json(peso_total=20000), headers=h_dador)
    comprobar("2.3 POST /contratos (peso > capacidad del camión)", "400/422", str(r.status_code), r.status_code in (400, 422))
    r = c.post("/auth/login", json={"email": "contacto@logisticasur.cl", "password": "incorrecta"})
    comprobar("2.4 POST /auth/login (clave errónea)", "401", str(r.status_code), r.status_code == 401)
    despues_u, despues_c = contar("usuarios"), contar("contratos")
    comprobar("2.5 Estado conservado", f"usuarios={antes_u}, contratos={antes_c}", f"usuarios={despues_u}, contratos={despues_c}", (antes_u, antes_c) == (despues_u, despues_c))


def caso_3_recurso_ausente(c: TestClient) -> None:
    print("\n== Caso 3: recurso ausente ==")
    h_dador = login(c, "contacto@logisticasur.cl", "dador123")
    h_trans = login(c, "juan.perez@rutanorte.cl", "camion123")
    inexistente = "00000000-0000-4000-8000-000000000000"
    r = c.get(f"/contratos/{inexistente}", headers=h_dador)
    comprobar("3.1 GET /contratos/{id inexistente}", "404", str(r.status_code), r.status_code == 404)
    r = c.post("/subastas/postular", json={"carga_id": inexistente, "transportista_id": id_usuario("juan.perez@rutanorte.cl"), "precio_oferta": 110000, "tiempo_entrega_horas": 8}, headers=h_trans)
    comprobar("3.2 POST /subastas/postular (carga inexistente)", "404", str(r.status_code), r.status_code == 404)
    r = c.get("/contratos")  # sin token: el recurso "sesión" falta
    comprobar("3.3 GET protegido sin token", "401/403", str(r.status_code), r.status_code in (401, 403))
    c.close()
    RUTA_BD.unlink()
    r = TestClient(app).post("/auth/login", json={"email": "contacto@logisticasur.cl", "password": "dador123"})
    comprobar("3.4 Archivo .db eliminado en caliente → login", "401 (BD recreada vacía, sin caída del servidor)", str(r.status_code), r.status_code == 401)
    comprobar("3.5 La BD se recrea con su esquema", "archivo existe de nuevo", "existe" if RUTA_BD.exists() else "no existe", RUTA_BD.exists())


def main() -> int:
    inicializar_bd(RUTA_BD, cargar_semilla=True)
    c = TestClient(app)
    caso_1_datos_validos(c)
    caso_2_datos_invalidos(c)
    caso_3_recurso_ausente(c)
    fallos = [r for r in REGISTRO if not r[3]]
    print(f"\nResumen: {len(REGISTRO) - len(fallos)}/{len(REGISTRO)} comprobaciones OK")
    return 1 if fallos else 0


if __name__ == "__main__":
    codigo = main()
    _TMP.cleanup()
    sys.exit(codigo)
