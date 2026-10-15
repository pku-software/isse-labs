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

课程 `simulate_traffic.py` 与已完成项目适配的 `project_adapter.py` 位于本目录。

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
$grafanaRoot = (Get-Location).Path
.\.tools\grafana\bin\grafana.exe server --homepath="$grafanaRoot/.tools/grafana" --config="$grafanaRoot/grafana.ini"
```

Prometheus 页面为 http://127.0.0.1:9090/targets，采集 job 为 `chat-app`，
目标 `127.0.0.1:5001`，间隔 2 秒、超时 1 秒。Grafana 页面为
http://127.0.0.1:3000/d/lab4-wangziyi 。工具均只监听本机。
数据源自动配置为 `http://127.0.0.1:9090`，UID 为 `lab4-prometheus`；
仪表盘通过 `provisioning/` 自动加载 `dashboards/chat.json`，匿名访问仅允许查看。
Prometheus 数据在 `.runtime/prometheus/`，Grafana 数据、日志和插件分别在
`.runtime/grafana/data/`、`logs/`、`plugins/`，工具和运行数据都不提交。

三个 Panel 默认每 2 秒刷新（截图时选择了 5 秒），使用以下 PromQL：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
sum(chat_inprogress_requests{job="chat-app"})
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

第一项是最近 30 秒平均每秒完成的成功/失败聊天数；第二项是当前在途聊天数，
不是在线用户数；第三项是最近窗口的服务端平均耗时，单位秒，无请求时可能无值。
Histogram 的 `_bucket{le="..."}` 为不超过指定耗时的累计样本数，
`_sum` 为总耗时，`_count` 为样本数。

## 实际模拟结果

首次完整模拟使用默认参数（五个阶段各 30 秒，slow 阶段并发上限 6），结果文件为
`results/first-run.json`。运行时间为 2026-10-14 18:19:00–18:21:43（北京时间）。
各阶段实际结果：baseline 发送 30、成功 30；burst 发送 120、成功 120；slow
发送 52、成功 52、因并发已满跳过 8；errors 发送 30、成功 20、预期业务错误 10；
recovery 发送 30、成功 30。全程无网络错误。slow 阶段服务端平均耗时接近 3 秒，
采集到的在途请求峰值为 6；errors 阶段错误速率上升，recovery 后回落。

第二次只运行 slow 阶段，使用 `--phase-seconds 30 --concurrency 3`，其余保持
每秒约 2 次、后端延迟 3 秒，结果文件为 `results/changed-run.json`。运行时间为
2026-10-14 18:42:54–18:43:36（北京时间），发送 27、成功 27、跳过 33、业务错误 0、
网络错误 0，客户端平均耗时约 3.03 秒，采集到的在途峰值为 3。并发降低后，达到
上限的调度机会直接跳过，所以成功数量下降但错误指标没有增加。

完整五阶段仪表盘截图为 `screenshots/grafana-dashboard.png`，slow 阶段的补充观察图为
`screenshots/grafana-slow-rate-inprogress.png` 和 `screenshots/grafana-slow-duration.png`；
Prometheus Target 截图为 `screenshots/prometheus-targets.png`。

## 复现脚本与仪表盘导入

`simulate_traffic.py` 与课程调度器一致。`project_adapter.py` 通过真实 HTTP
读取 `/api/lab-status`，拒绝非 mock 模式和重定向；构造原 `POST /api/messages`
请求，携带 mock 延迟/失败选项；以 HTTP 201 和有效记录 JSON 判断成功。
已验证正常请求、强制失败、无效响应、本机限制和 real 模式拒绝。
脚本不需要 Key，不直接修改指标。

在本目录运行：

```powershell
.\.venv\Scripts\python.exe simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
.\.venv\Scripts\python.exe simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --phase-seconds 30 --concurrency 3 --output results/changed-run.json
```

运行期间保持电脑唤醒。目标速率是发送机会，实际完成量受延迟和并发上限影响；
JSON 的客户端耗时包含网络开销，不能当作服务端 Histogram。
30 秒窗口会平滑阶段边界并产生恢复滞后；2 秒采集可能错过短请求的在途峰值。

`grafana-dashboard.json` 是从实际运行的 Grafana 导出的仪表盘，包含三个 Panel。
在另一套 Grafana 导入前，创建 UID 为 `lab4-prometheus` 的 Prometheus 数据源，
地址指向实际本机 Prometheus；或把 JSON 中该 UID 改成对应数据源 UID。
当前环境启动脚本会自动配置数据源并加载 `dashboards/chat.json`。
