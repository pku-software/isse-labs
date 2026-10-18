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

mock 模式的聊天 JSON 除 `message` 外，可选 `mock_delay_seconds`（0～8 秒）和 `mock_force_error`（布尔值）。延迟与模拟失败均在原聊天接口的后端处理过程中发生。实验消息请使用非敏感文本。

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

准备好工具后，在三个独立终端中从本目录依次运行：

```sh
LAB4_MODE=mock ./.venv/bin/python app.py
./start-prometheus.sh
./start-grafana.sh
```

Prometheus 在 `http://127.0.0.1:9090` 使用 `prometheus.yml`，每 2 秒采集一次应用 `/metrics`，数据库及日志写入 `.runtime/prometheus/`。Grafana 在 `http://127.0.0.1:3000` 使用 `grafana.ini`；数据源配置位于 `grafana-provisioning/datasources/prometheus.yml`，其数据库、日志和插件位于 `.runtime/grafana/`。应用日志可放在 `.runtime/app/`。这些路径由启动脚本显式指定，服务只监听本机地址。

仪表盘使用三个 PromQL 查询：

| Panel | 查询 | 显示值 |
| --- | --- | --- |
| 成功与失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 最近 30 秒窗口内各类请求平均每秒完成数 |
| 正在处理的聊天请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 当前在途请求数 |
| 平均聊天处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 最近窗口内服务端平均耗时，单位秒 |

仪表盘每 5 秒刷新。无请求时平均耗时可能没有值，不补零；Histogram 的 `_bucket` 表示落在各耗时上限内的累计样本数，本仪表盘用 `_sum` 与 `_count` 计算平均值。
