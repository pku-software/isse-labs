# Lab 4：本地聊天应用监控

王珮源，2500013167。应用来源为个人 Lab 3 Flask 项目，保留 HTML/CSS/JavaScript 前端与内存聊天记录 CRUD。

## Windows 本地运行

在本目录执行：

```powershell
python -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
./start-app.ps1
```

页面为 http://127.0.0.1:5001/，指标为 http://127.0.0.1:5001/metrics。启动脚本明确设置 `MODEL_MODE=mock`，单进程线程并发，无重载器。可用 `./start-app.ps1 -Port 5002` 更换端口。

`POST /api/messages` 接收 `message`。mock 模式返回固定测试回复，可选 `mock_delay_seconds`（0～30 秒有限数值）和 `mock_force_error`（布尔值）；模拟失败返回 HTTP 503。`GET /api/lab-status` 仅在 mock 模式提供，返回实际模式及 `external_model_calls=false`。mock 路径不读取 Key、不调用外部模型。聊天记录仅在内存中，重启清空，读写使用线程锁。

保留 `MODEL_MODE=real` 功能，需自行配置后端环境变量 `DEEPSEEK_API_KEY`；real 模式忽略模拟选项。本实验使用 mock。应用不加载 `.env`。

## 指标

仅聊天创建请求记录业务指标；静态资源、读取/修改/删除记录、状态和采集请求均不计入。

- `chat_requests_total{outcome="success"或"error"}`：处理完成后累计，两种结果初始化为零。
- `chat_inprogress_requests`：处理开始增加，所有结束路径减少。
- `chat_request_duration_seconds`：服务端处理耗时，含失败；桶覆盖 0.05～30 秒，并暴露总和与次数。

HTTP 验证通过首页、mock 状态、创建/修改/删除、一次模拟失败及慢请求期间指标响应。三次聊天测试产生成功 2、失败 1，结束后在途为 0，耗时样本数为 3。慢请求等待 2 秒期间，指标接口约 0.025 秒响应；再次运行会继续累加，时延随环境变化。

工具、运行数据和虚拟环境分别保存在本目录 `.tools/`、`.runtime/`、`.venv/`，均不提交。

## Prometheus 与 Grafana

Windows x64 官方稳定版本：Prometheus 3.15.0（2026-09-24）、Grafana OSS 13.2.3（2026-09-29）。安装包和官方 SHA256 记录放在 `.tools/downloads/`；校验后将包内顶层目录的内容分别解压到 `.tools/prometheus/`、`.tools/grafana/`。

从干净环境重建工具时，先在仓库根目录核验个人忽略规则；以下下载、校验和解压命令在个人目录执行（下载失败可重试，校验不通过则停止）：

```powershell
New-Item -ItemType Directory -Force .tools/downloads, .tools/prometheus, .tools/grafana | Out-Null
$labPromUrl = 'https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.windows-amd64.zip'
$labGrafUrl = 'https://dl.grafana.com/grafana/release/13.2.3/grafana_13.2.3_36482603486_windows_amd64.tar.gz'
curl.exe -fL --retry 3 -o .tools/downloads/prometheus.zip $labPromUrl
if ($LASTEXITCODE -ne 0) { throw 'Prometheus download failed' }
curl.exe -fL --retry 3 -o .tools/downloads/grafana.tar.gz $labGrafUrl
if ($LASTEXITCODE -ne 0) { throw 'Grafana download failed' }
$labPromSha = '5d333b385557d9adc2ff015d13da9809baccc52fb800a82d1e5c94b79258f87e'
$labGrafSha = 'dafe883a7c15543c6d6710b868eb8b4053353441ce7ceacf150942b8de3960f0'
@("$labPromSha prometheus.zip", "$labGrafSha grafana.tar.gz") | Set-Content .tools/downloads/checksums.txt
if ((Get-FileHash .tools/downloads/prometheus.zip -Algorithm SHA256).Hash.ToLower() -ne $labPromSha) { throw 'Prometheus checksum mismatch' }
if ((Get-FileHash .tools/downloads/grafana.tar.gz -Algorithm SHA256).Hash.ToLower() -ne $labGrafSha) { throw 'Grafana checksum mismatch' }
tar.exe -xf .tools/downloads/prometheus.zip -C .tools/prometheus --strip-components 1
if ($LASTEXITCODE -ne 0) { throw 'Prometheus extraction failed' }
tar.exe -xf .tools/downloads/grafana.tar.gz -C .tools/grafana --strip-components 1
if ($LASTEXITCODE -ne 0) { throw 'Grafana extraction failed' }
```

校验值对应上述固定版本的官方发行包。首次运行先启动应用，再运行监控启动脚本；重新启动前停止本实验已有实例，避免端口冲突。前台应用在其终端按 Ctrl+C 停止，监控启动脚本记录的进程 ID 位于各自 `.runtime/` 子目录的 `process.pid`，停止时须核对进程路径属于本项目工具。

应用启动后在个人目录执行 `./start-monitoring.ps1`。Prometheus 启动参数为 `--config.file=<个人目录>/prometheus.yml --storage.tsdb.path=<个人目录>/.runtime/prometheus --web.listen-address=127.0.0.1:9090`，每 2 秒采集 `127.0.0.1:5001/metrics`，超时 1 秒。Targets 页面为 http://127.0.0.1:9090/targets。

Grafana 启动命令为 `.tools/grafana/bin/grafana.exe server --homepath=<个人目录>/.tools/grafana --config=<个人目录>/grafana.ini`。脚本将 `GF_PATHS_DATA`、`GF_PATHS_LOGS`、`GF_PATHS_PLUGINS` 分别设为 `.runtime/grafana/data`、`logs`、`plugins`；`GF_PATHS_PROVISIONING` 指向个人 `grafana/provisioning/`。数据源为 `http://127.0.0.1:9090`，UID 为 `lab4-prometheus`。启动脚本将仪表盘复制到 `.runtime/grafana/dashboards/`，并设置 provisioning 使用该目录。

Grafana 仅监听 `127.0.0.1:3000`，允许本机匿名 Viewer 查看仪表盘，刷新为 2 秒。页面为 http://127.0.0.1:3000/d/lab4-wangpeiyuan/ 。配置内包含三个查询：

```promql
sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))
sum(chat_inprogress_requests{job="chat-app"})
sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))
```

分别表示最近 30 秒内平均每秒完成的请求数（成功/失败分组）、当前在途聊天请求数、最近 30 秒内平均服务端处理秒数。无请求时平均耗时可能无值，不填充假零值。Histogram 的 `_bucket{le="..."}` 是耗时不超过该上界的累计次数，`_sum` 是耗时总和，`_count` 是样本数。

仪表盘引用数据源 UID `lab4-prometheus`；重新部署可沿用 provisioning，手工导入时须先创建相同 UID 的 Prometheus 数据源或调整仪表盘引用。更换端口时同步修改采集配置、数据源与监听配置。

## 课程访问脚本适配

`simulate_traffic.py` 是课程 `lab4/starter/` 调度器的原样副本，未修改发送节奏、并发、阶段、地址检查或统计逻辑。个人 `project_adapter.py` 通过 `/api/lab-status` 实际核验 mock，禁用代理及重定向；只允许本机根地址。聊天请求为 `POST /api/messages`，包含 `message`、`mock_delay_seconds`、`mock_force_error`。成功要求 HTTP 201 及有效的记录 ID、消息、非空回复，错误和无效 JSON 均判定失败。

适配验证通过一次成功（201）、一次强制失败（503）、无效响应及非本地地址拒绝；临时启动的实际 real 模式服务被脚本拒绝，未发送聊天请求。验证完成后设 `ADAPTER_READY=True`。这些 mock 验证会增加累计指标；脚本结果只统计本次脚本发送的请求。

## 首次完整模拟结果

在个人目录使用实际运行命令：

```powershell
& ./.venv/Scripts/python.exe -u ./simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
```

2026-10-13 北京时间 19:35:47 开始，最后一阶段 19:38:22 结束，再等待 10 秒。使用课程默认参数：每阶段发送持续 30 秒，baseline/burst/slow 目标速率分别为 1/4/2 次每秒；普通延迟 0.1 秒，slow 延迟 3 秒；并发上限 6；errors 每第 3 次强制失败。JSON 时间为 UTC，下表为北京时间。

| 阶段 | 实际起止时间 | 发送 | 成功 | 业务/HTTP 失败 | 跳过发送机会 |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline | 19:35:47–19:36:17 | 30 | 30 | 0 | 0 |
| burst | 19:36:17–19:36:48 | 113 | 113 | 0 | 7 |
| slow | 19:36:48–19:37:22 | 43 | 43 | 0 | 17 |
| errors | 19:37:22–19:37:52 | 30 | 20 | 10 | 0 |
| recovery | 19:37:52–19:38:22 | 30 | 30 | 0 | 0 |

合计发送 246，成功 236，预期模拟失败 10，网络错误和非预期结果均为 0，脚本退出码 0。并发容量满时共跳过 24 个发送机会，调度器不无限排队；阶段结束等待在途请求完成，因此阶段实际结束可能晚于发送窗口。目标发送频率不等于实际完成速率。

在完整时间范围以 2 秒步长查询 Prometheus：成功速率峰值约 3.786 次/秒，失败速率峰值约 0.357 次/秒，在途采样峰值 5，服务端窗口平均耗时约 0.101～3.001 秒。`first-run.json` 的客户端平均耗时包含网络及客户端开销，例如 baseline 约 1.125 秒、slow 约 4.019 秒，不等同于服务端 Histogram。

原始仪表盘截图覆盖北京时间 19:35:30–19:38:42，三个 Panel 均可见。burst 的成功速率上升；slow 的在途数量和平均耗时升高；errors 出现失败速率，recovery 后回落。30 秒查询窗口混合相邻阶段的样本，使速率和平均耗时平滑变化并有滞后；2 秒采样可能漏掉 0.1 秒请求的在途短峰值。

## 调整 burst 频率后的模拟

只把 burst 目标频率由 4 改为 30 次/秒，单跑该场景，其余参数保持默认：后端延迟 0.1 秒、并发上限 6、发送持续 30 秒、收尾等待 10 秒。

```powershell
& ./.venv/Scripts/python.exe -u ./simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario burst --burst-rate 30 --output results/changed-run.json
```

实际运行时间为 2026-10-13 北京时间 19:44:07–19:44:38，然后等待 10 秒。896 个调度机会中发送 173 次，全部成功，跳过 723 次；业务/HTTP 失败、网络错误和非预期结果均为 0，退出码 0。客户端平均耗时约 1.031 秒。

与首次 burst 的 113 次成功、7 次跳过相比，本次完成量有所增加，但没有达到目标 30 次/秒。Prometheus 2 秒步长查询的成功速率峰值约 5.75 次/秒，在途采样峰值 1，服务端平均耗时约 0.101～0.102 秒。客户端在途位置覆盖完整 HTTP 往返，不能用服务端 Gauge 替代其并发统计；本环境客户端耗时高于服务端处理耗时。客户端并发容量满时，脚本直接跳过发送机会，这些机会未发送 HTTP 请求，不属于服务器拒绝，也不计入应用错误指标。

两张学生原始截图保存在 `screenshots/prometheus-targets.png` 和 `screenshots/grafana-dashboard.png`，未经重绘或转换。两次实际运行 JSON 保存在 `results/`，重复实验须使用不同输出文件名以保留原结果。重新运行后曲线和吞吐量可受本机环境影响。
