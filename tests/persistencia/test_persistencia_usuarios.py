"""Tests unitarios de la persistencia de usuarios (SQL directo en usuario_service)."""

from __future__ import annotations

from uuid import uuid4

from database.conexion import obtener_conexion
from domain.modelos_usuario import EstadoUsuario, RolUsuario, UsuarioModelo
from services.usuario_service import (
    buscar_todos_los_usuarios,
    buscar_usuario_por_email,
    buscar_usuario_por_id,
    guardar_usuario,
)
from tests.persistencia.base import BaseTestPersistencia


class TestPersistenciaUsuarios(BaseTestPersistencia):
    """Pruebas dedicadas a las operaciones de persistencia de usuarios en SQLite."""

    def _guardar(self, usuario: UsuarioModelo) -> UsuarioModelo:
        with obtener_conexion(self.db_path) as conn:
            return guardar_usuario(conn, usuario)

    def test_guardar_y_obtener_por_id(self) -> None:
        user = UsuarioModelo(
            id=uuid4(),
            nombre="Juan Chofer",
            email="juan.chofer@transporte.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password_hash="hash_secreto_123",
            estado=EstadoUsuario.APROBADO,
        )
        guardado = self._guardar(user)
        self.assertEqual(guardado.id, user.id)

        with obtener_conexion(self.db_path) as conn:
            recuperado = buscar_usuario_por_id(conn, user.id)
        self.assertIsNotNone(recuperado)
        assert recuperado is not None
        self.assertEqual(recuperado.nombre, "Juan Chofer")
        self.assertEqual(recuperado.email, "juan.chofer@transporte.cl")
        self.assertEqual(recuperado.rol, RolUsuario.TRANSPORTISTA)
        self.assertEqual(recuperado.estado, EstadoUsuario.APROBADO)

    def test_obtener_por_id_inexistente_retorna_none(self) -> None:
        with obtener_conexion(self.db_path) as conn:
            self.assertIsNone(buscar_usuario_por_id(conn, uuid4()))

    def test_obtener_por_email_insensible_a_mayusculas(self) -> None:
        user = UsuarioModelo(
            id=uuid4(),
            nombre="Pedro Pérez",
            email="pedro@empresa.cl",
            rol=RolUsuario.DADOR_CARGA,
            password_hash="hash_456",
            estado=EstadoUsuario.EN_REVISION,
        )
        self._guardar(user)

        with obtener_conexion(self.db_path) as conn:
            recuperado = buscar_usuario_por_email(conn, "  PEDRO@EMPRESA.CL ")
        self.assertIsNotNone(recuperado)
        assert recuperado is not None
        self.assertEqual(recuperado.id, user.id)

    def test_guardar_mismo_id_actualiza_en_lugar_de_duplicar(self) -> None:
        user = UsuarioModelo(
            nombre="U1",
            email="u1@test.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password_hash="h1",
        )
        self._guardar(user)
        user.estado = EstadoUsuario.APROBADO
        self._guardar(user)

        with obtener_conexion(self.db_path) as conn:
            todos = buscar_todos_los_usuarios(conn)
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].estado, EstadoUsuario.APROBADO)

    def test_obtener_todos_en_orden_de_creacion(self) -> None:
        for nombre, correo, rol in (
            ("U1", "u1@test.cl", RolUsuario.TRANSPORTISTA),
            ("U2", "u2@test.cl", RolUsuario.DADOR_CARGA),
        ):
            self._guardar(
                UsuarioModelo(nombre=nombre, email=correo, rol=rol, password_hash="h")
            )
        with obtener_conexion(self.db_path) as conn:
            todos = buscar_todos_los_usuarios(conn)
        self.assertEqual([u.nombre for u in todos], ["U1", "U2"])

    def test_el_correo_se_guarda_en_minusculas(self) -> None:
        self._guardar(
            UsuarioModelo(
                nombre="Mayus",
                email="Mayus@Test.CL",
                rol=RolUsuario.TRANSPORTISTA,
                password_hash="h",
            )
        )
        filas = self.consultar("SELECT email FROM usuarios")
        self.assertEqual(filas[0]["email"], "mayus@test.cl")
