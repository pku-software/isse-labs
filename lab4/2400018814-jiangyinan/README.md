# Lab 4：一问聊天应用的监控

基于本人 Lab 2 的 HTML/CSS/JavaScript + Flask 应用，保留聊天记录的创建、查看、修改、删除与 JSON 保存功能。新增聊天指标和本地模拟回复，用于 Prometheus 采集及 Grafana 展示。

## 本地启动

Python 3.9 或更新版本；本次使用 macOS arm64、Python 3.12.14。在个人项目目录执行：

```bash
cd /Users/carrie/isse-labs/lab4/2400018814-jiangyinan
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
LAB4_MODEL_MODE=mock .venv/bin/python app.py
```

其他电脑请替换第一行目录。浏览器打开 `http://127.0.0.1:5001/`，不要直接打开 HTML 文件。服务使用单进程、线程并发，关闭 debug/reloader，只监听本机。聊天数据写入 `.runtime/app/messages.json`，该文件不提交。停止时在启动终端按 Control+C。

## mock 与 real

`LAB4_MODEL_MODE` 默认值为 `mock`：不读取 `.env`，不请求外部模型接口，无需密钥。原聊天接口 `POST /api/messages` 仍接收 `message`，返回包含 `id`、`message`、`reply` 的记录；模拟回复会明确标注。

mock 请求还接受两个实验字段：`mock_delay` 为 0～30 秒的数字（默认 0.1），`mock_error` 为布尔值（默认 false）。等待在后端发生；强制失败等待后返回 HTTP 503 与 `simulated: true`，不会保存成功记录。无效字段返回 HTTP 400。

`GET /api/lab4/status` 在 mock 模式返回 `{"mode":"mock","external_model_calls":false}`，real 模式返回 404。

显式设置 `LAB4_MODEL_MODE=real` 时保留 Lab 2 的中转站 Responses API 调用及 `OPENAI_API_KEY`（兼容 `DEEPSEEK_API_KEY`）环境变量方式，此时才可读取本目录 `.env`。实验字段不会影响真实调用。本实验只运行 mock；不需要配置或提交真实密钥。

## 三种聊天指标

访问 `http://127.0.0.1:5001/metrics` 查看 Prometheus 标准文本格式的指标。定义位于 `metrics.py`，只包裹原 `POST /api/messages` 处理函数。

| 指标 | 含义 |
| --- | --- |
| `chat_requests_total{outcome="success"}` | 已完成且返回 2xx 的聊天请求累计数。 |
| `chat_requests_total{outcome="error"}` | 失败的聊天请求累计数，包括输入错误、模拟失败和存储异常。 |
| `chat_inprogress_requests` | 开始处理时加一，结束时减一的在途请求数。 |
| `chat_request_duration_seconds` | 服务端处理耗时，单位秒；包括输入检查、模拟等待、保存记录和失败路径。 |

Histogram 的桶上界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30 秒及自动追加的正无穷。`_bucket{le="…"}` 是不超过该上界的累计次数，`_sum` 是总耗时，`_count` 是总次数。Counter 的两种结果启动时都初始化为零。进程重启后指标重新累计，历史数据由 Prometheus 保存。

网页、静态资源、健康/实验状态接口、查看/修改/删除记录和 `/metrics` 自身不计入聊天处理数。指标标签只包含结果类别，不包含提问内容或记录 ID。

## 运行测试

```bash
.venv/bin/python -m unittest -v test_app
```

测试使用临时聊天数据，检查模拟回复、CRUD、错误和异常后的指标收尾、参数验证、模式隔离，以及多个慢请求期间 `/metrics` 仍能及时响应。real 分支测试使用替身响应，不访问真实模型。

2026 年 10 月 18 日，七项测试全部通过。另在实际运行的 `127.0.0.1:5001` 服务上分别发送一次正常请求和一次模拟失败请求，确认 HTTP 201/503、成功和错误计数各增加一次、耗时次数为 2、Gauge 回到 0。浏览器手动发送消息也会继续增加计数；独立测试进程的指标不计入这一服务。

## 文件与运行数据

课程访问脚本的个人副本为 `simulate_traffic.py`；项目适配位于 `project_adapter.py`。采集配置为 `prometheus.yml`，目标为 `127.0.0.1:5001`，采集间隔 2 秒，超时 1 秒。

`.venv/` 存放 Python 环境；`.tools/` 用于本地监控程序；`.runtime/` 用于运行数据库和日志，均被 Git 忽略。模拟结果、仪表盘配置及截图保留为可提交文件。

## Prometheus 与 Grafana

本项目使用官方稳定版 Prometheus 3.13.4（LTS）和 Grafana OSS 13.2.4 的 macOS arm64 二进制程序。下载来源为 [Prometheus 官方下载页](https://prometheus.io/download/) 和 [Grafana OSS 官方下载页](https://grafana.com/grafana/download?edition=oss&platform=mac)。其他系统应选对应的官方架构包，并调整可执行文件名。

在个人目录下载、校验和解压：

```bash
mkdir -p .tools/downloads .tools/prometheus .tools/grafana
curl -fL -o .tools/downloads/prometheus-3.13.4.darwin-arm64.tar.gz https://github.com/prometheus/prometheus/releases/download/v3.13.4/prometheus-3.13.4.darwin-arm64.tar.gz
curl -fL -o .tools/downloads/grafana_13.2.4_darwin_arm64.tar.gz https://dl.grafana.com/grafana/release/13.2.4/grafana_13.2.4_38252365904_darwin_arm64.tar.gz
shasum -a 256 .tools/downloads/*.tar.gz
```

对照以下官方 SHA256，两份均一致后才解压和执行：

- Prometheus：`0714a2812b2880078eeb10244d684981905fda568b50351ad6eea29397e55996`
- Grafana：`a910966466359212f1d875748a72a4638c7d3724448d0c369210b31d763b165d`

```bash
tar -xzf .tools/downloads/prometheus-3.13.4.darwin-arm64.tar.gz -C .tools/prometheus --strip-components=1
tar -xzf .tools/downloads/grafana_13.2.4_darwin_arm64.tar.gz -C .tools/grafana --strip-components=1
```

保持聊天应用运行，另开两个终端进入个人目录，分别运行：

```bash
./start-prometheus.sh
```

```bash
./start-grafana.sh
```

- Prometheus：`http://127.0.0.1:9090/`，Targets 页面检查 `chat-app`；数据库显式保存在 `.runtime/prometheus/`。
- Grafana：`http://127.0.0.1:3000/d/lab4-2400018814`；数据、日志、插件分别位于 `.runtime/grafana/` 的子目录。
- 两者只监听本机，Grafana 开启匿名 Viewer 供本地实验查看。配置文件自动加载 `Lab4 Prometheus` 数据源及三个 Panel，无需云账号。
- `start-grafana.sh` 将可提交的 `grafana-dashboard.json` 复制到专用运行目录，再由 provisioning 导入。启动脚本使用自身目录定位文件，不依赖启动时所在目录。
- 停止时分别在对应终端按 Control+C。不要关闭其他应用的进程。端口被其他程序占用时，需要同时调整启动配置、数据源 URL 和访问地址。

### 三个查询

成功与失败请求速率，单位为次/秒，采用最近 30 秒窗口：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
```

当前正在处理的请求数：

```promql
sum(chat_inprogress_requests{job="chat-app"})
```

最近窗口内的服务端平均处理耗时，单位秒：

```promql
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s]))
/
sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

图表每 2 秒刷新。刚启动时样本不足，或者最近没有请求，平均耗时可能无值；不把这些空值伪造为 0。Histogram 的桶是累计分布；此处用总耗时与次数的变化率计算平均值，并未计算分位数。30 秒窗口会使阶段边界平滑，恢复也会有滞后。

### 仪表盘导入

从干净环境运行以上启动脚本，会按 `provisioning/datasources/prometheus.yml` 创建 UID 为 `lab4-prometheus` 的数据源，并自动导入仪表盘。已有 Grafana 可导入 `grafana-dashboard.json`，将各 Panel 的数据源选择为自己的 Prometheus；或者沿用本项目 provisioning 文件创建同名 UID。数据源地址需能访问实际 Prometheus 服务。

`grafana-dashboard.json` 从本次实际运行的 Grafana 导出，保留三个查询与数据源 UID，移除本机数据库 ID。默认展示最近 10 分钟；导入的是图表配置，历史数据仍保存在本机 Prometheus，复现实验需重新运行访问脚本。

## 访问模拟与实验结果

`simulate_traffic.py` 与课程 starter 调度脚本一致。`project_adapter.py` 实现三个适配函数：通过 `GET /api/lab4/status` 实际核验 mock 模式且外部模型调用关闭；构造原 `POST /api/messages` 的消息、延迟和失败字段；校验 HTTP 201 及有效的记录和回复。模式核验禁止重定向，调度器限制本机地址和有限并发。非 mock 状态、错误响应与无效响应的检查，以及一次实际正常请求和一次模拟失败验证均已通过。

保持应用、Prometheus 和 Grafana 运行，在个人目录执行：

```bash
.venv/bin/python simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
.venv/bin/python simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --slow-delay 1 --phase-seconds 30 --output results/changed-run.json
```

两条命令应先后运行，避免流量叠加。重复实验时改用新的输出文件名，避免覆盖已有结果。首次使用默认五阶段，每阶段发送窗口 30 秒、并发上限 6，结束后等待在途请求完成并留出 10 秒采集时间。第二次仅将 slow 场景延迟从 3 秒改为 1 秒，目标频率仍为每秒 2 次、并发上限仍为 6。

### 首次完整实验

2026 年 10 月 18 日实际运行结果如下，时间为北京时间（JSON 内保存 UTC 时间）：

| 场景 | 起止时间 | 目标频率（次/秒） | 后端延迟（秒） | 实际发送 | 成功 | 业务/HTTP 错误 | 跳过发送机会 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 20:17:49–20:18:19 | 1 | 0.1 | 30 | 30 | 0 | 0 |
| burst | 20:18:19–20:18:49 | 4 | 0.1 | 120 | 120 | 0 | 0 |
| slow | 20:18:49–20:19:22 | 2 | 3 | 52 | 52 | 0 | 8 |
| errors | 20:19:22–20:19:52 | 1 | 0.1 | 30 | 20 | 10 | 0 |
| recovery | 20:19:52–20:20:22 | 1 | 0.1 | 30 | 30 | 0 | 0 |

共发送 262 次，252 次成功，10 次为每第 3 次请求产生的预设失败；网络错误与非预期结果均为 0。slow 阶段因并发名额已满跳过 8 次发送机会，跳过不算已发送或失败请求；阶段结束包含在途请求收尾，因此实际起止时间可超过 30 秒。

真实 Prometheus 历史查询中，成功请求速率最高约 4 次/秒，慢请求期间在途请求峰值为 6，平均服务端耗时升至约 3.006 秒；错误阶段失败速率上升，恢复后回落。0.1 秒短请求可能在两次采集之间完成，因此 Gauge 为 0 的采样点不代表那段时间完全没有请求。30 秒速率窗口使曲线变化平滑，并使部分变化延后显示。

原始截图：`screenshots/prometheus-targets.png` 显示 `127.0.0.1:5001/metrics`、`job="chat-app"` 和 `UP`；`screenshots/grafana-dashboard.png` 展示 20:17:34–20:21:02 的三个 Panel，覆盖五个阶段及恢复。

### 缩短延迟的对照实验

第二次于 20:45:08–20:45:38 运行 slow 场景，实际发送 60 次，全部成功，跳过、业务/HTTP 错误、网络错误与非预期结果均为 0。

| 对比项 | 首次 slow：延迟 3 秒 | 第二次 slow：延迟 1 秒 |
| --- | --- | --- |
| 脚本客户端平均耗时 | 3.018 秒 | 1.015 秒 |
| Prometheus 采集的在途请求峰值 | 6 | 2 |
| 图表服务端平均耗时峰值 | 约 3.006 秒 | 约 1.008 秒 |
| 实际发送 / 跳过机会 | 52 / 8 | 60 / 0 |

缩短处理时间后，请求更快释放并发名额，平均耗时及在途数量降低，本次没有因并发已满跳过发送。客户端耗时包含网络等开销，与服务端 Histogram 不是同一指标；两者分别取自结果 JSON 与 Prometheus 历史查询。两次实验在不同时间执行，横轴位置不同本身不表示处理变慢。
