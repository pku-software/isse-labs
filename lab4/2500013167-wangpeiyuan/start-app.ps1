param([int]$Port = 5001)
$ErrorActionPreference = 'Stop'
$env:MODEL_MODE = 'mock'
$env:APP_PORT = "$Port"
& "$PSScriptRoot/.venv/Scripts/python.exe" "$PSScriptRoot/app.py"
