# Lab 4：聊天应用监控（Prometheus + Grafana）

本项目在 Lab 2/3 的 Flask 聊天应用上增加指标，由 Prometheus 周期采集，再由
Grafana 画出请求速率、在途请求数和平均处理耗时三个 Panel。全部在本机运行，
不需要 Docker、WSL 或云服务器。

## 项目结构

```text
app.py                     Flask 应用（页面、聊天 CRUD、mock/real 模式、/metrics）
metrics.py                 Counter / Gauge / Histogram 三个指标的定义
frontend/                  原有前端页面和静态资源
prometheus.yml             本次实际使用的采集配置（应用地址 127.0.0.1:5001）
grafana.ini                本机 Grafana 配置（数据、日志、插件都写入 .runtime/）
grafana-dashboard.json     可导入的仪表盘，包含三个 Panel
provisioning/              Grafana 数据源和仪表盘的自动加载配置
simulate_traffic.py        课程提供的访问调度器（个人副本，未改调度逻辑）
project_adapter.py         本项目接口适配，三个函数已补齐
results/first-run.json     首次完整五阶段模拟的真实输出
results/changed-run.json   把 slow 延迟改为 1 秒后的真实输出
screenshots/               Prometheus Target 与 Grafana 仪表盘截图
start-app.ps1              启动聊天应用（mock 模式）
start-monitoring.ps1       启动 Prometheus 与 Grafana
```

## 运行模式

应用用环境变量 `CHAT_MODE` 区分两种模式，默认是 `mock`：

- `mock`：不创建、不调用真实模型客户端，用固定测试回复代替，因此不需要
  DeepSeek Key。`POST /api/messages` 额外接受两个实验选项：
  `delay_seconds`（0～5 秒，后端在处理期间真实等待）和 `force_error`
  （返回 503 和明确的错误 JSON）。这两个选项只在 mock 模式生效。
- `real`：保持 Lab 3 的行为，读取 `.env` 中的 `DEEPSEEK_API_KEY` 调用
  DeepSeek；实验选项被忽略。

实验用的状态接口是 `GET /api/status`，如实返回当前模式，例如
`{"mode":"mock","external_model_calls":false}`。访问脚本在发送聊天请求前
先核验这个接口。

## 指标

定义在 `metrics.py`，由 `GET /metrics` 按 prometheus_client 标准格式暴露：

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | Counter | 聊天请求处理完成的总次数，按结果区分 |
| `chat_inprogress_requests` | Gauge | 此刻正在处理、尚未结束的聊天请求数 |
| `chat_request_duration_seconds` | Histogram | 每次聊天处理的服务端耗时，桶为 0.05、0.1、0.25、0.5、1、2、3、5、10 秒 |

只有 `POST /api/messages` 进入聊天处理后才计数；`/metrics`、`/api/status`
和静态资源不计入。在途数在 `finally` 中减一，成功、模拟失败和异常都会回落；
失败计入 `outcome="error"`。聊天记录列表用线程锁保护，应用单进程多线程运行，
慢请求期间 `/metrics` 仍可响应。

## 本机工具与端口

| 程序 | 版本 | 地址 |
| --- | --- | --- |
| 聊天应用 | Flask 3.1.3 | http://127.0.0.1:5001 |
| Prometheus | 3.13.4（windows-amd64，SHA-256 已核对） | http://127.0.0.1:9090 |
| Grafana | 11.0.0（官方 Enterprise 安装包，使用免费 OSS 功能，SHA-256 已核对） | http://127.0.0.1:3000 |

工具解压在 `.tools/prometheus/`、`.tools/grafana/`；Prometheus 数据在
`.runtime/prometheus/`，Grafana 数据、日志、插件在 `.runtime/grafana/`，
应用日志在 `.runtime/app/`。这些目录和个人 `.venv/` 都被 `.gitignore` 排除。

## 从干净环境重新运行（Windows PowerShell）

```powershell
# 1. 在个人目录创建虚拟环境并安装依赖
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. 启动聊天应用（mock，无需 Key）
.\start-app.ps1

# 3. 启动 Prometheus 与 Grafana
.\start-monitoring.ps1
```

两个启动脚本会显式指定配置文件、数据目录和监听地址，只绑定 127.0.0.1。
Prometheus 每 2 秒采集一次 `/metrics`，超时 1 秒，job 名为 `chat-app`。
Grafana 启动时通过 `provisioning/` 自动添加数据源 `Prometheus`
（uid `lab4-prometheus`，地址 `http://127.0.0.1:9090`）并加载
`grafana-dashboard.json`。

手动导入仪表盘时，在 Grafana 选择 Dashboards → Import → 上传
`grafana-dashboard.json`，数据源选本机 Prometheus；若 uid 不一致，
导入后把三个 Panel 的数据源改为新数据源即可。

## 三个 Panel 的查询

1. 成功 / 失败请求速率：

   ```promql
   sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
   ```

   最近 30 秒内平均每秒完成的请求数，两条曲线分别对应 success 和 error，
   不是累计次数。

2. 在途请求：

   ```promql
   sum(chat_inprogress_requests{job="chat-app"})
   ```

   瞬时值，表示此刻正在处理的聊天数量，不是在线用户数。

3. 平均处理耗时：

   ```promql
   sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s]))
     / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
   ```

   最近 30 秒的服务端平均耗时，单位秒；没有请求时可能无值。

Histogram 除了 `_sum` 和 `_count`，还暴露按桶累计的 `_bucket`，
用来观察慢请求的分布；平均耗时用总和除以次数得到。

## 访问脚本适配

`simulate_traffic.py` 是课程调度器的个人副本，负责发送节奏、并发上限、
五阶段切换和结果统计，没有改动调度逻辑。`project_adapter.py` 补齐了三处：

- `confirm_mock_mode()`：GET `/api/status`，只有 `mode=mock` 且
  `external_model_calls=false` 才允许运行，且拒绝跟随重定向；
- `build_chat_request()`：POST `/api/messages`，JSON 字段为 `message`、
  `delay_seconds`、`force_error`；
- `response_is_success()`：仅当 HTTP 201 且 `reply` 为非空字符串时判为成功，
  503 模拟错误和 400 校验错误都判为失败。

## 实验记录（真实运行）

环境：Windows，应用 127.0.0.1:5001，Prometheus 采集间隔 2 秒。

### 第一次：完整五阶段

参数：`--scenario all`，每阶段 30 秒，`--slow-delay 3`，并发上限 6。
时间：2026-10-18 23:07:11 – 23:09:43（脚本 JSON 中为 UTC）。

| 阶段 | 目标速率 | 后端延迟 | 发送 | 成功 | 失败 | 跳过 | 客户端平均耗时 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 1 次/秒 | 0.1 秒 | 30 | 30 | 0 | 0 | 0.13 秒 |
| burst | 4 次/秒 | 0.1 秒 | 120 | 120 | 0 | 0 | 0.14 秒 |
| slow | 2 次/秒 | 3 秒 | 52 | 52 | 0 | 8 | 3.04 秒 |
| errors | 1 次/秒 | 0.1 秒 | 30 | 20 | 10 | 0 | 0.14 秒 |
| recovery | 1 次/秒 | 0.1 秒 | 30 | 30 | 0 | 0 | 0.13 秒 |

Prometheus 观测到的同区间数值：在途请求峰值 6，平均耗时峰值约 3.0 秒，
成功速率峰值 4.0 次/秒，错误速率峰值约 0.36 次/秒。slow 阶段的 8 次
`skipped` 是并发槽位（6 个）占满后放弃发送，网络错误和业务错误都是 0，
不是请求超时。`rate(...[30s])` 的窗口平滑会让速率曲线的下降滞后于阶段边界。

### 第二次：只改 slow 延迟

参数：`--scenario slow --slow-delay 1`，速率 2 次/秒，并发上限 6。
时间：2026-10-18 23:29:13 – 23:29:44。

结果：发送 60、成功 60、失败 0、跳过 0，客户端平均耗时 1.03 秒；
Prometheus 中在途请求峰值 2，平均耗时约 1.00 秒。

对比说明：在途请求数约等于"到达速率 × 单个请求处理时间"。第一次
2 × 3 = 6，正好顶到并发上限，导致 8 次发送被跳过；第二次 2 × 1 = 2，
远低于上限 6，所以没有跳过。burst 虽然达到 4 次/秒，但每次仅 0.1 秒，
4 × 0.1 = 0.4，因此在途曲线基本贴近 0，主要变化体现在请求速率上。
