$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$prometheusExe = Join-Path $projectRoot ".tools\prometheus\prometheus.exe"
$grafanaRoot = Join-Path $projectRoot ".tools\grafana"
$grafanaExe = Join-Path $grafanaRoot "bin\grafana.exe"
$prometheusConfig = Join-Path $projectRoot "prometheus.yml"
$grafanaConfig = Join-Path $projectRoot "grafana.ini"
$provisioningRoot = Join-Path $projectRoot "provisioning"
$prometheusData = Join-Path $projectRoot ".runtime\prometheus"
$grafanaRuntime = Join-Path $projectRoot ".runtime\grafana"
$grafanaDashboards = Join-Path $grafanaRuntime "dashboards"
$grafanaPasswordFile = Join-Path $grafanaRuntime "admin-password.txt"

foreach ($required in @($prometheusExe, $grafanaExe, $prometheusConfig, $grafanaConfig)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "缺少必需文件：$required"
    }
}

New-Item -ItemType Directory -Force -Path `
    $prometheusData, `
    (Join-Path $grafanaRuntime "data"), `
    (Join-Path $grafanaRuntime "log"), `
    (Join-Path $grafanaRuntime "plugins"), `
    $grafanaDashboards | Out-Null
Copy-Item -LiteralPath (Join-Path $projectRoot "grafana-dashboard.json") `
    -Destination (Join-Path $grafanaDashboards "grafana-dashboard.json") -Force

if (Test-Path -LiteralPath $grafanaPasswordFile) {
    $grafanaAdminPassword = (Get-Content -Raw -LiteralPath $grafanaPasswordFile).Trim()
} else {
    $grafanaAdminPassword = [Guid]::NewGuid().ToString("N")
    $grafanaAdminPassword | Set-Content -Encoding ascii -LiteralPath $grafanaPasswordFile
}

$prometheus = Start-Process -FilePath $prometheusExe `
    -ArgumentList @(
        "--config.file=$prometheusConfig",
        "--storage.tsdb.path=$prometheusData",
        "--web.listen-address=127.0.0.1:9090"
    ) `
    -WorkingDirectory $projectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $prometheusData "stdout.log") `
    -RedirectStandardError (Join-Path $prometheusData "stderr.log") `
    -PassThru
$prometheus.Id | Set-Content -Encoding ascii -LiteralPath (Join-Path $prometheusData "prometheus.pid")

$grafanaEnvironment = @{
    GF_PATHS_DATA = Join-Path $grafanaRuntime "data"
    GF_PATHS_LOGS = Join-Path $grafanaRuntime "log"
    GF_PATHS_PLUGINS = Join-Path $grafanaRuntime "plugins"
    GF_PATHS_PROVISIONING = $provisioningRoot
    GF_SECURITY_ADMIN_USER = "admin"
    GF_SECURITY_ADMIN_PASSWORD = $grafanaAdminPassword
}
$grafana = Start-Process -FilePath $grafanaExe `
    -ArgumentList @("server", "--homepath", $grafanaRoot, "--config", $grafanaConfig) `
    -WorkingDirectory $projectRoot `
    -WindowStyle Hidden `
    -Environment $grafanaEnvironment `
    -RedirectStandardOutput (Join-Path $grafanaRuntime "stdout.log") `
    -RedirectStandardError (Join-Path $grafanaRuntime "stderr.log") `
    -PassThru
$grafana.Id | Set-Content -Encoding ascii -LiteralPath (Join-Path $grafanaRuntime "grafana.pid")

$deadline = (Get-Date).AddSeconds(45)
do {
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/health" -TimeoutSec 2 | Out-Null
        $grafanaReady = $true
    } catch {
        Start-Sleep -Milliseconds 500
    }
} while (-not $grafanaReady -and (Get-Date) -lt $deadline)
if (-not $grafanaReady) {
    throw "Grafana 未在 45 秒内就绪，请查看 .runtime/grafana/log/。"
}

$basicToken = [Convert]::ToBase64String(
    [Text.Encoding]::UTF8.GetBytes("admin:$grafanaAdminPassword")
)
$dashboard = Get-Content -Raw -Encoding UTF8 `
    -LiteralPath (Join-Path $projectRoot "grafana-dashboard.json") | ConvertFrom-Json
$payload = @{
    dashboard = $dashboard
    overwrite = $true
    message = "Provisioned by start-monitoring.ps1"
} | ConvertTo-Json -Depth 100
Invoke-RestMethod -Method Post `
    -Uri "http://127.0.0.1:3000/api/dashboards/db" `
    -Headers @{ Authorization = "Basic $basicToken" } `
    -ContentType "application/json" `
    -Body $payload | Out-Null

Write-Output "Prometheus 已启动：http://127.0.0.1:9090/ （PID $($prometheus.Id)）"
Write-Output "Grafana 已启动：http://127.0.0.1:3000/ （PID $($grafana.Id)）"
