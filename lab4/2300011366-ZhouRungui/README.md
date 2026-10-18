# Lab 4：用 Prometheus 和 Grafana 监控聊天应用

## 项目说明

本项目在 Flask 聊天接口中记录成功/失败请求数、当前处理中的请求数和服务端处理耗时。Prometheus 每 2 秒读取一次 `/metrics` 并保存时间序列；Grafana 通过 Prometheus 数据源展示三个图表。本实验默认使用 mock 回复与模拟延迟/错误，不调用外部模型，也不需要 API Key。

## 指标和图表

- `chat_requests_total{outcome="success|error"}`：聊天请求完成数，按成功或失败累计。
- `chat_inprogress_requests`：正在处理的聊天请求数，处理结束或异常时都会减回。
- `chat_request_duration_seconds`：服务端处理耗时直方图，包含成功和失败请求。

Grafana 仪表盘包含以下 Panel：

1. 成功/失败请求速率：`sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))`，表示最近 30 秒窗口内每秒完成请求的速率。
2. 当前在途请求：`sum(chat_inprogress_requests{job="chat-app"})`，表示当前正在处理的聊天请求数。
3. 平均服务端耗时：`sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))`，单位为秒；没有样本时可能暂时没有数据。

直方图还会导出 `_bucket` 桶计数、`_sum` 耗时总和和 `_count` 样本数。本仪表盘用总和除以样本数计算窗口平均值。

## 本机运行

本次运行环境为 Windows x86-64、Python 3.11.7、Prometheus 3.15.0、Grafana OSS 13.2.4。工具包与运行数据放在 `.tools/`、`.runtime/`，均由个人 `.gitignore` 排除。

在两个 PowerShell 终端中，从本目录启动：

```powershell
.\start-app.ps1
.\start-monitoring.ps1
```

访问应用 `http://127.0.0.1:5001/`、应用指标 `http://127.0.0.1:5001/metrics`、Prometheus `http://127.0.0.1:9090/` 和 Grafana `http://127.0.0.1:3000/`。Prometheus Target 名为 `chat-app`。Grafana 首次登录使用本机首次启动时显示的凭据，并按提示修改密码；在 Dashboards 中打开 `Lab 4` 文件夹下的 `Lab 4 聊天应用监控`。启动脚本会在本地配置 Prometheus 数据源并加载仓库内的仪表盘 JSON。

停止本实验启动的服务：

```powershell
.\stop-monitoring.ps1
.\stop-app.ps1
```

启动脚本使用 `.tools/prometheus/` 与 `.tools/grafana/` 中的程序；Prometheus 数据写入 `.runtime/prometheus/`，Grafana 数据/日志/插件写入 `.runtime/grafana/`，应用日志写入 `.runtime/app/`。如果端口已被占用，脚本会停止并提示，不会自动关闭未知进程。

## 访问模拟与实际结果

适配器通过真实 HTTP 请求核验 `/api/lab4/status`，只在服务报告 `mode=mock` 且 `external_model_calls=false` 时允许模拟；聊天请求调用原有 `POST /api/messages` 接口。适配器成功请求返回 HTTP 201，模拟失败返回 HTTP 503。脚本对 `mode=real` 的状态拒绝发送请求。

首次完整模拟使用默认参数，五个阶段各运行 30 秒：

| 阶段 | 实际发送 | 成功 | HTTP/业务错误 | 跳过 | 客户端平均耗时 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 30 | 30 | 0 | 0 | 0.116 秒 |
| burst | 120 | 120 | 0 | 0 | 0.113 秒 |
| slow（延迟 3 秒） | 52 | 52 | 0 | 8 | 3.014 秒 |
| errors（每第 3 次失败） | 30 | 20 | 10 | 0 | 0.113 秒 |
| recovery | 30 | 30 | 0 | 0 | 0.109 秒 |

第二次只运行 slow 阶段，将后端模拟延迟从 3 秒改为 5 秒：发送 35 次、成功 35 次、跳过 25 次，客户端平均耗时约 5.014 秒。并发数上限为 6；延迟增加后，请求占用并发槽位更久，因此更多发送机会被跳过。这里的客户端平均耗时含 HTTP 网络开销，不等于服务端直方图的均值。

运行后在 Grafana 选择覆盖相应运行时间的范围并观察三个 Panel。访问频率提高时，请求速率图会升高；慢请求阶段耗时均值和在途请求会升高；错误阶段失败速率会升高；恢复阶段延迟和在途请求回落。Prometheus 抓取 `UP` 只说明 `/metrics` 可访问并成功采集，不能单独证明聊天请求处理正常。

本次真实脚本输出保存在 `results/first-run.json` 和 `results/changed-run.json`。以下命令可重新生成结果（覆盖对应 JSON）：

```powershell
.\.venv\Scripts\python.exe simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario all --output results/first-run.json
.\.venv\Scripts\python.exe simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --phase-seconds 30 --slow-delay 5 --output results/changed-run.json
```

## 截图

- `screenshots/prometheus-targets.png`：Prometheus 中 `chat-app` Target 状态为 `UP`。
- `screenshots/grafana-dashboard.<扩展名>`：待补充覆盖完整模拟时间范围、包含三个 Panel 的 Grafana 原始截图。