$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$monitorRoot = $PSScriptRoot.Replace('\', '/')
New-Item -ItemType Directory -Force -Path '.runtime/prometheus', '.runtime/grafana/data', '.runtime/grafana/logs', '.runtime/grafana/plugins' | Out-Null
$env:GF_PATHS_DATA = "$monitorRoot/.runtime/grafana/data"
$env:GF_PATHS_LOGS = "$monitorRoot/.runtime/grafana/logs"
$env:GF_PATHS_PLUGINS = "$monitorRoot/.runtime/grafana/plugins"
$env:GF_PATHS_PROVISIONING = "$monitorRoot/provisioning"
$env:LAB4_DASHBOARD_DIR = "$monitorRoot/dashboards"
foreach ($listenPort in @(9090, 3000)) {
    if (Get-NetTCPConnection -LocalPort $listenPort -State Listen -ErrorAction SilentlyContinue) {
        throw "Port $listenPort is already in use; no existing process was stopped."
    }
}
$promProcess = Start-Process -FilePath "$PSScriptRoot/.tools/prometheus/prometheus.exe" -ArgumentList '--config.file=prometheus.yml', '--storage.tsdb.path=.runtime/prometheus', '--web.listen-address=127.0.0.1:9090' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput '.runtime/prometheus/stdout.log' -RedirectStandardError '.runtime/prometheus/stderr.log' -PassThru
$promProcess.Id | Set-Content '.runtime/prometheus/process.pid'
$grafArgs = @('server', ('--homepath="' + $monitorRoot + '/.tools/grafana"'), ('--config="' + $monitorRoot + '/grafana.ini"'))
$grafProcess = Start-Process -FilePath "$PSScriptRoot/.tools/grafana/bin/grafana.exe" -ArgumentList $grafArgs -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput '.runtime/grafana/stdout.log' -RedirectStandardError '.runtime/grafana/stderr.log' -PassThru
$grafProcess.Id | Set-Content '.runtime/grafana/process.pid'
Write-Output "Prometheus PID: $($promProcess.Id); Grafana PID: $($grafProcess.Id)"
