$root = $PSScriptRoot
$exe = Join-Path $root ".tools\grafana\bin\grafana.exe"
$grafanaHome = Join-Path $root ".tools\grafana"
if (-not (Test-Path $exe)) { Write-Error "未找到 $exe，请先下载解压 Grafana"; exit 1 }
New-Item -ItemType Directory -Force -Path (Join-Path $root ".runtime\app") | Out-Null
$proc = Start-Process -FilePath $exe -ArgumentList "server", "--config", "grafana.ini", "--homepath", "`"$grafanaHome`"" `
  -WorkingDirectory $root -WindowStyle Hidden `
  -RedirectStandardOutput (Join-Path $root ".runtime\app\grafana-stdout.log") `
  -RedirectStandardError (Join-Path $root ".runtime\app\grafana-stderr.log") -PassThru
$proc.Id | Out-File -Encoding ascii (Join-Path $root ".runtime\app\grafana.pid")
Write-Host "Grafana 已启动：http://127.0.0.1:3000（PID $($proc.Id)）"