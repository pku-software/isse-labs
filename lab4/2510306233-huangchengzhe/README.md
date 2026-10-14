# Lab 4：黄诚哲 2510306233 —— 聊天应用监控

本项目源自个人 Lab 3 的 Flask 聊天应用，在此基础上加入 Prometheus 指标、mock 模拟模式和 `/metrics` 接口，并用 Prometheus + Grafana 完成本地监控。

## 项目功能

- 保留原聊天应用的前端与 CRUD：会话/消息的增删改查，聊天接口为 `POST /api/conversations/<id>/messages`。
- 新增 mock 模式（默认）：不创建、不调用真实 DeepSeek 客户端，返回固定测试回复；聊天接口在 mock 模式下接受实验用的 `delay` 与 `fail` 字段。
- real 模式（保留）：设置 `APP_MODE=real` 且提供 `DEEPSEEK_API_KEY` 时走真实模型调用；本实验不运行它。
- 暴露 `/metrics`，只统计聊天处理，不统计静态资源、状态接口或 `/metrics` 自身。

## 指标

| 类型 | 指标 | 含义 |
| --- | --- | --- |
| Counter | `chat_requests_total{outcome="success"\|"error"}` | 累计聊天处理次数，按结果区分 |
| Gauge | `chat_inprogress_requests` | 当前正在处理的聊天请求数 |
| Histogram | `chat_request_duration_seconds` | 每次聊天服务端处理耗时（含失败） |

## 本地运行

环境：Windows 11（AMD64），Python 3.14。

首次准备：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

启动应用（默认 mock 模式）：

```powershell
.venv\Scripts\python.exe app.py
```

启动监控（Prometheus + Grafana）：

```powershell
powershell -ExecutionPolicy Bypass -File start-monitoring.ps1
```

端口：应用 5001、Prometheus 9090、Grafana 3000，均绑定 `127.0.0.1`。

工具版本与固定位置：

- Prometheus v3.15.0，解压于 `.tools/prometheus/`，数据目录 `.runtime/prometheus/`。
- Grafana v13.2.4，解压于 `.tools/grafana/`，数据/日志/插件在 `.runtime/grafana/` 下。

## 采集与仪表盘

`prometheus.yml`：job `chat-app`，采集间隔 2 秒、超时 1 秒，目标 `127.0.0.1:5001`。

Grafana 数据源 `Lab4 Prometheus`（uid `lab4-prometheus`）指向 `http://127.0.0.1:9090`，由 `provisioning/datasources/prometheus.yml` 自动配置；仪表盘由 `provisioning/dashboards/lab4.yml` 自动从 `dashboards/grafana-dashboard.json` 导入。

三个 Panel 与查询：

| Panel | PromQL | 意义 |
| --- | --- | --- |
| 成功/失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近 30 秒窗口内平均每秒完成的请求数 |
| 正在处理的聊天请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 当前正在处理的请求数 |
| 平均服务端处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近 30 秒窗口内的平均处理秒数 |

## 访问模拟脚本

调度器 `simulate_traffic.py` 是课程模板副本（未改调度逻辑），负责发送节奏与并发。`project_adapter.py` 是项目适配层，实现三处：`confirm_mock_mode()` 读 `/api/lab-status` 核验 mock、`build_chat_request()` 构造聊天接口请求、`response_is_success()` 判断业务结果。消息需挂在会话下，适配器会先自动创建并缓存一个「监控实验会话」。

## 实验运行结果

第一次完整运行（`results/first-run.json`，北京时间 2026-10-14 09:18:52–09:21:25，五阶段各 30 秒）：

| 阶段 | 发送 | 成功 | 业务错误 | 跳过 | 客户端平均耗时 |
| --- | --- | --- | --- | --- | --- |
| baseline | 30 | 30 | 0 | 0 | 0.15s |
| burst | 120 | 120 | 0 | 0 | 0.15s |
| slow | 52 | 52 | 0 | 8 | 3.06s |
| errors | 30 | 20 | 10 | 0 | 0.16s |
| recovery | 30 | 30 | 0 | 0 | 0.16s |

第二次运行（`results/changed-run.json`）：只跑 `slow` 场景，把 `--slow-delay` 从 3 改为 1.5，北京时间 2026-10-14 09:32:34–09:33:05。发送 60、成功 60、跳过 0，客户端平均耗时 1.56 秒。

观察结论：访问频率提高主要改变「成功/失败请求速率」；后端延迟改长会把「正在处理的聊天请求」和「平均服务端处理耗时」顶高，而不改变速率。慢请求延迟 3 秒时在途请求撞到并发上限 6，跳过 8 次；延迟减半到 1.5 秒后在途稳定在 3，一次不跳过。`rate()` 的 30 秒滑动窗口会把阶段切换平滑成斜坡。

## 截图

- `screenshots/prometheus-targets.png`：本应用 target 为 `UP`。
- `screenshots/grafana-dashboard-requests.png`、`grafana-dashboard-inprogress.png`、`grafana-dashboard-duration.png`：首次完整模拟的仪表盘三个 Panel（分别截取）。
