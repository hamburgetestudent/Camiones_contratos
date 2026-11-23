"""Entrypoint para Vercel Serverless Functions.

Expone la instancia ``app`` de FastAPI definida en ``main.py``.
"""

from main import app

__all__ = ["app"]
