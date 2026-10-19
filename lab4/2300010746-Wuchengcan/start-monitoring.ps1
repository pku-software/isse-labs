$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PromDir = Join-Path $Root ".tools\prometheus"
$GrafanaHome = Join-Path $Root ".tools\grafana"
$PromData = Join-Path $Root ".runtime\prometheus"
$GrafanaData = Join-Path $Root ".runtime\grafana"
$Provision = Join-Path $Root "grafana\provisioning"

New-Item -ItemType Directory -Force -Path $PromData, (Join-Path $GrafanaData "data"), (Join-Path $GrafanaData "logs"), (Join-Path $GrafanaData "plugins"), (Join-Path $Provision "dashboards") | Out-Null

$provider = @"
apiVersion: 1
providers:
  - name: lab4
    orgId: 1
    folder: ""
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: $($Root.Replace('\','/'))/grafana/dashboards
"@
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText((Join-Path $Provision "dashboards\provider.yml"), $provider.Trim() + "`n", $utf8)

function Test-Port([int] $Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $client.Connect("127.0.0.1", $Port)
        return $true
    } catch {
        return $false
    } finally {
        $client.Dispose()
    }
}

if (-not (Test-Port 5001)) {
    Start-Process -FilePath (Join-Path $Root ".venv\Scripts\python.exe") -ArgumentList "app.py" -WorkingDirectory $Root -WindowStyle Hidden
}

if (-not (Test-Port 9090)) {
    Start-Process -FilePath (Join-Path $PromDir "prometheus.exe") -ArgumentList @(
        "--config.file=$(Join-Path $Root 'prometheus.yml')",
        "--storage.tsdb.path=$PromData",
        "--web.listen-address=127.0.0.1:9090"
    ) -WorkingDirectory $PromDir -WindowStyle Hidden
}

if (-not (Test-Port 3000)) {
    $env:GF_SERVER_HTTP_ADDR = "127.0.0.1"
    $env:GF_SERVER_HTTP_PORT = "3000"
    $env:GF_PATHS_DATA = Join-Path $GrafanaData "data"
    $env:GF_PATHS_LOGS = Join-Path $GrafanaData "logs"
    $env:GF_PATHS_PLUGINS = Join-Path $GrafanaData "plugins"
    $env:GF_PATHS_PROVISIONING = $Provision
    $env:GF_SECURITY_ADMIN_USER = "admin"
    $env:GF_SECURITY_ADMIN_PASSWORD = "admin"
    Start-Process -FilePath (Join-Path $GrafanaHome "bin\grafana.exe") -ArgumentList @("server", "--homepath", $GrafanaHome) -WorkingDirectory $GrafanaHome -WindowStyle Hidden
}

Write-Host "chat    http://127.0.0.1:5001/"
Write-Host "metrics http://127.0.0.1:5001/metrics"
Write-Host "prom    http://127.0.0.1:9090/"
Write-Host "grafana http://127.0.0.1:3000/"
