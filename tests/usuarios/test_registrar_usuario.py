"""Tests unitarios dedicados a UsuarioService.registrar_usuario."""

from __future__ import annotations

from domain.modelos_usuario import EstadoUsuario, RolUsuario
from services.usuario_service import UsuarioService, hash_password
from tests.usuarios.base import BaseTestUsuarios


class TestRegistrarUsuario(BaseTestUsuarios):
    """Pruebas dedicadas al registro de cuentas (CA-01, CA-02)."""

    def test_registro_exitoso_transportista_con_documentos(self) -> None:
        dto = self.crear_dto_transportista_valido()
        usuario = UsuarioService.registrar_usuario(dto)

        self.assertIsNotNone(usuario.id)
        self.assertEqual(usuario.email, dto.email)
        self.assertEqual(usuario.rol, RolUsuario.TRANSPORTISTA)
        self.assertEqual(usuario.estado, EstadoUsuario.EN_REVISION)
        self.assertEqual(usuario.password_hash, hash_password(self.password_comun))

        # Verificar documentos persistidos en onboarding
        docs = self.onboarding_service.listar_documentos_transportista(usuario.id)
        self.assertEqual(len(docs), 5)

    def test_registro_exitoso_dador_con_perfil_tributario(self) -> None:
        dto = self.crear_dto_dador_valido()
        usuario = UsuarioService.registrar_usuario(dto)

        self.assertIsNotNone(usuario.id)
        self.assertEqual(usuario.email, dto.email)
        self.assertEqual(usuario.rol, RolUsuario.DADOR_CARGA)
        self.assertEqual(usuario.estado, EstadoUsuario.EN_REVISION)

        # Verificar perfil tributario persistido
        perfil = self.onboarding_service.obtener_perfil_dador(usuario.id)
        self.assertIsNotNone(perfil)
        assert perfil is not None
        self.assertEqual(perfil.rut_id_empresa, "76123456-0")

    def test_rechazo_correo_duplicado(self) -> None:
        # Intento de registrar correo ya existente (juan.chofer@transporte.cl)
        dto = self.crear_dto_transportista_valido(email="juan.chofer@transporte.cl")

        with self.assertHttpException(400, "el email ya está registrado"):
            UsuarioService.registrar_usuario(dto)
