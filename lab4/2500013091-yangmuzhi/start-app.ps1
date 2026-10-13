param([ValidateRange(1024, 65535)][int]$Port = 5001)

$ErrorActionPreference = 'Stop'
$labPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $labPython)) {
    throw 'Create .venv and install requirements.txt first; see README.md.'
}
$previousMode = $env:LAB4_MODEL_MODE
$previousPort = $env:LAB4_PORT
try {
    $env:LAB4_MODEL_MODE = 'mock'
    $env:LAB4_PORT = [string]$Port
    & $labPython -u (Join-Path $PSScriptRoot 'app.py')
} finally {
    $env:LAB4_MODEL_MODE = $previousMode
    $env:LAB4_PORT = $previousPort
}
