# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import copy_metadata

root = Path(SPECPATH).parent
a = Analysis(
    [str(root / "packaging" / "desktop_backend.py")],
    pathex=[str(root)],
    datas=[(str(root / "database" / "schema.sql"), "database")]
          + copy_metadata("email-validator"),
    hiddenimports=["uvicorn.loops.asyncio", "uvicorn.protocols.http.h11_impl",
                   "uvicorn.lifespan.on"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="mansoviaje-api",
          console=True, upx=False)
bundle = COLLECT(exe, a.binaries, a.datas, name="mansoviaje-api", upx=False)
