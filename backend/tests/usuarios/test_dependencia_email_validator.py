"""Evidencia de integración de la dependencia externa email-validator."""

import unittest
from importlib.metadata import version

from pydantic import ValidationError

from app.modules.usuarios.models import RolUsuario, UsuarioBase


class TestEmailValidator(unittest.TestCase):
    def _crear(self, email: str) -> UsuarioBase:
        return UsuarioBase(nombre="Ana", email=email, rol=RolUsuario.DADOR_CARGA)

    def test_version_fijada(self) -> None:
        self.assertGreaterEqual(int(version("email-validator").split(".")[0]), 2)

    def test_acepta_correo_valido(self) -> None:
        self.assertEqual(self._crear("ana@empresa.cl").email, "ana@empresa.cl")

    def test_rechaza_formatos_invalidos(self) -> None:
        for correo in ("ana@@empresa.cl", "ana@empresa", "ana perez@empresa.cl", "a..b@empresa.cl"):
            with self.subTest(correo=correo), self.assertRaises(ValidationError):
                self._crear(correo)

    def test_requirements_acota_version_mayor(self) -> None:
        """Mitigación: requirements.txt impide saltar a una versión mayor sin revisión."""
        from pathlib import Path

        texto = (Path(__file__).resolve().parents[3] / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("email-validator>=2.2.0,<3", texto)
