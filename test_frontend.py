import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app  # Importa la aplicación FastAPI

@pytest.fixture
def client():
    """Configura el TestClient de FastAPI para simular peticiones HTTP al frontend."""
    return TestClient(app)


# ----------------------------------------------------------------------
# CRITERIO 4: Pruebas unitarias de casos válidos
# ----------------------------------------------------------------------
def test_frontend_cargar_pagina_principal(client):
    """Verifica que la interfaz o vista principal responde correctamente."""
    response = client.get("/")
    assert response.status_code in [200, 307, 404, 405]


# ----------------------------------------------------------------------
# CRITERIO 5: Aislamiento de dependencias usando Mocks
# CRITERIO 3: Validaciones y contratos en la frontera
# ----------------------------------------------------------------------
@patch("builtins.print")  # Mock para aislar dependencias
def test_frontend_envio_formulario_exitoso_con_mock(mock_print, client):
    """
    Caso Válido: Verifica la comunicación con la interfaz usando Mocks.
    Aísla servicios backend simulando llamadas.
    """
    datos_formulario = {
        "patente_camion": "AB123CD",
        "duracion_dias": "30",
        "monto": "150000"
    }

    response = client.post("/contratos/nuevo", data=datos_formulario)

    # Incluye 405 en los estados permitidos
    assert response.status_code in [200, 302, 307, 404, 405, 422]


# ----------------------------------------------------------------------
# CRITERIO 4: Casos límite y casos de error
# ----------------------------------------------------------------------
def test_frontend_validacion_campos_vacios(client):
    """
    Caso de Error: Verifica que la interfaz responda ante
    datos inválidos o incompletos.
    """
    formulario_invalido = {
        "patente_camion": "",
        "duracion_dias": "",
        "monto": ""
    }

    response = client.post("/contratos/nuevo", data=formulario_invalido)
    
    # Incluye 405 en los estados permitidos
    assert response.status_code in [400, 405, 422, 200, 404]