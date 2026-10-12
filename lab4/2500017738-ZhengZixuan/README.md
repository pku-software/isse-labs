# Lab 4：本地聊天应用监控

## 项目与运行模式

本项目从个人 Lab 3 Flask 聊天应用复制，并在本目录中补充监控指标。默认使用 `CHAT_MODE=mock`：回复由本地模拟逻辑生成，不调用真实模型，也不需要 API Key。`CHAT_MODE=real` 是原项目的真实模型模式，本实验不启用它。

应用通过 `GET /metrics` 暴露 Prometheus 文本格式。`project_adapter.py` 核验 `GET /__lab4/status` 的 mock 状态，并把通用访问调度转换为 `POST /api/messages` 请求；模拟延迟和失败只用于 mock 模式。

## 指标与图表

- **完成请求数**：`chat_requests_total{outcome="success|error"}` 是 Counter，处理完成时按成功或错误累计；Counter 不会因请求结束而减少。
- **正在处理数**：`chat_inprogress_requests` 是 Gauge，请求开始时增加，成功、失败或异常结束时减少；它表示当前处理中的请求数，不是在线用户数。
- **处理耗时**：`chat_request_duration_seconds` 是 Histogram，记录服务端处理时间，暴露 `_bucket`、`_sum`、`_count`。本仪表盘用 `_sum` 与 `_count` 的速率计算最近 30 秒平均值；没有样本时可能无值。

Prometheus 2 秒抓取一次 `http://127.0.0.1:5001/metrics`，1 秒超时，job 名为 `chat-app`。Grafana 在本机 3000 端口展示 Prometheus 保存的时间序列。Prometheus 数据和 Grafana 运行数据均写入本目录下被 Git 忽略的 `.runtime/`。

仪表盘包含三个时间序列 Panel，定义保存在 `grafana-dashboard.json`，数据源 UID 为 `prometheus-lab4`，由 `grafana/provisioning/datasources/prometheus.yml` 提供。启动时会把该仪表盘配置加载到 Grafana 的 Lab 4 文件夹中；也可以在 Grafana 导入 JSON 时选择本地 Prometheus 数据源。

- 成功/失败请求速率：`sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))`，把完成次数换算为最近窗口内每秒平均请求数。
- 正在处理的请求：`sum(chat_inprogress_requests{job="chat-app"})`，表示当前执行聊天处理的数量。
- 平均服务端处理耗时：`sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))`，单位为秒。

仪表盘自动刷新间隔为 5 秒。所有服务仅监听本机地址。

## 工具版本

- Prometheus 3.15.0，macOS arm64 官方稳定版。
- Grafana OSS 13.2.3，macOS arm64 官方稳定版。
- Python 3.13，依赖见 `requirements.txt`。

工具归档位于 `.tools/downloads/`，解压程序位于 `.tools/prometheus/` 和 `.tools/grafana/`。这些程序和运行数据不提交 Git。

## 启动与复现

环境为 macOS arm64、Python 3.13。Prometheus 3.15.0 和 Grafana OSS 13.2.3 使用 macOS arm64 官方稳定版，程序分别放在 `.tools/prometheus/`、`.tools/grafana/`；下载包位于 `.tools/downloads/`。从干净环境准备同版本工具，并解压到上述目录后，在本目录运行：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./start_lab4.sh
```

启动脚本在需要时运行 mock Flask 应用、Prometheus 和 Grafana；所有服务绑定 `127.0.0.1`，日志分别写入 `.runtime/app/`、`.runtime/prometheus/` 与 `.runtime/grafana/`。本实验实际端口为应用 `5001`、Prometheus `9090`、Grafana `3000`。

页面地址：

- 聊天应用：<http://127.0.0.1:5001/>
- Prometheus Targets：<http://127.0.0.1:9090/targets>
- Prometheus 查询页：<http://127.0.0.1:9090/graph>
- Grafana：<http://127.0.0.1:3000/>

Prometheus 显示 Target 为 `UP` 只表示它成功抓取了 `/metrics`；它本身不能证明聊天请求均成功。仪表盘由 `grafana-dashboard.json` 定义，数据源由 `grafana/provisioning/datasources/prometheus.yml` 配置。

课程访问脚本只通过应用 HTTP 接口产生请求，不直接修改指标。完整模拟命令为：

```sh
.venv/bin/python simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
```

调整慢请求时长后的复现命令为：

```sh
.venv/bin/python simulate_traffic.py --base-url http://127.0.0.1:5001 --scenario slow --slow-delay 5 --output results/changed-run.json
```

## 实际运行结果

结果由脚本写入 `results/first-run.json` 和 `results/changed-run.json`；文件时间为 UTC。首次完整运行从 `2026-10-12 16:50:55 UTC` 开始，最后一个阶段于 `16:53:27 UTC` 结束，之后等待 10 秒采集收尾。第二次 `slow` 阶段从 `2026-10-12 17:04:16 UTC` 到 `17:04:51 UTC`，之后同样等待 10 秒。完整阶段统计如下：

| 阶段 | 设置 | 已发送 | 成功 | 业务/HTTP 错误 | 跳过 |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline | 1 次/秒，延迟 0.1 秒 | 30 | 30 | 0 | 0 |
| burst | 4 次/秒，延迟 0.1 秒 | 120 | 120 | 0 | 0 |
| slow | 2 次/秒，延迟 3 秒，并发上限 6 | 52 | 52 | 0 | 8 |
| errors | 1 次/秒，每第 3 次请求模拟失败 | 30 | 20 | 10 | 0 |
| recovery | 1 次/秒，延迟 0.1 秒 | 30 | 30 | 0 | 0 |

第二次只运行 `slow` 阶段，将延迟改为 5 秒，其余设置不变：30 秒内调度 60 次、发送并成功 35 次、跳过 25 次，没有网络错误。脚本记录的客户端平均耗时约 5.01 秒，包含客户端侧开销，不等同于服务端 Histogram。

首次运行的 Grafana 截图显示突发阶段成功速率峰值约 3.5 次/秒；慢请求阶段平均服务端耗时峰值约 2.9 秒，正在处理数被采到的最高值为 5。把延迟改为 5 秒后，平均耗时约升至 5 秒；正在处理数采到的最高值仍为 5。由于 Prometheus 每 2 秒抓取一次，图上的峰值是采样观察值。更长延迟下，调度器达到并发上限的时间增加，跳过数从 8 增至 25，完成请求数从 52 降至 35。原始仪表盘截图保存在 `screenshots/grafana-dashboard.png`。
