$ErrorActionPreference = 'Stop'
$lab4Root = $PSScriptRoot
$env:CHAT_MODE = 'mock'
$env:PORT = '5001'
$env:PYTHONUTF8 = '1'
$env:LAB4_PROJECT_DIR = $lab4Root.Replace('\', '/')
$env:GF_PATHS_DATA = "$lab4Root/.runtime/grafana/data"
$env:GF_PATHS_LOGS = "$lab4Root/.runtime/grafana/logs"
$env:GF_PATHS_PLUGINS = "$lab4Root/.runtime/grafana/plugins"
$env:GF_PATHS_PROVISIONING = "$lab4Root/grafana/provisioning"
New-Item -ItemType Directory -Path $env:GF_PATHS_DATA, $env:GF_PATHS_LOGS, $env:GF_PATHS_PLUGINS -Force | Out-Null

$lab4Services = @(
    @{
        Name = 'app'; Port = 5001
        File = "$lab4Root/.venv/Scripts/python.exe"
        Arguments = 'app.py'
    },
    @{
        Name = 'prometheus'; Port = 9090
        File = "$lab4Root/.tools/prometheus/prometheus.exe"
        Arguments = "--config.file=`"$lab4Root/prometheus.yml`" --storage.tsdb.path=`"$lab4Root/.runtime/prometheus`" --web.listen-address=127.0.0.1:9090"
    },
    @{
        Name = 'grafana'; Port = 3000
        File = "$lab4Root/.tools/grafana/bin/grafana.exe"
        Arguments = "server --homepath=`"$lab4Root/.tools/grafana`" --config=`"$lab4Root/grafana.ini`""
    }
)

foreach ($lab4Service in $lab4Services) {
    if (-not (Test-Path -LiteralPath $lab4Service.File)) {
        throw "Missing executable: $($lab4Service.File)"
    }
    $lab4Runtime = "$lab4Root/.runtime/$($lab4Service.Name)"
    New-Item -ItemType Directory -Path $lab4Runtime -Force | Out-Null
    $lab4PidPath = "$lab4Runtime/server.pid"
    $lab4Listener = Get-NetTCPConnection -State Listen -LocalPort $lab4Service.Port -ErrorAction SilentlyContinue
    if ($lab4Listener) {
        if ((Test-Path -LiteralPath $lab4PidPath) -and
            (($lab4Listener.OwningProcess | Select-Object -Unique) -eq [int](Get-Content -LiteralPath $lab4PidPath))) {
            Write-Output "$($lab4Service.Name) already running on $($lab4Service.Port)"
            continue
        }
        throw "Port $($lab4Service.Port) is occupied by another process; do not stop it."
    }
    $lab4Process = Start-Process -FilePath $lab4Service.File -ArgumentList $lab4Service.Arguments -WorkingDirectory $lab4Root -WindowStyle Hidden -RedirectStandardOutput "$lab4Runtime/stdout.log" -RedirectStandardError "$lab4Runtime/stderr.log" -PassThru
    $lab4Owner = $null
    for ($lab4Attempt = 0; $lab4Attempt -lt 60; $lab4Attempt++) {
        $lab4Listener = Get-NetTCPConnection -State Listen -LocalPort $lab4Service.Port -ErrorAction SilentlyContinue
        if ($lab4Listener) {
            $lab4Owner = Get-CimInstance Win32_Process -Filter "ProcessId=$($lab4Listener.OwningProcess)"
            if ($lab4Owner.ProcessId -eq $lab4Process.Id -or $lab4Owner.ParentProcessId -eq $lab4Process.Id) {
                break
            }
            throw "Port $($lab4Service.Port) is owned by an unexpected process."
        }
        Start-Sleep -Milliseconds 250
    }
    if (-not $lab4Owner) {
        throw "$($lab4Service.Name) did not start listening; inspect $lab4Runtime logs."
    }
    Set-Content -LiteralPath $lab4PidPath -Value $lab4Owner.ProcessId
    Write-Output "$($lab4Service.Name) started: PID $($lab4Owner.ProcessId), port $($lab4Service.Port)"
}
