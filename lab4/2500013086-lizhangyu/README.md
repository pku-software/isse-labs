# Lab 4：聊天应用本地监控

## 项目来源与功能

本项目是在 Lab 3 Flask 多会话聊天应用的个人副本上完成的。页面、会话管理和聊天 API 沿用原项目；Lab 4 为聊天请求加入指标，并用 Prometheus 采集、Grafana 展示。

## 模式与指标

应用默认使用 `CHAT_MODE=mock`。mock 模式返回固定测试回复，不创建或调用真实模型客户端，不读取 `.env`，也不要求 API Key。仅设置 `CHAT_MODE=real` 时才会读取运行环境中的 `DEEPSEEK_API_KEY` 并调用 DeepSeek。实验期间始终使用默认 mock 模式。

聊天指标由应用的 `/api/conversations/<id>/messages` 处理逻辑记录：

- `chat_requests_total{outcome="success|error"}`：聊天请求完成后的累计次数。
- `chat_inprogress_requests`：当前正在处理的聊天请求数；请求结束或异常时都会减回。
- `chat_request_duration_seconds`：每个聊天请求的服务端处理耗时 Histogram，包含模拟失败。Prometheus 文本输出同时包含各桶、`_sum` 与 `_count`。

`/metrics` 和其他页面/API 不计入聊天指标。标签不包含消息正文、姓名或请求 ID。mock 状态由 `/api/lab4/status` 报告，访问脚本在发送聊天请求前会通过本机 HTTP 读取并核验状态。

## 本地运行

本次环境为 Windows x64、Python 3.13.9。应用监听 `127.0.0.1:5001`；Prometheus 监听 `127.0.0.1:9090`，每 2 秒采集一次 `/metrics`；Grafana 监听 `127.0.0.1:3000`，数据源指向本机 Prometheus。

Prometheus 3.15.0 与 Grafana Enterprise 12.4.2 Windows x64 官方包放在个人 `.tools/downloads/`，SHA256 已与官方发布值核对。Grafana Enterprise 包含本实验使用的 OSS 仪表盘和 Prometheus 数据源能力。程序解压到 `.tools/prometheus/`、`.tools/grafana/`；TSDB、Grafana 数据库/日志/插件及会话数据写入 `.runtime/`。工具与运行数据被个人 `.gitignore` 忽略。

从仓库根目录在 PowerShell 运行：

```powershell
$project = Resolve-Path 'lab4/2500013086-lizhangyu'
& "$project/.venv/Scripts/python.exe" "$project/app.py"
```

另开一个 PowerShell 窗口启动监控工具：

```powershell
& "$project/start-monitoring.ps1"
```

首次在新环境准备 Python 时，在个人目录执行 `python -m venv .venv`，然后用 `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` 安装依赖。在当前电脑上使用 Python 3.13.9。Grafana 首次登录默认账号为 `admin`，初始密码为 `admin`；随后可在 Grafana 修改密码。

Prometheus Target 页面：<http://127.0.0.1:9090/targets>

Grafana 仪表盘：<http://127.0.0.1:3000/d/lab4-chat-monitoring/lab-4-chat-application-monitoring>

仪表盘 JSON 导出为 `grafana-dashboard.json`；Grafana 本地自动预置副本为 `dashboards/chat-monitoring.json`，数据源与仪表盘预置配置在 `provisioning/`。首次导入时选择 `Lab 4 Prometheus` 数据源。

## 仪表盘查询

1. 成功 / 失败请求速率：`sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))`。展示最近 30 秒窗口内每秒完成数，阶段边界会平滑。
2. 正在处理的聊天请求：`sum(chat_inprogress_requests{job="chat-app"})`。表示当前在处理的请求，不是在线用户数；持续数秒的慢请求较容易被 2 秒采集间隔观察到，极短峰值可能被漏过。
3. 平均聊天处理耗时：`sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))`。单位秒；没有近期样本时可能没有值。Histogram 同时提供桶、总和、样本数。

## 访问模拟与实际结果

`simulate_traffic.py` 是课程提供的原版调度器；`project_adapter.py` 将它连接到原聊天 API。适配器核验 mock 状态、创建一个专用实验会话，并构造 `POST /api/conversations/<id>/messages` 请求。延迟由后端在处理期间执行，指定失败也由后端返回 HTTP 503。调度器只发送 HTTP 请求，不直接修改指标或 Prometheus 数据。

首次完整模拟于 2026-10-19（上海时间）运行，默认每阶段 30 秒：

| 阶段 | 设置 | 实际发送 | 成功 | 业务/HTTP 错误 | 跳过 | 网络错误 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 1 次/秒，延迟 0.1 秒 | 30 | 30 | 0 | 0 | 0 |
| burst | 4 次/秒，延迟 0.1 秒 | 120 | 120 | 0 | 0 | 0 |
| slow | 2 次/秒，延迟 3 秒，并发上限 6 | 52 | 52 | 0 | 8 | 0 |
| errors | 1 次/秒，每第 3 次模拟失败 | 30 | 20 | 10 | 0 | 0 |
| recovery | 1 次/秒，延迟 0.1 秒 | 30 | 30 | 0 | 0 | 0 |

第二次运行只运行 slow 阶段，保持 2 次/秒与 3 秒延迟，将并发上限从 6 提高到 12：发送 60 次，60 次成功，0 错误、0 跳过、0 网络错误。并发上限增加后，慢阶段不再跳过调度机会；此运行没有启用 errors 场景的每第三次失败规则，因此没有模拟失败。目标速率是调度目标，实际完成数会受后端耗时和并发上限影响。

两次真实 JSON 结果分别保存在 `results/first-run.json` 和 `results/changed-run.json`。Targets 原始截图、包含三个 Panel 的完整仪表盘截图及各 Panel 细节截图保存在 `screenshots/`。
