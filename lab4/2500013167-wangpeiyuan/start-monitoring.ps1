$ErrorActionPreference = 'Stop'
$labRoot = $PSScriptRoot
$labPromRuntime = Join-Path $labRoot '.runtime/prometheus'
$labGrafRuntime = Join-Path $labRoot '.runtime/grafana'
New-Item -ItemType Directory -Force $labPromRuntime, "$labGrafRuntime/data", "$labGrafRuntime/logs", "$labGrafRuntime/plugins", "$labGrafRuntime/dashboards" | Out-Null
Copy-Item -LiteralPath "$labRoot/grafana-dashboard.json" -Destination "$labGrafRuntime/dashboards/lab4.json" -Force
$labPromArgs = @("--config.file=`"$labRoot/prometheus.yml`"", "--storage.tsdb.path=`"$labPromRuntime`"", '--web.listen-address=127.0.0.1:9090')
$labProm = Start-Process -FilePath "$labRoot/.tools/prometheus/prometheus.exe" -ArgumentList $labPromArgs -WorkingDirectory $labRoot -WindowStyle Hidden -RedirectStandardOutput "$labPromRuntime/stdout.log" -RedirectStandardError "$labPromRuntime/stderr.log" -PassThru
$labProm.Id | Set-Content "$labPromRuntime/process.pid"
$env:GF_PATHS_DATA = "$labGrafRuntime/data"
$env:GF_PATHS_LOGS = "$labGrafRuntime/logs"
$env:GF_PATHS_PLUGINS = "$labGrafRuntime/plugins"
$env:GF_PATHS_PROVISIONING = "$labRoot/grafana/provisioning"
$env:LAB4_DASHBOARD_DIR = "$labGrafRuntime/dashboards"
$labGrafArgs = @('server', "--homepath=`"$labRoot/.tools/grafana`"", "--config=`"$labRoot/grafana.ini`"")
$labGraf = Start-Process -FilePath "$labRoot/.tools/grafana/bin/grafana.exe" -ArgumentList $labGrafArgs -WorkingDirectory "$labRoot/.tools/grafana" -WindowStyle Hidden -RedirectStandardOutput "$labGrafRuntime/stdout.log" -RedirectStandardError "$labGrafRuntime/stderr.log" -PassThru
$labGraf.Id | Set-Content "$labGrafRuntime/process.pid"
Write-Output "Prometheus PID: $($labProm.Id); Grafana PID: $($labGraf.Id)"
