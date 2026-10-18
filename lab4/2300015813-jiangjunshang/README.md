# Lab4：姜珺尚 2300015813

基于本人 Lab3 的 Flask 多会话聊天应用，保留前端、会话和消息 CRUD，以及真实模型调用功能。本实验默认使用本地 mock 回复，不需要 Key，不读取 `.env`。

## Windows PowerShell 运行

在本目录执行：

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install --index-url https://pypi.org/simple -r requirements.txt
./start-app.ps1
```

浏览器打开 `http://127.0.0.1:5001/`，新建会话后发送测试消息。应用使用单进程、多线程，监听本机 5001 端口。启动脚本显式设置 `CHAT_MODE=mock`。聊天数据存于 `.runtime/app/conversations.json`，不提交到 Git。

`CHAT_MODE` 只接受 `mock` 和 `real`，默认 `mock`。`real` 保留原 DeepSeek 请求流程，只在调用时从后端环境变量读取 `DEEPSEEK_API_KEY`；本实验不运行 real 模式。mock 不调用外部模型，前端显示当前模式。

## 接口与指标

原聊天接口仍为 `POST /api/conversations/<id>/messages`，JSON 中 `message` 为非空字符串。mock 模式可额外传入 `mock_delay_seconds`（0–30 秒有限数，默认 0.1）及 `mock_force_error`（布尔值，默认 false）。延迟发生在后端，强制失败返回 HTTP 503 和 `simulated: true`；成功保存记录并返回 HTTP 201。real 模式忽略这两个测试选项。

`GET /api/lab/status` 仅在 mock 模式返回当前模式及 `external_model_calls: false`，real 模式返回 404。`GET /api/hello` 返回连通性信息及当前模式。

`http://127.0.0.1:5001/metrics` 使用 `prometheus_client` 标准文本格式提供：

| 指标 | 含义 |
| --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | 按最终处理结果累计聊天请求数，两个标签初始化为零 |
| `chat_inprogress_requests` | 当前正在处理的聊天请求数量 |
| `chat_request_duration_seconds` | 服务端处理耗时 Histogram，包含成功和失败 |

耗时桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30 秒及正无穷。指标装饰器覆盖原聊天 POST 处理，包括输入验证、模型回复和存储；异常时仍更新错误数、耗时并减少在途数量。创建会话、修改/删除记录、静态资源、状态和采集请求不计入聊天指标。指标不包含消息内容或请求 ID 标签，进程重启后重新计数。

数据锁只在读取和保存记录时持有，模拟等待不占有锁。原会话并发变更检查保留：如果生成回复期间会话被修改或删除，则返回 409，避免覆盖已有数据。

## 已核验的应用行为

本机使用 Python 3.14.6、Flask 3.1.3、prometheus-client 0.26.0、requests 2.34.2。Flask 测试客户端检查通过：mock 路径不调用真实模型函数，成功和模拟失败按结果累计；非法延迟和失败参数返回 400；未捕获异常仍完成指标收尾；页面、静态资源、状态、采集及 CRUD 不增加聊天请求数。real 分支仅用替身函数检查模式分流与测试参数隔离，未调用真实模型。

实际本地 HTTP 检查中，一个 2 秒慢聊天请求在处理中时，`/metrics` 约 0.018 秒返回且显示在途数为 1。请求成功后，再发送一次模拟失败请求，最终成功和错误各累计 1 次，耗时样本数为 2，在途数量回到 0。测试会话已删除，指标保留至进程重启。此检查不是课程完整五阶段模拟。

## 本地文件

`.venv/` 为 Python 虚拟环境，`.tools/` 存放后续监控工具，`.runtime/` 存放运行数据和日志，均由个人 `.gitignore` 忽略。课程 `simulate_traffic.py`、`project_adapter.py`、`prometheus.yml` 已复制到个人目录，适配器尚未启用，不能据此运行完整模拟。

## Prometheus 与 Grafana

本实验使用官方稳定版 Windows x64 程序：Prometheus 3.15.0、Grafana OSS 13.2.4。下载来源分别为 [Prometheus 官方下载页](https://prometheus.io/download/) 和 [Grafana OSS 官方下载页](https://grafana.com/grafana/download?edition=oss&platform=windows)。本机 Windows 系统为 ARM64，Python 进程为 AMD64，选择可在本机运行的 Windows x64 程序。

在个人目录中安装并启动监控：

```powershell
./.venv/Scripts/python.exe ./install-tools.py
./start-monitoring.ps1
```

安装脚本固定官方版本、下载地址和 SHA256；只在完整校验通过后解压，拒绝覆盖已存在的工具目录。若只需补装某一项，使用 `--only prometheus` 或 `--only grafana`。Grafana 使用八路有界 HTTP 字节范围下载，每段验证范围和长度，再合并并校验完整安装包；使用 Windows 自带 `tar.exe` 解压，跳过不参与运行的 `docs/`、`packaging/` 附带目录，以及 TypeScript、SCSS、源码映射、测试快照等开发文件。保留运行所需的程序、配置、JavaScript、CSS、HTML、JSON、字体和图片。安装包、分段及校验记录均位于 `.tools/downloads/`，程序分别解压到 `.tools/prometheus/`、`.tools/grafana/`。

启动脚本显式传入以下命令参数，并通过环境变量配置 Grafana 的运行路径：

```powershell
# start-monitoring.ps1 内执行的等价命令，路径相对于个人目录
./.tools/prometheus/prometheus.exe --config.file=prometheus.yml --storage.tsdb.path=.runtime/prometheus --web.listen-address=127.0.0.1:9090

$env:GF_PATHS_DATA = "$PWD/.runtime/grafana/data"
$env:GF_PATHS_LOGS = "$PWD/.runtime/grafana/logs"
$env:GF_PATHS_PLUGINS = "$PWD/.runtime/grafana/plugins"
$env:GF_PATHS_PROVISIONING = "$PWD/provisioning"
$env:LAB4_DASHBOARD_DIR = "$PWD/.runtime/grafana/dashboards"
# 启动脚本会先创建运行目录，并将根目录的仪表盘 JSON 复制到 dashboards 目录
./.tools/grafana/bin/grafana.exe server --homepath="$PWD/.tools/grafana" --config="$PWD/grafana.ini"
```

Prometheus 数据位于 `.runtime/prometheus/`；Grafana 数据库、日志、插件及仪表盘运行副本均位于 `.runtime/grafana/` 子目录。配置文件保留在个人目录，可随项目提交。启动脚本记录进程 ID，并在再次执行时复用已记录且程序路径一致的进程；其他进程占用端口时会报错，不关闭其他服务。

Prometheus 页面为 `http://127.0.0.1:9090/targets`，采集 `http://127.0.0.1:5001/metrics`，job 名为 `chat-app`，间隔 2 秒、超时 1 秒。可在查询页面执行 `chat_requests_total{job="chat-app"}` 查看累计值。Target 的 `UP` 仅表示指标采集成功。

Grafana 仪表盘为 `http://127.0.0.1:3000/d/lab4-chat/lab4-chat-monitoring`，仅监听本机，允许匿名 Viewer 查看。数据源通过 `provisioning/datasources/prometheus.yml` 配置，固定 UID 为 `lab4-prometheus`，URL 为 `http://127.0.0.1:9090`，不是应用地址。仪表盘通过 `provisioning/dashboards/lab4.yml` 加载，默认查看最近 15 分钟、每 5 秒刷新。

三个 Panel 的 PromQL：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))

sum(chat_inprogress_requests{job="chat-app"})

sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s]))
/
sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

第一个查询分别显示 success/error 最近 30 秒的平均每秒完成请求数，不是累计值。第二个显示当前在途量，不是在线用户数。第三个用最近窗口内耗时增加速率除以样本数增加速率，得到服务端平均秒数；没有请求时可能无值，不补造零值。

`grafana-dashboard.json` 中的 Panel 绑定 `lab4-prometheus` 数据源 UID。干净环境使用启动脚本即可自动创建对应数据源并加载；在已有 Grafana 中导入时，应先创建相同 UID 的 Prometheus 数据源，或将各 Panel 的数据源改选为已有 Prometheus。Histogram 的 `_bucket{le="..."}` 是不超过该边界的累计样本数，`_sum` 是总秒数，`_count` 是样本数；本次均值查询使用后两者。

本地连接核验：Prometheus Target 的 job 为 `chat-app`，采集 URL 为 `http://127.0.0.1:5001/metrics`，状态为 `up`，没有采集错误；可查询成功和失败累计次数。Grafana 健康接口返回 HTTP 200、数据库 `ok`、版本 13.2.4；仪表盘包含三个 Panel。通过 Grafana 数据源查询接口执行 `up{job="chat-app"}` 得到 1，三个 Panel 的实际范围查询均返回 HTTP 200 且无查询错误。仪表盘 HTML 及其引用的七个 JavaScript/CSS 资源均返回 HTTP 200。无新请求时，速率和在途量为 0，平均耗时无值；连接检查不等于完整访问模拟。

学生浏览器原始截图：Targets 显示 `chat-app` 为 `1/1 up`、地址为 `127.0.0.1:5001/metrics`；查询显示 success 为 2、error 为 1。

![Prometheus Target UP](screenshots/prometheus-targets.png)

![Prometheus 累计聊天请求查询](screenshots/prometheus-query.png)
