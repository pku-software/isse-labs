# Lab 4：杨沐之的聊天应用监控

本项目来自 `lab3/2500013091-yangmuzhi/`，保留 Flask 后端、原前端、会话管理和聊天记录的增删改查。在原聊天请求处理流程中加入 mock 回复与 Prometheus 指标，不需要真实模型 Key 即可本地运行。

## 本地运行

当前环境为 Windows x64、PowerShell 7、Python 3.9.12。以下命令从 `isse-labs` 仓库根目录执行；Python 要求 3.9 或更高版本。全局 pip 需支持 `--python`（本机为 26.0.1），它只负责向指定的个人虚拟环境安装依赖。

```powershell
$lab4 = Join-Path (Get-Location) 'lab4/2500013091-yangmuzhi'
python -m venv "$lab4/.venv"
python -m pip --python "$lab4/.venv/Scripts/python.exe" install -r "$lab4/requirements-lock.txt"
& "$lab4/start-app.ps1"
```

`requirements.txt` 声明直接依赖，`requirements-lock.txt` 记录本次实际安装的完整版本。若需要通过本机已配置的代理访问 PyPI，可在安装命令追加 `--index-url https://pypi.org/simple --proxy http://127.0.0.1:7897`；该代理端口是本机设置，其他电脑应使用自身可用的网络配置。

启动脚本明确使用 mock 模式，默认监听 `127.0.0.1:5001`。指定其他端口可运行 `& "$lab4/start-app.ps1" -Port 5002`。应用采用单进程、多线程，关闭 debug、自动重载和 `.env` 自动加载。终端前台运行时，按 Ctrl+C 停止。

- 聊天页面：<http://127.0.0.1:5001/>
- 指标文本：<http://127.0.0.1:5001/metrics>
- 实验状态：<http://127.0.0.1:5001/api/lab/status>

## mock 与 real

`LAB4_MODEL_MODE` 默认为 `mock`。原有 `generate_reply()` 在此模式下返回固定测试回复，不读取模型 Key、不导入或创建真实模型客户端，也不调用外部模型。实验状态接口实际检查启动配置，仅在 mock 模式返回 `{"mode":"mock","external_model_calls":false}`。

原有 real 模型调用代码保留。显式设置 `LAB4_MODEL_MODE=real` 时，它才会从进程环境变量读取 `DEEPSEEK_API_KEY` 并使用原有模型调用逻辑；本实验不运行 real 聊天。real 模式下实验状态接口返回 404，mock 参数不参与真实调用。任何模式均不自动读取 `.env`。

页面发送消息使用 `POST /api/conversations/<id>/messages`；独立聊天接口仍为 `POST /api/messages`，返回 HTTP 201 与包含 `id`、`message`、`reply` 的 JSON。两种聊天入口都接受 `message` 字符串。mock 模式可额外提供：

```json
{
  "message": "监控实验测试消息",
  "mock": {
    "delay_seconds": 0.1,
    "force_error": false
  }
}
```

延迟必须是 0～30 秒的有限数值，默认 0.1 秒；失败开关必须为布尔值。延迟发生在后端处理期间，强制失败在等待后返回 HTTP 503 和明确的 `error` JSON。共享存储的读取、修改和落盘受锁保护，等待回复时释放存储锁。会话数据位于个人 `.runtime/app/conversations.json`，不复制原实验聊天数据，也不提交本地聊天记录。

## 应用指标

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"}` | Counter | 成功完成的聊天请求累计次数 |
| `chat_requests_total{outcome="error"}` | Counter | 失败完成的聊天请求累计次数，包括参数错误与模拟失败 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求数 |
| `chat_request_duration_seconds` | Histogram | 每次聊天处理的服务端耗时，包括失败请求 |

指标只记录两个 POST 聊天入口，状态检查、页面、静态资源、CRUD 和 `/metrics` 采集本身不计入聊天数量。成功与错误计数都初始化为 0。响应构造或业务处理抛出异常时仍记录错误、耗时并收尾在途数量。标签只有 `outcome`，不包含用户信息或消息正文。

Histogram 的有限桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30 秒，另有 `+Inf` 桶；`_bucket` 是耗时不超过对应边界的累计样本数，`_sum` 是累计耗时，`_count` 是累计请求样本数。以上数据保存在应用内存，应用进程重启后重新累计。

实现见 `metrics.py` 与 `app.py`。Prometheus Python 客户端的指标类型说明见[官方文档](https://prometheus.github.io/client_python/instrumenting/)。

## 本地文件位置

工具下载包和校验文件位于 `.tools/downloads/`，工具目录为 `.tools/prometheus/` 与 `.tools/grafana/`。Prometheus 数据使用 `.runtime/prometheus/`，Grafana 数据、日志和插件使用 `.runtime/grafana/` 下的子目录，应用运行文件使用 `.runtime/app/`，Python 环境为 `.venv/`。这些路径均由个人 `.gitignore` 排除。

配置、仪表盘、`results/*.json` 和截图保留在可提交的位置。`simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 来自课程 starter，适配器通过验证前禁止运行模拟。

## 检查应用

从仓库根目录运行：

```powershell
& 'lab4/2500013091-yangmuzhi/.venv/Scripts/python.exe' -m unittest discover -s 'lab4/2500013091-yangmuzhi' -p 'test_app.py' -v
```

检查覆盖 mock 状态与输入校验、非聊天请求不计数、成功/失败与未捕获异常的指标收尾、原会话 CRUD，以及真实本地 HTTP 下的并发和慢请求期间的指标响应。测试进程独立于正在运行的实验应用；测试仅使用临时的本地数据文件。

本次环境的 5 项检查全部通过。在并发检查中，4 个后端延迟 1.5 秒的聊天请求同时处理中，`/metrics` 在 1 秒内响应并返回在途数 4；3 次成功与 1 次模拟失败结束后，在途数回到 0。独立启动的实验应用另经一次 HTTP 201 和一次 HTTP 503 验证，随后成功计数为 1、错误计数为 1、耗时样本数为 2、在途数为 0。这些连接检查也计入该应用进程的指标。

随后通过聊天页面发送 3 条测试消息，浏览器观察与实际读取的 `/metrics` 一致：成功计数为 4、错误计数为 1、耗时样本数为 5、在途数为 0。复现这组数值需从新启动的应用开始，依次执行上述两次连接检查，再通过页面发送 3 条成功消息。

## Prometheus 与 Grafana

| 程序 | Windows x64 版本 | 本地监听 | 运行数据位置 |
| --- | --- | --- | --- |
| Prometheus | 3.13.4 LTS | `127.0.0.1:9090` | `.runtime/prometheus/` |
| Grafana OSS | 13.2.3 | `127.0.0.1:3000` | `.runtime/grafana/data/`、`log/`、`plugins/` |

版本和下载来源：[Prometheus 官方下载页](https://prometheus.io/download/)、[Grafana OSS 官方 Windows 下载页](https://grafana.com/grafana/download?edition=oss&platform=windows)。下载包和校验文件均放入个人 `.tools/downloads/`。本次使用的包与官方 SHA-256 为：

```text
prometheus-3.13.4.windows-amd64.zip
9f8950c9c5092366368b674b098250c82e998f62b90e2fbe16e1a3bf773a1a0e

grafana_13.2.3_36482603486_windows_amd64.tar.gz
dafe883a7c15543c6d6710b868eb8b4053353441ce7ceacf150942b8de3960f0
```

在干净环境中，从仓库根目录下载并校验这两个官方安装包。以下命令使用本机代理端口；其他电脑可移除 `--proxy` 或替换为自身配置。

```powershell
$lab4 = Join-Path (Get-Location) 'lab4/2500013091-yangmuzhi'
$downloads = Join-Path $lab4 '.tools/downloads'
New-Item -ItemType Directory -Force -Path $downloads | Out-Null
curl.exe -fL --proxy http://127.0.0.1:7897 -o "$downloads/prometheus-3.13.4.windows-amd64.zip" 'https://github.com/prometheus/prometheus/releases/download/v3.13.4/prometheus-3.13.4.windows-amd64.zip'
if ($LASTEXITCODE -ne 0) { throw 'Prometheus download failed' }
curl.exe -fL --proxy http://127.0.0.1:7897 -o "$downloads/prometheus-sha256sums.txt" 'https://github.com/prometheus/prometheus/releases/download/v3.13.4/sha256sums.txt'
if ($LASTEXITCODE -ne 0) { throw 'Prometheus checksum download failed' }
curl.exe -fL --proxy http://127.0.0.1:7897 -o "$downloads/grafana_13.2.3_36482603486_windows_amd64.tar.gz" 'https://dl.grafana.com/grafana/release/13.2.3/grafana_13.2.3_36482603486_windows_amd64.tar.gz'
if ($LASTEXITCODE -ne 0) { throw 'Grafana download failed' }
$promHash = (Get-FileHash -Algorithm SHA256 "$downloads/prometheus-3.13.4.windows-amd64.zip").Hash
$grafanaHash = (Get-FileHash -Algorithm SHA256 "$downloads/grafana_13.2.3_36482603486_windows_amd64.tar.gz").Hash
if ($promHash -ne '9f8950c9c5092366368b674b098250c82e998f62b90e2fbe16e1a3bf773a1a0e') { throw 'Prometheus checksum mismatch' }
if ($grafanaHash -ne 'dafe883a7c15543c6d6710b868eb8b4053353441ce7ceacf150942b8de3960f0') { throw 'Grafana checksum mismatch' }
New-Item -ItemType Directory -Force -Path "$lab4/.tools/prometheus", "$lab4/.tools/grafana" | Out-Null
tar.exe -xf "$downloads/prometheus-3.13.4.windows-amd64.zip" -C "$lab4/.tools/prometheus" --strip-components 1
if ($LASTEXITCODE -ne 0) { throw 'Prometheus extraction failed' }
tar.exe -xf "$downloads/grafana_13.2.3_36482603486_windows_amd64.tar.gz" -C "$lab4/.tools/grafana" --strip-components 1
if ($LASTEXITCODE -ne 0) { throw 'Grafana extraction failed' }
```

应用启动后，在另一个 PowerShell 7 终端执行：

```powershell
& 'lab4/2500013091-yangmuzhi/start-monitoring.ps1'
```

脚本启动两个后台进程，显式指定配置、工具主目录和全部运行数据目录。它将 `grafana-dashboard.json` 复制到 `.runtime/grafana/dashboards/`，并用 `grafana-provisioning/` 自动配置数据源和仪表盘。进程 PID、启动时间和可执行文件位置记在各自运行目录的 `process.json`，已有本实验进程可复用。遇到其他进程占用端口时停止启动；可用 `-PrometheusPort 9091 -GrafanaPort 3001` 选择空闲端口，数据源地址也随之调整。应用端口若改变，需同步修改 `prometheus.yml` 的 target。

Prometheus 的实际参数为 `--config.file=<个人目录>/prometheus.yml --storage.tsdb.path=<个人目录>/.runtime/prometheus --storage.tsdb.retention.time=7d --web.listen-address=127.0.0.1:9090`。Grafana 使用 `grafana.exe server --homepath=<个人目录>/.tools/grafana --config=<个人目录>/grafana.ini`，路径变量由启动脚本设置。日志均位于个人 `.runtime/` 下。Grafana 仅向本机提供匿名 Viewer 访问，通过配置文件管理图表，无须输入真实账号或密码。

采集 job 为 `chat-app`，每 2 秒访问 `http://127.0.0.1:5001/metrics`，超时 1 秒。Grafana 数据源 UID 为 `lab4-prometheus`，连接 `http://127.0.0.1:9090`，仪表盘 UID 为 `lab4-yangmuzhi`，每 2 秒刷新，时区为 `Asia/Shanghai`。

- [Prometheus Targets](http://127.0.0.1:9090/targets)
- [Prometheus 查询页面](http://127.0.0.1:9090/query)
- [Grafana 仪表盘](http://127.0.0.1:3000/d/lab4-yangmuzhi)

## 三个 Panel 的查询

成功/失败请求速率：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
```

按结果分组，计算最近 30 秒窗口内平均每秒完成的聊天请求数，单位为次/秒。它不是请求累计总数。

正在处理的请求：

```promql
sum(chat_inprogress_requests{job="chat-app"})
```

表示采集时刻正在处理的聊天请求数，不代表在线用户数。

平均处理耗时：

```promql
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s]))
/
sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

分子是最近窗口内累计耗时的增长速率，分母是耗时样本数的增长速率，相除得到服务端平均处理耗时，单位秒。没有新请求时可能是 `NaN` 或图表无值，不补造零值。`rate` 需要多个采集样本；刚启动采集器时图表也可能暂时没有数据。

`grafana-dashboard.json` 是经典 Grafana 仪表盘 JSON，三个 Panel 均引用 `lab4-prometheus`。本地启动脚本会自动建立相同 UID 的数据源并导入；移到其他 Grafana 实例时，先建立此 UID 的 Prometheus 数据源，或把三个 Panel 及其查询中的数据源 UID 改为目标实例实际 UID，再从仪表盘导入页面上传 JSON。

本次采集验证中，`chat-app` Target 为 `UP`，采集地址为 `http://127.0.0.1:5001/metrics`；Prometheus 查询读到成功累计 4、错误累计 1。Grafana 健康接口报告版本 13.2.3、数据库正常，仪表盘已载入 3 个 Panel，经 Grafana 数据源执行的三个查询均返回 HTTP 200。空闲期间，成功/失败速率与在途数为 0，最近窗口的平均耗时为 `NaN`，因此耗时图保留无值；采集启动前的聊天历史不会自动补录成时间序列。
