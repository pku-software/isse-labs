# 启动本实验的 Grafana：数据、日志、插件都写到 .runtime/grafana 下，
# 数据源由 provisioning/ 自动导入，避免默认路径把运行数据写进可提交目录。
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$home = Join-Path $here ".tools\grafana"
$runtime = Join-Path $here ".runtime\grafana"

$env:GF_PATHS_DATA = Join-Path $runtime "data"
$env:GF_PATHS_LOGS = Join-Path $runtime "logs"
$env:GF_PATHS_PLUGINS = Join-Path $runtime "plugins"
$env:GF_PATHS_PROVISIONING = Join-Path $here "provisioning"
$env:GF_SERVER_HTTP_ADDR = "127.0.0.1"
$env:GF_SERVER_HTTP_PORT = "3000"

# 仅本机实验实例使用的一次性口令，不要用于任何真实环境。
$env:GF_SECURITY_ADMIN_USER = "admin"
$env:GF_SECURITY_ADMIN_PASSWORD = "admin"

& (Join-Path $home "bin\grafana.exe") server --homepath $home
