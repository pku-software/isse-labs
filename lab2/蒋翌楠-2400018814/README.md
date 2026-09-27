# AI 聊天 Web 应用

使用 HTML、CSS、JavaScript 和 Python Flask 构建的 AI 聊天 Web 项目。

## 项目功能

- 网页发送问题，显示真实模型回复。
- 创建、查看、修改、删除问答记录；修改提问不会重新生成回复。
- 页面内编辑、删除确认和错误提示。
- JSON 文件持久化：创建、修改、删除后保存，重启 Flask 后恢复记录。
- 每条问答独立，不支持多会话或多轮上下文。

当前通过 `https://ctmoai.com/v1/responses` 中转接口调用 `gpt-5.5`，使用 OpenAI Responses API 格式，并设置 `store: false`。此实现使用中转站模型，未接入 DeepSeek。

## 安装依赖

在终端执行：

```bash
cd /Users/carrie/isse-labs/lab2/蒋翌楠-2400018814
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

其他电脑请将第一行替换为该项目所在目录。建议使用 Python 3.9 或更新版本。

## 配置与启动

将 `.env.example` 复制为同目录的 `.env`：

```bash
cp .env.example .env
```

已有 `.env` 时不要执行复制，以免覆盖配置。自行编辑 `.env`，填入有权限访问上述中转站和模型的密钥：

```dotenv
OPENAI_API_KEY=your_api_key_here
```

后端兼容旧变量名 `DEEPSEEK_API_KEY`，优先使用 `OPENAI_API_KEY`。不要将真实密钥写入源码、网页或提交到 Git。`.env`、`.venv/` 和 Python 缓存已由 `.gitignore` 排除。

激活虚拟环境后启动：

```bash
python app.py
```

浏览器访问 <http://localhost:5001/>，不要直接打开 HTML 文件。保持终端运行；按 Control + C 停止，再执行启动命令即可重启。修改 `.env` 后需要重启。该启动方式用于本地开发。

## 数据保存

数据文件为本项目下的 `data/messages.json`。最外层是 JSON 数组，每个对象是一条问答：

```json
[
  {"id": 1, "message": "问题", "reply": "模型回复"}
]
```

启动时读取文件，文件不存在或为空时使用空列表；新 ID 从已有最大 ID 加一开始。每次写操作先保存临时文件，再替换正式文件并更新内存。请勿在服务运行时手工修改数据文件。聊天内容以明文保存在本机，不应写入密钥或其他敏感内容。

## API 用法

请求和响应使用 JSON，写请求需带 `Content-Type: application/json`。

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/api/hello` | 返回问候数据 |
| GET | `/api/messages` | 返回全部问答记录的数组 |
| POST | `/api/messages` | 接收 `message`，调用模型，返回完整记录，状态码 201 |
| PATCH | `/api/messages/<id>` | 接收 `message`，修改提问并返回记录 |
| DELETE | `/api/messages/<id>` | 删除记录并返回确认信息 |

缺少或空白 `message` 返回 400；记录不存在返回 404；密钥未配置返回 503；模型调用或响应格式失败返回 502，超时返回 504；文件保存失败返回 500。错误格式为 `{"error":"错误说明"}`。

保持 Flask 运行，在另一个终端测试：

```bash
curl http://localhost:5001/api/hello
curl -X POST http://localhost:5001/api/messages \
  -H 'Content-Type: application/json' \
  -d '{"message":"请用一句话介绍北京大学"}'
curl http://localhost:5001/api/messages
```

POST 会调用模型服务，可能消耗中转站额度。使用返回的真实 ID 替换下面的 `1`：

```bash
curl -X PATCH http://localhost:5001/api/messages/1 \
  -H 'Content-Type: application/json' \
  -d '{"message":"修改后的问题"}'
curl -X DELETE http://localhost:5001/api/messages/1
```

创建一条记录后停止并重启 Flask，再刷新网页，可检查 JSON 持久化是否生效。
