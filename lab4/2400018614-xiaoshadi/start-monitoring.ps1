# 启动 Prometheus（9090）和 Grafana（3000），只监听本机。
# 所有数据、日志都写在 .runtime/ 下，工具本体留在 .tools/ 下，两者都不提交。

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$prometheus = Join-Path $here ".tools\prometheus\prometheus.exe"
$grafana = Join-Path $here ".tools\grafana\bin\grafana.exe"
if (-not (Test-Path $prometheus) -or -not (Test-Path $grafana)) {
    throw "找不到 Prometheus 或 Grafana，请先按 README 把工具解压到 .tools/ 下"
}

$promDir = Join-Path $here ".runtime\prometheus"
$grafDir = Join-Path $here ".runtime\grafana"
New-Item -ItemType Directory -Force -Path $promDir, $grafDir, `
    (Join-Path $grafDir "data"), (Join-Path $grafDir "logs"), (Join-Path $grafDir "plugins") | Out-Null

$promProcess = Start-Process -FilePath $prometheus -WorkingDirectory $here `
    -ArgumentList "--config.file=$here\prometheus.yml", "--storage.tsdb.path=$promDir", `
                  "--web.listen-address=127.0.0.1:9090" `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $promDir "prometheus.log") `
    -RedirectStandardError (Join-Path $promDir "prometheus.err.log") -PassThru
$promProcess.Id | Set-Content -Path (Join-Path $promDir "prometheus.pid")

$grafProcess = Start-Process -FilePath $grafana -WorkingDirectory $here `
    -ArgumentList "server", "--homepath=$here\.tools\grafana", "--config=$here\grafana.ini" `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $grafDir "grafana.out.log") `
    -RedirectStandardError (Join-Path $grafDir "grafana.err.log") -PassThru
$grafProcess.Id | Set-Content -Path (Join-Path $grafDir "grafana.pid")

Write-Host "Prometheus: http://127.0.0.1:9090/targets"
Write-Host "Grafana:    http://127.0.0.1:3000/d/lab4-chat-monitoring"
