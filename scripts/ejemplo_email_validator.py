"""Ejemplo ejecutable de la dependencia email-validator.

Uso: python scripts/ejemplo_email_validator.py
Muestra la versión instalada y valida el correo con el mismo modelo del proyecto.
"""

import sys
from importlib.metadata import version
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import ValidationError  # noqa: E402

from domain.modelos_usuario import UsuarioBase  # noqa: E402

CASOS = ["ana@empresa.cl", "ana@@empresa.cl", "ana@empresa", "ana perez@empresa.cl", "a..b@empresa.cl"]

if __name__ == "__main__":
    print(f"email-validator {version('email-validator')}")
    for correo in CASOS:
        try:
            UsuarioBase(nombre="Ana", email=correo, rol="DADOR_CARGA")
            print(f"OK       {correo}")
        except ValidationError as exc:
            print(f"RECHAZA  {correo} -> {exc.errors()[0]['msg']}")
