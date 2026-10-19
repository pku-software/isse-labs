# 通过 Grafana HTTP API 导入个人仪表盘。
# 数据源由 provisioning/datasources/prometheus.yml 自动导入，不需要手工添加。
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dashboard = Get-Content (Join-Path $here "grafana-dashboard.json") -Raw | ConvertFrom-Json
$body = @{ dashboard = $dashboard; overwrite = $true; message = "lab4 monitoring dashboard" } | ConvertTo-Json -Depth 40
$auth = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:admin"))

Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/dashboards/db" -Method POST `
    -Headers @{ Authorization = $auth } -ContentType "application/json" -Body $body
