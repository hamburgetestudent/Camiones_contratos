"""
Pruebas unitarias e integracion para el backend refactorizado.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from main import app
from domain.reglas import ReglasNegocio
from domain.maquina_estados import MaquinaEstadosContrato, EstadoContrato
from domain.postulacion import MaquinaEstadoPostulacion, EstadoPostulacion

client = TestClient(app)


def get_datos_contrato_validos():
    ahora = datetime.now(timezone.utc)
    return {
        "id_empresa_generadora": str(uuid4()),
        "origen": "Santiago Centro",
        "destino": "Valparaiso Puerto",
        "f_estimada_salida": (ahora + timedelta(hours=5)).isoformat(),
        "f_estimada_llegada": (ahora + timedelta(hours=10)).isoformat(),
        "f_cierre_postulaciones": (ahora + timedelta(hours=3)).isoformat(),
        "input_camionKG": 10000.0,
        "tipo_carga": "GENERAL",
        "peso_total": 5000.0,
        "volumen_m3": 20.0,
        "moneda": "CLP",
        "monto_neto": 100000.0,
        "monto_iva": 19000.0,
        "monto_total": 119000.0,
    }


def test_reglas_negocio_singleton():
    config1 = ReglasNegocio.obtener_configuracion()
    assert config1["iva_porcentaje"] == 0.19

    ReglasNegocio.actualizar_configuracion(iva_porcentaje=0.19)
    config2 = ReglasNegocio.obtener_configuracion()
    assert config2["iva_porcentaje"] == 0.19

    with pytest.raises(ValueError):
        ReglasNegocio.actualizar_configuracion(iva_porcentaje=1.5)


def test_maquina_estados_contrato():
    assert MaquinaEstadosContrato.validar_transicion(EstadoContrato.BORRADOR, EstadoContrato.PUBLICADO) is True
    assert MaquinaEstadosContrato.validar_transicion(EstadoContrato.BORRADOR, EstadoContrato.ENTREGADO) is False


def test_maquina_estados_postulacion():
    assert MaquinaEstadoPostulacion.validar_transicion(EstadoPostulacion.BORRADOR, EstadoPostulacion.POSTULADA) is True
    assert MaquinaEstadoPostulacion.validar_transicion(EstadoPostulacion.POSTULADA, EstadoPostulacion.SELECCIONADA) is True


def test_crear_y_obtener_contrato_api():
    payload = get_datos_contrato_validos()
    response = client.post("/contratos", json=payload)
    assert response.status_code == 201
    datos = response.json()
    assert datos["estado"] == "BORRADOR"
    contrato_id = datos["id"]

    response_get = client.get(f"/contratos/{contrato_id}")
    assert response_get.status_code == 200
    assert response_get.json()["id"] == contrato_id


def test_subasta_y_postulacion_flow():
    # 1. Crear contrato
    payload = get_datos_contrato_validos()
    res_contrato = client.post("/contratos", json=payload)
    contrato_id = res_contrato.json()["id"]

    # 2. Transicionar a PUBLICADO
    res_patch = client.patch(f"/contratos/{contrato_id}/estado", json={"nuevo_estado": "PUBLICADO"})
    assert res_patch.status_code == 200

    # 3. Postular a la carga
    postulante_id = str(uuid4())
    res_post = client.post("/subastas/postular", json={
        "carga_id": contrato_id,
        "transportista_id": postulante_id,
        "precio_oferta": 95000.0,
        "tiempo_entrega_horas": 4.5,
        "comentario": "Transporte rapido"
    })
    assert res_post.status_code == 201
    postulacion_id = res_post.json()["id"]

    # 4. Adjudicar subasta
    res_adj = client.post("/subastas/adjudicar", json={
        "carga_id": contrato_id,
        "postulacion_id": postulacion_id
    })
    assert res_adj.status_code == 200
    assert res_adj.json()["estado"] == "SELECCIONADA"

    # 5. Verificar que el contrato paso a ADJUDICADO
    res_check = client.get(f"/contratos/{contrato_id}")
    assert res_check.json()["estado"] == "ADJUDICADO"
    assert res_check.json()["id_transportista"] == postulante_id
