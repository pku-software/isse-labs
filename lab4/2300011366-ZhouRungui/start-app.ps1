$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$runtime = Join-Path $projectRoot '.runtime\app'
$pidFile = Join-Path $runtime 'app-pid.json'
$port = 5001

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Project virtual environment not found: $python"
}

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
try {
    $listener.Start()
} catch {
    throw "Local port $port is already in use. Do not stop an unknown process; inspect the owner first."
} finally {
    $listener.Stop()
}

New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$oldMode = [Environment]::GetEnvironmentVariable('CHAT_MODE', 'Process')
try {
    [Environment]::SetEnvironmentVariable('CHAT_MODE', 'mock', 'Process')
    $process = Start-Process -PassThru -WindowStyle Hidden `
        -FilePath $python `
        -ArgumentList 'app.py' `
        -WorkingDirectory $projectRoot `
        -RedirectStandardOutput (Join-Path $runtime 'stdout.log') `
        -RedirectStandardError (Join-Path $runtime 'stderr.log')
} finally {
    [Environment]::SetEnvironmentVariable('CHAT_MODE', $oldMode, 'Process')
}

@{ pid = $process.Id; executable = $python; project = $projectRoot } |
    ConvertTo-Json | Set-Content -LiteralPath $pidFile -Encoding UTF8
Write-Output "Flask mock app: http://127.0.0.1:$port/"
Write-Output "Metrics:        http://127.0.0.1:$port/metrics"
Write-Output "App PID: $($process.Id) (recorded under .runtime/app/)"
