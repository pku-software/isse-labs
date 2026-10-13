param(
    [ValidateSet('All', 'Prometheus', 'Grafana')][string]$Service = 'All',
    [ValidateRange(1024, 65535)][int]$PrometheusPort = 9090,
    [ValidateRange(1024, 65535)][int]$GrafanaPort = 3000
)

$ErrorActionPreference = 'Stop'
$labRoot = $PSScriptRoot

function Start-LabService {
    param([string]$Name, [string]$Executable, [string[]]$Arguments,
          [string]$Runtime, [int]$Port, [string]$HealthPath)
    if (-not (Test-Path -LiteralPath $Executable)) {
        throw "Missing $Name executable: $Executable. Follow README.md installation instructions."
    }
    New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
    $metadataPath = Join-Path $Runtime 'process.json'
    $listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if ($listener) {
        if (Test-Path -LiteralPath $metadataPath) {
            $saved = Get-Content -Raw -LiteralPath $metadataPath | ConvertFrom-Json
            $existing = Get-Process -Id $saved.process_id -ErrorAction SilentlyContinue
            if ($existing -and $existing.Path -eq $Executable -and
                $existing.StartTime.ToUniversalTime() -eq ([DateTime]$saved.started_at_utc).ToUniversalTime() -and
                @($listener | Where-Object OwningProcess -eq $existing.Id).Count -gt 0) {
                Write-Host "$Name is already running on 127.0.0.1:$Port (PID $($existing.Id))."
                return
            }
        }
        throw "Port $Port is occupied by another process. Choose another port; do not stop it."
    }
    $launched = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $labRoot `
        -WindowStyle Hidden -RedirectStandardOutput (Join-Path $Runtime 'stdout.log') `
        -RedirectStandardError (Join-Path $Runtime 'stderr.log') -PassThru
    @{
        name = $Name; process_id = $launched.Id; executable = $Executable; port = $Port
        started_at_utc = $launched.StartTime.ToUniversalTime().ToString('o')
    } | ConvertTo-Json | Set-Content -Encoding utf8 -LiteralPath $metadataPath
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        if ($launched.HasExited) { throw "$Name exited. Inspect $Runtime/stdout.log and stderr.log." }
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port$HealthPath" -NoProxy -TimeoutSec 1
            if ($response.StatusCode -eq 200) {
                Write-Host "$Name ready: http://127.0.0.1:$Port (PID $($launched.Id))."
                return
            }
        } catch {}
        Start-Sleep -Milliseconds 300
    }
    throw "$Name has not become ready; inspect its logs before retrying."
}

if ($Service -in @('All', 'Prometheus')) {
    $prometheusExe = Join-Path $labRoot '.tools/prometheus/prometheus.exe'
    $prometheusRuntime = Join-Path $labRoot '.runtime/prometheus'
    $prometheusConfig = Join-Path $labRoot 'prometheus.yml'
    Start-LabService -Name 'Prometheus' -Executable $prometheusExe -Runtime $prometheusRuntime `
        -Port $PrometheusPort -HealthPath '/-/ready' -Arguments @(
            "--config.file=`"$prometheusConfig`"",
            "--storage.tsdb.path=`"$prometheusRuntime`"",
            '--storage.tsdb.retention.time=7d',
            "--web.listen-address=127.0.0.1:$PrometheusPort"
        )
}

if ($Service -in @('All', 'Grafana')) {
    $grafanaHome = Join-Path $labRoot '.tools/grafana'
    $grafanaRuntime = Join-Path $labRoot '.runtime/grafana'
    $grafanaDashboards = Join-Path $grafanaRuntime 'dashboards'
    foreach ($subdirectory in @('data', 'log', 'plugins', 'dashboards')) {
        New-Item -ItemType Directory -Force -Path (Join-Path $grafanaRuntime $subdirectory) | Out-Null
    }
    # Grafana scans these folders even when no extra plugins or alert rules are configured.
    foreach ($subdirectory in @('plugins', 'alerting')) {
        New-Item -ItemType Directory -Force -Path (Join-Path $labRoot "grafana-provisioning/$subdirectory") | Out-Null
    }
    Copy-Item -LiteralPath (Join-Path $labRoot 'grafana-dashboard.json') `
        -Destination (Join-Path $grafanaDashboards 'grafana-dashboard.json') -Force
    $grafanaVariables = @{
        LAB4_PROMETHEUS_URL = "http://127.0.0.1:$PrometheusPort"
        LAB4_GRAFANA_DATA = (Join-Path $grafanaRuntime 'data')
        LAB4_GRAFANA_LOGS = (Join-Path $grafanaRuntime 'log')
        LAB4_GRAFANA_PLUGINS = (Join-Path $grafanaRuntime 'plugins')
        LAB4_GRAFANA_DASHBOARDS = $grafanaDashboards
        LAB4_GRAFANA_HOME_DASHBOARD = (Join-Path $labRoot 'grafana-dashboard.json')
        LAB4_GRAFANA_PROVISIONING = (Join-Path $labRoot 'grafana-provisioning')
        GF_SERVER_HTTP_PORT = [string]$GrafanaPort
    }
    $previousValues = @{}
    try {
        foreach ($key in $grafanaVariables.Keys) {
            $previousValues[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
            [Environment]::SetEnvironmentVariable($key, $grafanaVariables[$key], 'Process')
        }
        Start-LabService -Name 'Grafana' -Executable (Join-Path $grafanaHome 'bin/grafana.exe') `
            -Runtime $grafanaRuntime -Port $GrafanaPort -HealthPath '/api/health' -Arguments @(
                'server', "--homepath=`"$grafanaHome`"",
                "--config=`"$(Join-Path $labRoot 'grafana.ini')`""
            )
    } finally {
        foreach ($key in $previousValues.Keys) {
            [Environment]::SetEnvironmentVariable($key, $previousValues[$key], 'Process')
        }
    }
}
