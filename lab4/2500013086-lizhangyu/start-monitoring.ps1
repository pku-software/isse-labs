param([switch]$AppOnly)
$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
$Prometheus = Join-Path $Project '.tools\prometheus\prometheus.exe'
$Grafana = Join-Path $Project '.tools\grafana\bin\grafana-server.exe'
if (!(Test-Path $Prometheus) -or (!$AppOnly -and !(Test-Path $Grafana))) {
    throw 'Tools are missing from .tools\prometheus or .tools\grafana.'
}
$Runtime = Join-Path $Project '.runtime'
$PromData = Join-Path $Runtime 'prometheus'
$GrafanaData = Join-Path $Runtime 'grafana\data'
$GrafanaLogs = Join-Path $Runtime 'grafana\log'
$GrafanaPlugins = Join-Path $Runtime 'grafana\plugins'
New-Item -ItemType Directory -Force $PromData, $GrafanaData, $GrafanaLogs, $GrafanaPlugins | Out-Null
$PromArgs = @('--config.file=' + (Join-Path $Project 'prometheus.yml'), '--storage.tsdb.path=' + $PromData, '--web.listen-address=127.0.0.1:9090')
Start-Process -FilePath $Prometheus -ArgumentList $PromArgs -WorkingDirectory $Project -WindowStyle Hidden -RedirectStandardOutput (Join-Path $Runtime 'prometheus.stdout.log') -RedirectStandardError (Join-Path $Runtime 'prometheus.stderr.log')
if (!$AppOnly) {
    $env:GF_PATHS_DATA = $GrafanaData
    $env:GF_PATHS_LOGS = $GrafanaLogs
    $env:GF_PATHS_PLUGINS = $GrafanaPlugins
    $env:GF_PATHS_PROVISIONING = Join-Path $Project 'provisioning'
    $env:GF_SERVER_HTTP_ADDR = '127.0.0.1'
    $env:GF_SERVER_HTTP_PORT = '3000'
    $HomePath = Split-Path -Parent (Split-Path -Parent $Grafana)
    Start-Process -FilePath $Grafana -ArgumentList @('--homepath=' + $HomePath) -WorkingDirectory $Project -WindowStyle Hidden -RedirectStandardOutput (Join-Path $Runtime 'grafana.stdout.log') -RedirectStandardError (Join-Path $Runtime 'grafana.stderr.log')
}
Write-Output 'Prometheus: http://127.0.0.1:9090/targets'
if (!$AppOnly) { Write-Output 'Grafana: http://127.0.0.1:3000' }
