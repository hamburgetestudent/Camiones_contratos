"""Base global para la suite de pruebas del proyecto Camiones_contratos.

Provee la clase BaseTestCase con utilidades de aserción, manejo de excepciones
y aislamiento de recursos para pruebas unitarias e integración.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from fastapi import HTTPException


class BaseTestCase(unittest.TestCase):
    """Clase base raíz para todos los tests del proyecto.s,
    manejo de excepciones HTTP y aislamiento de directorios temporales.
    """

    def setUp(self) -> None:
        super().setUp()
        self._temp_dirs: list[tempfile.TemporaryDirectory[str]] = []

    def tearDown(self) -> None:
        for temp_dir in self._temp_dirs:
            try:
                temp_dir.cleanup()
            except OSError:
                pass
        self._temp_dirs.clear()
        super().tearDown()

    def crear_directorio_temporal(self) -> Path:
        """Crea un directorio temporal que se limpiará automáticamente en tearDown."""
        td = tempfile.TemporaryDirectory()
        self._temp_dirs.append(td)
        return Path(td.name)

    def assertHttpException(  # noqa: N802
        self,
        status_code: int,
        detalle_esperado: str | None = None,
    ):
        """Context manager para verificar que una llamada lance HTTPException con código y detalle esperados."""
        return _AssertHttpExceptionContext(self, status_code, detalle_esperado)


class _AssertHttpExceptionContext:
    def __init__(
        self,
        test_case: unittest.TestCase,
        expected_status: int,
        expected_detail: str | None = None,
    ) -> None:
        self.test_case = test_case
        self.expected_status = expected_status
        self.expected_detail = expected_detail
        self.exception: HTTPException | None = None

    def __enter__(self) -> _AssertHttpExceptionContext:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_type is None:
            self.test_case.fail(f"Se esperaba HTTPException con status {self.expected_status}, pero no se lanzó ninguna excepción.")
        if not issubclass(exc_type, HTTPException):
            return False  # Propagar otra excepción

        self.exception = exc_val
        self.test_case.assertEqual(
            exc_val.status_code,
            self.expected_status,
            f"Status esperado {self.expected_status}, pero se obtuvo {exc_val.status_code}",
        )
        if self.expected_detail:
            self.test_case.assertIn(
                self.expected_detail.lower(),
                str(exc_val.detail).lower(),
                f"Detalle esperado '{self.expected_detail}' no encontrado en '{exc_val.detail}'",
            )
        return True