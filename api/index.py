"""Entrypoint para Vercel Serverless Functions.

Expone la instancia ``app`` de FastAPI definida en ``backend/app/main.py``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app  # noqa: E402

__all__ = ["app"]
