#!/usr/bin/env python3
"""Script principal para ejecutar simultaneamente el Backend (FastAPI)

y el Frontend visual (Electron + TypeScript).
"""

import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"


def get_python_executable() -> str:
    """Detecta el ejecutable de Python, priorizando el entorno virtual (.venv)."""
    posibles_venvs = [
        ROOT_DIR / ".venv" / "bin" / "python",
        ROOT_DIR / ".venv" / "Scripts" / "python.exe",
        ROOT_DIR / "venv" / "bin" / "python",
        ROOT_DIR / "venv" / "Scripts" / "python.exe",
    ]

    for venv_python in posibles_venvs:
        if venv_python.exists() and os.access(venv_python, os.X_OK):
            return str(venv_python)
        if venv_python.exists() and os.name == "nt":
            return str(venv_python)

    return sys.executable


def wait_for_port(host: str, port: int, timeout: float = 15.0) -> bool:
    """Espera hasta que el puerto especificado este abierto y aceptando conexiones."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except (socket.error, ConnectionRefusedError, OSError):
            time.sleep(0.3)
    return False


def terminate_process(proc: Optional[subprocess.Popen[Any]], name: str) -> None:
    """Termina un subproceso de forma segura."""
    if proc is not None and proc.poll() is None:
        print(f"[-] Deteniendo {name} (PID {proc.pid})...")
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except (subprocess.TimeoutExpired, ProcessLookupError):
            try:
                proc.kill()
            except ProcessLookupError:
                pass


def main() -> None:
    print("=" * 60)
    print("   Iniciando Plataforma de Contratos y Subastas")
    print("   Backend (FastAPI) + Frontend (Electron)")
    print("=" * 60)

    # 1. Determinar el ejecutable de Python
    python_bin = get_python_executable()
    print(f"[*] Usando Python: {python_bin}")

    # 2. Verificar que npm este instalado
    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        print("[!] ERROR: 'npm' no se encontro en el PATH del sistema.")
        print("    Por favor instala Node.js y npm para continuar.")
        sys.exit(1)

    # 3. Verificar dependencias de frontend
    if not (FRONTEND_DIR / "node_modules").exists():
        print("[*] node_modules no encontrado en 'frontend'. Ejecutando 'npm install'...")
        res = subprocess.run([npm_cmd, "install"], cwd=str(FRONTEND_DIR), shell=(os.name == "nt"))
        if res.returncode != 0:
            print("[!] Fallo la instalacion de dependencias del frontend.")
            sys.exit(1)

    backend_proc: Optional[subprocess.Popen[Any]] = None
    frontend_proc: Optional[subprocess.Popen[Any]] = None

    def signal_handler(signum, frame):
        print("\n\n[!] Señal de interrupcion recibida. Cerrando aplicacion...")
        terminate_process(frontend_proc, "Frontend")
        terminate_process(backend_proc, "Backend")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 4. Iniciar Backend FastAPI
        print("[*] Iniciando Backend FastAPI en http://127.0.0.1:8000 ...")
        backend_cmd = [python_bin, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=str(ROOT_DIR),
        )

        # Esperar a que el backend este listo
        print("[*] Esperando a que el backend responda en el puerto 8000...")
        if wait_for_port("127.0.0.1", 8000, timeout=12.0):
            print("[+] Backend iniciado exitosamente (Documentacion Swagger: http://127.0.0.1:8000/docs)")
        else:
            print("[!] Advertencia: Tiempo de espera agotado para el backend, iniciando frontend de todas formas...")

        # 5. Iniciar Frontend Electron
        print("[*] Iniciando Frontend Electron...")
        frontend_cmd = [npm_cmd, "start"]
        frontend_proc = subprocess.Popen(
            frontend_cmd,
            cwd=str(FRONTEND_DIR),
            shell=(os.name == "nt"),
        )

        print("[+] Ambos servicios estan en ejecucion.")
        print("    Cierra la ventana de la aplicacion o presiona Ctrl+C en la terminal para finalizar.")

        # Esperar a que termine el frontend (cuando el usuario cierra la ventana de Electron)
        frontend_proc.wait()
        print("\n[+] La ventana de Electron ha sido cerrada.")

    except KeyboardInterrupt:
        print("\n[!] Interrumpido por el usuario (Ctrl+C).")
    finally:
        # 6. Limpieza y cierre seguro de procesos
        print("[*] Finalizando procesos...")
        if frontend_proc:
            terminate_process(frontend_proc, "Frontend")
        if backend_proc:
            terminate_process(backend_proc, "Backend")
        print("[+] Todo cerrado correctamente.")


if __name__ == "__main__":
    main()