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
