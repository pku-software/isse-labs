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
