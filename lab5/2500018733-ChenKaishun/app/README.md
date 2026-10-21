# Lab5：聊天应用持续集成

沿用本人 Lab2 的 Flask 聊天应用，支持多个会话及聊天记录的创建、查询、修改和删除。

## 文件与接口

- `app.py`：Flask 后端入口；`get_ai_reply()` 负责调用模型。
- `frontend/`：HTML、CSS 和 JavaScript 页面。
- `requirements.txt`：应用依赖。
- `.env.example`：配置示例，只有占位值。
- `data/conversations.json`：会话持久化文件，初始为空数组。

`GET /` 返回首页，`GET /api/hello` 返回 `{"message":"你好"}`。
`/api/conversations` 管理会话；`/api/conversations/<id>/messages` 及其消息 ID 子路径提供聊天记录 CRUD。修改消息仅更新问题文本，保留已有回答。

## 本地环境

在本仓库根目录用 PowerShell 执行：

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

浏览器访问 http://localhost:5001/，按 Ctrl+C 停止服务。
首页和连通性接口不需要真实 API Key；真实聊天调用由 `DEEPSEEK_API_KEY` 配置。Lab5 自动测试将模拟模型调用，不需要真实 Key。

## 自动测试

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

`tests/test_chat_api.py` 检查单条聊天记录的创建、查询、修改、删除，以及空消息的拒绝处理。测试通过 Flask test client 发请求，并将 `get_ai_reply()` 替换为固定回复。

`tests/test_conversations.py` 补充检查会话查询、重命名、删除，以及从 JSON 文件重新读取会话和消息。覆盖率统计整个后端模块 `app`：

```powershell
.\.venv\Scripts\python.exe -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
```

每个测试加载一份独立应用，通过 `LAB5_DATA_DIR` 使用临时数据目录，不读取本地 `.env`。普通启动未设置该变量时，继续使用项目内的 `data/`。

`pytest.ini` 将测试临时目录设为 `.pytest_cache/tmp`，避开本机系统临时目录的权限问题。pytest 会在每次运行时清理这个专用目录；该目录仅保存测试生成的数据，并由 `.gitignore` 排除。

## 冒烟检查

`scripts/smoke_test.py` 复用课程骨架，入口为 `app:app`。脚本选择临时端口，启动 Flask 子进程，检查 `/` 返回 HTML、`/api/hello` 返回 `{"message":"你好"}`，最后停止服务。
脚本通过 `LAB5_DATA_DIR` 使用临时数据目录，并禁用本地 dotenv 配置读取；两项请求不调用模型。

```powershell
.\.venv\Scripts\python.exe scripts/smoke_test.py
```

成功时依次输出服务就绪、两项 PASS、服务停止和冒烟检查通过。该检查验证进程启动与基础 HTTP 响应，不覆盖浏览器按钮交互。

## GitHub Actions

`.github/workflows/ci.yml` 定义 `Chat CI` 工作流，在推送到 `main` 或向 `main` 发起 PR 时运行。
此前的云端版本使用 Ubuntu runner；当前同一工作流已配置为使用带有 `self-hosted`、`Windows`、`X64` 标签的本机 runner。

`Tests and coverage` 使用 Windows PowerShell，调用本机 `C:\Users\R32st\AppData\Local\Programs\Python\Python313\python.exe` 在 runner 检出目录创建 `.venv`、准备 pip、安装两份依赖清单，然后通过该虚拟环境运行相同的测试、70% 覆盖率检查和冒烟脚本。换机器时需调整基础 Python 路径。

runner 安装于 `D:\Tools\actions-runner-lab5`，在此目录执行 `.\run.cmd` 后保持终端打开。任务使用其 `_work` 下的检出目录，与日常开发目录分开。完成实验取证后，在 runner 终端按 Ctrl+C 停止监听。

推送后在仓库 Actions 页面打开对应提交的运行，进入 `Tests and coverage`，分别展开 `Run tests and coverage` 和 `Run smoke test` 查看结果。
