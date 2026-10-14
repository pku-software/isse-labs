# 王子懿的 Lab 4 聊天应用监控

项目源于 `lab3/2500013152-WangZiYi`，保留聊天页面和记录的增删改查。
聊天创建接口为 `POST /api/messages`，请求 JSON 使用 `message` 字段，
成功返回 HTTP 201 和 `id`、`message`、`reply`。

## 本地运行（Windows x64 / PowerShell）

在本目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\start-app.ps1
```

页面为 http://127.0.0.1:5001/，指标为 http://127.0.0.1:5001/metrics。
应用使用单进程、线程并发，只绑定本机。聊天存储使用锁保护，
数据保存到被忽略的 `.runtime/app/messages.json`。

默认 `CHAT_MODE=mock`，不创建或调用真实模型客户端，也不需要 Key。
`GET /api/lab-status` 返回实际 mock 模式和关闭外部调用的状态。
mock 聊天可附带 `mock_delay_seconds`（0–10 秒，默认 0.1 秒）与
`mock_force_error`（布尔值，默认 false）；模拟失败返回 HTTP 503。
`CHAT_MODE=real` 保留原 DeepSeek 调用，读取环境变量 `DEEPSEEK_API_KEY`，
不处理 mock 选项，实验状态接口返回 404。本实验只运行 mock。

## 业务指标

- `chat_requests_total{outcome="success"或"error"}`：聊天完成后的累计次数。
- `chat_inprogress_requests`：当前正在处理的聊天数量。
- `chat_request_duration_seconds`：服务端聊天处理耗时的 Histogram，单位秒。

指标仅覆盖 `POST /api/messages`，包括失败；异常也记录耗时并减少在途数量。
页面、状态接口、记录查询和 `/metrics` 不计入聊天指标。
指标标签不包含消息内容或用户身份。

课程 `simulate_traffic.py` 与待适配的 `project_adapter.py` 已复制到本目录。

## Prometheus 与 Grafana（Windows x64）

实际工具版本：Prometheus 3.15.0、Grafana OSS 13.2.4。官方来源：

- https://github.com/prometheus/prometheus/releases/tag/v3.15.0
- https://grafana.com/grafana/download/13.2.4?platform=windows&edition=oss

将官方 Windows amd64 包及校验文件下载到 `.tools/downloads/`，核验 SHA256
后去掉包的外层目录，分别解压到 `.tools/prometheus/` 和 `.tools/grafana/`。
Grafana 便携包的官方 SHA256 为
`3e005ff50fe3bb6b8cb428ef127636fac4ee676bf9b6d819c6a2297d21f4bcbd`；
Prometheus 校验值见该版本官方 `sha256sums.txt`。

应用启动后，在本目录运行 `./start-monitoring.ps1`。脚本检查端口占用，
不停止已有服务；启动命令对应：

```powershell
.\.tools\prometheus\prometheus.exe --config.file=prometheus.yml --storage.tsdb.path=.runtime/prometheus --web.listen-address=127.0.0.1:9090
# Grafana 运行前按 start-monitoring.ps1 设置 GF_PATHS_* 和 LAB4_DASHBOARD_DIR
.\.tools\grafana\bin\grafana.exe server --homepath=.tools/grafana --config=grafana.ini
```

Prometheus 页面为 http://127.0.0.1:9090/targets，采集 job 为 `chat-app`，
目标 `127.0.0.1:5001`，间隔 2 秒、超时 1 秒。Grafana 页面为
http://127.0.0.1:3000/d/lab4-wangziyi 。工具均只监听本机。
数据源自动配置为 `http://127.0.0.1:9090`，UID 为 `lab4-prometheus`；
仪表盘通过 `provisioning/` 自动加载 `dashboards/chat.json`，匿名访问仅允许查看。
Prometheus 数据在 `.runtime/prometheus/`，Grafana 数据、日志和插件分别在
`.runtime/grafana/data/`、`logs/`、`plugins/`，工具和运行数据都不提交。

三个 Panel 每 2 秒刷新，使用以下 PromQL：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
sum(chat_inprogress_requests{job="chat-app"})
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

第一项是最近 30 秒平均每秒完成的成功/失败聊天数；第二项是当前在途聊天数，
不是在线用户数；第三项是最近窗口的服务端平均耗时，单位秒，无请求时可能无值。
Histogram 的 `_bucket{le="..."}` 为不超过指定耗时的累计样本数，
`_sum` 为总耗时，`_count` 为样本数。
