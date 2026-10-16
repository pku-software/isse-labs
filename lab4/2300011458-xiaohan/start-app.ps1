$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$runtimeRoot = Join-Path $projectRoot ".runtime\app"

if (-not (Test-Path -LiteralPath $python)) {
    throw "未找到 .venv，请先创建虚拟环境并安装 requirements.txt。"
}

New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null
$process = Start-Process -FilePath $python `
    -ArgumentList (Join-Path $projectRoot "app.py") `
    -WorkingDirectory $projectRoot `
    -WindowStyle Hidden `
    -Environment @{ LAB4_APP_MODE = "mock"; LAB4_PORT = "5001" } `
    -RedirectStandardOutput (Join-Path $runtimeRoot "stdout.log") `
    -RedirectStandardError (Join-Path $runtimeRoot "stderr.log") `
    -PassThru

$process.Id | Set-Content -Encoding ascii -LiteralPath (Join-Path $runtimeRoot "app.pid")
Write-Output "应用已启动：http://127.0.0.1:5001/ （PID $($process.Id)）"
