from datetime import datetime, timezone, timedelta
from uuid import uuid4
from fastapi.testclient import TestClient
from main import app

cliente = TestClient(app)

def test_configuracion_endpoints():
    # Test GET configuracion
    res = cliente.get("/configuracion")
    assert res.status_code == 200
    data = res.json()
    assert "iva_porcentaje" in data
    assert "tolerancia_max" in data
    assert "anticipacion_min_h" in data

    # Test PATCH configuracion
    res_patch = cliente.patch("/configuracion", json={"iva_porcentaje": 0.19})
    assert res_patch.status_code == 200
    assert res_patch.json()["iva_porcentaje"] == 0.19


def test_contratos_endpoints():
    # Test GET contratos inicial (vacio o lista)
    res_list = cliente.get("/contratos")
    assert res_list.status_code == 200
    assert isinstance(res_list.json(), list)

    # Test POST contrato
    ahora = datetime.now(timezone.utc)
    salida = ahora + timedelta(hours=5)
    cierre = ahora + timedelta(hours=3)
    llegada = ahora + timedelta(hours=10)

    payload_contrato = {
        "id_empresa_generadora": str(uuid4()),
        "origen": "Valparaiso",
        "destino": "Santiago",
        "f_estimada_salida": salida.isoformat(),
        "f_estimada_llegada": llegada.isoformat(),
        "f_cierre_postulaciones": cierre.isoformat(),
        "input_camionKG": 2000.0,
        "tipo_carga": "GENERAL",
        "peso_total": 1500.0,
        "volumen_m3": 10.0,
        "monto_neto": 100000.0,
        "monto_iva": 19000.0,
        "monto_total": 119000.0,
    }

    res_crear = cliente.post("/contratos", json=payload_contrato)
    assert res_crear.status_code == 201
    contrato = res_crear.json()
    assert contrato["estado"] == "BORRADOR"
    contrato_id = contrato["id"]

    # Test GET contrato by id
    res_get = cliente.get(f"/contratos/{contrato_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == contrato_id
