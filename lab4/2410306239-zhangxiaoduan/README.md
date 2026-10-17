# Lab 4：聊天应用的 Prometheus + Grafana 监控

课程「智能化系统与软件工程」Lab 4 个人提交（学号 2410306239）。本实验在 Lab 2/3 的 Flask 聊天应用上接入 Prometheus 指标采集与 Grafana 看板，全部在本地完成：应用、Prometheus、Grafana 均运行于本机，不依赖 Docker 或云端。

## 项目来源

- 上游课程仓库：`pku-software/isse-labs` 的 `lab4/` 目录，fork 后在本目录完成个人部分。
- 聊天应用代码来自 Lab 2/3（Flask + 前端页面 + 会话 CRUD），本实验在其上新增指标与实验选项，原有功能保持可用。
- 流量模拟脚本来自课程 `lab4/starter/simulate_traffic.py`（调度器），本目录通过 `project_adapter.py` 适配本项目接口。

## 运行模式（mock / real）

应用通过环境变量 `APP_MODE` 区分两种模式（默认 `mock`）：

- **mock**：固定测试回复，不创建模型客户端、不调用真实模型，**不需要 API Key**。支持两个实验选项：`delay_seconds`（后端 sleep，上限 5 秒）、`force_error`（强制返回 503）。本实验全程使用该模式。
- **real**：沿用 Lab 2/3 行为，携带历史消息调用 DeepSeek，需要环境变量 `DEEPSEEK_API_KEY`（只存在于后端环境变量，不进入代码、仓库或截图）。

实验专用状态接口 `GET /api/mode` 按实际配置返回 `{"mode": ..., "external_model_calls": ...}`，供访问脚本核验当前是否为 mock 模式。

## 自定义指标（`metrics.py`）

| 指标 | 类型 | 含义 |
|---|---|---|
| `chat_requests_total{outcome}` | Counter | 聊天消息处理次数，按结果分为 `success` / `error` |
| `chat_inprogress_requests` | Gauge | 正在处理的聊天请求数（进入时 +1，`finally` 中 -1） |
| `chat_request_duration_seconds` | Histogram | 服务端处理耗时（秒），桶：0.05/0.1/0.25/0.5/1/2/3/5/10 |

指标在消息路由的 `try / except / finally` 中收尾，任何结果（成功、模拟失败、意外异常）都正确计数。`GET /metrics` 返回 Prometheus 文本格式。Flask 以**单进程 + 多线程**运行（`threaded=True, debug=False`），避免多进程各维护一套指标；会话存储用 `threading.Lock` 保护。

## 工具版本与端口

| 组件 | 版本 | 端口 | 说明 |
|---|---|---|---|
| Python | 3.9.6 | — | 虚拟环境 `.venv/`（git 忽略） |
| Flask | 3.1.3 | — | `requirements.txt` |
| prometheus-client | 0.26.0 | — | 指标库 |
| 聊天应用 | — | 5001 | `app.py`，仅监听 127.0.0.1 |
| Prometheus | 3.13.4 | 9090 | 抓取间隔 2s、超时 1s，目标 `127.0.0.1:5001` |
| Grafana | 13.2.4 | 3000 | 数据源指向 Prometheus |

工具二进制与运行数据放在 git 忽略的 `.tools/`、`.runtime/` 目录，不进入仓库。本机存在 HTTP 代理环境，启动以下进程时用 `NO_PROXY=127.0.0.1,localhost` 避免回环请求被代理转发。

### 启动命令

```bash
# 1. 应用（mock 模式）
NO_PROXY=127.0.0.1,localhost .venv/bin/python app.py

# 2. Prometheus（配置 lab4/prometheus.yml，数据目录 .runtime/prometheus）
NO_PROXY=127.0.0.1,localhost .tools/prometheus/prometheus \
  --config.file=prometheus.yml \
  --storage.tsdb.path=.runtime/prometheus \
  --web.listen-address=127.0.0.1:9090

# 3. Grafana（数据/日志/插件目录均在 .runtime/grafana 下）
NO_PROXY=127.0.0.1,localhost .tools/grafana/bin/grafana server \
  --homepath=<绝对路径>/.tools/grafana \
  --config=<绝对路径>/.tools/grafana/conf/defaults.ini \
  --paths.data=<绝对路径>/.runtime/grafana/data
```

## Grafana 看板与 PromQL

看板「聊天应用监控」（uid `lab4-chat`，5s 自动刷新，导出文件见 `grafana-dashboard.json`），三个面板：

| 面板 | 查询 | 意义 |
|---|---|---|
| 成功/失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 每秒成功/失败请求数，反映访问频率与错误占比 |
| 正在处理的请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 当前在途请求数，约等于频率 × 平均耗时，反映服务瞬时负载 |
| 平均处理耗时 | `sum(rate(chat_request_duration_seconds_sum[30s])) / sum(rate(chat_request_duration_seconds_count[30s]))` | 30s 窗口内平均服务端耗时，反映后端处理速度 |

## 调度器适配（`project_adapter.py`）

课程调度器（`simulate_traffic.py`）不假设本项目接口细节，由本目录的适配器翻译成实际 HTTP 调用：

- `confirm_mock_mode`：GET `/api/mode` 核验 `mode == "mock"` 且 `external_model_calls == false`，通过后创建一次测试会话供后续消息复用；任何异常或重定向均返回 False（HTTPRedirectHandler 禁止跟随重定向）。
- `build_chat_request`：构造 `POST /api/conversations/<测试会话>/messages` 请求，JSON 携带 `message` 与 `delay_seconds` / `force_error` 实验选项；延迟发生在后端，不是客户端 sleep 冒充。
- `response_is_success`：2xx 且 JSON 中最后一条消息有非空 `reply` 才判成功，503 等均判失败。

四项单请求验证全部通过：mock 服务核验、正常请求判成功、强制错误判失败、real 模式服务被拒绝。

## 两次模拟运行

模拟器参数：`--base-url http://127.0.0.1:5001`，每阶段 30s，在途上限 `--concurrency 6`（默认），输出 `results/*.json`。

### 第一次：全场景（`results/first-run.json`）

`--scenario all`（默认）：baseline 1 次/s → burst 4 次/s → slow 2 次/s、延迟 3s → errors 1 次/s、每 3 次失败 1 次 → recovery 1 次/s。

| 阶段 | 发送 | 成功 | 业务错误 | 跳过 | 客户端平均耗时 |
|---|---|---|---|---|---|
| baseline | 30 | 30 | 0 | 0 | 0.11s |
| burst | 120 | 120 | 0 | 0 | 0.11s |
| slow | 52 | 52 | 0 | 8 | 3.02s |
| errors | 30 | 20 | 10 | 0 | 0.11s |
| recovery | 30 | 30 | 0 | 0 | 0.12s |

观察：slow 阶段「正在处理的请求」升到约 6（2 次/s × 3s），8 次请求因在途上限被跳过；errors 阶段速率面板出现 `error` 线；recovery 后各项回到 baseline 水平。

### 第二次：提高 burst 频率（`results/changed-run.json`）

`--scenario burst --burst-rate 8`（默认 4 翻倍）：发送 240，成功 240，错误 0，跳过 0，客户端平均耗时 0.11s。

观察：成功速率升到约 8 次/s；在途请求与平均耗时几乎不变——频率 × 0.1s 延迟仍不足 1 个在途请求，耗时由后端延迟决定而非频率。

## 文件说明

- `app.py` / `metrics.py` / `project_adapter.py`：应用与实验代码
- `prometheus.yml`：Prometheus 抓取配置（课程提供）
- `simulate_traffic.py`：流量调度器（课程 starter，未修改）
- `results/first-run.json`、`results/changed-run.json`：两次模拟的逐阶段统计
- `grafana-dashboard.json`：从 Grafana API 导出的看板定义
- `screenshots/prometheus-targets.png`：Prometheus Targets 页面截图
- `screenshots/grafana-dashboard.png`、`screenshots/grafana-dashboard-panel3.png`：Grafana 看板上/下部分截图
- `.tools/`、`.runtime/`、`.venv/`、`data/`：工具、运行数据与依赖，git 忽略
