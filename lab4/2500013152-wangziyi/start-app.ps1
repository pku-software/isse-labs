$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$env:CHAT_MODE = 'mock'
$env:PORT = '5001'
& "$PSScriptRoot/.venv/Scripts/python.exe" "$PSScriptRoot/app.py"
