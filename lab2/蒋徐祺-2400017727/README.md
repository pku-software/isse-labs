# AI 聊天 Web 应用

一个最小但完整可运行的 AI 聊天 Web 应用：前端使用 HTML + CSS + JavaScript，后端使用 Python + Flask，
通过 DeepSeek 官方 API 获取真实的模型回复。

## 项目功能

- 在网页输入框中发送消息，页面同时显示用户消息与模型回复；
- 每条聊天记录都可以修改和删除，一次问答即一条记录；
- 每条记录的字段为 `id`（唯一）、`message`（用户消息）、`reply`（模型回复）；
- 聊天记录保存在 Flask 进程的内存中，重启服务后会清空；
- DeepSeek API Key 只保存在后端的 `.env` 文件中，前端不会接触 Key。

## 目录结构

```text
.
├── app.py              # Flask 后端：提供前端页面与聊天 API
├── requirements.txt    # 后端依赖
├── .env.example        # 环境变量示例（不包含真实 Key）
├── .gitignore          # 忽略 .env、__pycache__、.venv 等
└── frontend/
    ├── index.html      # 页面结构
    ├── style.css       # 页面样式
    └── app.js          # 页面逻辑，通过 fetch() 调用后端 API
```

## 环境要求

- Python 3.8 或更高版本；
- 一个可用的 DeepSeek API Key。

## 安装依赖

方式一，使用 venv：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

方式二，使用 uv：

```bash
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate
```

## 配置环境变量

1. 复制示例文件，得到本地的 `.env`：

```bash
cp .env.example .env
```

2. 打开 `.env`，把示例值替换成你自己的真实 Key：

```text
DEEPSEEK_API_KEY=你的真实APIKey
```

`.env.example` 只是给使用者看的模板，可以提交到版本库；`.env` 存放真实密钥，
已在 `.gitignore` 中忽略，不会被提交。

## 启动服务

```bash
python app.py
```

Flask 会监听 `5001` 端口，启动成功后终端会显示类似 `Running on http://127.0.0.1:5001` 的信息。
停止服务用 `Ctrl+C`。

## 浏览器访问

在浏览器中打开：

```text
http://localhost:5001/
```

页面由 Flask 直接提供，前端通过相对地址 `/api/messages` 调用同一个服务上的后端接口。

## 已实现的 API

| 方法   | 路径                   | 说明                                                             |
| ------ | ---------------------- | ---------------------------------------------------------------- |
| GET    | `/`                    | 返回前端页面 `index.html`                                        |
| GET    | `/api/hello`           | 连通性测试，返回 `{"message": "你好"}`                           |
| GET    | `/api/messages`        | 返回全部聊天记录                                                 |
| POST   | `/api/messages`        | 创建一条记录，请求体 `{"message": "..."}`，`reply` 由 DeepSeek 生成 |
| PATCH  | `/api/messages/<id>`   | 修改指定记录的 `message`，请求体 `{"message": "..."}`            |
| DELETE | `/api/messages/<id>`   | 删除指定记录                                                     |

创建成功的记录形如：

```json
{"id": 1, "message": "请用一句话介绍北京大学", "reply": "……"}
```

出错时统一返回带 `error` 字段的 JSON：

- `400`：请求体不是合法 JSON，或 `message` 为空；
- `404`：指定 `id` 的记录不存在；
- `502`：调用 DeepSeek 失败（未配置 Key、网络错误、接口报错等）。

## 最简单的 API 测试

服务启动后，在另一个终端中执行：

```bash
# 连通性测试
curl http://localhost:5001/api/hello

# 创建一条聊天记录（会真实调用 DeepSeek）
curl -X POST http://localhost:5001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'

# 查看全部记录
curl http://localhost:5001/api/messages

# 修改 id 为 1 的记录
curl -X PATCH http://localhost:5001/api/messages/1 \
  -H "Content-Type: application/json" \
  -d '{"message":"修改后的内容"}'

# 删除 id 为 1 的记录
curl -X DELETE http://localhost:5001/api/messages/1
```

## 选做功能

两个选做任务均未实现：

- JSON 文件持久化：未实现，聊天记录只保存在内存中；
- 多会话与多轮对话：未实现，每次问答相互独立，模型不会获得该会话的历史上下文。
