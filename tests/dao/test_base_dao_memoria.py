"""Tests unitarios para la clase genérica DAOMemoria y BaseDAO."""

from __future__ import annotations

from dao.base_dao import DAOMemoria
from tests.dao.base import BaseTestDAO


class TestBaseDAOMemoria(BaseTestDAO):
    """Pruebas dedicadas a las operaciones CRUD genéricas de persistencia en memoria."""

    def setUp(self) -> None:
        super().setUp()
        self.dao = DAOMemoria[dict, int](extractor_id=lambda item: item["id"])

    def test_guardar_y_obtener_por_id(self) -> None:
        item = {"id": 1, "nombre": "Camión Scania"}
        guardado = self.dao.guardar(item)
        self.assertEqual(guardado["id"], 1)

        recuperado = self.dao.obtener_por_id(1)
        self.assertEqual(recuperado, item)

    def test_obtener_por_id_no_existente_retorna_none(self) -> None:
        self.assertIsNone(self.dao.obtener_por_id(999))

    def test_obtener_todos(self) -> None:
        self.dao.guardar({"id": 1, "nombre": "A"})
        self.dao.guardar({"id": 2, "nombre": "B"})
        items = self.dao.obtener_todos()
        self.assertEqual(len(items), 2)

    def test_actualizar_item(self) -> None:
        self.dao.guardar({"id": 1, "nombre": "Original"})
        actualizado = self.dao.actualizar(1, {"id": 1, "nombre": "Modificado"})
        self.assertIsNotNone(actualizado)
        self.assertEqual(self.dao.obtener_por_id(1)["nombre"], "Modificado")

    def test_eliminar_item(self) -> None:
        self.dao.guardar({"id": 1, "nombre": "Por borrar"})
        self.assertTrue(self.dao.existe(1))
        borrado = self.dao.eliminar(1)
        self.assertTrue(borrado)
        self.assertFalse(self.dao.existe(1))
        self.assertFalse(self.dao.eliminar(1))  # Segunda vez retorna False

