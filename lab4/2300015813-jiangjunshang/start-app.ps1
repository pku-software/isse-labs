$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:CHAT_MODE = 'mock'
& "$PSScriptRoot/.venv/Scripts/python.exe" "$PSScriptRoot/app.py"
exit $LASTEXITCODE
