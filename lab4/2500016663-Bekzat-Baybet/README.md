# Lab 4：聊天应用监控（别克扎提·拜别提 2500016663）

本项目从 Lab 3 的 Flask 聊天应用复制而来，在不改动原有聊天与增删改查功能的前提下，为聊天接口加上 Prometheus 指标，由 Prometheus 按固定间隔采集、Grafana 用三个 Panel 展示，并用课程提供的访问脚本在本机模拟五种流量阶段。

## 项目功能

- 保留原聊天应用：前端页面（`frontend/`）收发消息，`POST /api/messages` 新建消息，`GET /api/messages` 列出、`PATCH /api/messages/<id>` 修改、`DELETE /api/messages/<id>` 删除。
- 回复来源由环境变量 `CHAT_MODE` 决定，默认 `mock`：
  - `mock`：返回本地固定文本，不创建也不调用真实模型客户端，不需要 DeepSeek Key；聊天接口额外接受两个实验选项——`delay_seconds`（后端真实 `sleep` 后再返回，上限 10 秒）和 `force_error`（返回 503 模拟外部模型调用失败）。
  - `real`：沿用原来的 DeepSeek 调用，忽略上述实验选项。**本次实验全程只运行 `mock`，没有产生任何真实模型调用。**
- 暴露 `GET /metrics`（prometheus_client 标准文本格式）与实验状态接口 `GET /api/status`，后者返回 `{"mode": ..., "external_model_calls": ...}`。
- 三个业务指标**只统计聊天请求**，`/metrics`、`/api/status`、`/api/hello` 和静态资源都不计入：
  - Counter `chat_requests_total{outcome="success"|"error"}`：成功／错误累计，两种 outcome 在启动时初始化为 0。
  - Gauge `chat_inprogress_requests`：正在处理中的聊天请求数。
  - Histogram `chat_request_duration_seconds`：服务端处理耗时（含模拟失败），桶覆盖 0.05s 到 10s。
- 记账放在 `try/finally` 中：即使模型调用抛异常，也会执行 `Gauge.dec()` 并按 error 累计，不会出现"在途数卡住不回落"。
- 多线程共享的聊天记录列表和 id 计数器用一把 `threading.Lock` 保护；应用以 `threaded=True` 运行，慢聊天请求不会阻塞 `/metrics`。

## 运行环境

- Windows 11 x64，Git Bash，Python 3.13.6。
- Python 依赖见 `requirements.txt`：Flask 3.1.3、prometheus-client 0.26.0、python-dotenv 1.2.4、requests 2.34.2。
- **Prometheus 3.15.0（windows-amd64）**：取自官方 GitHub Release
  `https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.windows-amd64.zip`，
  同一 Release 的 `sha256sums.txt` 一并下载用于校验。
- **Grafana 12.4.2 Enterprise（windows-amd64）**：官方 `dl.grafana.com` 在本机实测下载速度只有 30–45 KB/s，OSS 包（13.2.4 约 473 MB、12.4.2 约 267 MB）无法在合理时间内下完，因此改从华为云镜像
  `https://mirrors.huaweicloud.com/grafana/12.4.2/` 获取 `grafana-enterprise_12.4.2_23531306697_windows_amd64.tar.gz`（296 MB）。
  该镜像的 12.4.2 目录下只提供 Enterprise 版和源码包，没有官方 OSS 的 windows-amd64 zip，所以本实验用的是 Enterprise 版；
  本实验用到的数据源、仪表盘与 Provisioning 功能与 OSS 版一致。
- 目录约定（均在个人目录内，且都被 `.gitignore` 忽略，不提交）：
  - `.tools/downloads/` 下载包与校验文件，`.tools/prometheus/`、`.tools/grafana/` 解压后的工具
  - `.runtime/prometheus/` 采集数据，`.runtime/grafana/` 数据／日志／插件，`.runtime/app/` 应用日志
  - `.venv/` Python 虚拟环境

## 端口与启动命令

三个程序都只监听本机：

| 程序 | 地址 |
| --- | --- |
| 应用 | `127.0.0.1:5001` |
| Prometheus | `127.0.0.1:9090` |
| Grafana | `127.0.0.1:3000` |

在个人目录内依次执行（可重复运行）：

```bash
bash start-app.sh          # CHAT_MODE=mock，日志追加到 .runtime/app/app.log
bash start-prometheus.sh   # --config.file=prometheus.yml --storage.tsdb.path=.runtime/prometheus --web.listen-address=127.0.0.1:9090
bash start-grafana.sh      # GF_PATHS_* 全部指向 .runtime/grafana/ 与 provisioning/，监听 127.0.0.1:3000
bash import-dashboard.sh   # 通过 Grafana HTTP API 导入 grafana-dashboard.json（幂等，覆盖同名仪表盘）
```

- `prometheus.yml`：采集间隔 2s、超时 1s，job 名 `chat-app`，target `127.0.0.1:5001`，采集路径 `/metrics`。
- Grafana 通过 `provisioning/datasources/prometheus.yml` 自动创建数据源（名称 Prometheus，uid `prometheus-lab4`，指向 `http://127.0.0.1:9090`，且为默认数据源），登录账号 `admin` / `admin`（仅本机实验用的默认口令）。
- 仪表盘也可以直接在 Grafana 界面导入 `grafana-dashboard.json`；它引用的是上面的数据源 uid。

## 三个 Panel 的查询含义

| Panel | PromQL | 含义 |
| --- | --- | --- |
| 成功／失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近 30 秒窗口内平均每秒**完成**的成功／错误请求数，不是累计次数 |
| 正在处理中的请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 当前瞬时的在途聊天请求数 |
| 平均处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近 30 秒窗口内服务端平均每请求耗时，单位秒 |

三个窗口都用 `[30s]`，所以曲线对突变的反应有约 30 秒的滞后；仪表盘刷新间隔 2s。

## 访问脚本与适配

`simulate_traffic.py` 是课程调度器的个人副本，只负责发送节奏、并发上限、阶段切换和结果统计，**不直接改指标**。`project_adapter.py` 补齐了三处适配：

- `confirm_mock_mode()`：`GET /api/status`，只有响应为 `mode == "mock"` 且 `external_model_calls is False` 时才返回 True；禁用代理、不跟随重定向，避免被引导到别的主机。
- `build_chat_request()`：构造 `POST /api/messages`，请求体 `{"message", "delay_seconds", "force_error"}`，`Content-Type: application/json`。延迟由后端在处理期间真实消耗，客户端不做 sleep。
- `response_is_success()`：HTTP 201 且响应 JSON 中的 `reply` 为非空字符串时判成功；只做判断，不输出聊天正文。

单请求核验通过后才把 `ADAPTER_READY` 置为 `True`。

## 两次真实模拟结果

### 第一次：默认参数整轮运行

本地时间 17:49:03 – 17:51:36，完整结果见 `results/first-run.json`：

| 阶段 | 发送 | 成功 | 业务错误 | 跳过 | 客户端平均耗时 |
| --- | --- | --- | --- | --- | --- |
| baseline | 30 | 30 | 0 | 0 | 0.15s |
| burst | 120 | 120 | 0 | 0 | 0.15s |
| slow | 52 | 52 | 0 | 8 | 3.05s |
| errors | 30 | 20 | 10 | 0 | 0.15s |
| recovery | 30 | 30 | 0 | 0 | 0.15s |

### 第二次：只把 `--concurrency` 从 6 改成 3

本地时间 18:04:55 – 18:07:27，完整结果见 `results/changed-run.json`：

| 阶段 | 发送 | 成功 | 业务错误 | 跳过 | 客户端平均耗时 |
| --- | --- | --- | --- | --- | --- |
| baseline | 30 | 30 | 0 | 0 | 0.14s |
| burst | 120 | 120 | 0 | 0 | 0.14s |
| slow | 27 | 27 | 0 | 33 | 3.05s |
| errors | 30 | 20 | 10 | 0 | 0.15s |
| recovery | 30 | 30 | 0 | 0 | 0.15s |

### 两次运行在 Prometheus / Grafana 上的对照

以下都是按 30 秒窗口实际采集到的值：

| 观测项 | 第一次（并发 6） | 第二次（并发 3） |
| --- | --- | --- |
| 成功速率峰值 | 4.00 次/秒（burst 结束，17:50:03） | 4.00 次/秒（burst 结束，18:05:55） |
| slow 阶段稳态速率 | 约 1.68 次/秒 | 约 0.86 次/秒 |
| 在途请求峰值 | 6（17:50:21） | 3（18:05:57） |
| 平均耗时峰值 | 3.00 秒（17:50:33） | 3.00 秒（18:06:25） |

截图：

- `screenshots/prometheus-targets.png`：本应用 job 的 Target 状态为 `UP`。
- `screenshots/grafana-dashboard.png`：第一次运行的完整三 Panel。
- `screenshots/grafana-two-runs.png`：同一个 30 分钟时间轴上并排显示两次运行。

### 从两次结果能直接读出的结论

- 把并发上限从 6 降到 3 后，slow 阶段被跳过的调度机会从 8 次增加到 33 次，成功请求速率从约 1.68 次/秒降到约 0.86 次/秒，在途请求峰值从 6 降到 3；服务端的平均耗时峰值两次都是 3.00 秒，**没有变化**。
  原因是 `--concurrency` 限制的是"同时能发出去多少个请求"，被跳过的请求根本没有到达服务端；服务端每个请求的耗时由请求体里的 `delay_seconds` 决定，与到达率无关。
- burst 阶段两次完全一致（120 发送、0 跳过），因为该阶段延迟只有 0.1 秒，在途数远低于并发上限，降并发没有影响。
- 由于窗口是 `[30s]`，阶段边界是平滑的：slow 阶段开始后平均耗时曲线从 0.10 秒斜着爬升，约 30 秒后才达到真实的 3.00 秒；slow 结束后同样斜着回落。曲线不会垂直跳变。
- 截图 `grafana-two-runs.png` 里第一轮在途请求的峰值看起来是 5，而 Prometheus 里查到原始值是 6：Grafana 在 30 分钟时间范围下会自动降采样（约每 10 秒取一个点），短峰值可能被跳过。图是数据的抽样视图，不是数据本身。

## 从干净环境复现

```bash
# 1. 建虚拟环境并装依赖
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt

# 2. 启动三个服务（各自一个终端；mock 模式不需要 .env 和任何 Key）
bash start-app.sh
bash start-prometheus.sh
bash start-grafana.sh

# 3. 导入仪表盘，并在 Prometheus 的 Targets 页确认 chat-app 为 UP
bash import-dashboard.sh

# 4. 跑两次模拟（第二次只改一个参数，结果写到另一个文件）
./.venv/Scripts/python.exe simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
./.venv/Scripts/python.exe simulate_traffic.py --base-url http://127.0.0.1:5001 --concurrency 3 --output results/changed-run.json

# 5. 在 Grafana（127.0.0.1:3000）看 Lab 4 聊天应用监控仪表盘
```
