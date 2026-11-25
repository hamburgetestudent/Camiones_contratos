"""Prepara recursos de distribución desde el mismo commit que las fuentes."""

import json
import re
import shutil
import subprocess
from html import unescape
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def git(*argumentos: str) -> str:
    return subprocess.check_output(
        ["git", *argumentos], cwd=RAIZ, text=True, encoding="utf-8"
    ).strip()


def main() -> None:
    cambios = git("status", "--porcelain")
    if cambios:
        raise SystemExit("Confirma los cambios en Git antes de identificar el paquete.")
    commit = git("rev-parse", "HEAD")
    version = json.loads((RAIZ / "package.json").read_text(encoding="utf-8"))["version"]
    destino = RAIZ / "build/entrega"
    destino.mkdir(parents=True, exist_ok=True)
    git(
        "archive", "--format=zip", f"--output={destino / 'fuentes.zip'}",
        commit, "--", ".", ":(exclude)frontend/herramientas/node.zip",
    )
    for nombre in ("README.md", "CHANGELOG.md", ".env.example"):
        shutil.copyfile(RAIZ / nombre, destino / nombre)
    shutil.copyfile(RAIZ / "docs/revision-externa.md", destino / "revision-externa.md")
    base = "https://github.com/hamburgetestudent/Camiones_contratos"
    (destino / "VERSION.txt").write_text(
        f"MansoViaje {version}\nWindows x64\nCommit {commit}\n"
        f"{base}/tree/{commit}\nCI y cobertura: {base}/commit/{commit}/checks\n",
        encoding="utf-8",
    )

    dist = RAIZ / "frontend/node_modules/electron/dist"
    chromium = (dist / "LICENSES.chromium.html").read_text(encoding="utf-8")
    node = re.search(
        r'<span class="title">Node\.js</span>.*?<pre>(.*?)</pre>', chromium, re.S
    )
    if not node:
        raise SystemExit("No se encontró el aviso de Node.js en la distribución de Electron.")
    python = (RAIZ / "build/backend/THIRD_PARTY_LICENSES_PYTHON.txt").read_text(encoding="utf-8")
    electron = (dist / "LICENSE").read_text(encoding="utf-8")
    (destino / "THIRD_PARTY_LICENSES.txt").write_text(
        "MansoViaje · Avisos de componentes distribuidos\n"
        "El archivo LICENSES.chromium.html junto al ejecutable contiene los avisos "
        "completos de Chromium y sus componentes.\n\n"
        f"Electron\n{electron}\n\nNode.js\n{unescape(node[1])}\n\n{python}",
        encoding="utf-8",
    )
    print(f"Recursos de MansoViaje {version} preparados desde {commit}.")


if __name__ == "__main__":
    main()
