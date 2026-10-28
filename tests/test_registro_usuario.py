"""Pruebas unitarias e integración para HU-IAM-01: Registrar usuario.

Criterios de Aceptación:
- CA-01: Registro exitoso (Transportista y Dador de carga con estado inicial EN_REVISION).
- CA-02: Correo electrónico duplicado (Impide creación en cualquier rol e informa al usuario).
- CA-03: Campos obligatorios incompletos (Rol no permitido, datos personales o requisitos ausentes).
- CA-04: Contraseña inválida (Rechaza < 6 caracteres, acepta >= 6 caracteres).
- CA-05: Formato de correo electrónico inválido (Rechaza formatos sin @, sin dominio, espacios, etc.).
- CA-06: Formato de documentos (Formatos admitidos: .pdf, .jpg, .jpeg, .png; rechaza otros).
- CA-07: Validación del perfil tributario (RUT con DV modulo 11, razón social, dirección, correo facturación).

Trazabilidad técnica:
- domain/modelos_usuario.py
- domain/modelos_onboarding.py
- services/usuario_service.py
- routers/auth_router.py
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from pydantic import ValidationError

import services.usuario_service as usuario_service_modulo
from dao.onboarding_dao import DadorCargaDAOInMemory, DocumentoDAOInMemory
from dao.usuario_dao import UsuarioDAOMemoria, UsuarioDAOSQLite
from domain.modelos_onboarding import (
    CargarDocumentoDTO,
    CrearPerfilDadorDTO,
    DatosFacturacion,
    TipoDocumento,
)
from domain.modelos_usuario import EstadoUsuario, RolUsuario, UsuarioCrear
from routers.auth_router import registrar_usuario as router_registrar_usuario
from services.onboarding_service import (
    DOCUMENTOS_REQUERIDOS_TRANSPORTISTA,
    OnboardingService,
)
from services.usuario_service import UsuarioService, hash_password


class BaseTestRegistro(unittest.TestCase):
    """Configuración base con aislamiento de DAOs en memoria para pruebas rápidas y deterministas."""

    def setUp(self) -> None:
        # Guardar referencias originales de los singletons
        self._orig_usuario_dao = usuario_service_modulo.usuario_dao
        self._orig_onboarding_service = (
            usuario_service_modulo.onboarding_service_instancia
        )

        # Inyectar DAOs en memoria para total aislamiento
        self.usuario_dao_memoria = UsuarioDAOMemoria()
        self.doc_dao_memoria = DocumentoDAOInMemory()
        self.dador_dao_memoria = DadorCargaDAOInMemory()

        self.onboarding_service_memoria = OnboardingService(
            documento_dao=self.doc_dao_memoria,
            dador_dao=self.dador_dao_memoria,
        )

        usuario_service_modulo.usuario_dao = self.usuario_dao_memoria
        usuario_service_modulo.onboarding_service_instancia = (
            self.onboarding_service_memoria
        )

    def tearDown(self) -> None:
        # Restaurar referencias originales
        usuario_service_modulo.usuario_dao = self._orig_usuario_dao
        usuario_service_modulo.onboarding_service_instancia = (
            self._orig_onboarding_service
        )

    def _crear_documentos_transportista_validos(self) -> list[CargarDocumentoDTO]:
        """Genera la lista con los 5 documentos requeridos en formatos válidos."""
        return [
            CargarDocumentoDTO(
                tipo=TipoDocumento.LICENCIA_CONDUCIR, archivo="docs/licencia.pdf"
            ),
            CargarDocumentoDTO(
                tipo=TipoDocumento.PADRON_VEHICULO, archivo="docs/padron.jpg"
            ),
            CargarDocumentoDTO(
                tipo=TipoDocumento.REVISION_TECNICA, archivo="docs/rev_tec.jpeg"
            ),
            CargarDocumentoDTO(
                tipo=TipoDocumento.SEGURO_CARGA, archivo="docs/seguro.png"
            ),
            CargarDocumentoDTO(
                tipo=TipoDocumento.ANTECEDENTES, archivo="docs/antecedentes.pdf"
            ),
        ]

    def _crear_perfil_dador_valido(
        self,
        correo_facturacion: str = "facturacion@empresa.cl",
        rut: str = "76.123.456-0",
    ) -> CrearPerfilDadorDTO:
        """Genera un perfil tributario válido para dador de carga con RUT y DV correctos."""
        return CrearPerfilDadorDTO(
            rut_id_empresa=rut,
            datos_facturacion=DatosFacturacion(
                razon_social="Transportes del Pacífico S.A.",
                direccion="Av. Libertador Bernardo O'Higgins 1234, Santiago",
                correo_facturacion=correo_facturacion,
            ),
        )


class TestCA01RegistroExitoso(BaseTestRegistro):
    """CA-01: Registro exitoso con estado inicial EN_REVISION para Transportista y Dador de Carga."""

    def test_registro_exitoso_transportista_con_documentos(self) -> None:
        """Transportista completa datos y sus 5 documentos -> Cuenta creada con rol TRANSPORTISTA y EN_REVISION."""
        documentos = self._crear_documentos_transportista_validos()
        dto = UsuarioCrear(
            nombre="Carlos Conductor",
            email="carlos.conductor@example.com",
            rol=RolUsuario.TRANSPORTISTA,
            password="passwordSegura123",
            documentos=documentos,
        )

        usuario_creado = UsuarioService.registrar_usuario(dto)

        # Validaciones de cuenta creada
        self.assertIsInstance(usuario_creado.id, UUID)
        self.assertEqual(usuario_creado.nombre, "Carlos Conductor")
        self.assertEqual(usuario_creado.email, "carlos.conductor@example.com")
        self.assertEqual(usuario_creado.rol, RolUsuario.TRANSPORTISTA)
        self.assertEqual(usuario_creado.estado, EstadoUsuario.EN_REVISION)

        # Contraseña hasheada (no texto plano)
        self.assertNotEqual(usuario_creado.password_hash, "passwordSegura123")
        self.assertEqual(
            usuario_creado.password_hash, hash_password("passwordSegura123")
        )

        # Verificación de persistencia en SQLite/DAO
        guardado = self.usuario_dao_memoria.obtener_por_id(usuario_creado.id)
        self.assertIsNotNone(guardado)
        assert guardado is not None
        self.assertEqual(guardado.email, "carlos.conductor@example.com")

        # Documentos cargados en onboarding asociados al usuario
        docs_guardados = self.doc_dao_memoria.get_by_user_id(usuario_creado.id)
        self.assertEqual(len(docs_guardados), 5)
        tipos_guardados = {d.tipo for d in docs_guardados}
        self.assertEqual(tipos_guardados, set(DOCUMENTOS_REQUERIDOS_TRANSPORTISTA))

    def test_registro_exitoso_dador_carga_con_perfil_tributario(self) -> None:
        """Dador de carga completa datos y perfil tributario -> Cuenta creada con rol DADOR_CARGA y EN_REVISION."""
        perfil = self._crear_perfil_dador_valido(
            correo_facturacion="contacto@pacificosrl.cl"
        )
        dto = UsuarioCrear(
            nombre="Marcela Gerente",
            email="marcela@pacificosrl.cl",
            rol=RolUsuario.DADOR_CARGA,
            password="miPassword123",
            perfil_tributario=perfil,
        )

        usuario_creado = UsuarioService.registrar_usuario(dto)

        self.assertIsInstance(usuario_creado.id, UUID)
        self.assertEqual(usuario_creado.nombre, "Marcela Gerente")
        self.assertEqual(usuario_creado.email, "marcela@pacificosrl.cl")
        self.assertEqual(usuario_creado.rol, RolUsuario.DADOR_CARGA)
        self.assertEqual(usuario_creado.estado, EstadoUsuario.EN_REVISION)

        # Perfil tributario persistido en onboarding
        perfil_guardado = self.dador_dao_memoria.get_by_user_id(usuario_creado.id)
        self.assertIsNotNone(perfil_guardado)
        assert perfil_guardado is not None
        self.assertEqual(perfil_guardado.rut_id_empresa, "76123456-0")
        self.assertEqual(
            perfil_guardado.datos_facturacion.razon_social,
            "Transportes del Pacífico S.A.",
        )

    def test_registro_exitoso_a_traves_del_router(self) -> None:
        """El endpoint en auth_router delega correctamente y responde con el nuevo usuario."""
        dto = UsuarioCrear(
            nombre="Roberto Transportes",
            email="roberto@transportes.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="claveValida123",
        )

        resultado_router = router_registrar_usuario(dto)

        self.assertEqual(resultado_router.email, "roberto@transportes.cl")
        self.assertEqual(resultado_router.rol, RolUsuario.TRANSPORTISTA)
        self.assertEqual(resultado_router.estado, EstadoUsuario.EN_REVISION)

    def test_normalizacion_de_roles_independiente_y_empresa(self) -> None:
        """Valida que valores de formulario frontend ('independiente', 'empresa') se normalizan correctamente."""
        dto_indep = UsuarioCrear(
            nombre="Juan Chofer",
            email="chofer@correo.cl",
            rol="independiente",  # type: ignore[arg-type]
            password="passwordValido",
        )
        self.assertEqual(dto_indep.rol, RolUsuario.TRANSPORTISTA)

        dto_emp = UsuarioCrear(
            nombre="Empresa Logistica",
            email="empresa@correo.cl",
            rol="empresa",  # type: ignore[arg-type]
            password="passwordValido",
        )
        self.assertEqual(dto_emp.rol, RolUsuario.DADOR_CARGA)


class TestCA02CorreoDuplicado(BaseTestRegistro):
    """CA-02: Correo electrónico duplicado en la plataforma."""

    def test_impedir_registro_con_correo_duplicado_mismo_rol(self) -> None:
        """Si un transportista ya existe con un email, otro transportista no puede usarlo."""
        dto1 = UsuarioCrear(
            nombre="Primer Usuario",
            email="duplicado@transporte.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="password123",
        )
        UsuarioService.registrar_usuario(dto1)

        dto2 = UsuarioCrear(
            nombre="Segundo Usuario",
            email="duplicado@transporte.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="otraPassword123",
        )

        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.registrar_usuario(dto2)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("email ya está registrado", ctx.exception.detail)

    def test_impedir_registro_con_correo_duplicado_distinto_rol(self) -> None:
        """El correo debe ser único en toda la plataforma independientemente del rol."""
        dto_transportista = UsuarioCrear(
            nombre="Usuario Transportista",
            email="compartido@correo.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="password123",
        )
        UsuarioService.registrar_usuario(dto_transportista)

        dto_dador = UsuarioCrear(
            nombre="Usuario Dador Carga",
            email="compartido@correo.cl",
            rol=RolUsuario.DADOR_CARGA,
            password="password123",
        )

        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.registrar_usuario(dto_dador)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("email ya está registrado", ctx.exception.detail)

    def test_correo_duplicado_es_insensible_a_mayusculas(self) -> None:
        """La detección de correo duplicado no debe ser burlada por diferencias de mayúsculas/minúsculas."""
        dto1 = UsuarioCrear(
            nombre="Usuario Uno",
            email="juan.perez@empresa.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="password123",
        )
        UsuarioService.registrar_usuario(dto1)

        dto2 = UsuarioCrear(
            nombre="Usuario Dos",
            email="JUAN.PEREZ@EMPRESA.CL",
            rol=RolUsuario.TRANSPORTISTA,
            password="password123",
        )

        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.registrar_usuario(dto2)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("email ya está registrado", ctx.exception.detail)

    def test_intento_duplicado_no_sobreescribe_cuenta_existente(self) -> None:
        """El intento fallido por email duplicado no debe modificar el registro original."""
        dto1 = UsuarioCrear(
            nombre="Usuario Original",
            email="original@correo.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="passwordOriginal1",
        )
        creado = UsuarioService.registrar_usuario(dto1)

        dto2 = UsuarioCrear(
            nombre="Usuario Impostor",
            email="original@correo.cl",
            rol=RolUsuario.DADOR_CARGA,
            password="passwordNueva999",
        )

        with self.assertRaises(HTTPException):
            UsuarioService.registrar_usuario(dto2)

        en_bd = self.usuario_dao_memoria.obtener_por_id(creado.id)
        self.assertIsNotNone(en_bd)
        assert en_bd is not None
        self.assertEqual(en_bd.nombre, "Usuario Original")
        self.assertEqual(en_bd.password_hash, hash_password("passwordOriginal1"))


class TestCA03CamposObligatoriosIncompletos(BaseTestRegistro):
    """CA-03: Campos obligatorios incompletos o rol inválido."""

    def test_rol_no_permitido_en_registro(self) -> None:
        """Roles distintos a TRANSPORTISTA o DADOR_CARGA (como ADMIN_BACKOFFICE) no se permiten al registrarse."""
        with self.assertRaises(ValidationError) as ctx:
            UsuarioCrear(
                nombre="Admin Infiltrado",
                email="admin@plataforma.cl",
                rol=RolUsuario.ADMIN_BACKOFFICE,
                password="password123",
            )
        self.assertIn(
            "El rol al registrarse solo puede ser TRANSPORTISTA o DADOR_CARGA",
            str(ctx.exception),
        )

    def test_rol_invalido_cadena_desconocida(self) -> None:
        """Un rol inexistente debe lanzar ValidationError."""
        with self.assertRaises(ValidationError):
            UsuarioCrear(
                nombre="Usuario Invalido",
                email="invalido@correo.cl",
                rol="SUPER_USUARIO",  # type: ignore[arg-type]
                password="password123",
            )

    def test_nombre_faltante_o_muy_corto(self) -> None:
        """El nombre es obligatorio y debe tener al menos 2 caracteres."""
        with self.assertRaises(ValidationError):
            UsuarioCrear(
                nombre="",
                email="correo@valido.cl",
                rol=RolUsuario.TRANSPORTISTA,
                password="password123",
            )

        with self.assertRaises(ValidationError):
            UsuarioCrear(
                nombre="A",  # Menor a min_length=2
                email="correo@valido.cl",
                rol=RolUsuario.TRANSPORTISTA,
                password="password123",
            )

    def test_email_faltante(self) -> None:
        """El correo electrónico es un campo obligatorio."""
        with self.assertRaises(ValidationError):
            UsuarioCrear.model_validate(
                {
                    "nombre": "Juan Valenzuela",
                    "rol": "TRANSPORTISTA",
                    "password": "password123",
                }
            )

    def test_password_faltante(self) -> None:
        """La contraseña es un campo obligatorio."""
        with self.assertRaises(ValidationError):
            UsuarioCrear.model_validate(
                {
                    "nombre": "Juan Valenzuela",
                    "email": "juan@correo.cl",
                    "rol": "TRANSPORTISTA",
                }
            )

    def test_perfil_dador_datos_facturacion_incompletos(self) -> None:
        """El perfil tributario exige razon_social y direccion válidas."""
        with self.assertRaises(ValidationError):
            # Falta razon_social
            DatosFacturacion(
                razon_social="",
                direccion="Calle 123",
                correo_facturacion="fac@empresa.cl",
            )

        with self.assertRaises(ValidationError):
            # Falta direccion
            DatosFacturacion(
                razon_social="Empresa S.A.",
                direccion="",
                correo_facturacion="fac@empresa.cl",
            )


class TestCA04PasswordInvalida(BaseTestRegistro):
    """CA-04: Validación de longitud mínima de contraseña."""

    def test_password_menos_de_seis_caracteres_rechazada(self) -> None:
        """Contraseñas de longitud menor a 6 deben ser rechazadas."""
        passwords_invalidas = ["", "1", "12", "123", "1234", "12345", "abcde"]
        for pwd in passwords_invalidas:
            with self.subTest(password=pwd):
                with self.assertRaises(ValidationError) as ctx:
                    UsuarioCrear(
                        nombre="Usuario Test",
                        email="test@correo.cl",
                        rol=RolUsuario.TRANSPORTISTA,
                        password=pwd,
                    )
                self.assertIn("password", str(ctx.exception).lower())

    def test_password_exactamente_seis_caracteres_aceptada(self) -> None:
        """Contraseña con exactamente 6 caracteres es válida según la regla de negocio."""
        dto = UsuarioCrear(
            nombre="Usuario Valido",
            email="test6@correo.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="123456",
        )
        self.assertEqual(dto.password, "123456")

    def test_password_larga_sin_restricciones_complejas(self) -> None:
        """La regla de negocio no impone restricciones adicionales más allá de >= 6 caracteres."""
        dto = UsuarioCrear(
            nombre="Usuario Valido",
            email="test_largo@correo.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="sololetrasminusculas",
        )
        self.assertEqual(dto.password, "sololetrasminusculas")


class TestCA05FormatoCorreoInvalido(BaseTestRegistro):
    """CA-05: Validación de formato de correo electrónico."""

    def test_correos_con_formato_invalido_rechazados(self) -> None:
        """Formatos sin @, sin dominio, con espacios o incompletos deben ser rechazados."""
        correos_invalidos = [
            "correo_sin_arroba",
            "correo@",
            "@dominio.cl",
            "correo@dominio",
            "usuario @correo.cl",
            "usuario@correo .cl",
            "usuario@@correo.cl",
            "",
        ]
        for correo in correos_invalidos:
            with self.subTest(correo=correo):
                with self.assertRaises(ValidationError) as ctx:
                    UsuarioCrear(
                        nombre="Usuario Test",
                        email=correo,
                        rol=RolUsuario.TRANSPORTISTA,
                        password="password123",
                    )
                self.assertIn("email", str(ctx.exception).lower())

    def test_correos_validos_aceptados(self) -> None:
        """Formatos comunes válidos deben ser aceptados."""
        correos_validos = [
            "contacto@empresa.cl",
            "juan.perez@transporte.com",
            "marcela_rojas@subasta.org",
            "test-123@envios.net",
        ]
        for correo in correos_validos:
            with self.subTest(correo=correo):
                dto = UsuarioCrear(
                    nombre="Usuario Valido",
                    email=correo,
                    rol=RolUsuario.TRANSPORTISTA,
                    password="password123",
                )
                self.assertEqual(dto.email, correo)


class TestCA06FormatoDocumentos(BaseTestRegistro):
    """CA-06: Formato de documentos para el transportista."""

    def test_formatos_admitidos_pdf_jpg_jpeg_png(self) -> None:
        """La plataforma admite archivos .pdf, .jpg, .jpeg y .png."""
        archivos_validos = [
            ("licencia.pdf", TipoDocumento.LICENCIA_CONDUCIR),
            ("padron.jpg", TipoDocumento.PADRON_VEHICULO),
            ("revision.jpeg", TipoDocumento.REVISION_TECNICA),
            ("seguro.png", TipoDocumento.SEGURO_CARGA),
            ("antecedentes.PDF", TipoDocumento.ANTECEDENTES),
            ("documento.PNG", TipoDocumento.ANTECEDENTES),
        ]
        for nombre_archivo, tipo in archivos_validos:
            with self.subTest(archivo=nombre_archivo, tipo=tipo):
                doc = CargarDocumentoDTO(tipo=tipo, archivo=nombre_archivo)
                self.assertEqual(doc.archivo, nombre_archivo)

    def test_formatos_no_admitidos_rechazados(self) -> None:
        """Archivos con extensiones no permitidas (.exe, .docx, .zip, etc.) deben ser rechazados."""
        archivos_invalidos = [
            "malware.exe",
            "documento.docx",
            "comprimido.zip",
            "script.sh",
            "texto.txt",
            "archivo_sin_extension",
        ]
        for nombre_archivo in archivos_invalidos:
            with self.subTest(archivo=nombre_archivo):
                with self.assertRaises(ValidationError) as ctx:
                    CargarDocumentoDTO(
                        tipo=TipoDocumento.LICENCIA_CONDUCIR,
                        archivo=nombre_archivo,
                    )
                self.assertIn(".pdf, .jpg, .jpeg o .png", str(ctx.exception))

    def test_cinco_documentos_obligatorios_identificados(self) -> None:
        """Valida que los 5 tipos de documentos obligatorios especificados existan en TipoDocumento."""
        esperados = {
            TipoDocumento.LICENCIA_CONDUCIR,
            TipoDocumento.PADRON_VEHICULO,
            TipoDocumento.REVISION_TECNICA,
            TipoDocumento.SEGURO_CARGA,
            TipoDocumento.ANTECEDENTES,
        }
        self.assertEqual(set(DOCUMENTOS_REQUERIDOS_TRANSPORTISTA), esperados)


class TestCA07ValidacionPerfilTributario(BaseTestRegistro):
    """CA-07: Validación del perfil tributario del dador de carga (RUT, DV, facturación)."""

    def test_ruts_con_formato_y_digito_verificador_validos(self) -> None:
        """Valida RUTs chilenos reales con DV numérico y con K, con puntos y guión."""
        ruts_validos = [
            "76.123.456-0",
            "76123456-0",
            "77.987.654-3",
            "11.111.111-1",
            "60.803.000-K",
            "60803000-k",  # K minúscula normalizada a mayúscula
            "12.345.678-5",
        ]
        for rut in ruts_validos:
            with self.subTest(rut=rut):
                perfil = self._crear_perfil_dador_valido(rut=rut)
                self.assertTrue(len(perfil.rut_id_empresa) >= 3)

    def test_rut_con_digito_verificador_invalido_rechazado(self) -> None:
        """Si el dígito verificador no coincide según cálculo módulo 11, se rechaza."""
        ruts_dv_invalido = [
            "76.123.456-9",  # DV real es 0
            "77.987.654-K",  # DV real es 3
            "11.111.111-2",  # DV real es 1
            "60.803.000-0",  # DV real es K
        ]
        for rut in ruts_dv_invalido:
            with self.subTest(rut=rut):
                with self.assertRaises(ValidationError) as ctx:
                    self._crear_perfil_dador_valido(rut=rut)
                self.assertIn("dígito verificador", str(ctx.exception).lower())

    def test_rut_con_formato_invalido_rechazado(self) -> None:
        """RUT con letras en el cuerpo o muy corto se rechaza."""
        ruts_formato_invalido = [
            "ABC-1",
            "12.34A.567-8",
            "1-9",
            "",
            "AB",
        ]
        for rut in ruts_formato_invalido:
            with self.subTest(rut=rut):
                with self.assertRaises(ValidationError):
                    self._crear_perfil_dador_valido(rut=rut)

    def test_correo_facturacion_valido_aceptado(self) -> None:
        """Correo de facturación con sintaxis válida es admitido."""
        perfil = self._crear_perfil_dador_valido(
            correo_facturacion="cobranzas@empresa.com"
        )
        self.assertEqual(
            perfil.datos_facturacion.correo_facturacion, "cobranzas@empresa.com"
        )

    def test_correo_facturacion_invalido_rechazado(self) -> None:
        """Correo de facturación sin formato válido debe ser rechazado."""
        with self.assertRaises(ValidationError) as ctx:
            self._crear_perfil_dador_valido(correo_facturacion="factura_sin_arroba")
        self.assertIn("correo_facturacion", str(ctx.exception))

    def test_correo_facturacion_puede_coincidir_con_correo_principal(self) -> None:
        """Regla de negocio: El correo de facturación puede coincidir con el correo principal."""
        email_comun = "contacto@empresa.cl"
        perfil = self._crear_perfil_dador_valido(correo_facturacion=email_comun)
        dto = UsuarioCrear(
            nombre="Representante Legal",
            email=email_comun,
            rol=RolUsuario.DADOR_CARGA,
            password="password123",
            perfil_tributario=perfil,
        )

        creado = UsuarioService.registrar_usuario(dto)
        self.assertEqual(creado.email, email_comun)

        perfil_db = self.dador_dao_memoria.get_by_user_id(creado.id)
        self.assertIsNotNone(perfil_db)
        assert perfil_db is not None
        self.assertEqual(perfil_db.datos_facturacion.correo_facturacion, email_comun)

    def test_correo_facturacion_puede_ser_diferente_del_correo_principal(self) -> None:
        """Regla de negocio: El correo de facturación puede ser diferente al correo principal."""
        email_principal = "operaciones@empresa.cl"
        email_facturacion = "pagos@empresa.cl"
        perfil = self._crear_perfil_dador_valido(correo_facturacion=email_facturacion)
        dto = UsuarioCrear(
            nombre="Jefe Operaciones",
            email=email_principal,
            rol=RolUsuario.DADOR_CARGA,
            password="password123",
            perfil_tributario=perfil,
        )

        creado = UsuarioService.registrar_usuario(dto)
        perfil_db = self.dador_dao_memoria.get_by_user_id(creado.id)
        self.assertIsNotNone(perfil_db)
        assert perfil_db is not None
        self.assertEqual(
            perfil_db.datos_facturacion.correo_facturacion, email_facturacion
        )
        self.assertNotEqual(
            creado.email, perfil_db.datos_facturacion.correo_facturacion
        )


class TestPersistenciaSQLiteIntegracion(unittest.TestCase):
    """Prueba de integración end-to-end con una base de datos SQLite real y aislada."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_usuarios.db"

        self.sqlite_dao = UsuarioDAOSQLite(db_path=self.db_path, cargar_semilla=False)
        self._orig_usuario_dao = usuario_service_modulo.usuario_dao
        usuario_service_modulo.usuario_dao = self.sqlite_dao

    def tearDown(self) -> None:
        usuario_service_modulo.usuario_dao = self._orig_usuario_dao
        self.temp_dir.cleanup()

    def test_ciclo_completo_registro_y_persistencia_sqlite(self) -> None:
        """Verifica que el usuario se guarda en SQLite con estado EN_REVISION y password hasheada."""
        dto = UsuarioCrear(
            nombre="Transportista SQLite",
            email="sqlite.test@correo.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="claveSQLite123",
        )

        creado = UsuarioService.registrar_usuario(dto)

        # Recuperar desde SQLite mediante DAO
        recuperado = self.sqlite_dao.obtener_por_id(creado.id)
        self.assertIsNotNone(recuperado)
        assert recuperado is not None
        self.assertEqual(recuperado.nombre, "Transportista SQLite")
        self.assertEqual(recuperado.email, "sqlite.test@correo.cl")
        self.assertEqual(recuperado.rol, RolUsuario.TRANSPORTISTA)
        self.assertEqual(recuperado.estado, EstadoUsuario.EN_REVISION)
        self.assertEqual(recuperado.password_hash, hash_password("claveSQLite123"))

        # Recuperar por email insensible a mayúsculas
        recuperado_email = self.sqlite_dao.obtener_por_email("SQLITE.TEST@CORREO.CL")
        self.assertIsNotNone(recuperado_email)
        assert recuperado_email is not None
        self.assertEqual(recuperado_email.id, creado.id)


if __name__ == "__main__":
    unittest.main()
