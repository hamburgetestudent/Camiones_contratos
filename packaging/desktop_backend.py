"""Servidor local cuyo ciclo de vida pertenece al proceso principal de Electron."""

import sys
from threading import Thread

import uvicorn

from app.main import app


def ejecutar() -> None:
    config = uvicorn.Config(
        app, host="127.0.0.1", port=8000, workers=1, loop="asyncio", http="h11",
        ws="none", lifespan="on", timeout_graceful_shutdown=5,
    )
    servidor = uvicorn.Server(config)

    def esperar_cierre() -> None:
        # Electron cierra la tubería al salir, incluso si su proceso termina de golpe.
        sys.stdin.buffer.readline()
        servidor.should_exit = True

    Thread(target=esperar_cierre, daemon=True).start()
    servidor.run()


if __name__ == "__main__":
    ejecutar()
