$root = $PSScriptRoot
foreach ($name in @("app","prometheus","grafana")) {
  $pidFile = Join-Path $root ".runtime\app\$name.pid"
  if (Test-Path $pidFile) {
    $procId = [int](Get-Content $pidFile)
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($proc) { Stop-Process -Id $procId -Force; Write-Host "已停止 $name（PID $procId）" } else { Write-Host "$name 未在运行" }
    Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
  } else { Write-Host "$name 没有 PID 文件，跳过" }
}