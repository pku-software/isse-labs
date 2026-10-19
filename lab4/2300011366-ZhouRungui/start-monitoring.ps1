param(
    [int]$PrometheusPort = 9090,
    [int]$GrafanaPort = 3000
)

$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$prometheusRoot = Join-Path $projectRoot '.tools\prometheus'
$grafanaRoot = Join-Path $projectRoot '.tools\grafana'
$runtimeRoot = Join-Path $projectRoot '.runtime'

$prometheus = Get-ChildItem -LiteralPath $prometheusRoot -Filter 'prometheus.exe' -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
$grafanaServer = Get-ChildItem -LiteralPath $grafanaRoot -Filter 'grafana.exe' -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
$grafanaDefaults = Get-ChildItem -LiteralPath $grafanaRoot -Filter 'defaults.ini' -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Directory.Name -eq 'conf' } | Select-Object -First 1

if (-not $prometheus) { throw "Prometheus executable not found under $prometheusRoot. Extract the verified archive first." }
if (-not $grafanaServer -or -not $grafanaDefaults) { throw "Grafana files not found under $grafanaRoot. Extract the verified archive first." }

function Assert-LoopbackPortAvailable([int]$Port) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
    try {
        $listener.Start()
    } catch {
        throw "Local port $Port is already in use. Stop only the known owner or choose another port."
    } finally {
        $listener.Stop()
    }
}

Assert-LoopbackPortAvailable $PrometheusPort
Assert-LoopbackPortAvailable $GrafanaPort

$prometheusRuntime = Join-Path $runtimeRoot 'prometheus'
$prometheusLogs = Join-Path $prometheusRuntime 'logs'
$grafanaRuntime = Join-Path $runtimeRoot 'grafana'
$grafanaData = Join-Path $grafanaRuntime 'data'
$grafanaLogs = Join-Path $grafanaRuntime 'logs'
$grafanaPlugins = Join-Path $grafanaRuntime 'plugins'
$grafanaProvisioning = Join-Path $grafanaRuntime 'provisioning'
$grafanaProvisioningDatasources = Join-Path $grafanaProvisioning 'datasources'
$grafanaProvisioningDashboards = Join-Path $grafanaProvisioning 'dashboards'
$grafanaProvisioningPlugins = Join-Path $grafanaProvisioning 'plugins'
$grafanaDashboardFiles = Join-Path $grafanaRuntime 'dashboards'

foreach ($directory in @(
    $prometheusRuntime,
    $prometheusLogs,
    $grafanaData,
    $grafanaLogs,
    $grafanaPlugins,
    $grafanaProvisioningDatasources,
    $grafanaProvisioningDashboards,
    $grafanaProvisioningPlugins,
    $grafanaDashboardFiles
)) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
}

$datasourceProvisioning = @'
apiVersion: 1
datasources:
  - name: Prometheus
    uid: prometheus
    type: prometheus
    access: proxy
    url: http://127.0.0.1:9090
    isDefault: true
    editable: true
'@
[System.IO.File]::WriteAllText(
    (Join-Path $grafanaProvisioningDatasources 'prometheus.yml'),
    $datasourceProvisioning.TrimStart([char[]]"`r`n"),
    [System.Text.UTF8Encoding]::new($false)
)

$dashboardProvider = @"
apiVersion: 1
providers:
  - name: Lab 4
    orgId: 1
    folder: Lab 4
    type: file
    disableDeletion: true
    allowUiUpdates: true
    options:
      path: `"$($grafanaDashboardFiles.Replace('\','/'))`"
      foldersFromFilesStructure: false
"@
[System.IO.File]::WriteAllText(
    (Join-Path $grafanaProvisioningDashboards 'lab4.yml'),
    $dashboardProvider.TrimStart([char[]]"`r`n"),
    [System.Text.UTF8Encoding]::new($false)
)

$dashboardFile = Join-Path $projectRoot 'grafana-dashboard.json'
$dashboard = Get-Content -LiteralPath $dashboardFile -Raw -Encoding UTF8 | ConvertFrom-Json
$dashboard.PSObject.Properties.Remove('__inputs')
$dashboard | Add-Member -NotePropertyName 'uid' -NotePropertyValue 'lab4-chat-monitoring' -Force
foreach ($panel in $dashboard.panels) {
    if ($panel.datasource -and $panel.datasource.type -eq 'prometheus') {
        $panel.datasource.uid = 'prometheus'
    }
}
[System.IO.File]::WriteAllText(
    (Join-Path $grafanaDashboardFiles 'lab4-chat-monitoring.json'),
    ($dashboard | ConvertTo-Json -Depth 100),
    [System.Text.UTF8Encoding]::new($false)
)

$prometheusBin = $prometheus.Directory.FullName
$prometheusArgs = @(
    "--config.file=`"$(Join-Path $projectRoot 'prometheus.yml')`"",
    "--storage.tsdb.path=`"$prometheusRuntime`"",
    "--web.listen-address=127.0.0.1:$PrometheusPort",
    "--web.console.templates=`"$(Join-Path $prometheusBin 'consoles')`"",
    "--web.console.libraries=`"$(Join-Path $prometheusBin 'console_libraries')`""
) -join ' '

$prometheusProcess = Start-Process -PassThru -WindowStyle Hidden `
    -FilePath $prometheus.FullName `
    -ArgumentList $prometheusArgs `
    -WorkingDirectory $prometheusBin `
    -RedirectStandardOutput (Join-Path $prometheusLogs 'stdout.log') `
    -RedirectStandardError (Join-Path $prometheusLogs 'stderr.log')

$grafanaHome = Split-Path (Split-Path $grafanaDefaults.FullName -Parent) -Parent
$grafanaArgs = "server --homepath=`"$grafanaHome`" --config=`"$($grafanaDefaults.FullName)`""
$grafanaEnvironment = @{
    GF_SERVER_HTTP_ADDR     = '127.0.0.1'
    GF_SERVER_HTTP_PORT     = [string]$GrafanaPort
    GF_PATHS_DATA           = $grafanaData
    GF_PATHS_LOGS           = $grafanaLogs
    GF_PATHS_PLUGINS        = $grafanaPlugins
    GF_PATHS_PROVISIONING   = $grafanaProvisioning
}
$oldEnvironment = @{}
$grafanaProcess = $null

try {
    foreach ($name in $grafanaEnvironment.Keys) {
        $oldEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
        [Environment]::SetEnvironmentVariable($name, $grafanaEnvironment[$name], 'Process')
    }
    $grafanaProcess = Start-Process -PassThru -WindowStyle Hidden `
        -FilePath $grafanaServer.FullName `
        -ArgumentList $grafanaArgs `
        -WorkingDirectory $grafanaHome `
        -RedirectStandardOutput (Join-Path $grafanaLogs 'stdout.log') `
        -RedirectStandardError (Join-Path $grafanaLogs 'stderr.log')
} catch {
    Stop-Process -Id $prometheusProcess.Id -Force -ErrorAction SilentlyContinue
    throw
} finally {
    foreach ($name in $oldEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $oldEnvironment[$name], 'Process')
    }
}

$pidFile = Join-Path $runtimeRoot 'monitoring-pids.json'
@{
    prometheus = @{ pid = $prometheusProcess.Id; executable = $prometheus.FullName }
    grafana    = @{ pid = $grafanaProcess.Id; executable = $grafanaServer.FullName }
} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $pidFile -Encoding UTF8

Write-Output "Prometheus: http://127.0.0.1:$PrometheusPort/"
Write-Output "Grafana:    http://127.0.0.1:$GrafanaPort/"
Write-Output 'Local services were started in hidden windows; stop only these recorded processes with stop-monitoring.ps1.'
