# 聊天应用监控

在实验 2/3 的 Flask 聊天应用上记录 Prometheus 指标，由本机 Prometheus 采集，并在 Grafana 中查看。实验使用 mock，不调用外部模型。

## 应用行为

服务监听 `127.0.0.1:5001`。`CHAT_MODE` 默认为 `mock`，也可设为 `real`。

- `POST /api/messages` 是唯一计入指标的接口。请求体至少包含 `message`。
- mock 成功时固定回复 `这是模拟回复。`，状态码 201，并保存 `{id, message, reply}`。
- mock 接受 `delay_seconds`（大于等于 0、小于 30 的数字；布尔值无效）和 `force_error`（布尔值）。延迟用服务端 `sleep` 完成。`force_error` 为真时返回 503 `{"error":"模拟失败"}`，不保存记录。
- `real` 会忽略上述模拟字段，并使用环境变量 `DEEPSEEK_API_KEY` 调用 DeepSeek。本实验没有运行 real，也没有提交密钥。
- `GET /api/status` 返回当前配置，mock 下为 `{"mode":"mock","external_model_calls":false}`。

## 指标

三个指标只围绕 `POST /api/messages` 更新。`/metrics`、状态接口、静态页面以及其他消息接口不计数。

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"\|"error"}` | Counter | 处理结束时加 1。成功和失败标签在启动时都初始化为 0。 |
| `chat_inprogress_requests` | Gauge | 开始处理时加 1，结束时在 `finally` 中减 1，异常退出也会减。 |
| `chat_request_duration_seconds` | Histogram | 服务端处理耗时，单位秒。桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、30。 |

`GET /metrics` 返回 Prometheus 文本格式。

## 本机监控

在 Windows x64 上使用官方稳定版：Prometheus 3.15.0、Grafana 13.2.4。程序位于个人目录的 `.tools/`，运行数据位于 `.runtime/`，这两处不提交。

在个人目录执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start-monitoring.ps1
```

脚本会在端口空闲时启动三个进程：

| 程序 | 地址 | 说明 |
| --- | --- | --- |
| 聊天应用 | http://127.0.0.1:5001/ | `CHAT_MODE=mock` |
| Prometheus | http://127.0.0.1:9090/ | 配置为个人目录的 `prometheus.yml`，数据目录 `.runtime/prometheus/` |
| Grafana | http://127.0.0.1:3000/ | 数据、日志、插件在 `.runtime/grafana/`，本地登录 `admin` / `admin` |

`prometheus.yml` 中 job 名为 `chat-app`，目标 `127.0.0.1:5001`，路径 `/metrics`，采集间隔 2 秒，超时 1 秒。

Grafana 数据源名称 Prometheus，uid 为 `prometheus`，地址 `http://127.0.0.1:9090`。仪表盘 uid 为 `lab4-chat`，每 5 秒刷新。重新导入时使用个人目录的 `grafana-dashboard.json`，数据源选择这个 uid 为 `prometheus` 的数据源。

三个 Panel：

| Panel | PromQL | 含义 |
| --- | --- | --- |
| 成功/失败请求变化 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近 30 秒内平均每秒完成的成功或失败次数，不是累计值。 |
| 正在处理的请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 当前尚未处理完的聊天请求数。 |
| 平均处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近 30 秒内的服务端平均耗时，单位秒。没有新样本时可能无值。 |

Histogram 同时暴露桶、总和和次数。平均耗时使用总和除以次数。30 秒窗口会让阶段边界变平滑。

## 访问脚本

调度器是个人目录中的 `simulate_traffic.py`。项目差异写在 `project_adapter.py`：

- `confirm_mock_mode`：`GET /api/status`，只有 `mode` 为 `mock` 且 `external_model_calls` 为 false 才继续。
- `build_chat_request`：`POST /api/messages`，正文包含 `message`、`delay_seconds`、`force_error`。
- `response_is_success`：状态码 201，且 JSON 中有编号和非空 `reply`。

脚本只访问本机。并发满时跳过本次发送机会，不在客户端排队。客户端耗时包含网络开销，不等于服务端 Histogram。

## 第一次完整模拟

命令：

```powershell
.\.venv\Scripts\python.exe .\simulate_traffic.py --base-url http://127.0.0.1:5001 --output .\results\first-run.json
```

北京时间 2026-10-19 01:29:19 至 01:31:52，五个阶段各约 30 秒，随后等待 10 秒。默认参数：baseline 每秒 1 次、延迟 0.1 秒；burst 每秒 4 次、延迟 0.1 秒；slow 每秒 2 次、延迟 3 秒、并发上限 6；errors 每秒 1 次、每第 3 次强制失败；recovery 回到每秒 1 次、延迟 0.1 秒。没有网络错误，也没有非预期结果。

| 阶段 | 发出 | 成功 | 业务失败 | 跳过 |
| --- | --- | --- | --- | --- |
| baseline | 30 | 30 | 0 | 0 |
| burst | 120 | 120 | 0 | 0 |
| slow | 52 | 52 | 0 | 8 |
| errors | 30 | 20 | 10 | 0 |
| recovery | 30 | 30 | 0 | 0 |

仪表盘上，burst 期间成功速率升到接近每秒 4 次。slow 期间正在处理的请求升到 5，平均耗时大约 2.5 秒；服务端延迟是 3 秒，30 秒窗口混入了阶段边缘更快的请求。errors 期间失败曲线上升，recovery 后失败速率随 30 秒窗口回落。截图为 `screenshots/grafana-dashboard.jpg`，采集目标截图为 `screenshots/prometheus-targets.jpg`。

## 第二次模拟

只改变并发上限，其余 slow 参数不变。命令：

```powershell
.\.venv\Scripts\python.exe .\simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --concurrency 2 --output .\results\changed-run.json
```

北京时间 2026-10-19 11:40:55 至 11:41:27。计划发送 60 次，发出 18 次且全部成功，跳过 42 次，业务失败和网络错误都是 0。客户端平均耗时约 3.05 秒。同一窗口内 Prometheus 看到的正在处理数量最高为 2，服务端平均耗时约 3.0 秒。

与第一次 slow（并发上限 6，发出 52 次，跳过 8 次）相比，完成次数下降，跳过次数增加，正在处理的请求不超过 2。平均耗时仍约为 3 秒：跳过的请求没有进入处理函数，Histogram 只记录已经开始处理的请求，这段时间由 `delay_seconds` 决定。

## 从头运行

1. 用 Python 3 创建 `.venv`，执行 `pip install -r requirements.txt`。
2. 将 Prometheus 3.15.0 和 Grafana 13.2.4 的 Windows amd64 程序分别解压到 `.tools/prometheus/` 与 `.tools/grafana/`，使 `prometheus.exe` 和 `bin/grafana.exe` 位于上述位置。
3. 执行 `start-monitoring.ps1`。
4. 用上面的两条命令分别生成 `results/first-run.json` 和 `results/changed-run.json`。不要让两次输出写到同一个文件。
