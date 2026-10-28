"""Tests unitarios dedicados a validaciones Pydantic de modelos de Usuario."""

from __future__ import annotations

from pydantic import ValidationError
from domain.modelos_usuario import RolUsuario, UsuarioCrear
from tests.usuarios.base import BaseTestUsuarios


class TestModelosUsuario(BaseTestUsuarios):
    """Pruebas dedicadas a las validaciones de esquemas de usuario (CA-03, CA-04, CA-05)."""

    def test_normalizacion_de_alias_de_rol(self) -> None:
        dto_indep = self.crear_dto_transportista_valido()
        dto_indep.rol = "INDEPENDIENTE"  # Alias
        val = UsuarioCrear(nombre="Test", email="test@test.cl", rol="INDEPENDIENTE", password="password123")
        self.assertEqual(val.rol, RolUsuario.TRANSPORTISTA)

        dto_empresa = UsuarioCrear(nombre="Emp", email="emp@test.cl", rol="EMPRESA", password="password123")
        self.assertEqual(dto_empresa.rol, RolUsuario.DADOR_CARGA)

    def test_rechazo_password_corta_menos_de_6_caracteres(self) -> None:
        with self.assertRaises(ValidationError):
            UsuarioCrear(nombre="Test", email="test@test.cl", rol=RolUsuario.TRANSPORTISTA, password="12345")

    def test_rechazo_email_formato_invalido(self) -> None:
        emails_invalidos = ["sin_arroba.cl", "espacios en@correo.cl", "@sin_usuario.cl", "correo@"]
        for email in emails_invalidos:
            with self.assertRaises(ValidationError):
                UsuarioCrear(nombre="Test", email=email, rol=RolUsuario.TRANSPORTISTA, password="password123")