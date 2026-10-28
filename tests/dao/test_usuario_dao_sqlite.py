"""Tests unitarios dedicados a la clase UsuarioDAOSQLite."""

from __future__ import annotations

from uuid import uuid4
from dao.usuario_dao import UsuarioDAOSQLite
from domain.modelos_usuario import EstadoUsuario, RolUsuario, UsuarioModelo
from tests.dao.base import BaseTestDAO


class TestUsuarioDAOSQLite(BaseTestDAO):
    """Pruebas dedicadas a las operaciones de persistencia de usuarios en SQLite."""

    def setUp(self) -> None:
        super().setUp()
        self.usuario_dao = UsuarioDAOSQLite(db_path=self.db_path, cargar_semilla=False)

    def test_guardar_y_obtener_por_id(self) -> None:
        user = UsuarioModelo(
            id=uuid4(),
            nombre="Juan Chofer",
            email="juan.chofer@transporte.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password_hash="hash_secreto_123",
            estado=EstadoUsuario.APROBADO,
        )
        guardado = self.usuario_dao.guardar(user)
        self.assertEqual(guardado.id, user.id)

        recuperado = self.usuario_dao.obtener_por_id(user.id)
        self.assertIsNotNone(recuperado)
        assert recuperado is not None
        self.assertEqual(recuperado.nombre, "Juan Chofer")
        self.assertEqual(recuperado.email, "juan.chofer@transporte.cl")

    def test_obtener_por_email_insensible_a_mayusculas(self) -> None:
        user = UsuarioModelo(
            id=uuid4(),
            nombre="Pedro Pérez",
            email="pedro@empresa.cl",
            rol=RolUsuario.DADOR_CARGA,
            password_hash="hash_456",
            estado=EstadoUsuario.EN_REVISION,
        )
        self.usuario_dao.guardar(user)

        recuperado = self.usuario_dao.obt_por_email("PEDRO@EMPRESA.CL")
        self.assertIsNotNone(recuperado)
        assert recuperado is not None
        self.assertEqual(recuperado.id, user.id)

    def test_obtener_todos(self) -> None:
        self.usuario_dao.guardar(UsuarioModelo(nombre="U1", email="u1@test.cl", rol=RolUsuario.TRANSPORTISTA, password_hash="h1"))
        self.usuario_dao.guardar(UsuarioModelo(nombre="U2", email="u2@test.cl", rol=RolUsuario.DADOR_CARGA, password_hash="h2"))
        todos = self.usuario_dao.obtener_todos()
        self.assertEqual(len(todos), 2)

    def test_eliminar_usuario(self) -> None:
        user = UsuarioModelo(nombre="U3", email="u3@test.cl", rol=RolUsuario.TRANSPORTISTA, password_hash="h3")
        self.usuario_dao.guardar(user)
        self.assertTrue(self.usuario_dao.eliminar(user.id))
        self.assertIsNone(self.usuario_dao.obtener_por_id(user.id))

