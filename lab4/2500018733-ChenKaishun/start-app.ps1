param(
    [ValidateSet('mock', 'real')][string]$Mode = 'mock',
    [ValidateRange(1024, 65535)][int]$Port = 5001
)

$ErrorActionPreference = 'Stop'
$appPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $appPython)) {
    throw '请先在个人目录创建 .venv 并安装 requirements.txt 中的依赖。'
}
$previousMode = $env:CHAT_MODE
$previousPort = $env:PORT
$previousUtf8 = $env:PYTHONUTF8
try {
    $env:CHAT_MODE = $Mode
    $env:PORT = "$Port"
    $env:PYTHONUTF8 = '1'
    & $appPython (Join-Path $PSScriptRoot 'app.py')
} finally {
    $env:CHAT_MODE = $previousMode
    $env:PORT = $previousPort
    $env:PYTHONUTF8 = $previousUtf8
}
