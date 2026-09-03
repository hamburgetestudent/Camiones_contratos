"""Pruebas del login sin implementar la validación de credenciales."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.login_router import crear_login_router


class ValidadorFalso:
    """Simula únicamente la respuesta del módulo de otro compañero."""

    def __init__(self, resultado: bool) -> None:
        self.resultado = resultado
        self.usuario_recibido: str | None = None
        self.password_recibida: str | None = None

    def validar(self, usuario: str, password: str) -> bool:
        self.usuario_recibido = usuario
        self.password_recibida = password
        return self.resultado


def crear_cliente(resultado_validacion: bool) -> tuple[TestClient, ValidadorFalso]:
    validador = ValidadorFalso(resultado_validacion)
    app = FastAPI()
    app.include_router(crear_login_router(validador))
    return TestClient(app), validador


def test_login_exitoso() -> None:
    cliente, _ = crear_cliente(resultado_validacion=True)

    respuesta = cliente.post(
        "/auth/login",
        json={"usuario": "cristian", "password": "clave-del-usuario"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Inicio de sesión exitoso",
        "usuario": "cristian",
    }


def test_login_delega_usuario_y_password_al_validador() -> None:
    cliente, validador = crear_cliente(resultado_validacion=True)

    cliente.post(
        "/auth/login",
        json={"usuario": "cristian", "password": "mi-clave"},
    )

    assert validador.usuario_recibido == "cristian"
    assert validador.password_recibida == "mi-clave"


def test_login_rechazado_por_el_validador() -> None:
    cliente, _ = crear_cliente(resultado_validacion=False)

    respuesta = cliente.post(
        "/auth/login",
        json={"usuario": "cristian", "password": "incorrecta"},
    )

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detail": "Usuario o contraseña incorrectos"}


def test_login_requiere_usuario() -> None:
    cliente, _ = crear_cliente(resultado_validacion=True)

    respuesta = cliente.post(
        "/auth/login",
        json={"password": "mi-clave"},
    )

    assert respuesta.status_code == 422


def test_login_requiere_password() -> None:
    cliente, _ = crear_cliente(resultado_validacion=True)

    respuesta = cliente.post(
        "/auth/login",
        json={"usuario": "cristian"},
    )

    assert respuesta.status_code == 422


def test_integracion_registro_y_login_en_app_principal() -> None:
    from main import app
    from domain.modelos_usuario import RolUsuario
    
    cliente = TestClient(app)

    # 1. Registrar usuario
    email_test = "cristian_test@ejemplo.com"
    password_test = "password123"
    res_reg = cliente.post(
        "/auth/registro",
        json={
            "nombre": "Cristian Palma",
            "email": email_test,
            "password": password_test,
            "rol": RolUsuario.INDEPENDIENTE,
        },
    )
    assert res_reg.status_code == 200

    # 2. Login con credenciales correctas
    res_login_ok = cliente.post(
        "/auth/login",
        json={"usuario": email_test, "password": password_test},
    )
    assert res_login_ok.status_code == 200
    assert res_login_ok.json() == {
        "mensaje": "Inicio de sesión exitoso",
        "usuario": email_test,
    }

    # 3. Login con contraseña incorrecta
    res_login_fail = cliente.post(
        "/auth/login",
        json={"usuario": email_test, "password": "clave_equivocada"},
    )
    assert res_login_fail.status_code == 401

    # 4. Verificar que rutas de otros módulos siguen funcionando sin problemas
    res_config = cliente.get("/configuracion")
    assert res_config.status_code == 200

