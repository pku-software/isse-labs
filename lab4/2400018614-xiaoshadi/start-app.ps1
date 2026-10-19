# 启动本地聊天应用（mock 模式，不需要 DeepSeek Key）。
# 日志写入 .runtime/app/，进程号写入 .runtime/app/app.pid 便于之后停止。

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$python = Join-Path $here ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "找不到 .venv，请先创建虚拟环境并安装 requirements.txt 中的依赖"
}

$runtime = Join-Path $here ".runtime\app"
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$log = Join-Path $runtime "app.log"

# 本次实验固定使用 mock 模式：不调用真实模型，也就不需要任何 Key
$env:CHAT_MODE = "mock"

$process = Start-Process -FilePath $python -ArgumentList "app.py" -WorkingDirectory $here `
    -WindowStyle Hidden -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru
$process.Id | Set-Content -Path (Join-Path $runtime "app.pid")

Write-Host "已启动聊天应用（mock 模式），PID $($process.Id)"
Write-Host "页面：http://127.0.0.1:5001/"
Write-Host "指标：http://127.0.0.1:5001/metrics"
