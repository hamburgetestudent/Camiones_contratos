# Requiere Windows x64, Git, Node/npm y .venv de Python 3.12.
$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..')
try {
    $python = '.\.venv\Scripts\python.exe'
    $version = (Get-Content -Raw package.json | ConvertFrom-Json).version
    $commit = git rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Se requiere una copia Git.' }
    $cambios = git status --porcelain
    if ($cambios) { throw 'Confirma los cambios antes de generar la entrega.' }

    & $python -m pip install -r packaging/requirements-windows.lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'Falló la instalación de dependencias Python.' }
    npm.cmd --prefix frontend ci
    if ($LASTEXITCODE -ne 0) { throw 'Falló npm ci.' }
    # Electron 44 instala su runtime bajo demanda, incluso después de npm ci.
    & .\frontend\node_modules\.bin\install-electron.cmd
    if ($LASTEXITCODE -ne 0) { throw 'Falló la preparación del runtime y sus avisos de Electron.' }
    & $python scripts/build_backend.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la construcción del backend.' }
    & $python scripts/preparar_entrega.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la preparación de fuentes y avisos.' }
    npm.cmd --prefix frontend run dist:win
    if ($LASTEXITCODE -ne 0) { throw 'Falló la construcción del instalador.' }

    $archivo = "MansoViaje-$version-win-x64.exe"
    $ruta = Join-Path release $archivo
    $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ruta).Hash
    "$sha  $archivo" | Set-Content -Encoding ascii "release/SHA256SUMS.txt"
    foreach ($nombre in 'VERSION.txt', 'README.md', 'revision-externa.md', 'fuentes.zip', 'CHANGELOG.md') {
        Copy-Item -LiteralPath "build/entrega/$nombre" -Destination "release/$nombre"
    }
    Write-Output "$ruta | commit $commit | SHA256 $sha"
} finally {
    Pop-Location
}
