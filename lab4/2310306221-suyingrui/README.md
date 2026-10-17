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
