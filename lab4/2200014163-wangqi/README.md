# Lab 4：聊天应用监控（王琪 2200014163）

本项目从 Lab 3 的 Flask 聊天应用复制而来，在不改动原聊天和 CRUD 功能的前提下，加入 Prometheus 指标，用 Prometheus 采集、Grafana 展示，并用课程访问脚本模拟流量。

## 项目功能

- 保留原聊天接口与前端：`POST /api/conversations/<id>/messages` 收发消息，以及会话和消息的增删改查。
- 两种运行模式由环境变量 `APP_MODE` 区分，默认 `mock`：
  - `mock`：不创建、不调用真实模型客户端，不需要 DeepSeek Key；聊天接口支持实验选项 `delay_seconds`（后端真实 sleep）与 `force_error`（返回 503 模拟失败）。
  - `real`：调用 DeepSeek 真实模型，忽略上述两个实验选项。
- 暴露 `GET /metrics`（prometheus_client 标准文本格式），以及实验状态接口 `GET /api/experiment/status`，返回 `{"mode": ..., "external_model_calls": ...}`。
- 三个业务指标只统计聊天请求，不统计 `/metrics`、状态接口与静态资源：
  - Counter `chat_requests_total{outcome="success"|"error"}`：成功/错误累计，两种 outcome 初始化为 0。
  - Gauge `chat_inprogress_requests`：正在处理的聊天请求数。
  - Histogram `chat_request_duration_seconds`：服务端处理耗时（含模拟失败），桶覆盖 0.05s 到 10s。

## 运行环境

- Windows 11 x64，PowerShell，Python 3.9.1。
- Python 依赖见 `requirements.txt`：Flask 3.1.3、prometheus-client 0.26.0、python-dotenv、requests。
- Prometheus 3.13.4（windows-amd64）。因本机无法访问 GitHub，官方二进制改从清华 TUNA 的 github-release 镜像获取。
- Grafana 13.2.4 OSS（windows-amd64），来自官方 dl.grafana.com。

工具下载包放在 `.tools/downloads/`，解压到 `.tools/prometheus/` 与 `.tools/grafana/`；运行数据在 `.runtime/`，Python 虚拟环境在 `.venv/`。这些目录均被 `.gitignore` 忽略，不提交。

## 端口与启动命令

三个程序均只监听本机：

- 应用：`127.0.0.1:5001`
- Prometheus：`127.0.0.1:9090`
- Grafana：`127.0.0.1:3000`

在个人目录内依次启动（示例，路径按实际调整）：

```text
.venv\Scripts\python.exe app.py
.tools\prometheus\prometheus.exe --config.file=prometheus.yml --storage.tsdb.path=.runtime\prometheus --web.listen-address=127.0.0.1:9090
.tools\grafana\bin\grafana.exe server --homepath=.tools\grafana --config=grafana.ini
```

`prometheus.yml` 以 2 秒间隔、1 秒超时采集 `chat-app`（`http://127.0.0.1:5001/metrics`）。Grafana 通过 `provisioning/` 自动创建 Prometheus 数据源（uid `prometheus`，指向 `http://127.0.0.1:9090`）并加载 `grafana-dashboard.json`；默认账号 `admin/admin`，匿名用户只读。

## 三个 Panel 的查询含义

- 成功/失败请求速率：`sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))`，最近 30 秒窗口内平均每秒完成的成功/错误请求数，不是累计次数。
- 正在处理的请求：`sum(chat_inprogress_requests{job="chat-app"})`，当前瞬时在途请求数。
- 平均处理耗时：`sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))`，最近 30 秒窗口内服务端平均每请求耗时，单位秒。

## 访问脚本与适配

`simulate_traffic.py` 是课程调度器的个人副本，只负责发送节奏、并发上限、阶段切换与结果统计，不直接改指标。`project_adapter.py` 补齐三处适配：

- `confirm_mock_mode()`：GET `/api/experiment/status` 核验 mock 且外部模型调用关闭，并准备一个会话。
- `build_chat_request()`：构造 `POST /api/conversations/<id>/messages`，请求体带 `message`、`delay_seconds`、`force_error`。
- `response_is_success()`：HTTP 201 且返回体为 `{"id": int, "role": "assistant", "content": 非空}` 时判成功。

## 两次真实模拟结果

第一次完整五阶段（默认参数），本地时间 02:20:03–02:22:36，结果见 `results/first-run.json`：

| 阶段 | 发送 | 成功 | 业务错误 | 跳过 | 客户端平均 |
| --- | --- | --- | --- | --- | --- |
| baseline | 30 | 30 | 0 | 0 | 0.12s |
| burst | 120 | 120 | 0 | 0 | 0.12s |
| slow | 52 | 52 | 0 | 8 | 3.03s |
| errors | 30 | 20 | 10 | 0 | 0.12s |
| recovery | 30 | 30 | 0 | 0 | 0.13s |

第二次仅重跑 slow 场景，`--concurrency 10`，本地时间 02:34:19–02:34:51，结果见 `results/changed-run.json`：发送 60、成功 60、跳过 0、客户端平均 3.03s。与第一次 slow（并发 6，跳过 8）相比，在途请求数峰值仍为 6、成功速率仍约 2 次/秒、平均耗时仍约 3 秒，变化只是不再跳过发送机会。
