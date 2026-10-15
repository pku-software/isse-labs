$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$grafRoot = $PSScriptRoot.Replace('\', '/')
$pidFile = Join-Path $PSScriptRoot '.runtime/grafana/process.pid'
if (Test-Path -LiteralPath $pidFile) {
    $grafProcessId = [int](Get-Content -LiteralPath $pidFile)
    $oldGraf = Get-Process -Id $grafProcessId -ErrorAction SilentlyContinue
    if ($oldGraf) {
        if ($oldGraf.Path -ne (Join-Path $PSScriptRoot '.tools/grafana/bin/grafana.exe')) {
            throw 'Saved PID belongs to another process; it was not stopped.'
        }
        Stop-Process -Id $grafProcessId
        $oldGraf.WaitForExit(5000) | Out-Null
    }
}
if (Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 3000 is occupied; no unrelated service was stopped.'
}
$env:GF_PATHS_DATA = "$grafRoot/.runtime/grafana/data"
$env:GF_PATHS_LOGS = "$grafRoot/.runtime/grafana/logs"
$env:GF_PATHS_PLUGINS = "$grafRoot/.runtime/grafana/plugins"
$env:GF_PATHS_PROVISIONING = "$grafRoot/provisioning"
$env:LAB4_DASHBOARD_DIR = "$grafRoot/dashboards"
$grafArgs = @('server', ('--homepath="' + $grafRoot + '/.tools/grafana"'), ('--config="' + $grafRoot + '/grafana.ini"'))
$newGraf = Start-Process -FilePath "$PSScriptRoot/.tools/grafana/bin/grafana.exe" -ArgumentList $grafArgs -WorkingDirectory "$PSScriptRoot/.tools/grafana" -WindowStyle Hidden -RedirectStandardOutput "$PSScriptRoot/.runtime/grafana/stdout.log" -RedirectStandardError "$PSScriptRoot/.runtime/grafana/stderr.log" -PassThru
$newGraf.Id | Set-Content -LiteralPath $pidFile
Write-Output "Grafana restarted, PID: $($newGraf.Id)"
