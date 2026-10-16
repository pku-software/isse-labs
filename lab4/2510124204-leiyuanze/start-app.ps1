param([int]$Port = 5001)
$root = $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { Write-Error "未找到 $python，请先创建虚拟环境并安装 requirements.txt"; exit 1 }
New-Item -ItemType Directory -Force -Path (Join-Path $root ".runtime\app") | Out-Null
$proc = Start-Process -FilePath $python -ArgumentList "app.py" -WorkingDirectory $root -WindowStyle Hidden `
  -RedirectStandardOutput (Join-Path $root ".runtime\app\stdout.log") `
  -RedirectStandardError (Join-Path $root ".runtime\app\stderr.log") -PassThru
$proc.Id | Out-File -Encoding ascii (Join-Path $root ".runtime\app\app.pid")
Write-Host "聊天应用已启动：http://127.0.0.1:$Port（PID $($proc.Id)）"