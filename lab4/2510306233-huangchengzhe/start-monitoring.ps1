$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$tools = Join-Path $here ".tools"
$runtime = Join-Path $here ".runtime"

$env:LAB4_DASHBOARD_DIR = Join-Path $here "dashboards"
$env:GF_PATHS_DATA = Join-Path $runtime "grafana\data"
$env:GF_PATHS_LOGS = Join-Path $runtime "grafana\logs"
$env:GF_PATHS_PLUGINS = Join-Path $runtime "grafana\plugins"
$env:GF_PATHS_PROVISIONING = Join-Path $here "provisioning"

New-Item -ItemType Directory -Force -Path $env:GF_PATHS_DATA | Out-Null
New-Item -ItemType Directory -Force -Path $env:GF_PATHS_LOGS | Out-Null
New-Item -ItemType Directory -Force -Path $env:GF_PATHS_PLUGINS | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $runtime "prometheus") | Out-Null

$prom = Join-Path $tools "prometheus\prometheus.exe"
$grafana = Join-Path $tools "grafana\bin\grafana.exe"
$promCfg = Join-Path $here "prometheus.yml"
$promData = Join-Path $runtime "prometheus"
$grafanaIni = Join-Path $here "grafana.ini"

Start-Process -FilePath $prom -ArgumentList @(
  "--config.file=$promCfg",
  "--storage.tsdb.path=$promData",
  "--web.listen-address=127.0.0.1:9090"
) -WorkingDirectory $here -WindowStyle Hidden

Start-Process -FilePath $grafana -ArgumentList @(
  "server",
  "--config=$grafanaIni",
  "--homepath=$tools\grafana"
) -WorkingDirectory $here -WindowStyle Hidden

Write-Host "Prometheus: http://127.0.0.1:9090"
Write-Host "Grafana:    http://127.0.0.1:3000"
