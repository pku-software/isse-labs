# Lab 4：聊天应用监控（Prometheus + Grafana）

本项目基于 Lab 3 的 Flask 聊天应用。应用默认以 mock 模式运行，不读取 `.env`，不调用真实 DeepSeek API；原 real 模式代码保留，但不作为本实验运行路径。

## 项目结构

- `app.py`：Flask 应用、聊天接口、mock/real 模式、`/metrics` 和 `/api/status`。
- `metrics.py`：Prometheus 指标定义。
- `frontend/`：原聊天前端。
- `project_adapter.py`：访问脚本适配器。
- `simulate_traffic.py`：课程提供的五阶段访问调度器。
- `prometheus.yml`：Prometheus 采集配置。
- `grafana-dashboard.json`：可导入的 Grafana 仪表盘，包含三个 Panel。
- `results/`：两次真实模拟结果。
- `screenshots/`：Prometheus Targets 和 Grafana 仪表盘截图。

## 指标定义

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"}` | Counter | 成功完成的聊天请求累计数 |
| `chat_requests_total{outcome="error"}` | Counter | 失败或异常的聊天请求累计数 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求数 |
| `chat_request_duration_seconds` | Histogram | 服务端聊天处理耗时，单位秒 |

聊天接口处理完成时更新 Counter，处理开始/结束时增减 Gauge，耗时写入 Histogram。异常路径也保证 Gauge 回落。

## mock 与 real 模式

应用通过环境变量 `APP_MODE` 区分模式，默认值为 `mock`。

- mock 模式：不创建真实模型客户端，返回固定测试回复；支持 `delay_seconds` 和 `force_error` 实验选项。
- real 模式：沿用原 DeepSeek 调用逻辑，需要自行配置真实 Key；本实验不运行。

`GET /api/status` 返回实际模式和外部模型调用状态。mock 模式为：

```json
{"mode": "mock", "external_model_calls": false}
```

## 本机运行

当前环境为 Windows 11 AMD64，Python 3.13。

### 应用

```powershell
python -m venv .venv
python -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

应用监听 `http://127.0.0.1:5001`。

### Prometheus

版本：`3.15.0`

```powershell
.\.tools\prometheus\prometheus-3.15.0.windows-amd64\prometheus.exe `
  --config.file=prometheus.yml `
  --storage.tsdb.path=.runtime/prometheus/data `
  --web.listen-address=127.0.0.1:9090
```

监听 `http://127.0.0.1:9090`。

### Grafana

版本：`13.2.4`

```powershell
$env:GF_PATHS_DATA = ".runtime/grafana/data"
$env:GF_PATHS_LOGS = ".runtime/grafana/logs"
$env:GF_PATHS_PLUGINS = ".runtime/grafana/plugins"
$env:GF_PATHS_PROVISIONING = ".runtime/grafana/provisioning"
$env:GF_SERVER_HTTP_ADDR = "127.0.0.1"
$env:GF_SERVER_HTTP_PORT = "3000"
$env:GF_SERVER_ROOT_URL = "http://127.0.0.1:3000/"

.\.tools\grafana\grafana-13.2.4\bin\grafana.exe server `
  --homepath=.tools/grafana/grafana-13.2.4
```

Grafana 监听 `http://127.0.0.1:3000`，默认账号 `admin`，密码 `admin`。

## 三个 Panel 的查询含义

数据源为 Prometheus，地址 `http://127.0.0.1:9090`，UID 为 `prometheus`。

1. 成功/失败请求变化

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
```

表示最近 30 秒窗口内平均每秒完成的成功/失败请求数。

2. 正在处理的请求

```promql
sum(chat_inprogress_requests{job="chat-app"})
```

表示当前正在执行的聊天处理数量，不是在线用户数。

3. 平均处理耗时

```promql
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s]))
/
sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

表示最近 30 秒窗口内服务端平均处理耗时，单位秒。

## 访问脚本适配位置

`project_adapter.py` 中实现：

- `confirm_mock_mode`：GET `/api/status`，核验 mock 且外部模型调用关闭。
- `build_chat_request`：POST `/api/messages`，携带 `message`、`delay_seconds`、`force_error`。
- `response_is_success`：仅当 HTTP 201 且响应 JSON 包含 `reply` 和 `id` 时判定成功。

## 两次真实模拟结果

### 第一次完整模拟

输出：`results/first-run.json`

五阶段各 30 秒：

| 阶段 | 时间（UTC） | 主要结果 |
| --- | --- | --- |
| baseline | 2026-10-18T15:37:08Z | 发送 30，成功 30 |
| burst | 2026-10-18T15:37:38Z | 发送 120，成功 120 |
| slow | 2026-10-18T15:38:08Z | 发送 52，成功 52，跳过 8 |
| errors | 2026-10-18T15:38:41Z | 发送 30，成功 20，业务/HTTP 错误 10 |
| recovery | 2026-10-18T15:39:11Z | 发送 30，成功 30 |

可复现的图表现象：baseline 到 burst 时成功请求速率上升；slow 阶段平均耗时和在途请求数上升；errors 阶段 error 曲线上升；recovery 阶段恢复。

### 第二次参数调整模拟

参数：`--scenario burst --burst-rate 8 --phase-seconds 30`

输出：`results/changed-run.json`

阶段时间：2026-10-18T16:34:29Z 到 2026-10-18T16:34:59Z，发送 240，成功 240，跳过 0。相比第一次 burst 阶段，成功请求速率明显更高，在途请求数只有小幅波动。

## 仪表盘导入

在 Grafana 中进入 Dashboards → New → Import，上传 `grafana-dashboard.json`；如果数据源 UID 不匹配，选择本机 Prometheus 数据源即可。
