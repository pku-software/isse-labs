# Lab 4：Flask 聊天应用监控

魏睿涵，2410124217。应用来自自己的 Lab 3 Flask 聊天项目，保留页面、聊天接口和聊天记录的增删改查。聊天记录保存在内存中，服务重启后清空。

## 本地运行（Windows x64 / PowerShell）

在个人 Fork 的 `isse-labs` 根目录执行，Python 版本为 3.14.3：

```powershell
python -m venv lab4/2410124217-WeiRuihan/.venv
& 'lab4/2410124217-WeiRuihan/.venv/Scripts/python.exe' -m pip install -r lab4/2410124217-WeiRuihan/requirements.txt
$env:CHAT_MODE = 'mock'
$env:PORT = '5001'
& 'lab4/2410124217-WeiRuihan/.venv/Scripts/python.exe' lab4/2410124217-WeiRuihan/app.py
```

页面为 `http://127.0.0.1:5001/`，指标为 `http://127.0.0.1:5001/metrics`。应用使用单进程、线程并发，监听本机地址；聊天记录读写使用锁保护，模型处理期间不持有存储锁。

默认 `CHAT_MODE=mock`：固定回复“你好”，不读取 `.env`、不创建真实模型客户端。`GET /api/lab-status` 返回实际 mock 配置以及 `external_model_calls: false`。`POST /api/messages` 接收 `message`，以及仅在 mock 模式使用的 `mock_delay`（0～10 秒，默认 0.1 秒）和 `mock_error`（布尔值，默认 false）；模拟失败返回 HTTP 503 和明确错误 JSON。

原模型功能保留在 `CHAT_MODE=real` 分支，从进程环境读取 `DEEPSEEK_API_KEY`；实验不进入这个分支。real 模式下实验状态接口返回 404，实验请求选项不改变真实调用行为。

## 指标

`metrics.py` 定义以下指标，仅统计 `POST /api/messages` 的聊天处理：

| 指标 | 内容 |
| --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | 已完成请求的成功/失败累计次数，两类从 0 初始化 |
| `chat_inprogress_requests` | 当前在途聊天处理数 |
| `chat_request_duration_seconds` | 服务端处理耗时，包含失败；桶上界为 0.05、0.1、0.25、0.5、1、2、3、5、10、+Inf 秒 |

`/metrics`、状态接口、页面、静态文件和记录查询/修改/删除不增加聊天处理计数。异常路径也记录耗时和错误，清理在途计数。指标标签不包含聊天内容。

## 验证

运行回归测试：

```powershell
& 'lab4/2410124217-WeiRuihan/.venv/Scripts/python.exe' -m unittest discover -s lab4/2410124217-WeiRuihan -p test_app.py -v
```

4 项测试验证 mock 不调用真实客户端、成功/失败与异常的指标收尾、非聊天接口不计数、real 模式关闭实验状态接口并忽略实验选项，以及无效模拟参数被拒绝。

本地 HTTP 验证发送一次延迟 0.5 秒的成功请求和一次延迟 0.01 秒的模拟失败请求；慢请求期间采集到在途数 1，指标接口在 0.3 秒以内响应。处理结束后成功/失败累计各 1 次，在途数为 0，耗时样本共 2 次；修改和删除接口也通过验证。上述验证请求本身会产生指标。

课程调度器副本为 `simulate_traffic.py`，接口适配模块为 `project_adapter.py`。工具下载与可执行文件放入 `.tools/`，数据库和日志放入 `.runtime/`，Python 虚拟环境放入 `.venv/`；这些目录及密钥文件均由个人 `.gitignore` 排除。

## Prometheus 与 Grafana

使用 Windows amd64 官方稳定程序：Prometheus 3.15.0 和 Grafana OSS 13.2.3。下载包分别来自 [Prometheus 官方下载页](https://prometheus.io/download/) 和 [Grafana OSS 官方下载页](https://grafana.com/grafana/download/13.2.3?edition=oss&platform=windows)，使用页面公布的 SHA256 核验后解压。

| 文件 | SHA256 |
| --- | --- |
| `prometheus-3.15.0.windows-amd64.zip` | `5d333b385557d9adc2ff015d13da9809baccc52fb800a82d1e5c94b79258f87e` |
| `grafana_13.2.3_windows_amd64.tar.gz` | `dafe883a7c15543c6d6710b868eb8b4053353441ce7ceacf150942b8de3960f0` |

从干净环境重新准备工具，在仓库根目录执行以下 PowerShell 命令。下载前确认个人 `.gitignore` 对 `.tools/`、`.runtime/`、`.venv/` 生效，且工具路径没有被 Git 跟踪：

```powershell
$lab4Dir = 'lab4/2410124217-WeiRuihan'
git check-ignore -v -- "$lab4Dir/.tools/downloads/prometheus.zip" "$lab4Dir/.tools/prometheus/prometheus.exe" "$lab4Dir/.tools/grafana/bin/grafana.exe" "$lab4Dir/.runtime/prometheus/wal" "$lab4Dir/.runtime/grafana/data/grafana.db" "$lab4Dir/.venv/pyvenv.cfg"
git ls-files -- "$lab4Dir/.tools" "$lab4Dir/.runtime" "$lab4Dir/.venv"
New-Item -ItemType Directory -Force -Path "$lab4Dir/.tools/downloads", "$lab4Dir/.tools/prometheus", "$lab4Dir/.tools/grafana" | Out-Null
curl.exe --fail --location --output "$lab4Dir/.tools/downloads/prometheus-3.15.0.windows-amd64.zip" https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.windows-amd64.zip
curl.exe --fail --location --output "$lab4Dir/.tools/downloads/grafana_13.2.3_windows_amd64.tar.gz" https://dl.grafana.com/grafana/release/13.2.3/grafana_13.2.3_36482603486_windows_amd64.tar.gz
if ((Get-FileHash "$lab4Dir/.tools/downloads/prometheus-3.15.0.windows-amd64.zip" -Algorithm SHA256).Hash -ne '5d333b385557d9adc2ff015d13da9809baccc52fb800a82d1e5c94b79258f87e') { throw 'Prometheus 校验失败' }
if ((Get-FileHash "$lab4Dir/.tools/downloads/grafana_13.2.3_windows_amd64.tar.gz" -Algorithm SHA256).Hash -ne 'dafe883a7c15543c6d6710b868eb8b4053353441ce7ceacf150942b8de3960f0') { throw 'Grafana 校验失败' }
tar.exe -xf "$lab4Dir/.tools/downloads/prometheus-3.15.0.windows-amd64.zip" -C "$lab4Dir/.tools/prometheus" --strip-components 1
tar.exe -xf "$lab4Dir/.tools/downloads/grafana_13.2.3_windows_amd64.tar.gz" -C "$lab4Dir/.tools/grafana" --strip-components 1
```

工具位置固定为 `.tools/prometheus/`、`.tools/grafana/`。配置文件和启动脚本保留在可提交位置。启动全部服务：

```powershell
& 'lab4/2410124217-WeiRuihan/start-local.ps1'
```

`start-local.ps1` 将应用设为 mock、端口 5001；Prometheus 使用个人 `prometheus.yml`，监听 `127.0.0.1:9090`，数据库显式放入 `.runtime/prometheus/`。其启动参数为 `--config.file="<个人目录>/prometheus.yml" --storage.tsdb.path="<个人目录>/.runtime/prometheus" --web.listen-address=127.0.0.1:9090`。Grafana 使用 `grafana.exe server --homepath="<个人目录>/.tools/grafana" --config="<个人目录>/grafana.ini"`，监听 `127.0.0.1:3000`；脚本通过 `GF_PATHS_DATA`、`GF_PATHS_LOGS`、`GF_PATHS_PLUGINS` 将数据库、日志、插件分别置于 `.runtime/grafana/data/`、`logs/`、`plugins/`，并显式指定可提交的 provisioning 配置目录。进程 PID 与输出日志也放在 `.runtime/` 下。

脚本遇到其他进程占用端口会停止并提示，不关闭其他应用；同一实验服务已经运行时可重复调用并跳过启动。Grafana 对本机启用匿名 Viewer，打开仪表盘无需登录，只提供查看权限。

Prometheus 每 2 秒访问 `http://127.0.0.1:5001/metrics`，采集超时 1 秒，job 为 `chat-app`。访问 `http://127.0.0.1:9090/targets` 查看目标，访问 `http://127.0.0.1:9090/query` 查询指标。

Grafana 通过 `grafana/provisioning/datasources/prometheus.yml` 自动配置数据源 `Lab4 Prometheus`（UID `lab4-prometheus`），地址为 `http://127.0.0.1:9090`。`grafana/dashboards/chat.json` 通过 provisioning 自动载入三个时间序列 Panel，仪表盘地址为 `http://127.0.0.1:3000/d/lab4-chat`，时区为 Asia/Shanghai，每 5 秒刷新。

| Panel | PromQL | 含义 |
| --- | --- | --- |
| 成功 / 失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近 30 秒窗口内平均每秒完成的请求数，按结果分组 |
| 正在处理的聊天请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 当前采集时刻的在途请求数 |
| 平均聊天处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近窗口内服务端平均耗时，单位秒，包含失败；没有请求时允许无值 |

Histogram 的 `_bucket{le="…"}` 是耗时小于等于上界的累计样本数，`_sum` 是耗时总和，`_count` 是样本数。本次平均耗时图使用 `_sum` 与 `_count` 的变化率；不把客户端往返耗时当作服务端耗时。采集间隔和查询窗口可能让短峰值遗漏或阶段边界变得平滑。

## 访问脚本适配

`simulate_traffic.py` 与课程 `lab4/starter/simulate_traffic.py` 内容一致，保留本机地址限制、mock 核验、有限并发及真实结果统计。调度器负责各阶段的发送频率和并发上限，个人 `project_adapter.py` 负责把请求转换为原项目的接口：

- `confirm_mock_mode()`：HTTP GET `/api/lab-status`，校验 `mode` 为 `mock` 且 `external_model_calls` 为布尔 false；禁用代理和重定向，核验失败返回 false。
- `build_chat_request()`：HTTP POST `/api/messages`，JSON 字段为 `message`、`mock_delay`、`mock_error`。
- `response_is_success()`：HTTP 201、有效 JSON 对象、整数记录 ID、非空回复且没有错误字段才算成功；不打印正文。

单请求验证确认 mock 模式下正常请求返回 201，强制失败返回 503，并被适配器正确识别。相同应用以 real 配置启动临时本地服务时，状态接口返回 404；调度器拒绝运行，没有发送聊天请求，也没有调用真实模型。验证通过后设置 `ADAPTER_READY=True`。对实际 mock 服务的验证产生成功、失败各 1 次计数。

## 首次完整模拟结果

在仓库根目录使用以下命令，默认五个阶段各发送 30 秒、并发上限 6、结束后等待 10 秒采集；结果文件由真实运行产生：

```powershell
& 'lab4/2410124217-WeiRuihan/.venv/Scripts/python.exe' -u lab4/2410124217-WeiRuihan/simulate_traffic.py --base-url http://127.0.0.1:5001 --output lab4/2410124217-WeiRuihan/results/first-run.json
```

2026 年 10 月 12 日实际运行时间如下（北京时间；JSON 内记录 UTC）：

| 阶段 | 起止时间 | 设置 | 发送 | 成功 | 业务/HTTP 错误 | 跳过 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| baseline | 19:16:21–19:16:51 | 1 次/秒，延迟 0.1 秒 | 30 | 30 | 0 | 0 |
| burst | 19:16:51–19:17:21 | 4 次/秒，延迟 0.1 秒 | 120 | 120 | 0 | 0 |
| slow | 19:17:21–19:17:53 | 2 次/秒，延迟 3 秒 | 52 | 52 | 0 | 8 |
| errors | 19:17:53–19:18:23 | 1 次/秒，延迟 0.1 秒，每第 3 次失败 | 30 | 20 | 10 | 0 |
| recovery | 19:18:23–19:18:53 | 1 次/秒，延迟 0.1 秒，无强制失败 | 30 | 30 | 0 | 0 |

共发送 262 次，成功 252 次，预期失败 10 次；各阶段网络错误与非预期结果均为 0，进程退出码为 0。slow 阶段等待在途请求收尾，因此实际结束时间比 30 秒发送窗口稍晚；达到并发上限时跳过发送机会，不无限排队。

按三个 Panel 的原查询、2 秒步长核对本次时间范围内的 Prometheus 历史数据：成功请求速率最高 4 次/秒，失败速率最高约 0.3214 次/秒，在途数最高 6，服务端平均处理耗时最高约 3.001 秒。slow 阶段在途数从低负载时的约 1 上升到 5～6，随后回落；延长处理时间使请求更容易重叠，`2 次/秒 × 3 秒 ≈ 6` 可作为目标负载的近似估计，但实际发送量还受并发上限与完成节奏限制。

`results/first-run.json` 中 `client_mean_seconds` 是客户端往返平均耗时，例如 slow 约 3.070 秒，包含网络与调度开销，不等同于服务端 Histogram。查询使用 30 秒窗口，因此速率和平均耗时曲线在阶段边界存在平滑与滞后。

首次运行可使用绝对时间范围 `2026-10-12 19:16:11` 至 `19:19:33`（Asia/Shanghai）对照图表；完整仪表盘链接为 `http://127.0.0.1:3000/d/lab4-chat?from=1791803771000&to=1791803973000&timezone=Asia%2FShanghai`。历史曲线依赖本地 Prometheus 数据库；干净环境需重新运行脚本，并使用新的实际起止时间查看，结果 JSON 不包含整套监控数据库。

## 延迟调整后的模拟结果

第二次仅运行 slow 场景，将 `--slow-delay` 从 3 秒改为 1 秒，其余负载参数保持默认：目标每秒 2 次、并发上限 6、发送窗口 30 秒、收尾等待 10 秒。burst 和 errors 没有重复运行。

```powershell
& 'lab4/2410124217-WeiRuihan/.venv/Scripts/python.exe' -u lab4/2410124217-WeiRuihan/simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --slow-delay 1 --output lab4/2410124217-WeiRuihan/results/changed-run.json
```

实际起止时间为 2026-10-12 19:31:40–19:32:11（北京时间），发送并成功处理 60 次，错误、网络错误、非预期结果和跳过均为 0，进程退出码为 0。客户端往返平均耗时约 1.070 秒。

| 对比项 | 首次 slow（3 秒延迟） | 第二次 slow（1 秒延迟） |
| --- | --- | --- |
| 实际发送 / 成功 | 52 / 52 | 60 / 60 |
| 跳过发送机会 | 8 | 0 |
| 采集到的在途数 | 主要为 5～6，最高 6 | 主要为 2，最高 2 |
| 服务端平均耗时 | 最高约 3.001 秒 | 约 1.000～1.001 秒 |
| 成功请求速率 | slow 窗口约 1.6～2 次/秒，边界混合前一阶段数据 | 最高 2 次/秒 |

减少延迟后，每个请求更快释放处理位置，在途数和平均耗时下降；发送频率仍为每秒 2 次，因此成功速率没有升到更高的负载水平。第二次未达到并发上限，消除了首次的跳过发送。两次运行的时间范围不同，比较应分别选择各自的实际阶段；速率使用 30 秒窗口，阶段边界不能按瞬时发送频率直接解读。

第二次图表范围为 `2026-10-12 19:31:30` 至 `19:32:51`（Asia/Shanghai），链接为 `http://127.0.0.1:3000/d/lab4-chat?from=1791804690000&to=1791804771000&timezone=Asia%2FShanghai`。

## 仪表盘导入与截图

`grafana-dashboard.json` 从本次实际 Grafana 仪表盘导出，包含三个 Panel、实际 PromQL 和数据源引用，内部数据库 ID 已置空以便导入。UID 为 `lab4-chat`，数据源 UID 为 `lab4-prometheus`。导入到干净实例时，先按 `grafana/provisioning/datasources/prometheus.yml` 创建数据源 `Lab4 Prometheus`（UID 保持 `lab4-prometheus`），地址指向本机 Prometheus，再在 Grafana 的 Dashboards → New → Import 上传该 JSON。使用其他数据源时，在三个 Panel 及其查询中选择对应的 Prometheus 数据源。导入文件保留最近 15 分钟的默认范围，历史实验对照请改为上文的绝对时间范围。

使用随仓库提供的 `start-local.ps1` 时，数据源与仪表盘会自动 provision，无需再次手工导入。可编辑的初始定义为 `grafana/dashboards/chat.json`，导出文件用于复用本次实际仪表盘。

`screenshots/` 均为学生从本地浏览器提供的原始 PNG，未拼接或生成：

- `prometheus-targets.png`：`chat-app` 的采集地址与 UP 状态。
- `grafana-dashboard-requests.png`：首次完整模拟的成功/失败速率与在途数。
- `grafana-dashboard.png`：首次完整模拟的平均耗时，配合上一张覆盖三个 Panel 与完整时段。
- `changed-run-requests.png`、`changed-run-duration.png`：延迟改为 1 秒后的三项曲线。
