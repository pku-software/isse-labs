# 本地聊天应用监控实验

应用源自本人 Lab 3 的 Flask 聊天项目，保留了原页面、`POST /api/messages` 聊天接口，以及记录的查看、修改和删除功能。本目录的记录保存在本地 `data/messages.json`，该文件不提交。

## 运行应用

在本目录中使用 Python 3.9 或更新版本：

```sh
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
LAB4_MODE=mock ./.venv/bin/python app.py
```

应用仅监听 `127.0.0.1:5001`。页面为 `http://127.0.0.1:5001/`，指标接口为 `http://127.0.0.1:5001/metrics`。默认 `mock` 模式返回固定测试回复，不读取 Key，也不调用外部模型。`GET /api/lab4/status` 仅在该模式下返回当前模式与外部模型调用状态，供课程访问脚本核验。

原有真实模型模式仍可使用：以 `LAB4_MODE=real` 启动，并在运行环境中单独配置 `DEEPSEEK_API_KEY`。本监控实验不使用真实模式，也不需要在仓库中保存 Key。

mock 模式的聊天 JSON 除 `message` 外，可选 `mock_delay_seconds`（0～10 秒）和 `mock_force_error`（布尔值）。延迟与模拟失败均在原聊天接口的后端处理过程中发生。实验消息请使用非敏感文本。

## 应用指标

| 指标 | 类型 | 记录内容 |
| --- | --- | --- |
| `chat_requests_total` | Counter | 用 `outcome` 标签区分聊天创建请求完成后的成功与错误次数 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天创建请求数 |
| `chat_request_duration_seconds` | Histogram | 每次聊天创建请求的服务端耗时，含失败请求 |

只有 `POST /api/messages` 计入以上业务指标；页面、静态资源、状态接口与 `/metrics` 不计入。指标标签不包含聊天内容。Histogram 同时提供 `_bucket`、`_sum` 和 `_count` 序列。

## 本地监控工具

本机为 macOS ARM64。使用以下官方稳定版压缩包；下载包放在 `.tools/downloads/`，按官网公布的 SHA-256 校验后，去掉压缩包最外层目录并分别解压到 `.tools/prometheus/` 与 `.tools/grafana/`。工具包与运行数据均不提交。

| 工具 | 官方下载 | SHA-256 |
| --- | --- | --- |
| Prometheus 3.15.0 | [macOS ARM64 包](https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.darwin-arm64.tar.gz) | `920df4d17e78b3b0175af144eb318b0c74d1cf7b1d1251b326966f0e81977260` |
| Grafana OSS 13.2.4 | [macOS ARM64 包](https://dl.grafana.com/grafana/release/13.2.4/grafana_13.2.4_38252365904_darwin_arm64.tar.gz) | `a910966466359212f1d875748a72a4638c7d3724448d0c369210b31d763b165d` |

从干净环境重现时，先用上表链接下载压缩包并校对 SHA-256，再解压。macOS ARM64 可在本目录执行：

```sh
mkdir -p .tools/downloads .tools/prometheus .tools/grafana
curl -fL --output .tools/downloads/prometheus.tar.gz 'https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.darwin-arm64.tar.gz'
curl -fL --output .tools/downloads/grafana.tar.gz 'https://dl.grafana.com/grafana/release/13.2.4/grafana_13.2.4_38252365904_darwin_arm64.tar.gz'
shasum -a 256 .tools/downloads/prometheus.tar.gz .tools/downloads/grafana.tar.gz
# 核对两行输出与上表完全一致后继续
tar -xzf .tools/downloads/prometheus.tar.gz -C .tools/prometheus --strip-components=1
tar -xzf .tools/downloads/grafana.tar.gz -C .tools/grafana --strip-components=1
```

安装 Python 依赖后，在三个独立终端中从本目录依次运行：

```sh
LAB4_MODE=mock ./.venv/bin/python app.py
./start-prometheus.sh
./start-grafana.sh
```

Prometheus 在 `http://127.0.0.1:9090` 使用 `prometheus.yml`，每 2 秒采集一次应用 `/metrics`，数据库及日志写入 `.runtime/prometheus/`。Grafana 在 `http://127.0.0.1:3000` 使用 `grafana.ini`；数据源配置位于 `grafana-provisioning/datasources/prometheus.yml`，其数据库、日志和插件位于 `.runtime/grafana/`。应用日志可放在 `.runtime/app/`。这些路径由启动脚本显式指定，服务只监听本机地址。

首次打开 Grafana 时按页面提示设置本机管理员密码。数据源由启动配置自动添加；`grafana-dashboard.json` 是从 Grafana 13.2.4 导出的 V2 Dashboard 原始 JSON，可在 Grafana 的仪表盘导入界面选择该文件，重建本实验的三个 Panel。仪表盘引用数据源 UID `lab4-prometheus`，与配置文件一致。

仪表盘使用三个 PromQL 查询：

| Panel | 查询 | 显示值 |
| --- | --- | --- |
| 成功与失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近 30 秒窗口内各类请求平均每秒完成数 |
| 正在处理的聊天请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 当前在途请求数 |
| 平均聊天处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近窗口内服务端平均耗时，单位秒 |

仪表盘每 5 秒刷新。无请求时平均耗时可能没有值，不补零；Histogram 的 `_bucket` 表示落在各耗时上限内的累计样本数，本仪表盘用 `_sum` 与 `_count` 计算平均值。

## 课程访问脚本与实际结果

`simulate_traffic.py` 是课程提供的调度器，控制五阶段的发送频率、并发和收尾等待；`project_adapter.py` 把它连接到本应用的 `POST /api/messages`，先经 `GET /api/lab4/status` 确认 mock 模式，再按 HTTP 状态与回复 JSON 判断成功。脚本只发送固定的非敏感测试文本。应用、Prometheus 与 Grafana 启动后，运行：

```sh
./.venv/bin/python -B simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
./.venv/bin/python -B simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --phase-seconds 30 --slow-delay 10 --timeout 12 --output results/changed-run.json
```

首次完整模拟于 2026-10-18 21:50:34～21:53:06（北京时间）运行。以下数量来自 `results/first-run.json`，阶段结束时间包含等待尚在处理的请求：

| 阶段 | 设置 | 实际发送 | 成功 | 模拟错误 | 因并发上限跳过 |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline | 1 次/秒，延迟 0.1 秒 | 30 | 30 | 0 | 0 |
| burst | 4 次/秒，延迟 0.1 秒 | 120 | 120 | 0 | 0 |
| slow | 2 次/秒，延迟 3 秒，最多并发 6 次 | 52 | 52 | 0 | 8 |
| errors | 1 次/秒，每第 3 次模拟失败 | 30 | 20 | 10 | 0 |
| recovery | 1 次/秒，延迟 0.1 秒 | 30 | 30 | 0 | 0 |

第二次仅运行 slow 阶段，于 2026-10-18 22:06:55～22:07:29（北京时间）把后端延迟改为 10 秒，仍限并发 6 次；`results/changed-run.json` 记录实际发送 18 次、成功 18 次、跳过 42 次。两次均无网络错误或非预期结果。首次 burst 的成功速率升高，errors 阶段出现错误速率；首次 slow 与第二次 slow 的服务端平均耗时峰值分别约为 3 秒和 10 秒。Prometheus 的 2 秒采样显示两次 slow 阶段在途请求峰值均为 6；延迟增加后，请求占用并发位置更久，跳过的发送机会更多。`rate(...[30s])` 使用滑动窗口，阶段切换时曲线可能平滑过渡。

首次模拟的原始仪表盘截图在 `screenshots/grafana-dashboard.png`；Target 与查询截图也保存在 `screenshots/`。脚本的 `client_mean_seconds` 包含网络和客户端处理时间，不等同于仪表盘显示的服务端 Histogram 平均耗时。
