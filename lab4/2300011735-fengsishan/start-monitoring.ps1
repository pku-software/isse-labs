$ErrorActionPreference = 'Stop'
$lab4Root = $PSScriptRoot
$lab4Repo = (Resolve-Path -LiteralPath (Join-Path $lab4Root '../..')).Path
$lab4Prefix = 'lab4/2300011735-fengsishan'

foreach ($lab4Relative in @('.tools/prometheus/prometheus.exe', '.tools/grafana/bin/grafana-server.exe', '.runtime/prometheus/wal', '.runtime/grafana/data/grafana.db', '.runtime/grafana/log/grafana.log', '.runtime/grafana/plugins/plugin.json')) {
    git -C $lab4Repo check-ignore -q -- "$lab4Prefix/$lab4Relative"
    if ($LASTEXITCODE -ne 0) { throw "Runtime path not ignored: $lab4Relative" }
}
$lab4Tracked = git -C $lab4Repo ls-files -- "$lab4Prefix/.tools" "$lab4Prefix/.runtime" "$lab4Prefix/.venv"
if ($lab4Tracked) { throw 'Tools or runtime files are tracked. Resolve this before starting.' }

$lab4PromExe = Join-Path $lab4Root '.tools/prometheus/prometheus.exe'
$lab4GrafanaHome = Join-Path $lab4Root '.tools/grafana'
$lab4GrafanaExe = Join-Path $lab4GrafanaHome 'bin/grafana-server.exe'
if (-not (Test-Path -LiteralPath $lab4GrafanaExe)) { $lab4GrafanaExe = Join-Path $lab4GrafanaHome 'bin/grafana.exe' }
foreach ($lab4Exe in @($lab4PromExe, $lab4GrafanaExe)) {
    if (-not (Test-Path -LiteralPath $lab4Exe)) { throw "Missing tool: $lab4Exe. Run install-tools.py first." }
}
foreach ($lab4Port in @(9090, 3000)) {
    $lab4Socket = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $lab4Port)
    try { $lab4Socket.Start() } catch { throw "Port $lab4Port is occupied; no existing service was stopped." } finally { $lab4Socket.Stop() }
}
foreach ($lab4Relative in @('.runtime/prometheus', '.runtime/grafana/data', '.runtime/grafana/log', '.runtime/grafana/plugins', '.runtime/grafana/dashboards')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $lab4Root $lab4Relative) | Out-Null
}
Copy-Item -LiteralPath (Join-Path $lab4Root 'grafana-dashboard.json') -Destination (Join-Path $lab4Root '.runtime/grafana/dashboards/grafana-dashboard.json')

$lab4PromArgs = @(
    '--config.file="' + (Join-Path $lab4Root 'prometheus.yml') + '"'
    '--storage.tsdb.path="' + (Join-Path $lab4Root '.runtime/prometheus') + '"'
    '--web.listen-address=127.0.0.1:9090'
    '--storage.tsdb.retention.time=7d'
)
$lab4PromProcess = Start-Process -FilePath $lab4PromExe -ArgumentList $lab4PromArgs -WorkingDirectory $lab4Root -WindowStyle Hidden -RedirectStandardOutput (Join-Path $lab4Root '.runtime/prometheus/stdout.log') -RedirectStandardError (Join-Path $lab4Root '.runtime/prometheus/stderr.log') -PassThru

$lab4Environment = @{
    GF_PATHS_DATA = Join-Path $lab4Root '.runtime/grafana/data'
    GF_PATHS_LOGS = Join-Path $lab4Root '.runtime/grafana/log'
    GF_PATHS_PLUGINS = Join-Path $lab4Root '.runtime/grafana/plugins'
    GF_PATHS_PROVISIONING = Join-Path $lab4Root 'provisioning'
    LAB4_DASHBOARD_DIR = Join-Path $lab4Root '.runtime/grafana/dashboards'
}
$lab4Previous = @{}
try {
    foreach ($lab4Name in $lab4Environment.Keys) {
        $lab4Previous[$lab4Name] = [Environment]::GetEnvironmentVariable($lab4Name, 'Process')
        [Environment]::SetEnvironmentVariable($lab4Name, $lab4Environment[$lab4Name], 'Process')
    }
    $lab4GrafanaArgs = @(
        ('--homepath="' + $lab4GrafanaHome + '"')
        ('--config="' + (Join-Path $lab4Root 'grafana.ini') + '"')
    )
    if ((Split-Path -Leaf $lab4GrafanaExe) -eq 'grafana.exe') { $lab4GrafanaArgs = @('server') + $lab4GrafanaArgs }
    $lab4GrafanaProcess = Start-Process -FilePath $lab4GrafanaExe -ArgumentList $lab4GrafanaArgs -WorkingDirectory $lab4GrafanaHome -WindowStyle Hidden -RedirectStandardOutput (Join-Path $lab4Root '.runtime/grafana/log/stdout.log') -RedirectStandardError (Join-Path $lab4Root '.runtime/grafana/log/stderr.log') -PassThru
} finally {
    foreach ($lab4Name in $lab4Previous.Keys) { [Environment]::SetEnvironmentVariable($lab4Name, $lab4Previous[$lab4Name], 'Process') }
}
@{
    prometheus_pid = $lab4PromProcess.Id
    grafana_pid = $lab4GrafanaProcess.Id
    started_at = (Get-Date).ToString('o')
    prometheus_port = 9090
    grafana_port = 3000
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $lab4Root '.runtime/monitoring-processes.json') -Encoding utf8
Write-Output "Started Prometheus PID $($lab4PromProcess.Id) at http://127.0.0.1:9090"
Write-Output "Started Grafana PID $($lab4GrafanaProcess.Id) at http://127.0.0.1:3000"
