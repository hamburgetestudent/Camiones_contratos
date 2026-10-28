"""Tests de endpoints del router de configuración."""

from __future__ import annotations

from fastapi import HTTPException
from routers.config_router import ActualizarConfiguracionNegocio, actualizar_configuracion, get_configuracion
from tests.configuracion.base import BaseTestConfiguracion


class TestRouterConfiguracion(BaseTestConfiguracion):
    """Pruebas dedicadas a las funciones endpoint de routers/config_router.py."""

    def test_get_configuracion_endpoint(self) -> None:
        respuesta = get_configuracion()
        self.assertEqual(respuesta["iva_porcentaje"], 0.19)

    def test_actualizar_configuracion_endpoint_exitoso(self) -> None:
        payload = ActualizarConfiguracionNegocio(iva_porcentaje=0.21, tolerancia_max=0.02)
        respuesta = actualizar_configuracion(payload)
        self.assertEqual(respuesta["iva_porcentaje"], 0.21)
        self.assertEqual(respuesta["tolerancia_max"], 0.02)

    def test_actualizar_configuracion_endpoint_error_negativo(self) -> None:
        # Pydantic valida ge=0, pero si llega un error a ReglasNegocio se traduce en HTTPException
        with self.assertRaises(HTTPException) as ctx:
            actualizar_configuracion(ActualizarConfiguracionNegocio.model_construct(iva_porcentaje=-0.1))
        self.assertEqual(ctx.exception.status_code, 400)

