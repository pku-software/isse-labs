# 启动本实验的 Prometheus：只监听本机，采集配置与数据目录都固定在个人目录内。
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

& (Join-Path $here ".tools\prometheus\prometheus.exe") `
    --config.file="$(Join-Path $here 'prometheus.yml')" `
    --storage.tsdb.path="$(Join-Path $here '.runtime\prometheus')" `
    --web.listen-address="127.0.0.1:9090"
