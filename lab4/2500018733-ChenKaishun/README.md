# Lab4：聊天应用指标监控

陈楷舜，2500018733。应用源自个人 Lab3 提交 `f69e8df3`，保留会话及消息的增删改查、原前端与聊天接口。

## Windows 本地启动

在个人 Fork 的 `isse-labs` 根目录使用 PowerShell：

```powershell
python -m venv lab4/2500018733-ChenKaishun/.venv
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe -m pip install -r lab4/2500018733-ChenKaishun/requirements.txt
& ./lab4/2500018733-ChenKaishun/start-app.ps1
```

使用 Python 3.13.5 验证；本次安装 Flask 3.1.3、requests 2.34.2、prometheus-client 0.26.0。
应用以单进程多线程运行，监听 `127.0.0.1:5001`。端口占用时为启动脚本传入 `-Port <可用端口>`，并同步修改 `prometheus.yml` 中的目标地址。

- 聊天页面：`http://127.0.0.1:5001/`
- 指标文本：`http://127.0.0.1:5001/metrics`
- 实验状态：`http://127.0.0.1:5001/api/lab/status`

应用数据写入个人目录的 `.runtime/app/conversations.json`，该目录和 `.venv/`、`.tools/` 均被忽略，不纳入提交。运行路径依据脚本位置确定，不受当前终端目录影响。

## mock 与 real 模式

默认 `CHAT_MODE=mock`：返回固定测试回复，不读取 `.env`，不调用外部模型。实验状态接口返回 `{"mode":"mock","external_model_calls":false}`。

原 `POST /api/messages` 和 `POST /api/conversations/<id>/messages` 接口支持以下 JSON：

```json
{"message":"非敏感测试消息","mock_delay_seconds":0.1,"mock_force_error":false}
```

延迟必须是 0～30 秒的有限数字，失败开关必须为布尔值。延迟在后端处理期间发生，强制失败返回 HTTP 503 和明确的错误 JSON。成功返回 HTTP 201，包含 `id`、`message`、`reply`。mock 仍执行原来的请求校验、会话查找与成功结果保存。

显式传入 `-Mode real` 才启用原 DeepSeek 调用，此时密钥仅从 `DEEPSEEK_API_KEY` 环境变量取得，实验状态接口返回 404，mock 参数不影响真实调用。监控实验使用 mock。

原存储锁及同一会话历史变化检查保留，多个会话可并发处理；同一会话同时修改历史可能返回 HTTP 409。

## 指标

| 指标 | 类型 | 记录范围 |
| --- | --- | --- |
| `chat_requests_total{outcome="success或error"}` | Counter | 聊天 POST 完成后的成功或失败次数；两种标签初始化为 0 |
| `chat_inprogress_requests` | Gauge | 当前尚未结束的聊天 POST 数量 |
| `chat_request_duration_seconds` | Histogram | 每次聊天处理的服务端耗时，包含失败；单位秒 |

计数范围涵盖原聊天处理函数的校验、模型回复和保存。`finally` 负责记录耗时与结果，并减少在途数量，包含预期 HTTP 错误和未处理异常。耗时不含客户端网络传输。

Histogram 桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30、60 秒及正无穷。`_bucket` 记录不超过各边界的累计样本数，`_sum` 记录耗时总和，`_count` 记录样本总数。

页面、`/metrics`、状态接口及会话/消息的查询、修改、删除不计入聊天指标。标签不含消息内容、会话 ID 或用户身份。

## 应用验证

在仓库根目录运行：

```powershell
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe -m unittest discover -s lab4/2500018733-ChenKaishun -p test_app.py -v
```

测试使用独立临时聊天数据，覆盖成功与失败指标、异常收尾、输入校验、非聊天接口排除、原 CRUD、real/mock 路径区分，以及两个慢请求并发时的指标读取。测试禁止实际外部模型调用。

`simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 是课程 `63c1038` 版本的个人副本。访问适配器中的三个函数用于核验 mock 状态、构造聊天请求和判断响应。

## Prometheus 与 Grafana

安装脚本固定使用 [Prometheus 3.15.0](https://github.com/prometheus/prometheus/releases/tag/v3.15.0) 和 [Grafana OSS 13.2.4](https://grafana.com/grafana/download/13.2.4?edition=oss&platform=windows) 的 Windows x64 官方包。安装时验证脚本中固定的 SHA-256，下载中断后可重复运行以复用完整分块。

在仓库根目录使用已创建的虚拟环境：

```powershell
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe lab4/2500018733-ChenKaishun/install-monitoring.py
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe lab4/2500018733-ChenKaishun/start-monitoring.py
```

启动脚本同时启动 mock 聊天应用、Prometheus 和 Grafana，启动前要求 5001、9090、3001 端口空闲。若之前在终端中运行了 `start-app.ps1`，先在该终端用 Ctrl+C 停止它，再启动整套服务。启动失败会停止本次脚本已启动的进程；成功后进程记录写入 `.runtime/processes.json`。

也可以添加 `--service app`、`--service prometheus` 或 `--service grafana` 分别启动某个尚未运行的服务；此时只检查该服务的端口。Windows 后台进程使用隐藏控制台，并将标准输出与错误写入对应的 `.runtime/<服务名>/`。

| 服务 | 地址与配置 |
| --- | --- |
| 聊天应用 | `http://127.0.0.1:5001/`，单进程多线程 |
| Prometheus Targets | `http://127.0.0.1:9090/targets` |
| Grafana 仪表盘 | `http://127.0.0.1:3001/d/lab4-chat` |

3000 端口已有其他程序，因此 Grafana 使用 3001。三个服务均只绑定 `127.0.0.1`。Grafana 允许本机匿名只读查看，数据源与仪表盘由配置文件导入；管理账户的随机密码保存在被忽略的 `.runtime/grafana/admin-password.txt` 中。

相对于个人目录，下载包、分块及校验文件位于 `.tools/downloads/`，解压目录固定为 `.tools/prometheus/` 和 `.tools/grafana/`。Prometheus 时间序列存入 `.runtime/prometheus/`；Grafana 的数据库、日志、插件和仪表盘运行副本分别放在 `.runtime/grafana/data/`、`logs/`、`plugins/`、`dashboards/`。源码配置与可导入的 `grafana-dashboard.json` 保留在可提交目录。

Prometheus 的实际参数为：

```text
prometheus.exe --config.file=<个人目录>/prometheus.yml --storage.tsdb.path=<个人目录>/.runtime/prometheus --web.listen-address=127.0.0.1:9090 --storage.tsdb.retention.time=7d
```

Grafana 的实际参数为 `grafana.exe server --homepath <个人目录>/.tools/grafana --config <个人目录>/grafana.ini`；启动脚本通过 `GF_PATHS_DATA`、`GF_PATHS_LOGS`、`GF_PATHS_PLUGINS` 和 `GF_PATHS_PROVISIONING` 指定各路径。

`prometheus.yml` 每 2 秒采集一次 `127.0.0.1:5001/metrics`，超时 1 秒，job 为 `chat-app`。Grafana 数据源地址为 `http://127.0.0.1:9090`，UID 固定为 `lab4-prometheus`。启动脚本自动导入；若手工导入仪表盘，应先按 `grafana-provisioning/datasources/prometheus.yml` 建立同 UID 的数据源，或将 JSON 中的数据源 UID 换成目标实例的 UID。

仪表盘每 2 秒刷新，三个查询如下：

| 图表 | PromQL | 单位与意义 |
| --- | --- | --- |
| 成功 / 失败请求速率 | `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))` | 请求/秒；最近 30 秒窗口内的平均完成速率 |
| 正在处理的请求 | `sum(chat_inprogress_requests{job="chat-app"})` | 请求数；当前在途处理数量 |
| 平均处理耗时 | `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))` | 秒；最近 30 秒窗口内的服务端平均耗时 |

平均耗时查询在没有新请求时可能得到无值，面板保留空缺。应用重启后内存指标重新累计，Prometheus 已采集的历史仍在其数据目录中。

2026-10-14 的本地连接核验中，`chat-app` 的采集地址为 `http://127.0.0.1:5001/metrics`，Target 为 `UP`；Grafana 数据源健康检查为 `OK`，三个面板查询均返回 HTTP 200。通过原聊天接口发送一条延迟 0.1 秒的 mock 请求后，平均耗时查询取得约 0.105 秒。此为连接核验，不是五阶段访问模拟结果。
