"""Tests unitarios dedicados a la función hash_password."""

from __future__ import annotations

import hashlib
from services.usuario_service import hash_password
from tests.usuarios.base import BaseTestUsuarios


class TestHashPassword(BaseTestUsuarios):
    """Pruebas dedicadas exclusivamente a la función hash_password."""

    def test_hashing_determinista_sha256(self) -> None:
        pwd = "miPasswordSecreta99"
        esperado = hashlib.sha256(pwd.encode()).hexdigest()
        self.assertEqual(hash_password(pwd), esperado)

    def test_passwords_distintas_producen_hashes_distintos(self) -> None:
        self.assertNotEqual(hash_password("clave1"), hash_password("clave2"))

    def test_password_vacia(self) -> None:
        self.assertEqual(hash_password(""), hashlib.sha256(b"").hexdigest())