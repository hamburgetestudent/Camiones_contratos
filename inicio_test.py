#!/usr/bin/env python3
"""
===============================================================================
 inicio_test.py - Compilador, Verificador y Lanzador Integral de la Aplicación
===============================================================================

Este script cumple dos propósitos fundamentales:
 1. COMPILACIÓN Y VERIFICACIÓN COMPLETA:
    - Analiza y compila al 100% todos los archivos Python del proyecto a bytecode (.pyc).
    - Valida la sintaxis (AST) y lectura UTF-8.
    - Verifica la integridad del Frontend (archivos HTML, CSS, JS, TS) y paquetes backend.
    - Es compatible con test runners: `pytest inicio_test.py -v` o `python -m unittest inicio_test.py`.

 2. USO COMPLETO DE LA APLICACIÓN:
    - Iniciar servidor backend FastAPI (Uvicorn) y abrir documentación Swagger interactiva (/docs).
    - Iniciar Frontend (vía Electron o servidor web local con apertura automática de navegador).
    - Iniciar Backend + Frontend de forma simultánea.
    - Consola interactiva CLI completa para operar la lógica de negocio sin dependencias externas:
        * Gestión de Contratos (Crear, listar, transiciones de estado con máquina de estados).
        * Registro y Autenticación de Usuarios (con hashing SHA-256).
        * Onboarding y Verificación KYC (Carga de documentos y validación tributaria).
        * Motor de Subastas y Postulaciones (Exploración de cargas, ofertas y adjudicación).
        * Reglas de Negocio globales (Configuración de IVA y tolerancias).
        * Carga automática de Datos Demo para pruebas inmediatas.

Uso rápido:
    python inicio_test.py             # Compila y abre el menú interactivo completo
    python inicio_test.py -c          # Solo compilar y verificar integridad
    python inicio_test.py -s          # Iniciar servidor backend FastAPI
    python inicio_test.py -f          # Abrir frontend en el navegador
    python inicio_test.py -a          # Iniciar backend + frontend juntos
    python inicio_test.py --cli       # Abrir directamente la consola interactiva CLI
    python inicio_test.py -t          # Ejecutar suite de pruebas automatizadas
    python inicio_test.py --clean     # Limpiar carpetas __pycache__ y temporales
"""

from __future__ import annotations

import argparse
import ast
import http.server
import os
import py_compile
import shutil
import socket
import socketserver
import subprocess
import sys
import threading
import time
import unittest
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

# Directorio raíz del proyecto
DIRECTORIO_PROYECTO = Path(__file__).resolve().parent

# Asegurar que el directorio raíz esté en sys.path para importaciones
if str(DIRECTORIO_PROYECTO) not in sys.path:
    sys.path.insert(0, str(DIRECTORIO_PROYECTO))

# Carpetas a excluir de la compilación de código fuente del proyecto
DIRECTORIOS_EXCLUIDOS: Set[str] = {
    "__pycache__",
    ".git",
    ".vscode",
    ".idea",
    "venv",
    ".venv",
    "env",
    "ENV",
    "node_modules",
    "dist",
    "build",
    ".eggs",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

# Python del entorno virtual si existe
PYTHON_VENV = DIRECTORIO_PROYECTO / "venv" / "bin" / "python"
if not PYTHON_VENV.exists():
    PYTHON_VENV = DIRECTORIO_PROYECTO / "venv" / "Scripts" / "python.exe"


# =============================================================================
# Formateo y Colores de Terminal ANSI
# =============================================================================

class Colores:
    """Códigos ANSI para salida con colores en terminales compatibles."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    VERDE = "\033[92m"
    ROJO = "\033[91m"
    AMARILLO = "\033[93m"
    AZUL = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BLANCO = "\033[97m"

    @classmethod
    def desactivar(cls) -> None:
        """Desactiva los colores para entornos sin soporte TTY o con flag --no-color."""
        for attr in dir(cls):
            if attr.isupper() and not attr.startswith("_"):
                setattr(cls, attr, "")


# =============================================================================
# Clases de Datos para Compilación y Resultados
# =============================================================================

@dataclass
class DetalleError:
    """Encapsula los detalles de un fallo de sintaxis o compilación."""
    archivo: Path
    tipo_error: str
    mensaje: str
    linea: Optional[int] = None
    columna: Optional[int] = None
    codigo_fuente: Optional[str] = None


@dataclass
class ResultadoArchivo:
    """Resultado del análisis y compilación de un archivo individual."""
    ruta: Path
    ruta_relativa: Path
    exito: bool
    lineas: int = 0
    tamanio_bytes: int = 0
    tiempo_ms: float = 0.0
    error: Optional[DetalleError] = None


@dataclass
class ReporteCompilacion:
    """Resumen consolidado del proceso de compilación del proyecto."""
    archivos: List[ResultadoArchivo] = field(default_factory=list)
    tiempo_total_segundos: float = 0.0
    directorio_raiz: Path = DIRECTORIO_PROYECTO

    @property
    def total_archivos(self) -> int:
        return len(self.archivos)

    @property
    def archivos_exitosos(self) -> int:
        return sum(1 for a in self.archivos if a.exito)

    @property
    def archivos_fallidos(self) -> int:
        return sum(1 for a in self.archivos if not a.exito)

    @property
    def total_lineas(self) -> int:
        return sum(a.lineas for a in self.archivos)

    @property
    def total_bytes(self) -> int:
        return sum(a.tamanio_bytes for a in self.archivos)

    @property
    def todo_exitoso(self) -> bool:
        return self.archivos_fallidos == 0 and self.total_archivos > 0

    @property
    def lista_fallidos(self) -> List[ResultadoArchivo]:
        return [a for a in self.archivos if not a.exito]


# =============================================================================
# Motor de Compilación y Verificación
# =============================================================================

def buscar_archivos_python(
    directorio_raiz: Path,
    excluir_dirs: Optional[Set[str]] = None,
) -> List[Path]:
    """Busca recursivamente todos los archivos .py a partir del directorio raíz."""
    exclusiones = excluir_dirs or DIRECTORIOS_EXCLUIDOS
    archivos_encontrados: List[Path] = []

    for raiz, dirs, archivos in os.walk(directorio_raiz):
        # Excluir directorios ignorados in-place
        dirs[:] = [d for d in dirs if d not in exclusiones and not d.startswith(".")]

        for nombre_archivo in archivos:
            if nombre_archivo.endswith(".py"):
                ruta_completa = Path(raiz) / nombre_archivo
                archivos_encontrados.append(ruta_completa)

    archivos_encontrados.sort()
    return archivos_encontrados


def compilar_archivo(ruta_archivo: Path, directorio_base: Path) -> ResultadoArchivo:
    """
    Compila y analiza sintácticamente un archivo Python individual.
    Verifica:
      1. Lectura en codificación UTF-8.
      2. Análisis del Árbol de Sintaxis Abstracta (AST).
      3. Compilación a bytecode (.pyc) con py_compile.
    """
    inicio = time.perf_counter()
    ruta_relativa = ruta_archivo.relative_to(directorio_base)

    # 1. Verificar lectura y contar líneas
    try:
        contenido = ruta_archivo.read_text(encoding="utf-8")
        num_lineas = len(contenido.splitlines())
        tamanio = ruta_archivo.stat().st_size
    except UnicodeDecodeError as err:
        return ResultadoArchivo(
            ruta=ruta_archivo,
            ruta_relativa=ruta_relativa,
            exito=False,
            tiempo_ms=(time.perf_counter() - inicio) * 1000,
            error=DetalleError(
                archivo=ruta_archivo,
                tipo_error="Error de Codificación UTF-8",
                mensaje=f"No se pudo decodificar como UTF-8: {err}",
            ),
        )
    except Exception as err:
        return ResultadoArchivo(
            ruta=ruta_archivo,
            ruta_relativa=ruta_relativa,
            exito=False,
            tiempo_ms=(time.perf_counter() - inicio) * 1000,
            error=DetalleError(
                archivo=ruta_archivo,
                tipo_error="Error de Lectura",
                mensaje=str(err),
            ),
        )

    # 2. Análisis sintáctico mediante AST (Abstract Syntax Tree)
    try:
        ast.parse(contenido, filename=str(ruta_archivo))
    except SyntaxError as err:
        return ResultadoArchivo(
            ruta=ruta_archivo,
            ruta_relativa=ruta_relativa,
            exito=False,
            lineas=num_lineas,
            tamanio_bytes=tamanio,
            tiempo_ms=(time.perf_counter() - inicio) * 1000,
            error=DetalleError(
                archivo=ruta_archivo,
                tipo_error="Error de Sintaxis (AST)",
                mensaje=err.msg or "Sintaxis inválida",
                linea=err.lineno,
                columna=err.offset,
                codigo_fuente=err.text.strip() if err.text else None,
            ),
        )

    # 3. Compilación a bytecode (.pyc)
    try:
        py_compile.compile(str(ruta_archivo), doraise=True)
    except py_compile.PyCompileError as err:
        return ResultadoArchivo(
            ruta=ruta_archivo,
            ruta_relativa=ruta_relativa,
            exito=False,
            lineas=num_lineas,
            tamanio_bytes=tamanio,
            tiempo_ms=(time.perf_counter() - inicio) * 1000,
            error=DetalleError(
                archivo=ruta_archivo,
                tipo_error="Error de Compilación a Bytecode",
                mensaje=str(err),
            ),
        )

    duracion_ms = (time.perf_counter() - inicio) * 1000
    return ResultadoArchivo(
        ruta=ruta_archivo,
        ruta_relativa=ruta_relativa,
        exito=True,
        lineas=num_lineas,
        tamanio_bytes=tamanio,
        tiempo_ms=duracion_ms,
    )


def compilar_proyecto(
    directorio_raiz: Optional[Path] = None,
    excluir_dirs: Optional[Set[str]] = None,
) -> ReporteCompilacion:
    """Ejecuta el proceso completo de compilación de todos los archivos Python del proyecto."""
    raiz = directorio_raiz or DIRECTORIO_PROYECTO
    inicio_total = time.perf_counter()

    archivos = buscar_archivos_python(raiz, excluir_dirs)
    reporte = ReporteCompilacion(directorio_raiz=raiz)

    for ruta in archivos:
        resultado = compilar_archivo(ruta, raiz)
        reporte.archivos.append(resultado)

    reporte.tiempo_total_segundos = time.perf_counter() - inicio_total
    return reporte


def verificar_frontend(directorio_raiz: Optional[Path] = None) -> Dict[str, Any]:
    """Verifica el estado y la existencia de los archivos del Frontend."""
    raiz = directorio_raiz or DIRECTORIO_PROYECTO
    carpeta_frontend = raiz / "frontend"

    archivos_clave = {
        "index.html": carpeta_frontend / "paginas" / "index.html",
        "style.css": carpeta_frontend / "paginas" / "style.css",
        "script.js": carpeta_frontend / "paginas" / "script.js",
        "package.json": carpeta_frontend / "package.json",
        "dist/main.js": carpeta_frontend / "dist" / "main.js",
        "src/main.ts": carpeta_frontend / "src" / "main.ts",
    }

    resultados = {nombre: ruta.exists() for nombre, ruta in archivos_clave.items()}
    todos_ok = all(resultados.values())

    return {
        "ok": todos_ok,
        "detalles": resultados,
        "carpeta": carpeta_frontend,
    }


def limpiar_pycache(directorio_raiz: Optional[Path] = None) -> int:
    """Elimina las carpetas __pycache__ y archivos .pyc dentro del proyecto (sin tocar venv)."""
    raiz = directorio_raiz or DIRECTORIO_PROYECTO
    eliminados = 0

    for item in raiz.rglob("__pycache__"):
        if "venv" not in item.parts and ".venv" not in item.parts and "node_modules" not in item.parts:
            try:
                shutil.rmtree(item)
                eliminados += 1
            except OSError:
                pass

    return eliminados


def imprimir_reporte_compilacion(
    reporte: ReporteCompilacion,
    verbose: bool = False,
    quiet: bool = False,
) -> None:
    """Imprime en consola los resultados formateados de la compilación."""
    if quiet and reporte.todo_exitoso:
        return

    ancho = 78
    print(f"\n{Colores.CYAN}{Colores.BOLD}{'=' * ancho}{Colores.RESET}")
    print(f"{Colores.CYAN}{Colores.BOLD}  🚀 VERIFICACIÓN Y COMPILACIÓN COMPLETA DEL CÓDIGO FUENTE 🚀  {Colores.RESET}".center(ancho + 10))
    print(f"{Colores.CYAN}{Colores.BOLD}{'=' * ancho}{Colores.RESET}")
    print(f"{Colores.DIM}  Directorio base: {reporte.directorio_raiz}{Colores.RESET}\n")

    if verbose or not reporte.todo_exitoso:
        for r in reporte.archivos:
            if r.exito and verbose:
                print(f"  {Colores.VERDE}✔ OK{Colores.RESET}  {str(r.ruta_relativa):<50} {Colores.DIM}({r.lineas} líneas, {r.tiempo_ms:.1f}ms){Colores.RESET}")
            elif not r.exito:
                print(f"  {Colores.ROJO}✖ ERROR{Colores.RESET}  {Colores.BOLD}{r.ruta_relativa}{Colores.RESET}")
                if r.error:
                    print(f"         {Colores.ROJO}Tipo:{Colores.RESET} {r.error.tipo_error}")
                    print(f"         {Colores.ROJO}Mensaje:{Colores.RESET} {r.error.mensaje}")
                    if r.error.linea is not None:
                        print(f"         {Colores.ROJO}Ubicación:{Colores.RESET} Línea {r.error.linea}, Columna {r.error.columna}")
                    if r.error.codigo_fuente:
                        print(f"         {Colores.DIM}Código:   {r.error.codigo_fuente}{Colores.RESET}")

    kb_totales = reporte.total_bytes / 1024
    print(f"\n{Colores.BOLD}RESUMEN DE COMPILACIÓN:{Colores.RESET}")
    print(f"  • Archivos analizados : {Colores.BOLD}{reporte.total_archivos}{Colores.RESET}")
    print(f"  • Archivos exitosos   : {Colores.VERDE}{Colores.BOLD}{reporte.archivos_exitosos}{Colores.RESET}")
    if reporte.archivos_fallidos > 0:
        print(f"  • Archivos con error  : {Colores.ROJO}{Colores.BOLD}{reporte.archivos_fallidos}{Colores.RESET}")
    else:
        print(f"  • Archivos con error  : {Colores.VERDE}0{Colores.RESET}")
    print(f"  • Líneas de código    : {Colores.CYAN}{reporte.total_lineas:,}{Colores.RESET}")
    print(f"  • Tamaño analizado    : {Colores.CYAN}{kb_totales:.2f} KB{Colores.RESET}")
    print(f"  • Tiempo transcurrido : {Colores.AMARILLO}{reporte.tiempo_total_segundos * 1000:.2f} ms{Colores.RESET}")

    # Verificar Frontend
    estado_front = verificar_frontend(reporte.directorio_raiz)
    print(f"\n{Colores.BOLD}ESTADO DEL FRONTEND (Electron + Web):{Colores.RESET}")
    for archivo, existe in estado_front["detalles"].items():
        simbolo = f"{Colores.VERDE}✔{Colores.RESET}" if existe else f"{Colores.AMARILLO}⚠{Colores.RESET}"
        print(f"  {simbolo} frontend/{archivo:<25} {'Presente' if existe else 'No encontrado'}")

    print(f"\n{'-' * ancho}")
    if reporte.todo_exitoso:
        print(f"{Colores.VERDE}{Colores.BOLD}  ✔ COMPILACIÓN 100% EXITOSA:{Colores.RESET} Todos los módulos compilaron a bytecode sin errores.")
    else:
        print(f"{Colores.ROJO}{Colores.BOLD}  ✖ COMPILACIÓN FALLIDA:{Colores.RESET} Se detectaron errores en {reporte.archivos_fallidos} archivo(s).")
    print(f"{'=' * ancho}\n")


# =============================================================================
# Suite de Pruebas Unitarias Automatizadas (pytest / unittest)
# =============================================================================

class TestCompilacionCodigo(unittest.TestCase):
    """
    Suite de pruebas automatizadas compatible con `pytest` y `python -m unittest`.
    Verifica compilación completa, arquitectura y modelos de negocio.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.reporte = compilar_proyecto(DIRECTORIO_PROYECTO)

    def test_compilacion_integral_sin_errores(self) -> None:
        """Verifica que el 100% de los archivos Python compilen a bytecode sin errores."""
        fallidos = self.reporte.lista_fallidos
        mensajes_error = []
        for f in fallidos:
            detalle = f.error.mensaje if f.error else "Error desconocido"
            mensajes_error.append(f"{f.ruta_relativa}: {detalle}")

        self.assertEqual(
            self.reporte.archivos_fallidos,
            0,
            f"Archivos con error de sintaxis/compilación ({len(fallidos)}):\n" + "\n".join(mensajes_error),
        )

    def test_minimo_archivos_analizados(self) -> None:
        """Verifica que se haya analizado la estructura completa del proyecto."""
        self.assertGreaterEqual(
            self.reporte.total_archivos,
            20,
            f"Se esperaban al menos 20 archivos .py en el proyecto, pero se encontraron {self.reporte.total_archivos}.",
        )

    def test_paquetes_tienen_init(self) -> None:
        """Verifica que los paquetes de arquitectura modular posean __init__.py."""
        paquetes_requeridos = ["dao", "domain", "routers", "services"]
        for pkg in paquetes_requeridos:
            init_path = DIRECTORIO_PROYECTO / pkg / "__init__.py"
            self.assertTrue(
                init_path.exists(),
                f"El paquete '{pkg}' no contiene un archivo __init__.py",
            )

    def test_modulos_principales_importables(self) -> None:
        """Verifica que los módulos centrales de negocio puedan importarse sin errores."""
        try:
            from domain.reglas import ReglasNegocio
            from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
            from services.usuario_service import UsuarioService, ValidadorUsuario
            from dao.contrato_dao import ContratoDAOMemoria
            from services.contrato_service import ServicioContrato

            # Test Reglas de negocio singleton
            reglas1 = ReglasNegocio()
            reglas2 = ReglasNegocio()
            self.assertIs(reglas1, reglas2, "ReglasNegocio debe cumplir con el patrón Singleton.")

            # Test transiciones de máquina de estados
            self.assertTrue(
                MaquinaEstadosContrato.vali_transicion(EstadoContrato.BORRADOR, EstadoContrato.PUBLICADO)
            )
            self.assertFalse(
                MaquinaEstadosContrato.vali_transicion(EstadoContrato.FINALIZADO, EstadoContrato.BORRADOR)
            )
        except ImportError as err:
            self.fail(f"Fallo al importar módulos centrales: {err}")

    def test_frontend_archivos_base(self) -> None:
        """Verifica que los archivos esenciales del frontend existan."""
        info = verificar_frontend(DIRECTORIO_PROYECTO)
        self.assertTrue(info["detalles"]["index.html"], "Falta frontend/paginas/index.html")
        self.assertTrue(info["detalles"]["style.css"], "Falta frontend/paginas/style.css")
        self.assertTrue(info["detalles"]["script.js"], "Falta frontend/paginas/script.js")


# =============================================================================
# Lanzadores de la Aplicación: Backend, Frontend y Servidor Local
# =============================================================================

def puerto_en_uso(puerto: int, host: str = "127.0.0.1") -> bool:
    """Comprueba si un puerto de red ya está ocupado."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, puerto)) == 0


def esperar_puerto(puerto: int, host: str = "127.0.0.1", tiempo_max: float = 10.0) -> bool:
    """Espera activamente a que un puerto esté abierto."""
    inicio = time.time()
    while time.time() - inicio < tiempo_max:
        if puerto_en_uso(puerto, host):
            return True
        time.sleep(0.3)
    return False


def obtener_comando_python() -> str:
    """Retorna la ruta al ejecutable de Python más apropiado (prioriza venv si tiene dependencias)."""
    if PYTHON_VENV.exists():
        return str(PYTHON_VENV)
    return sys.executable


def iniciar_servidor_backend(abrir_docs: bool = True, puerto: int = 8000) -> None:
    """Inicia el servidor backend FastAPI con Uvicorn."""
    print(f"\n{Colores.CYAN}{Colores.BOLD}🚀 Iniciando Servidor Backend FastAPI en http://127.0.0.1:{puerto} ...{Colores.RESET}")

    if puerto_en_uso(puerto):
        print(f"{Colores.AMARILLO}⚠ El puerto {puerto} ya se encuentra ocupado.{Colores.RESET}")
        print(f"Accede directamente a la API en: {Colores.BOLD}http://127.0.0.1:{puerto}/docs{Colores.RESET}\n")
        if abrir_docs:
            webbrowser.open(f"http://127.0.0.1:{puerto}/docs")
        return

    python_bin = obtener_comando_python()
    comando = [python_bin, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(puerto), "--reload"]

    if abrir_docs:
        def _abrir_navegador_demorado() -> None:
            if esperar_puerto(puerto):
                print(f"\n{Colores.VERDE}✔ Servidor listo. Abriendo documentación interactiva Swagger UI...{Colores.RESET}")
                webbrowser.open(f"http://127.0.0.1:{puerto}/docs")

        threading.Thread(target=_abrir_navegador_demorado, daemon=True).start()

    print(f"{Colores.DIM}Comando ejecutado: {' '.join(comando)}{Colores.RESET}")
    print(f"{Colores.BOLD}Presiona Ctrl+C en cualquier momento para detener el servidor.{Colores.RESET}\n")

    try:
        subprocess.run(comando, cwd=str(DIRECTORIO_PROYECTO))
    except KeyboardInterrupt:
        print(f"\n{Colores.AMARILLO}Servidor backend detenido por el usuario.{Colores.RESET}")


def iniciar_servidor_estatico_frontend(puerto: int = 5500, abrir_navegador: bool = True) -> Optional[socketserver.TCPServer]:
    """Inicia un servidor HTTP ligero en segundo plano para servir la interfaz web de frontend."""
    directorio_paginas = DIRECTORIO_PROYECTO / "frontend" / "paginas"
    if not directorio_paginas.exists():
        print(f"{Colores.ROJO}Error: No se encontró la carpeta {directorio_paginas}{Colores.RESET}")
        return None

    if puerto_en_uso(puerto):
        url = f"http://127.0.0.1:{puerto}/index.html"
        print(f"{Colores.VERDE}✔ Frontend web disponible en: {Colores.BOLD}{url}{Colores.RESET}")
        if abrir_navegador:
            webbrowser.open(url)
        return None

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(directorio_paginas), **kwargs)

        def log_message(self, format: str, *args: Any) -> None:
            # Silenciar logs del servidor estático para mantener limpia la consola
            pass

    try:
        httpd = socketserver.TCPServer(("127.0.0.1", puerto), Handler)
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()

        url = f"http://127.0.0.1:{puerto}/index.html"
        print(f"{Colores.VERDE}✔ Servidor de Frontend iniciado en: {Colores.BOLD}{url}{Colores.RESET}")
        if abrir_navegador:
            webbrowser.open(url)
        return httpd
    except Exception as err:
        print(f"{Colores.AMARILLO}Aviso: No se pudo iniciar el servidor estático ({err}). Abriendo archivo directamente...{Colores.RESET}")
        archivo_html = directorio_paginas / "index.html"
        if abrir_navegador:
            webbrowser.open(f"file://{archivo_html.resolve()}")
        return None


def iniciar_frontend_electron_o_web() -> None:
    """Intenta iniciar el Frontend mediante Electron; si no está disponible, lo abre en el navegador web."""
    frontend_dir = DIRECTORIO_PROYECTO / "frontend"
    npm_path = shutil.which("npm")
    electron_local = frontend_dir / "node_modules" / ".bin" / "electron"

    if npm_path and electron_local.exists():
        print(f"\n{Colores.CYAN}{Colores.BOLD}🖥 Iniciando Frontend con Electron (Aplicación de Escritorio)...{Colores.RESET}")
        try:
            subprocess.run(["npm", "start"], cwd=str(frontend_dir))
            return
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"{Colores.AMARILLO}Electron falló ({err}). Recurriendo al navegador web...{Colores.RESET}")

    print(f"\n{Colores.CYAN}{Colores.BOLD}🌐 Iniciando Frontend en el Navegador Web...{Colores.RESET}")
    iniciar_servidor_estatico_frontend(puerto=5500, abrir_navegador=True)


def iniciar_todo_el_sistema() -> None:
    """Inicia el Backend FastAPI y el Frontend de forma coordinada."""
    print(f"\n{Colores.CYAN}{Colores.BOLD}🚀 INICIANDO SISTEMA COMPLETO (BACKEND + FRONTEND)...{Colores.RESET}\n")

    # 1. Iniciar frontend estático en hilo secundario
    iniciar_servidor_estatico_frontend(puerto=5500, abrir_navegador=True)

    # 2. Iniciar backend en el hilo principal
    iniciar_servidor_backend(abrir_docs=True, puerto=8000)


# =============================================================================
# Consola Interactiva CLI para Uso y Demostración Integral
# =============================================================================

def cargar_datos_demo() -> Dict[str, Any]:
    """Carga automáticamente un conjunto coherente de datos de prueba para operar la plataforma."""
    try:
        from domain.modelos_usuario import UsuarioCrear, RolUsuario
        from domain.modelos_onboarding import DatosFacturacion, TipoDocumento, EstadoValidacion
        from domain.modelos import ContratoCrear, TipoCarga, Moneda
        from domain.postulacion import PostulacionCrear
        from services.usuario_service import UsuarioService, usuario_dao
        from services.dependencies import servicio_contrato, servicio_subasta
        from services.onboarding_service import onboarding_service_instancia

        # 1. Registrar Empresa Generadora
        empresa_email = f"contacto_{uuid4().hex[:4]}@generadorachile.cl"
        empresa_usr = UsuarioService.registrar_usuario(
            UsuarioCrear(
                nombre="Frutos del Valle S.A.",
                email=empresa_email,
                password="password123",
                rol=RolUsuario.EMPRESA,
            )
        )

        # Aprobar KYC tributario de la empresa
        dador = onboarding_service_instancia.registrar_o_actualizar_perfil_dador(
            user_id=empresa_usr.id,
            rut_id_empresa="76999888-2",
            datos_facturacion=DatosFacturacion(
                razon_social="Frutos del Valle Exportadora SpA",
                direccion="Ruta 5 Sur Km 120, Rancagua",
                correo_facturacion="facturacion@generadorachile.cl",
            ),
        )
        onboarding_service_instancia.validar_dador(dador.id, EstadoValidacion.APROBADO)

        # 2. Registrar Transportista
        transp_email = f"chofer_{uuid4().hex[:4]}@transportesnorte.cl"
        transp_usr = UsuarioService.registrar_usuario(
            UsuarioCrear(
                nombre="Carlos Silva - Transportes Chile",
                email=transp_email,
                password="password123",
                rol=RolUsuario.TRANSPORTISTA,
            )
        )

        # Cargar y aprobar los 5 documentos obligatorios de transportista
        for tipo in [
            TipoDocumento.LICENCIA_CONDUCIR,
            TipoDocumento.PADRON_VEHICULO,
            TipoDocumento.REVISION_TECNICA,
            TipoDocumento.SEGURO_CARGA,
            TipoDocumento.ANTECEDENTES,
        ]:
            doc = onboarding_service_instancia.cargar_documento(
                user_id=transp_usr.id,
                tipo=tipo,
                archivo=f"https://storage.camiones.cl/{transp_usr.id}/{tipo.value}.pdf",
            )
            onboarding_service_instancia.validar_documento(doc.id, EstadoValidacion.APROBADO)

        # 3. Crear Contratos de Demostración
        ahora = datetime.now(timezone.utc)
        salida1 = ahora + timedelta(hours=24)
        llegada1 = salida1 + timedelta(hours=8)
        cierre1 = salida1 - timedelta(hours=4)

        neto1 = 1200000.0
        iva1 = round(neto1 * 0.19, 2)
        total1 = neto1 + iva1

        contrato1_datos = ContratoCrear(
            id_empresa_generadora=empresa_usr.id,
            origen="Santiago Centro, RM",
            destino="Valparaíso Puerto, V Región",
            f_estimada_salida=salida1,
            f_estimada_llegada=llegada1,
            f_cierre_postulaciones=cierre1,
            input_camionKG=15000.0,
            tipo_carga=TipoCarga.GENERAL,
            peso_total=12000.0,
            volumen_m3=45.0,
            moneda=Moneda.CLP,
            monto_neto=neto1,
            monto_iva=iva1,
            monto_total=total1,
        )
        c1 = servicio_contrato.crear_contrato(contrato1_datos)

        # Publicar el primer contrato
        from domain.maquina_estados import EstadoContrato
        c1 = servicio_contrato.cambiar_estado(c1.id, EstadoContrato.PUBLICADO)

        # 4. Crear Postulación de prueba
        postulacion = servicio_subasta.postular_a_carga(
            PostulacionCrear(
                carga_id=c1.id,
                transportista_id=transp_usr.id,
                precio_oferta=1150000.0,
                tiempo_entrega_horas=8.0,
                comentario="Flota moderna con GPS y chofer con seguro al día.",
            ),
            onboarding_aprobado=True,
        )

        return {
            "empresa": empresa_usr,
            "transportista": transp_usr,
            "contrato": c1,
            "postulacion": postulacion,
        }
    except Exception as err:
        print(f"{Colores.ROJO}Error al cargar datos demo: {err}{Colores.RESET}")
        return {}


def leer_linea(mensaje: str = "", valor_por_defecto: str = "") -> str:
    """Lee una línea de la entrada estándar de manera segura ante EOF o interrupción."""
    try:
        entrada = input(mensaje).strip()
        return entrada if entrada else valor_por_defecto
    except (EOFError, KeyboardInterrupt):
        return ""


def consola_interactiva_negocio() -> None:
    """Ejecuta una consola interactiva por terminal para probar todas las operaciones del backend."""
    try:
        from domain.reglas import ReglasNegocio
        from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
        from domain.modelos import ContratoCrear, TipoCarga, Moneda
        from domain.postulacion import PostulacionCrear
        from services.usuario_service import UsuarioService, usuario_dao
        from services.dependencies import servicio_contrato, servicio_subasta
        from services.onboarding_service import onboarding_service_instancia
    except ImportError as err:
        print(f"{Colores.ROJO}No se pudieron importar los módulos de negocio: {err}{Colores.RESET}")
        print("Asegúrate de ejecutar con el entorno virtual activado o dependencias instaladas.")
        return

    while True:
        print(f"\n{Colores.CYAN}{Colores.BOLD}{'=' * 60}{Colores.RESET}")
        print(f"{Colores.CYAN}{Colores.BOLD}   🚚 CONSOLA INTERACTIVA DE OPERACIÓN DEL NEGOCIO 🚚   {Colores.RESET}".center(70))
        print(f"{Colores.CYAN}{Colores.BOLD}{'=' * 60}{Colores.RESET}")
        print("  1. 📦 Contratos: Listar contratos registrados")
        print("  2. 📝 Contratos: Crear nuevo contrato rápido")
        print("  3. 🔄 Contratos: Avanzar estado (Máquina de Estados)")
        print("  4. 👥 Usuarios: Listar usuarios del sistema")
        print("  5. 🔐 Usuarios: Registrar nuevo usuario")
        print("  6. 🔑 Usuarios: Probar autenticación / login")
        print("  7. 📋 Onboarding: Ver estado KYC de transportistas")
        print("  8. 🏷️ Subastas: Explorar cargas y ofertas")
        print("  9. 🏆 Subastas: Adjudicar una subasta")
        print(" 10. ⚙️  Reglas: Consultar / Actualizar configuración global")
        print(" 11. 🪄 Cargar Datos de Demostración Iniciales")
        print("  0. ⬅ Volver al Menú Principal")
        print(f"{Colores.CYAN}{'-' * 60}{Colores.RESET}")

        opcion = leer_linea(f"{Colores.BOLD}Selecciona una opción [0-11]: {Colores.RESET}")

        if opcion in ("0", ""):
            break

        elif opcion == "1":
            contratos = servicio_contrato.listar_contratos()
            print(f"\n{Colores.BOLD}Contratos registrados ({len(contratos)}):{Colores.RESET}")
            if not contratos:
                print(f"{Colores.AMARILLO}No hay contratos registrados. Usa la opción 11 para cargar datos demo.{Colores.RESET}")
            for c in contratos:
                print(f"  • ID: {Colores.CYAN}{c.id}{Colores.RESET} | Estado: {Colores.VERDE}{c.estado.value}{Colores.RESET}")
                print(f"    {c.origen} ➔ {c.destino} | Carga: {c.peso_total} KG ({c.tipo_carga.value}) | Total: ${c.monto_total:,.0f} {c.moneda.value}")
                if c.id_transportista:
                    print(f"    Transportista asignado: {c.id_transportista}")

        elif opcion == "2":
            print(f"\n{Colores.BOLD}Creación rápida de Contrato de Transporte:{Colores.RESET}")
            # Buscar una empresa aprobada
            dadores_aprobados = [d for d in onboarding_service_instancia.dador_dao.obt_todos() if d.estado_validacion.value == "APROBADO"]
            if not dadores_aprobados:
                print(f"{Colores.AMARILLO}Aviso: No hay empresas con KYC Aprobado. Usa la opción 11 para cargar datos de prueba primero.{Colores.RESET}")
                continue

            empresa_id = dadores_aprobados[0].user_id
            origen = leer_linea("Origen [Santiago]: ", "Santiago")
            destino = leer_linea("Destino [Concepción]: ", "Concepción")
            peso = float(leer_linea("Peso en KG [10000]: ", "10000"))
            neto = float(leer_linea("Monto Neto CLP [1000000]: ", "1000000"))
            iva = round(neto * 0.19, 2)
            total = neto + iva

            ahora = datetime.now(timezone.utc)
            salida = ahora + timedelta(hours=24)
            llegada = salida + timedelta(hours=10)
            cierre = salida - timedelta(hours=2)

            datos = ContratoCrear(
                id_empresa_generadora=empresa_id,
                origen=origen,
                destino=destino,
                f_estimada_salida=salida,
                f_estimada_llegada=llegada,
                f_cierre_postulaciones=cierre,
                input_camionKG=peso * 1.2,
                tipo_carga=TipoCarga.GENERAL,
                peso_total=peso,
                moneda=Moneda.CLP,
                monto_neto=neto,
                monto_iva=iva,
                monto_total=total,
            )

            try:
                nuevo = servicio_contrato.crear_contrato(datos)
                print(f"{Colores.VERDE}✔ Contrato creado exitosamente en estado BORRADOR con ID: {nuevo.id}{Colores.RESET}")
            except Exception as err:
                print(f"{Colores.ROJO}Error al crear contrato: {err}{Colores.RESET}")

        elif opcion == "3":
            contratos = servicio_contrato.listar_contratos()
            if not contratos:
                print(f"{Colores.AMARILLO}No hay contratos registrados.{Colores.RESET}")
                continue

            print("\nSelecciona el contrato:")
            for i, c in enumerate(contratos, start=1):
                print(f"  [{i}] ID: {c.id} | Estado: {c.estado.value} | {c.origen} -> {c.destino}")

            try:
                idx = int(leer_linea("Número de contrato: ", "1")) - 1
                contrato_elegido = contratos[idx]
            except (ValueError, IndexError):
                print(f"{Colores.ROJO}Selección inválida.{Colores.RESET}")
                continue

            transiciones = MaquinaEstadosContrato.obt_estados(contrato_elegido.estado)
            print(f"\nEstado actual: {Colores.BOLD}{contrato_elegido.estado.value}{Colores.RESET}")
            print(f"Transiciones permitidas: {[t.value for t in transiciones]}")

            if not transiciones:
                print(f"{Colores.AMARILLO}Este contrato se encuentra en un estado terminal.{Colores.RESET}")
                continue

            nuevo_estado_str = leer_linea("Ingresa el nuevo estado: ").upper()
            try:
                nuevo_estado = EstadoContrato(nuevo_estado_str)
                id_transp = None
                if nuevo_estado == EstadoContrato.ADJUDICADO:
                    id_transp_str = leer_linea("ID de Transportista a adjudicar: ")
                    id_transp = UUID(id_transp_str) if id_transp_str else uuid4()

                actualizado = servicio_contrato.cambiar_estado(
                    contrato_elegido.id,
                    nuevo_estado,
                    id_transportista=id_transp,
                )
                print(f"{Colores.VERDE}✔ Estado actualizado exitosamente a: {actualizado.estado.value}{Colores.RESET}")
            except Exception as err:
                print(f"{Colores.ROJO}Error al cambiar estado: {err}{Colores.RESET}")

        elif opcion == "4":
            usuarios = usuario_dao.obt_todos()
            print(f"\n{Colores.BOLD}Usuarios registrados ({len(usuarios)}):{Colores.RESET}")
            for u in usuarios:
                print(f"  • {u.nombre} ({u.email}) | Rol: {Colores.CYAN}{u.rol.value}{Colores.RESET} | ID: {u.id}")

        elif opcion == "5":
            from domain.modelos_usuario import UsuarioCrear, RolUsuario
            print(f"\n{Colores.BOLD}Registro de nuevo usuario:{Colores.RESET}")
            nombre = leer_linea("Nombre completo: ", "Usuario Prueba")
            email = leer_linea("Email: ", "prueba@camiones.cl")
            pwd = leer_linea("Contraseña: ", "password123")
            rol_str = leer_linea("Rol (empresa/transportista/admin) [empresa]: ", "empresa").lower()

            rol_map = {
                "empresa": RolUsuario.EMPRESA,
                "transportista": RolUsuario.TRANSPORTISTA,
                "admin": RolUsuario.ADMIN,
            }
            rol = rol_map.get(rol_str, RolUsuario.EMPRESA)

            try:
                nuevo_u = UsuarioService.registrar_usuario(
                    UsuarioCrear(nombre=nombre, email=email, password=pwd, rol=rol)
                )
                print(f"{Colores.VERDE}✔ Usuario registrado con ID: {nuevo_u.id}{Colores.RESET}")
            except Exception as err:
                print(f"{Colores.ROJO}Error al registrar usuario: {err}{Colores.RESET}")

        elif opcion == "6":
            print(f"\n{Colores.BOLD}Prueba de Autenticación / Login:{Colores.RESET}")
            email = leer_linea("Email: ")
            pwd = leer_linea("Contraseña: ")
            try:
                u = UsuarioService.autenticar_usuario(email, pwd)
                print(f"{Colores.VERDE}✔ Credenciales válidas. Bienvenido {u.nombre} (Rol: {u.rol.value}){Colores.RESET}")
            except Exception as err:
                print(f"{Colores.ROJO}✖ Autenticación fallida: {err}{Colores.RESET}")

        elif opcion == "7":
            print(f"\n{Colores.BOLD}Verificación KYC de Transportistas:{Colores.RESET}")
            docs_pendientes = onboarding_service_instancia.listar_documentos_pendientes_admin()
            print(f"Documentos pendientes de revisión: {len(docs_pendientes)}")
            for d in docs_pendientes:
                print(f"  • Doc ID: {d.id} | Tipo: {d.tipo.value} | User: {d.user_id} | Archivo: {d.archivo}")

        elif opcion == "8":
            cargas = servicio_subasta.explorar_cargas()
            print(f"\n{Colores.BOLD}Cargas disponibles en subasta/postulación ({len(cargas)}):{Colores.RESET}")
            for c in cargas:
                posts = servicio_subasta.listar_postulaciones_carga(c.id)
                print(f"  • Carga {c.id}: {c.origen} -> {c.destino} | Estado: {c.estado.value} | Postulaciones: {len(posts)}")

        elif opcion == "9":
            cargas = servicio_subasta.explorar_cargas()
            cargas_con_post = []
            for c in cargas:
                posts = servicio_subasta.listar_postulaciones_carga(c.id)
                if posts:
                    cargas_con_post.append((c, posts))

            if not cargas_con_post:
                print(f"{Colores.AMARILLO}No hay cargas con postulaciones activas para adjudicar.{Colores.RESET}")
                continue

            for i, (c, posts) in enumerate(cargas_con_post, start=1):
                print(f"  [{i}] Carga: {c.origen} -> {c.destino} (${c.monto_total:,.0f})")
                for p in posts:
                    print(f"      Postulación {p.id}: Chofer {p.transportista_id} | Oferta: ${p.precio_oferta:,.0f} CLP | Tiempo: {p.tiempo_entrega_horas}h")

            try:
                c_idx = int(leer_linea("Elige carga [1]: ", "1")) - 1
                carga_sel, posts_sel = cargas_con_post[c_idx]
                post_ganadora = posts_sel[0]
                adjudicada = servicio_subasta.adjudicar_subasta(carga_sel.id, post_ganadora.id)
                print(f"{Colores.VERDE}✔ Subasta adjudicada con éxito a la postulación {adjudicada.id}!{Colores.RESET}")
            except Exception as err:
                print(f"{Colores.ROJO}Error al adjudicar subasta: {err}{Colores.RESET}")

        elif opcion == "10":
            cfg = ReglasNegocio.obt_configuracion()
            print(f"\n{Colores.BOLD}Configuración actual de Reglas de Negocio:{Colores.RESET}")
            for k, v in cfg.items():
                print(f"  • {k}: {v}")

        elif opcion == "11":
            datos = cargar_datos_demo()
            if datos:
                print(f"\n{Colores.VERDE}{Colores.BOLD}✔ Datos demo cargados exitosamente:{Colores.RESET}")
                print(f"  • Empresa Generadora : {datos['empresa'].nombre} ({datos['empresa'].email})")
                print(f"  • Transportista KYC   : {datos['transportista'].nombre} ({datos['transportista'].email})")
                print(f"  • Contrato Publicado : ID {datos['contrato'].id} ({datos['contrato'].origen} -> {datos['contrato'].destino})")
                print(f"  • Postulación Creada : ID {datos['postulacion'].id} (${datos['postulacion'].precio_oferta:,.0f} CLP)")

        leer_linea(f"\n{Colores.DIM}Presiona Enter para continuar...{Colores.RESET}")


# =============================================================================
# Menú Principal Interactivo
# =============================================================================

def menu_principal() -> None:
    """Muestra el menú principal de opciones para operar la plataforma."""
    ancho = 68

    while True:
        print(f"\n{Colores.CYAN}{Colores.BOLD}{'=' * ancho}{Colores.RESET}")
        print(f"{Colores.CYAN}{Colores.BOLD} 🚚 PLATAFORMA DE CONTRATOS Y MOTOR DE SUBASTAS 🚚 {Colores.RESET}".center(ancho + 10))
        print(f"{Colores.DIM}    Centro de Control, Compilación y Lanzador de Aplicación{Colores.RESET}".center(ancho + 10))
        print(f"{Colores.CYAN}{Colores.BOLD}{'=' * ancho}{Colores.RESET}")
        print(f"  {Colores.BOLD}[1]{Colores.RESET} 🚀 Iniciar Servidor Backend (FastAPI + Swagger Docs)")
        print(f"  {Colores.BOLD}[2]{Colores.RESET} 🖥️ Abrir Frontend de Usuario (Web / Electron)")
        print(f"  {Colores.BOLD}[3]{Colores.RESET} 🌟 Iniciar Sistema Completo (Backend + Frontend juntos)")
        print(f"  {Colores.BOLD}[4]{Colores.RESET} 💻 Consola Interactiva CLI (Operar negocio completo)")
        print(f"  {Colores.BOLD}[5]{Colores.RESET} 🪄 Cargar Datos de Demostración Iniciales")
        print(f"  {Colores.BOLD}[6]{Colores.RESET} 🔍 Re-ejecutar Verificación y Compilación de Código")
        print(f"  {Colores.BOLD}[7]{Colores.RESET} 🧪 Ejecutar Suite Completa de Tests Automatizados")
        print(f"  {Colores.BOLD}[8]{Colores.RESET} 🧹 Limpiar Bytecode y Carpetas __pycache__")
        print(f"  {Colores.BOLD}[0]{Colores.RESET} 🚪 Salir")
        print(f"{Colores.CYAN}{'-' * ancho}{Colores.RESET}")

        opcion = leer_linea(f"{Colores.BOLD}Selecciona una opción [0-8]: {Colores.RESET}")

        if opcion in ("0", ""):
            print(f"\n{Colores.VERDE}¡Gracias por usar la plataforma de Contratos de Camiones! Hasta pronto.{Colores.RESET}\n")
            break

        elif opcion == "1":
            iniciar_servidor_backend(abrir_docs=True, puerto=8000)

        elif opcion == "2":
            iniciar_frontend_electron_o_web()

        elif opcion == "3":
            iniciar_todo_el_sistema()

        elif opcion == "4":
            consola_interactiva_negocio()

        elif opcion == "5":
            datos = cargar_datos_demo()
            if datos:
                print(f"\n{Colores.VERDE}{Colores.BOLD}✔ Datos demo cargados exitosamente.{Colores.RESET}")

        elif opcion == "6":
            rep = compilar_proyecto(DIRECTORIO_PROYECTO)
            imprimir_reporte_compilacion(rep, verbose=True)

        elif opcion == "7":
            print(f"\n{Colores.CYAN}{Colores.BOLD}🧪 Ejecutando Suite de Pruebas Automatizadas...{Colores.RESET}\n")
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCompilacionCodigo)
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)

        elif opcion == "8":
            eliminados = limpiar_pycache(DIRECTORIO_PROYECTO)
            print(f"\n{Colores.VERDE}✔ Limpieza completada: se eliminaron {eliminados} carpetas __pycache__.{Colores.RESET}")

        else:
            print(f"{Colores.ROJO}Opción no reconocida. Por favor intenta de nuevo.{Colores.RESET}")


# =============================================================================
# Punto de Entrada CLI
# =============================================================================

def main() -> int:
    """Función principal que procesa argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Compilador, Verificador y Lanzador Integral de la Plataforma de Contratos de Camiones.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c", "--compile-only",
        action="store_true",
        help="Solo compila y verifica el código, saliendo con código 0 (éxito) o 1 (fallo).",
    )
    parser.add_argument(
        "-s", "--server",
        action="store_true",
        help="Inicia directamente el servidor backend FastAPI y abre Swagger Docs.",
    )
    parser.add_argument(
        "-f", "--frontend",
        action="store_true",
        help="Inicia directamente el Frontend (Electron o navegador web).",
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Inicia el sistema completo (Backend FastAPI + Frontend web).",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Abre directamente la consola interactiva CLI de operaciones de negocio.",
    )
    parser.add_argument(
        "-t", "--test",
        action="store_true",
        help="Ejecuta la suite de pruebas unitarias automatizadas y finaliza.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Carga los datos demo de prueba y abre la consola interactiva CLI.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Limpia las carpetas __pycache__ del proyecto y finaliza.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Muestra el detalle de cada archivo analizado.",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Modo silencioso: no muestra el banner si no hay errores.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Desactiva los colores ANSI en la terminal.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Puerto para el servidor FastAPI (por defecto: 8000).",
    )

    args = parser.parse_args()

    # Desactivar colores si se solicita o si no es una terminal TTY interactiva
    if args.no_color or not sys.stdout.isatty():
        Colores.desactivar()

    # 1. Limpieza solicitada
    if args.clean:
        eliminados = limpiar_pycache(DIRECTORIO_PROYECTO)
        print(f"Limpieza completada: se eliminaron {eliminados} carpeta(s) __pycache__.")
        return 0

    # 2. Compilar el código siempre antes de cualquier ejecución
    reporte = compilar_proyecto(DIRECTORIO_PROYECTO)
    imprimir_reporte_compilacion(reporte, verbose=args.verbose, quiet=args.quiet)

    if not reporte.todo_exitoso:
        print(f"{Colores.ROJO}{Colores.BOLD}No se puede continuar debido a errores de compilación.{Colores.RESET}")
        return 1

    # 3. Flujos directos por CLI flags
    if args.compile_only:
        return 0

    if args.test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCompilacionCodigo)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if res.wasSuccessful() else 1

    if args.server:
        iniciar_servidor_backend(abrir_docs=True, puerto=args.port)
        return 0

    if args.frontend:
        iniciar_frontend_electron_o_web()
        return 0

    if args.all:
        iniciar_todo_el_sistema()
        return 0

    if args.demo:
        cargar_datos_demo()
        consola_interactiva_negocio()
        return 0

    if args.cli:
        consola_interactiva_negocio()
        return 0

    # 4. Modo por defecto: Menú interactivo completo
    menu_principal()
    return 0


if __name__ == "__main__":
    sys.exit(main())
