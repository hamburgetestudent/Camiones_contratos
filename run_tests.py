"""Script runner para ejecutar todos los tests del proyecto y calcular la cobertura de código.

Uso:
    python run_tests.py          # Corre tests y muestra cobertura en consola
    python run_tests.py --html   # Genera reporte interactivo HTML en htmlcov/
    python run_tests.py --clean  # Elimina archivos temporales de cobertura (.coverage, htmlcov, *.cover)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def limpiar_archivos_temporales(project_root: Path) -> None:
    """Elimina archivos y carpetas temporales generados por herramientas de cobertura."""
    eliminados = 0

    # 1. Eliminar archivos *.cover y .coverage*
    for patron in ("*.cover", ".coverage", ".coverage.*"):
        for archivo in project_root.rglob(patron):
            try:
                if archivo.is_file():
                    archivo.unlink()
                    eliminados += 1
            except OSError:
                pass

    # 2. Eliminar carpeta htmlcov
    htmlcov_dir = project_root / "htmlcov"
    if htmlcov_dir.is_dir():
        try:
            shutil.rmtree(htmlcov_dir)
            eliminados += 1
        except OSError:
            pass

    print(f"Limpieza completada. Se eliminaron {eliminados} elementos temporales.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ejecuta la suite de pruebas unitarias y genera el reporte de cobertura de código."
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Genera un reporte interactivo en HTML dentro del directorio htmlcov/",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Limpia archivos y directorios temporales de cobertura (.coverage, *.cover, htmlcov/)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent

    if args.clean:
        limpiar_archivos_temporales(project_root)
        return 0

    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(project_root)
        if not current_pythonpath
        else f"{project_root}{os.pathsep}{current_pythonpath}"
    )

    print("=" * 70)
    print("1. Ejecutando tests unitarios con medición de líneas y ramas...")
    print("=" * 70)

    # 1. Ejecutar pruebas con coverage
    run_cmd = [
        sys.executable,
        "-m",
        "coverage",
        "run",
        "-m",
        "unittest",
        "discover",
        "-t",
        ".",
        "-s",
        "tests",
    ]
    test_result = subprocess.run(run_cmd, cwd=project_root, env=env)

    print("\n" + "=" * 70)
    print("2. Reporte de Cobertura de Código (Líneas y Ramas)")
    print("=" * 70)

    # 2. Generar reporte en terminal
    report_cmd = [sys.executable, "-m", "coverage", "report", "-m"]
    subprocess.run(report_cmd, cwd=project_root, env=env)

    # 3. Reporte HTML opcional
    if args.html:
        print("\n" + "=" * 70)
        print("3. Generando reporte HTML interactivo...")
        print("=" * 70)
        html_cmd = [sys.executable, "-m", "coverage", "html"]
        subprocess.run(html_cmd, cwd=project_root, env=env)
        html_index = project_root / "htmlcov" / "index.html"
        print(f"Reporte HTML disponible en: {html_index}")

    return test_result.returncode


if __name__ == "__main__":
    sys.exit(main())
