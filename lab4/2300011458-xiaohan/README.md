# Lab 4：聊天应用可观测性

- 姓名：肖涵
- 学号：2300011458
- 项目来源：`lab3/2300011458-XiaoHan`
- 实验环境：Windows、Python 3.11、Prometheus 3.15.0、Grafana OSS 10.1.5

本目录在 Lab 3 聊天应用的基础上加入 Prometheus 指标、mock 实验模式、
本地 Prometheus/Grafana 配置，以及课程访问模拟脚本的项目适配层。所有服务
只监听本机地址；实验流量不调用外部模型，也不需要真实 API Key。

## 应用模式

应用读取进程环境变量 `LAB4_APP_MODE`：

- `mock`（默认）：返回固定测试回复，允许实验脚本设置后端延迟和强制错误；
  `/api/lab4/status` 返回 `mode=mock` 和 `external_model_calls=false`。
- `real`：使用进程环境中的 `DEEPSEEK_API_KEY` 调用原聊天模型；mock 状态接口
  返回 404。应用不会自动读取 `.env` 文件。

`project_adapter.py` 将课程调度器的通用动作转换为本项目的
`POST /api/conversations/<id>/messages` 请求。适配器通过真实 HTTP 状态接口
确认 mock 模式，必要时创建实验会话，并结合 HTTP 201 与响应 JSON 判断成功。

## 指标

应用在 `http://127.0.0.1:5001/metrics` 暴露以下指标：

- `chat_requests_total{outcome="success|error"}`：已完成聊天请求的累计次数；
- `chat_inprogress_requests`：当前正在处理的聊天请求数；
- `chat_request_duration_seconds`：服务端聊天请求耗时 Histogram。

错误路径也会增加 `outcome="error"`、记录耗时并在 `finally` 中减少 Gauge。

Grafana 仪表盘包含三个查询：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
```

```promql
sum(chat_inprogress_requests{job="chat-app"})
```

```promql
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s]))
/
sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

它们分别显示成功/错误请求速率、瞬时在途请求数和最近窗口内的平均服务端耗时。

## 本地启动

首次运行先创建虚拟环境并安装 Python 依赖：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

从官方发行包取得 Prometheus 3.15.0 与 Grafana OSS 10.1.5，并分别解压到
`.tools/prometheus/` 和 `.tools/grafana/`。这些本地工具、运行数据和虚拟环境均被
`.gitignore` 排除。

在两个 PowerShell 窗口中从本目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\start-app.ps1
powershell -ExecutionPolicy Bypass -File .\start-monitoring.ps1
```

本地端口如下：

- 聊天应用与 `/metrics`：`http://127.0.0.1:5001`
- Prometheus：`http://127.0.0.1:9090`
- Grafana：`http://127.0.0.1:3000`

`prometheus.yml` 每 2 秒抓取一次 `job="chat-app"`。
`provisioning/datasources/prometheus.yml` 配置 Prometheus 数据源；
`start-monitoring.ps1` 在 Grafana 就绪后通过本地 API 导入
`grafana-dashboard.json`。本地管理员密码只写入被忽略的 `.runtime/` 目录。

## 复现实验

应用、Prometheus 和 Grafana 就绪后，在本目录运行完整模拟：

```powershell
.\.venv\Scripts\python.exe -X utf8 .\simulate_traffic.py `
  --base-url http://127.0.0.1:5001 `
  --output .\results\first-run.json
```

调度器只访问本机 HTTP 接口，不直接修改指标。默认依次运行 baseline、burst、
slow、errors 和 recovery，每阶段 30 秒，最后等待 10 秒让 Prometheus 记录恢复。

本次首次运行发生于 2026-10-16 05:43:11–05:45:44 UTC：

| 阶段 | 发送 | 成功 | 业务/HTTP 错误 | 跳过 | 客户端平均耗时 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 30 | 30 | 0 | 0 | 0.118 s |
| burst | 120 | 120 | 0 | 0 | 0.121 s |
| slow | 52 | 52 | 0 | 8 | 3.023 s |
| errors | 30 | 20 | 10 | 0 | 0.119 s |
| recovery | 30 | 30 | 0 | 0 | 0.123 s |

所有阶段的网络错误与非预期结果均为 0。Grafana 中 burst 的成功请求速率峰值约
为 4 req/s；slow 的在途请求峰值为 6、平均服务端耗时峰值约为 3 秒；errors
阶段出现错误速率，recovery 后各速率与 Gauge 回落。

第二次运行只把 `--burst-rate` 从 4 改为 8：

```powershell
.\.venv\Scripts\python.exe -X utf8 .\simulate_traffic.py `
  --base-url http://127.0.0.1:5001 `
  --scenario burst --phase-seconds 30 --burst-rate 8 `
  --output .\results\changed-run.json
```

该运行发生于 2026-10-16 05:59:34–06:00:04 UTC，共发送并成功处理 240 次请求，
无错误、跳过或非预期结果。Prometheus 记录的成功请求速率峰值约为 8.04 req/s，
在途请求采样峰值为 1，平均服务端耗时峰值约为 0.117 秒。与首次 burst 相比，
吞吐率翻倍，但短请求没有造成明显的在途请求堆积或平均耗时增长。

真实结果保存在 `results/first-run.json` 和 `results/changed-run.json`；实验截图
保存在 `screenshots/prometheus-targets.png` 和
`screenshots/grafana-dashboard.png`。
