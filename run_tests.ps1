# Script de ejecución para Windows PowerShell
param (
    [switch]$Html,
    [switch]$Clean
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    $pythonPath = "python"
}

if ($Clean) {
    & $pythonPath (Join-Path $projectRoot "run_tests.py") --clean
} elseif ($Html) {
    & $pythonPath (Join-Path $projectRoot "run_tests.py") --html
} else {
    & $pythonPath (Join-Path $projectRoot "run_tests.py")
}
