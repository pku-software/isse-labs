# AI 聊天 Web 应用（Lab 3 云端部署）

这是一个使用原生 HTML、CSS、JavaScript 和 Python Flask 构建的 AI 聊天 Web 应用。前端通过 `fetch()` 调用同源 Flask API，Flask 后端再调用 DeepSeek API。浏览器不会接触 DeepSeek API Key。

## 功能

- 创建、查看、修改和删除多个聊天会话。
- 每个会话支持创建、修改和删除消息。
- 使用 DeepSeek 生成真实 AI 回复。
- 同一会话会携带最近 10 轮历史消息作为模型上下文。
- 页面内显示确认、错误和状态反馈，不使用浏览器弹窗。

## 项目结构

```text
.
|-- app.py
|-- frontend/
|   |-- index.html
|   |-- style.css
|   `-- app.js
|-- requirements.txt
|-- Dockerfile
|-- .dockerignore
|-- .gitignore
|-- .env.example
`-- README.md
```

## 本地运行

环境要求为 Python 3.9 或更高版本，并需要能够访问 DeepSeek API。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

在 `.env` 中设置：

```dotenv
DEEPSEEK_API_KEY=你的真实APIKey
```

启动开发服务器：

```powershell
.\.venv\Scripts\python.exe app.py
```

浏览器访问 `http://localhost:5001/`。生产容器使用以下 Gunicorn 命令启动：

```text
gunicorn --bind 0.0.0.0:5001 --workers 1 --timeout 120 app:app
```

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/hello` | 后端连通性测试 |
| `GET` | `/api/conversations` | 获取会话摘要列表 |
| `POST` | `/api/conversations` | 创建会话 |
| `GET` | `/api/conversations/<id>` | 获取会话及消息 |
| `PATCH` | `/api/conversations/<id>` | 修改会话名称 |
| `DELETE` | `/api/conversations/<id>` | 删除会话 |
| `POST` | `/api/conversations/<id>/messages` | 创建消息并生成 AI 回复 |
| `PATCH` | `/api/conversations/<id>/messages/<messageId>` | 修改消息 |
| `DELETE` | `/api/conversations/<id>/messages/<messageId>` | 删除消息 |

## ACR 云端构建

- 云服务：阿里云容器镜像服务 ACR 个人版
- 地域：华北 2（北京）
- GitHub 个人仓库：`leiyuanze/isse-labs`
- 构建分支：`lab3/2510124204-leiyuanze`
- 构建上下文目录：`/lab3/2510124204-leiyuanze/`
- Dockerfile：`Dockerfile`
- 镜像版本：`lab3-1454ed6`
- 构建方式：海外机器构建，关闭自动构建，由“立即构建”手动触发
- 构建结果：成功

ACR 从 GitHub 远端分支拉取代码并构建镜像，再将镜像保存到个人版实例的私有镜像仓库中。修改代码后必须先 Push 到 GitHub 的对应分支，再由 ACR 手动重新构建。

## ECI 部署与公网验证

- 云服务：阿里云弹性容器实例 ECI
- 地域与可用区：华北 2（北京），北京可用区 H
- 实例名称/ID：`eci-2zedish0bzjgnsnhnhgf`
- 容器组名称：`container-group-1790689154920`
- 算力规格：经济型，0.25 vCPU、512 MiB
- 镜像地址：`crpi-saj2ljxashd028dn-vpc.cn-beijing.personal.cr.aliyuncs.com/isse-labs-lab3/isse-labs-lab3:lab3-1454ed6`
- 容器监听端口：`5001`
- 环境变量名称：`DEEPSEEK_API_KEY`
- 公网弹性 IP：`39.105.88.8`
- 私网 IP：`172.20.99.246`
- 公网访问地址：`http://39.105.88.8:5001/`
- 安全组：`sg-2zegaj6071nb2utqs90m`
- 临时入方向规则：允许来源 `0.0.0.0/0` 访问 TCP `5001/5001`

公网验证结果：

- `GET /api/hello` 返回 `200` 和 `{"message":"你好"}`。
- `GET /`、`/style.css`、`/app.js` 均返回 `200`。
- `GET /api/conversations` 返回正常 JSON。
- 直连 `POST /api/conversations` 返回 `201`，删除测试会话返回 `200`。
- 学生已在自己的浏览器中访问公网页面，并确认非敏感聊天记录和 DeepSeek 回复正常显示。
- 验证截图：`screenshots/eci-created.png`、`screenshots/public-page.png`。

## 安全与数据说明

- `.env` 已被 `.gitignore` 忽略，真实 Key 不进入 Git、Dockerfile、镜像或前端。
- ECI 运行时通过后端环境变量 `DEEPSEEK_API_KEY` 提供 Key。
- `.dockerignore` 排除了 `.env`、虚拟环境、缓存、日志、聊天数据和对话轨迹。
- 本 Lab 未配置云端持久化存储，容器重建后聊天记录可能丢失。
- 本实验使用公网 HTTP，聊天内容不加密；不要通过该地址发送敏感信息。
- 公网聊天 API 没有鉴权，知道地址的其他人可能访问或调用后端并消耗 DeepSeek 额度。
- ECI 验证和 PR 完成后必须删除 ECI，并检查关联 EIP；临时安全组规则也应清理。
