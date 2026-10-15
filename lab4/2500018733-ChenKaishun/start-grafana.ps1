# 在单独的 PowerShell 终端运行并保持终端开启；Ctrl+C 停止本服务。
$ErrorActionPreference = 'Stop'
$grafanaEnvironment = @{
    GF_PATHS_DATA = Join-Path $PSScriptRoot '.runtime/grafana/data'
    GF_PATHS_LOGS = Join-Path $PSScriptRoot '.runtime/grafana/logs'
    GF_PATHS_PLUGINS = Join-Path $PSScriptRoot '.runtime/grafana/plugins'
    GF_PATHS_PROVISIONING = Join-Path $PSScriptRoot 'grafana-provisioning'
    LAB4_DASHBOARD_PATH = Join-Path $PSScriptRoot '.runtime/grafana/dashboards'
}
$passwordFile = Join-Path $PSScriptRoot '.runtime/grafana/admin-password.txt'
foreach ($directory in @('data', 'logs', 'plugins', 'dashboards')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $PSScriptRoot ".runtime/grafana/$directory") | Out-Null
}
if (-not (Test-Path -LiteralPath $passwordFile)) {
    [System.IO.File]::WriteAllText($passwordFile, [guid]::NewGuid().ToString('N'))
}
$grafanaEnvironment.GF_SECURITY_ADMIN_PASSWORD = [System.IO.File]::ReadAllText($passwordFile).Trim()
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'grafana-dashboard.json') -Destination (Join-Path $PSScriptRoot '.runtime/grafana/dashboards/grafana-dashboard.json')
$previousEnvironment = @{}
try {
    foreach ($entry in $grafanaEnvironment.GetEnumerator()) {
        $previousEnvironment[$entry.Key] = [Environment]::GetEnvironmentVariable($entry.Key, 'Process')
        [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value, 'Process')
    }
    & (Join-Path $PSScriptRoot '.tools/grafana/bin/grafana.exe') server --homepath (Join-Path $PSScriptRoot '.tools/grafana') --config (Join-Path $PSScriptRoot 'grafana.ini')
} finally {
    foreach ($entry in $previousEnvironment.GetEnumerator()) {
        [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value, 'Process')
    }
}
