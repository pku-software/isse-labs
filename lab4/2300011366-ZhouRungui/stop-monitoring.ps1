$ErrorActionPreference = 'Stop'
$pidFile = Join-Path $PSScriptRoot '.runtime\monitoring-pids.json'

if (-not (Test-Path -LiteralPath $pidFile -PathType Leaf)) {
    Write-Output 'No Lab 4 Prometheus/Grafana process record was found.'
    exit 0
}

$records = Get-Content -LiteralPath $pidFile -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($name in @('prometheus', 'grafana')) {
    $entry = $records.$name
    if (-not $entry) { continue }

    $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$entry.pid)" -ErrorAction SilentlyContinue
    if (-not $processInfo) {
        Write-Output "$name process $($entry.pid) is already stopped."
        continue
    }
    if (-not [string]::Equals($processInfo.ExecutablePath, [string]$entry.executable, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Warning "$name PID $($entry.pid) now belongs to a different executable; leaving it untouched."
        continue
    }

    Stop-Process -Id ([int]$entry.pid) -Force
    Write-Output "Stopped this Lab 4 $name process ($($entry.pid))."
}

Remove-Item -LiteralPath $pidFile -ErrorAction SilentlyContinue
