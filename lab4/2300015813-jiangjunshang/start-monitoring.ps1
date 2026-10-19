$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

$prometheusExe = "$PSScriptRoot/.tools/prometheus/prometheus.exe"
$grafanaHome = "$PSScriptRoot/.tools/grafana"
$grafanaExe = "$grafanaHome/bin/grafana.exe"
foreach ($tool in @($prometheusExe, $grafanaExe)) {
    if (-not (Test-Path -LiteralPath $tool)) { throw "Missing tool: $tool. Run install-tools.py first." }
}
function Start-LabTool($Executable, $Arguments, $Port, $WorkingDirectory, $PidFile, $Stdout, $Stderr) {
    if (Test-Path -LiteralPath $PidFile) {
        $recordedId = [int](Get-Content -LiteralPath $PidFile)
        $existing = Get-Process -Id $recordedId -ErrorAction SilentlyContinue
        if ($existing -and $existing.Path -eq (Resolve-Path -LiteralPath $Executable).Path) {
            Write-Host "Already running: $Executable (PID $recordedId)"
            return $existing
        }
    }
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
    try { $listener.Start() } finally { $listener.Stop() }
    $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory -WindowStyle Hidden -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr -PassThru
    $process.Id | Set-Content -LiteralPath $PidFile
    return $process
}

$prometheusRuntime = "$PSScriptRoot/.runtime/prometheus"
$grafanaRuntime = "$PSScriptRoot/.runtime/grafana"
foreach ($directory in @($prometheusRuntime, "$grafanaRuntime/data", "$grafanaRuntime/logs", "$grafanaRuntime/plugins", "$grafanaRuntime/dashboards")) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}
Copy-Item -LiteralPath "$PSScriptRoot/grafana-dashboard.json" -Destination "$grafanaRuntime/dashboards/grafana-dashboard.json" -Force

$env:GF_PATHS_DATA = "$grafanaRuntime/data"
$env:GF_PATHS_LOGS = "$grafanaRuntime/logs"
$env:GF_PATHS_PLUGINS = "$grafanaRuntime/plugins"
$env:GF_PATHS_PROVISIONING = "$PSScriptRoot/provisioning"
$env:LAB4_DASHBOARD_DIR = "$grafanaRuntime/dashboards" -replace '\\', '/'

$prometheusArgs = @(
    "--config.file=`"$PSScriptRoot/prometheus.yml`"",
    "--storage.tsdb.path=`"$prometheusRuntime`"",
    '--web.listen-address=127.0.0.1:9090'
)
$prometheusProcess = Start-LabTool $prometheusExe $prometheusArgs 9090 $PSScriptRoot "$prometheusRuntime/process.pid" "$prometheusRuntime/stdout.log" "$prometheusRuntime/stderr.log"

$grafanaArgs = @('server', "--homepath=`"$grafanaHome`"", "--config=`"$PSScriptRoot/grafana.ini`"")
$grafanaProcess = Start-LabTool $grafanaExe $grafanaArgs 3000 $grafanaHome "$grafanaRuntime/process.pid" "$grafanaRuntime/logs/stdout.log" "$grafanaRuntime/logs/stderr.log"
Write-Output "Prometheus PID: $($prometheusProcess.Id), http://127.0.0.1:9090/targets"
Write-Output "Grafana PID: $($grafanaProcess.Id), http://127.0.0.1:3000/d/lab4-chat/lab4-chat-monitoring"
