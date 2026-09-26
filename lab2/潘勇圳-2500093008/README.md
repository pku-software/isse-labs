# AI 聊天 Web 应用

一个最小但完整的 AI 聊天应用：前端使用 HTML + CSS + JavaScript，后端使用 Python + Flask，由 Flask 调用 DeepSeek API 生成回复。

聊天以「会话」为单位组织，支持多个会话和多轮对话；聊天记录通过 RESTful API 完成创建、读取、修改和删除，并保存在 JSON 文件中。

## 功能

- 在浏览器中与 AI 对话，回复由 DeepSeek API 真实生成；
- 支持多个会话：可以新建、切换、重命名、删除会话，每个会话独立保存自己的消息；
- 在一个会话里连续追问时，模型能拿到该会话的历史消息作为上下文，不同会话的上下文互不影响；
- 每条消息都能修改（改用户消息内容）和删除；
- 聊天数据保存在 `data/conversations.json`，重启 Flask 后依然存在；
- API Key 只保存在后端的 `.env` 文件中，前端接触不到。

## 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 配置

先根据示例文件创建自己的 `.env`：

```bash
cp .env.example .env
```

再把里面的示例值换成自己的 DeepSeek API Key：

```
DEEPSEEK_API_KEY=你的真实APIKey
```

`.env` 已经被 `.gitignore` 忽略，不会进入版本库；`.env.example` 中只有示例值。

## 启动

```bash
python app.py
```

Flask 监听 5001 端口，调试模式下会自动重载。

## 浏览器访问

```
http://localhost:5001/
```

## API

### 会话

| 方法与路径 | 说明 |
| --- | --- |
| `GET /api/conversations` | 返回全部会话，每个会话里包含自己的消息 |
| `POST /api/conversations` | 新建会话，请求体 `{"title": "会话名"}`（可省略，默认「新会话」） |
| `GET /api/conversations/<id>` | 查看指定会话及其消息 |
| `PATCH /api/conversations/<id>` | 重命名会话，请求体 `{"title": "新名字"}` |
| `DELETE /api/conversations/<id>` | 删除会话，会话里的消息一并删除 |
| `POST /api/conversations/<id>/messages` | 在指定会话里发一条消息，请求体 `{"message": "内容"}` |

### 消息

| 方法与路径 | 说明 |
| --- | --- |
| `PATCH /api/messages/<id>` | 修改某条消息的用户内容，请求体 `{"message": "新内容"}` |
| `DELETE /api/messages/<id>` | 删除某条消息 |

### 其它

| 方法与路径 | 说明 |
| --- | --- |
| `GET /api/hello` | 最简单的探活接口，返回 `{"message": "你好"}` |
| `GET /api/messages` | 兼容入口，返回默认会话（第一个会话）中的全部消息 |
| `POST /api/messages` | 兼容入口，在默认会话中创建一条消息 |

所有错误都以 JSON 形式返回，例如 `{"error": "id 为 9 的会话不存在"}`，并配合合适的 HTTP 状态码（参数不合法为 400，找不到为 404，模型调用失败为 502）。

## 最简单的 API 测试

启动服务后，在另一个终端里执行：

```bash
# 探活
curl http://localhost:5001/api/hello

# 查看全部会话
curl http://localhost:5001/api/conversations

# 新建一个会话
curl -X POST http://localhost:5001/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"测试会话"}'

# 在会话 1 里发一条消息，回复由 DeepSeek 生成
curl -X POST http://localhost:5001/api/conversations/1/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

## 数据存储

聊天数据保存在项目目录下的：

```
data/conversations.json
```

文件最外层是一个 JSON 数组，每个元素是一个会话：

```json
[
  {
    "id": 1,
    "title": "会话名",
    "messages": [
      {
        "id": 1,
        "message": "用户输入的内容",
        "reply": "AI 回复的内容"
      }
    ]
  }
]
```

- Flask 启动时读取该文件，把会话加载回内存；文件不存在或内容不是合法 JSON 时，从空数据开始，不影响服务启动。
- 每次新建、重命名、删除会话，或新增、修改、删除消息后，内存中的整个数组都会重新写回文件。
- 会话 id 和消息 id 都从已有数据的最大 id 往后递增，重启后新增的数据不会和文件里的记录冲突。
- 不使用数据库。

## 传给 DeepSeek 的上下文

在某个会话里发消息时，Flask 会把**该会话已有的消息**按顺序还原，再把本次提问接在最后，一起发给 DeepSeek：

```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "user", "content": "上一轮用户说的话"},
    {"role": "assistant", "content": "上一轮 AI 的回复"},
    {"role": "user", "content": "本次用户输入"}
  ],
  "stream": false
}
```

历史只取当前会话，所以不同会话之间不会串上下文；模型返回的文本会作为新记录的 `reply` 保存。

## 选做功能

本项目已完成两个选做任务：

1. **JSON 文件持久化**：聊天数据写入 `data/conversations.json`，重启后仍可恢复，详见「数据存储」。
2. **多个聊天会话与多轮对话**：会话的增删改查、切换，以及带上下文的模型调用，详见「API」与「传给 DeepSeek 的上下文」。
