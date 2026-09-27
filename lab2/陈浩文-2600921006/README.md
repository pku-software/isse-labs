# AI 聊天 Web 应用

基于 HTML、CSS、JavaScript 和 Python Flask 的 AI 聊天 Web 项目。

## 项目功能

- 在同一个 Flask 服务中提供聊天页面和 JSON API，浏览器使用相对 URL 与后端通信。
- 由 Flask 调用 DeepSeek 获得真实 AI 回复，API Key 只由后端读取。
- 以一次问题和回答为一条记录，支持创建、查看、修改问题和删除记录；修改问题不重新生成已有回答。
- 支持创建、切换、重命名和删除多个会话，每个会话独立维护聊天历史并支持连续追问。
- 使用 JSON 文件保存会话与聊天记录，重启 Flask 后可以恢复。
- 修改输入、删除确认、请求状态和错误提示均显示在页面内。

## 环境与依赖

使用 Python 3.12、uv 和现代浏览器。所有命令均在包含 `app.py` 的项目根目录执行；以下命令适用于 macOS / Linux。

创建虚拟环境并安装依赖：

```bash
uv venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
```

依赖包括 Flask、python-dotenv 和用于调用 DeepSeek 兼容接口的 OpenAI Python SDK。前端使用原生 HTML、CSS 和 JavaScript，无需 Node.js 或构建步骤。

## 配置

在 [DeepSeek 开放平台](https://platform.deepseek.com/) 创建 API Key。将项目根目录的 `.env.example` 复制为同目录下的 `.env`，把其中的示例值替换为自己的 Key：

```dotenv
DEEPSEEK_API_KEY=your_api_key_here
```

`.env.example` 只保留示例值，供其他使用者了解配置项；真实 `.env` 已由 `.gitignore` 忽略，不应加入版本控制。后端会自动读取与 `app.py` 同目录的 `.env`。修改配置后需要重启 Flask，前端无需配置 API Key。

## 启动方式

在项目根目录启动本地开发服务：

```bash
uv run --no-project --python .venv/bin/python python app.py
```

保持该终端运行，在浏览器访问 [http://localhost:5001/](http://localhost:5001/)。Flask 监听端口 5001 并开启调试模式，同时提供前端页面、静态资源和 API；通过 Flask 地址访问页面即可使用聊天功能。

在左侧建立或选择会话，再输入问题并发送。等待回复后，可继续追问、修改或删除问答记录，也可以重命名或删除当前会话。停止服务时，在运行 Flask 的终端按 `Ctrl+C`；再次运行相同命令即可启动并加载已保存的数据。

## API 用法

所有 API 返回 JSON。下表中的 `conversation_id` 是会话 ID，`message_id` 是一次问答记录的 ID；前端使用相对 URL 访问同一个 Flask 服务。

| 方法 | 路径 | 请求体与结果 |
| --- | --- | --- |
| GET | `/api/hello` | 返回 `{"message":"你好"}`。 |
| GET | `/api/conversations` | 返回会话摘要数组，每项包含 `id`、`title`、`message_count`。 |
| POST | `/api/conversations` | 传入 `{"title":"会话名称"}`，创建空会话并返回完整会话，状态码为 201。 |
| GET | `/api/conversations/<conversation_id>` | 返回该会话及其中的全部问答记录。 |
| PATCH | `/api/conversations/<conversation_id>` | 传入 `{"title":"新名称"}`，返回更名后的完整会话。 |
| DELETE | `/api/conversations/<conversation_id>` | 删除会话及其中的全部记录，返回 `{"id":1,"deleted":true}`，其中 `id` 为被删除会话的 ID。 |
| GET | `/api/conversations/<conversation_id>/messages` | 返回该会话的问答记录数组。 |
| POST | `/api/conversations/<conversation_id>/messages` | 传入 `{"message":"新问题"}`，调用 DeepSeek 后返回新问答记录，状态码为 201。 |
| PATCH | `/api/conversations/<conversation_id>/messages/<message_id>` | 传入 `{"message":"修改后的问题"}`，只更新问题并返回问答记录，原有回答保持不变。 |
| DELETE | `/api/conversations/<conversation_id>/messages/<message_id>` | 删除指定问答记录，返回 `{"id":1,"deleted":true}`，其中 `id` 为被删除记录的 ID。 |

保留兼容接口 `GET /api/messages`、`POST /api/messages`、`PATCH /api/messages/<message_id>` 和 `DELETE /api/messages/<message_id>`，请求体与对应的会话内接口相同。这些接口固定操作 ID 为 1 的会话；如果该会话已被删除，则返回 404。前端使用带有明确会话 ID 的接口。

`title` 和 `message` 必须是去除首尾空白后非空的字符串，`title` 最多 80 个字符。错误响应统一为 `{"error":"错误说明"}`；无效输入返回 400，资源不存在返回 404，生成回复期间聊天历史改变返回 409，文件保存失败返回 500，模型调用或配置问题返回 502、503 或 504。

## 简单 API 测试

保持 Flask 运行，在另一个终端执行：

```bash
curl http://localhost:5001/api/hello
```

预期返回 `{"message":"你好"}`，此请求不调用模型。接着创建一个测试会话：

```bash
curl -X POST http://localhost:5001/api/conversations \
  -H 'Content-Type: application/json' \
  -d '{"title":"API 测试"}'
```

响应包含新会话的 `id`、`title` 和空的 `messages` 数组。将下面的 `2` 替换为实际返回的会话 ID，再发送问题：

```bash
chat_conversation_id=2
curl -X POST "http://localhost:5001/api/conversations/$chat_conversation_id/messages" \
  -H 'Content-Type: application/json' \
  -d '{"message":"请用一句话介绍北京大学"}'
```

成功时返回包含 `id`、`message`、`reply` 的问答记录，`reply` 是模型生成的文本。这一步需要有效的后端 Key、可用余额和网络连接。在同一终端查看该会话的全部内容：

```bash
curl "http://localhost:5001/api/conversations/$chat_conversation_id"
```

浏览器刷新后也能看到这个会话和问答记录。请求失败时，读取响应中的 `error` 说明；认证或配置错误需检查本地 `.env` 并重启服务，余额不足需检查平台账户，超时或限流可稍后重试。

## 会话与 JSON 数据保存

当前数据保存在项目根目录下的 `data/conversations.json`，使用 UTF-8 编码。文件最外层为数组，每个对象代表一个会话，包含唯一正整数 `id`、会话名称 `title` 和问答记录数组 `messages`。每条问答记录包含全局唯一的正整数 `id`、用户问题 `message` 和模型回答 `reply`。示例结构：

```json
[
  {
    "id": 1,
    "title": "默认会话",
    "messages": [
      {
        "id": 1,
        "message": "示例问题",
        "reply": "示例回复"
      }
    ]
  }
]
```

- Flask 启动时读取 `data/conversations.json`；文件为空或内容为 `[]` 时，从空会话列表开始。
- 当 `data/conversations.json` 不存在时，应用将旧版 `data/messages.json` 中的记录导入 ID 为 1 的默认会话，并创建新的数据文件；旧文件保留。如果旧文件也不存在或为空，则创建一个没有问答记录的默认会话。
- 新文件创建后，后续读写都使用 `data/conversations.json`。删除全部会话会保存 `[]`，重启时不会重新导入旧记录。
- 新建、更名、删除会话，或新增、修改、删除问答记录后，保存当前全部会话。保存成功后才更新内存并返回成功响应。
- 保存时先写入同目录的临时文件，再替换正式文件；写入失败时 API 返回 JSON 错误。
- 删除会话或记录不会使其他项目重新编号；重启时分别从已保存的最大会话 ID、最大问答记录 ID 加一开始分配，避免与现有数据冲突。
- 修改只更新用户消息，保留原有模型回复；发送新消息才会调用模型。

## 多轮对话上下文

发送新问题时，Flask 只取当前会话的历史记录，按原有顺序将每条记录拆为 `user` 问题和 `assistant` 回答，再把当前的新问题追加为最后一条 `user` 消息，组成发给 DeepSeek 的 `messages` 数组。例如：

```json
[
  {"role": "user", "content": "请用一句话介绍木星。"},
  {"role": "assistant", "content": "木星是太阳系中最大的行星。"},
  {"role": "user", "content": "我刚才问的是哪颗行星？"}
]
```

其他会话的记录不会加入这次请求。当前实现发送该会话的全部历史，不做截断或摘要；历史过长、超过模型上下文限制时，请创建新会话。修改或删除历史记录会影响后续请求的上下文，但不会重新生成已有回答。

后端通过 `https://api.deepseek.com` 调用 `deepseek-flash`，使用非流式响应并关闭思考模式。模型名和 `messages` 等生成参数由后端设置；API Key 由后端环境变量读取并交给 SDK 用于请求认证，不放入聊天记录或返回给前端。
