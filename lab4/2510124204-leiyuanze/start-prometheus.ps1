$root = $PSScriptRoot
$exe = Join-Path $root ".tools\prometheus\prometheus.exe"
if (-not (Test-Path $exe)) { Write-Error "未找到 $exe，请先下载解压 Prometheus"; exit 1 }
New-Item -ItemType Directory -Force -Path (Join-Path $root ".runtime\app") | Out-Null
$proc = Start-Process -FilePath $exe `
  -ArgumentList "--config.file=prometheus.yml", "--storage.tsdb.path=.runtime/prometheus", "--web.listen-address=127.0.0.1:9090" `
  -WorkingDirectory $root -WindowStyle Hidden `
  -RedirectStandardOutput (Join-Path $root ".runtime\app\prometheus-stdout.log") `
  -RedirectStandardError (Join-Path $root ".runtime\app\prometheus-stderr.log") -PassThru
$proc.Id | Out-File -Encoding ascii (Join-Path $root ".runtime\app\prometheus.pid")
Write-Host "Prometheus 已启动：http://127.0.0.1:9090（PID $($proc.Id)）"