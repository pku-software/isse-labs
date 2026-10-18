$ErrorActionPreference = 'Stop'
$pidFile = Join-Path $PSScriptRoot '.runtime\app\app-pid.json'

if (-not (Test-Path -LiteralPath $pidFile -PathType Leaf)) {
    Write-Output 'No Lab 4 app process record was found.'
    exit 0
}

$record = Get-Content -LiteralPath $pidFile -Raw -Encoding UTF8 | ConvertFrom-Json
$processInfo = Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$record.pid)" -ErrorAction SilentlyContinue
if (-not $processInfo) {
    Write-Output 'The recorded Lab 4 app process is already stopped.'
} elseif (
    [string]::Equals($processInfo.ExecutablePath, [string]$record.executable, [System.StringComparison]::OrdinalIgnoreCase) -and
    $processInfo.CommandLine.Contains([string]$record.project)
) {
    Stop-Process -Id ([int]$record.pid) -Force
    Write-Output "Stopped the Lab 4 Flask app ($($record.pid))."
} else {
    Write-Warning 'The recorded PID no longer matches this project app; leaving the process untouched.'
}

Remove-Item -LiteralPath $pidFile -ErrorAction SilentlyContinue
