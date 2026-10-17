# Lab 4：聊天应用监控

苏英睿，2310306221。应用来自 `lab3/2310306221-suyingrui/`，保留原 HTML/CSS/JavaScript 前端与 Flask 聊天记录增删改查 API。

## 本地运行

当前环境为 macOS arm64、zsh、Python 3.9.6。在仓库根目录执行：

```sh
cd lab4/2310306221-suyingrui
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
CHAT_MODE=mock .venv/bin/python app.py --port 5001
```

应用在前台运行，请保持该终端开启；另开终端进入同一个人目录，再安装、启动监控工具或运行访问脚本。

页面为 <http://127.0.0.1:5001/>，指标为 <http://127.0.0.1:5001/metrics>。应用使用单进程、线程并发，无调试重载。聊天记录写入 `.runtime/app/messages.json`，共享读写有锁保护；等待模型回复时不持有存储锁。

当前安装的主要依赖版本为 Flask 3.1.3、prometheus-client 0.26.0、openai 2.48.0。

默认 `CHAT_MODE=mock`，返回固定测试回复，不导入或创建真实模型客户端，无需 Key。`GET /api/lab/status` 返回当前 mock 模式及 `external_model_calls: false`。原聊天接口为 `POST /api/messages`，请求 JSON 中的 `message` 必须为非空字符串；成功返回 HTTP 201 和包含 `id`、`message`、`reply` 的记录。

mock 模式下可附加 `mock_delay`（0～30 秒，默认 0.1 秒）和 `mock_error`（布尔值，默认 false）。等待发生在后端；强制失败在等待结束后返回 HTTP 503 和 `{"error":"Simulated model failure"}`。失败不会创建聊天记录。

`CHAT_MODE=real` 保留原 DeepSeek 调用，通过进程环境变量 `DEEPSEEK_API_KEY` 配置凭据；程序不读取 `.env`。real 模式忽略 mock 选项，实验状态接口返回 404。本实验运行使用 mock 模式。

## 指标

指标定义在 `metrics.py`，仅统计 `POST /api/messages`；状态、静态资源、指标读取和其他 CRUD 请求均不计入。

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | Counter | 聊天处理完成后按结果累计，两个标签值初始化为零 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求数，异常时也完成收尾 |
| `chat_request_duration_seconds` | Histogram | 从聊天处理开始到响应构造完成的服务端耗时，包含失败，单位秒 |

Histogram 桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30 秒和正无穷。指标没有聊天正文或请求 ID 等标签。手动验证和页面聊天同样会产生真实计数。

## 回归验证

在个人目录执行 `CHAT_MODE=mock .venv/bin/python -m unittest -v test_app.py`。测试覆盖 mock 不导入模型 SDK、原 CRUD、模拟失败及未处理异常的指标收尾、保存失败回滚、非聊天访问不计数、实验选项校验和并发保存。测试使用独立的临时记录目录，不改变运行中服务的计数或聊天记录。

## 文件位置

课程 `simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 已复制到本目录。运行依赖放在 `.venv/`；监控下载包及校验文件使用 `.tools/downloads/`，工具使用 `.tools/prometheus/` 和 `.tools/grafana/`；运行数据使用 `.runtime/`。这些本地文件以及凭据均由个人 `.gitignore` 排除。结果 JSON、配置、仪表盘与截图保留为可提交文件。

## Prometheus 与 Grafana

本机使用官方稳定版 Prometheus 3.15.0 和 Grafana OSS 13.2.3，均为 macOS/Darwin arm64 构建。下载来源与 SHA-256：

- [Prometheus 官方下载页](https://prometheus.io/download/)，[固定版本安装包](https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.darwin-arm64.tar.gz)。SHA-256：`920df4d17e78b3b0175af144eb318b0c74d1cf7b1d1251b326966f0e81977260`。
- [Grafana 官方下载页](https://grafana.com/grafana/download/13.2.3?edition=oss&platform=mac)，[固定版本安装包](https://dl.grafana.com/grafana/release/13.2.3/grafana_13.2.3_36482603486_darwin_arm64.tar.gz)。SHA-256：`248a51bcfacdb1ec642006cee46b4de44a34bcf41ddea88d96a4605e2e9d808c`。

在个人目录安装并启动：

```sh
.venv/bin/python install-monitoring.py
.venv/bin/python start-monitoring.py
```

安装脚本在下载前检查忽略规则及跟踪状态，通过 HTTP/1.1 分块下载并保留完成的块，核验完整包的 SHA-256 后才解压。下载包、分块和校验文件保存在 `.tools/downloads/`。工具分别解压到 `.tools/prometheus/`、`.tools/grafana/`。这两个脚本使用 Python 标准库与 macOS 自带的 curl、tar，不需要 Docker 或系统级安装。

| 程序 | 监听地址 | 页面 / 配置 |
| --- | --- | --- |
| Flask 应用 | `127.0.0.1:5001` | [聊天页](http://127.0.0.1:5001/)、[原始指标](http://127.0.0.1:5001/metrics) |
| Prometheus | `127.0.0.1:9090` | [Targets](http://127.0.0.1:9090/targets)，配置为 `prometheus.yml` |
| Grafana | `127.0.0.1:3000` | [仪表盘](http://127.0.0.1:3000/d/lab4-chat)，配置为 `grafana.ini` |

本应用 Target 的原始浏览器截图保存在 [screenshots/prometheus-targets.png](screenshots/prometheus-targets.png)，显示 `job="chat-app"`、采集地址 `http://127.0.0.1:5001/metrics` 和 `UP` 状态。`temp/` 用于接收截图原图，提交使用 `screenshots/` 中的规范命名副本。

`prometheus.yml` 采集 `127.0.0.1:5001/metrics`，job 为 `chat-app`，间隔 2 秒、超时 1 秒。Prometheus 的实际启动命令如下（在个人目录执行）：

```sh
.tools/prometheus/prometheus --config.file="$PWD/prometheus.yml" --storage.tsdb.path="$PWD/.runtime/prometheus" --storage.tsdb.retention.time=7d --web.listen-address=127.0.0.1:9090
```

Grafana 的实际启动命令如下（在个人目录执行）：

```sh
LAB4_PROJECT_DIR="$PWD" \
GF_PATHS_DATA="$PWD/.runtime/grafana/data" \
GF_PATHS_LOGS="$PWD/.runtime/grafana/logs" \
GF_PATHS_PLUGINS="$PWD/.runtime/grafana/plugins" \
GF_PATHS_PROVISIONING="$PWD/grafana/provisioning" \
.tools/grafana/bin/grafana server --homepath "$PWD/.tools/grafana" --config "$PWD/grafana.ini"
```

辅助脚本以相同参数后台启动两个进程，先检查两个端口，遇到占用就退出并保留已有进程，不重复启动。Prometheus 数据与日志在 `.runtime/prometheus/`；Grafana 数据库在 `.runtime/grafana/data/grafana.db`，日志在 `.runtime/grafana/logs/`，插件在 `.runtime/grafana/plugins/`。两个进程的 PID 分别记录在 `.runtime/prometheus/server.pid` 和 `.runtime/grafana/server.pid`。应用进程 PID 为 `.runtime/app/server.pid`。

安装或启动时可以使用 `--component prometheus` 或 `--component grafana` 单独处理一个工具；默认处理两者。重新运行前先检查已记录 PID 对应的命令，确认属于本项目后再停止对应进程，保留数据库以便查看历史数据。

Grafana 只在本机开放匿名 Viewer 查看，无需登录；数据源与仪表盘由配置文件建立。`grafana/provisioning/datasources/prometheus.yml` 建立名为 `Lab4 Prometheus`、UID 为 `lab4-prometheus` 的数据源，连接 `http://127.0.0.1:9090`。`grafana/provisioning/dashboards/lab4.yml` 通过启动脚本设置的 `LAB4_PROJECT_DIR` 找到 `dashboards/chat-monitoring.json`，自动导入三个时间序列图表。

### 三个查询

成功/失败请求速率：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
```

两条曲线按 `outcome` 区分，表示最近 30 秒窗口内平均每秒完成的聊天请求数，单位为次/秒。

正在处理的请求：

```promql
sum(chat_inprogress_requests{job="chat-app"})
```

表示采集时正在执行且尚未结束的请求数量，不是在线用户数。

平均处理耗时：

```promql
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s]))
/
sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

表示最近 30 秒窗口内聊天处理的服务端平均耗时，包含失败请求，单位秒。没有新请求时可能无值；仪表盘不将其补零。仪表盘每 2 秒刷新，不连接空值。

Histogram 的 `_bucket{le="..."}` 表示耗时不超过该上界的累计次数；`_sum` 是处理耗时总和，`_count` 是处理次数，正无穷桶包含全部样本。平均耗时图使用窗口内总和与次数的增长率之比。Prometheus 启动前的请求可以体现为累计值，但不会自动拥有过去的时间序列历史。

## 访问脚本适配

`simulate_traffic.py` 原样复用课程调度器，负责阶段切换、发送节奏、有限并发及真实结果统计；项目差异在 `project_adapter.py` 中实现：

- `confirm_mock_mode()` 通过真实 HTTP GET 读取 `/api/lab/status`，仅接受 `mode="mock"` 且 `external_model_calls` 为布尔值 false。拒绝重定向，不使用系统代理，目标仅限本机服务根地址。
- `build_chat_request()` 构造 `POST /api/messages`，JSON 包含 `message`、`mock_delay`、`mock_error`，不携带模型 Key。
- `response_is_success()` 仅将 HTTP 201 且包含有效整数 `id`、非空 `message` 和 `reply` 的 JSON 记录判为成功；模拟错误、空回复和无效响应均判为失败，不打印正文。

运行完整模拟的命令为：

```sh
.venv/bin/python -u simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
```

默认五阶段各发送 30 秒，阶段之间等待在途请求收尾，最后等待 10 秒用于采集。并发上限为 6；容量满时跳过发送机会并计数，不无限排队。目标发送频率不等于实际完成频率，JSON 中的客户端耗时包含网络开销，不等同于服务端 Histogram。

适配器验证命令为 `.venv/bin/python -m unittest -v test_adapter.py`。测试覆盖请求字段、有效回复判断、本机地址限制、HTTP 状态配置核验、禁止重定向，以及实际 real 模式应用在任何聊天请求构造前被课程脚本拒绝；临时服务验证后会停止，不进行真实模型调用。

### 首次完整模拟（2026-10-18）

真实结果文件：[results/first-run.json](results/first-run.json)。运行命令见上文；使用默认五阶段各 30 秒、并发上限 6、请求超时 10 秒、收尾等待 10 秒。下表时间为北京时间（Asia/Shanghai），JSON 保留 UTC 时间。

| 阶段 | 实际起止时间 | 发送 | 成功 | 业务/HTTP 失败 | 跳过 | 客户端平均耗时（秒） |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | 01:27:59～01:28:29 | 30 | 30 | 0 | 0 | 0.1084 |
| burst | 01:28:29～01:28:59 | 120 | 120 | 0 | 0 | 0.1103 |
| slow | 01:28:59～01:29:32 | 52 | 52 | 0 | 8 | 3.0102 |
| errors | 01:29:32～01:30:02 | 30 | 20 | 10 | 0 | 0.1114 |
| recovery | 01:30:02～01:30:32 | 30 | 30 | 0 | 0 | 0.1123 |

共发送 262 次，成功 252 次，预期模拟失败 10 次，跳过 8 次；网络错误和非预期结果均为 0，退出码为 0。慢请求阶段发出请求持续 30 秒，等待在途请求收尾后实际结束稍晚。累计业务指标还包含手动聊天及单请求验证，不能直接当作本次脚本发送数量。

以 2 秒步长查询本次运行的真实 Prometheus 历史数据：成功速率峰值为 4.000 次/秒，error 速率峰值约 0.321 次/秒；在途数量峰值为 6，末尾回到 0；窗口平均服务端耗时峰值约 3.007 秒，恢复后约 0.109 秒。该区间采集状态均为 UP。30 秒查询窗口会平滑阶段边界，客户端平均耗时与服务端图表应分别解读。

[查看首次完整模拟的固定时间范围](http://127.0.0.1:3000/d/lab4-chat?from=1792258069000&to=1792258242000)（北京时间 01:27:49～01:30:42）。

首次完整模拟的原始浏览器截图：[screenshots/grafana-dashboard.png](screenshots/grafana-dashboard.png)，覆盖上述时间范围并包含三个 Panel 及其图例。

### 调整延迟后的模拟（2026-10-18）

真实结果文件：[results/changed-run.json](results/changed-run.json)。本次仅运行 slow 场景，将后端延迟从 3 秒改为 6 秒；目标频率仍为每秒 2 次、并发上限仍为 6、超时仍为 10 秒。实际运行区间为北京时间 02:41:42～02:42:16，其中发出请求持续 30 秒，其余时间等待在途请求收尾，之后再等待 10 秒用于采集。

```sh
.venv/bin/python -u simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --phase-seconds 30 --slow-rate 2 --slow-delay 6 --concurrency 6 --timeout 10 --settle-seconds 10 --output results/changed-run.json
```

| 实际比较项 | 首次 slow（延迟 3 秒） | 第二次 slow（延迟 6 秒） |
| --- | --- | --- |
| 发送 / 成功 | 52 / 52 | 30 / 30 |
| 跳过发送机会 | 8 | 30 |
| 客户端平均耗时 | 3.0102 秒 | 6.0152 秒 |
| 服务端窗口平均耗时峰值 | 3.007 秒 | 6.011 秒 |
| 在途请求峰值 | 6 | 6 |

第二次业务/HTTP 失败、网络错误和非预期结果均为 0，退出码为 0，在途数量最终回到 0，采集区间均为 UP。服务端平均耗时约翻倍；两次在途峰值都受到并发上限 6 的限制。延迟变长使并发名额被占用更久，满额时跳过的发送机会增加，因此实际发送数量减少。单独的 slow 场景结束后没有低延迟恢复请求，平均耗时曲线不会立即归零；窗口内无新样本后可变为无值。

[查看第二次模拟的固定时间范围](http://127.0.0.1:3000/d/lab4-chat?from=1792262492000&to=1792262546000)（北京时间 02:41:32～02:42:26）。首次结果文件保留独立内容，未被第二次运行覆盖。

## 仪表盘导入与复现

[grafana-dashboard.json](grafana-dashboard.json) 从实际运行的 Grafana 实例导出，保留三个 Panel 的查询、单位、图例和刷新设置；导出时移除数据库 ID，并将数据源引用参数化为 `${DS_PROMETHEUS}`。导入时在有导入权限的 Grafana 中选择此 JSON，在 Prometheus 输入项选择 `Lab4 Prometheus` 或同样连接本机 Prometheus 的数据源。该数据源 URL 为 `http://127.0.0.1:9090`，类型必须为 Prometheus。

本项目的本地启动脚本通过 provisioning 自动创建 UID 为 `lab4-prometheus` 的数据源并加载 `dashboards/chat-monitoring.json`，匿名 Viewer 可以直接查看，无需手动导入导出文件。导出文件的数据源变量绑定回该 UID 后，与实际运行仪表盘的配置完全一致。

从干净环境复现时，先按本文创建 `.venv/` 并安装依赖，启动 mock 应用，再安装并启动两个监控工具，核对 Target 后运行上述两个命令。结果文件名固定，重新实验前应另存已有结果或选择新的 `--output` 路径，避免覆盖历史记录。根据新运行 JSON 的实际起止时间选择 Grafana 时间范围。仪表盘 JSON 包含配置，不包含 Prometheus 历史数据；历史曲线需由重新运行的真实 HTTP 请求及采集产生。原始截图和两份结果 JSON 保留了本次实验记录。
