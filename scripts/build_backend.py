"""Construye el backend Windows x64 con el entorno congelado de la entrega."""

import platform
import subprocess
import sys
from importlib.metadata import distribution
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "backend"


def generar_avisos() -> None:
    licencia_python = Path(sys.base_prefix) / "LICENSE.txt"
    textos = [f"Python {platform.python_version()}", licencia_python.read_text(encoding="utf-8")]
    for linea in (ROOT / "packaging/requirements-windows.lock.txt").read_text().splitlines():
        nombre, version = linea.split("==")
        paquete = distribution(nombre)
        if paquete.version != version:
            raise RuntimeError(f"Se requiere {linea}, instalado {paquete.version}")
        avisos = [
            f for f in paquete.files or []
            if "licenses" in f.parts
            or f.name.lower().split(".")[0] in {"license", "licence", "copying", "notice"}
        ]
        if not avisos:
            raise RuntimeError(f"Revisar avisos para {linea}")
        textos.append(linea)
        for archivo in avisos:
            textos.extend((str(archivo), Path(paquete.locate_file(archivo)).read_text(
                encoding="utf-8-sig", errors="replace"
            )))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "THIRD_PARTY_LICENSES_PYTHON.txt").write_text("\n\n".join(textos), encoding="utf-8")


if __name__ == "__main__":
    if sys.platform != "win32" or platform.machine().upper() not in {"AMD64", "X86_64"}:
        raise SystemExit("Esta distribución se construye en Windows x64.")
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("Construir con Python 3.12 x64 y el lock de Windows.")
    generar_avisos()
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
         "--distpath", str(OUT), "--workpath", str(ROOT / "build/pyinstaller"),
         str(ROOT / "packaging/backend.spec")],
        cwd=ROOT,
        check=True,
    )
