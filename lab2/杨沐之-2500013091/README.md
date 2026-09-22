# AI 聊天 Web 应用

一个使用 HTML、CSS、JavaScript 和 Flask 构建的 AI 聊天 Web 应用。

## 功能

- 创建、查看、切换、重命名和删除聊天会话；
- 在每个会话中进行多轮 AI 对话；
- 修改或删除会话内的一轮问答；
- 使用 JSON 文件持久化会话，Flask 重启后仍可恢复数据；
- 由 Flask 后端安全调用 DeepSeek API，API Key 不进入浏览器。

## 安装依赖

建议使用 Python 3.9 或更高版本。在项目目录中运行：

```powershell
python -m pip install -r requirements.txt
```

## 配置

复制示例配置文件：

```powershell
Copy-Item .env.example .env
```

然后编辑本地 `.env`，将示例值替换为自己的 DeepSeek API Key：

```dotenv
DEEPSEEK_API_KEY=你的真实APIKey
```

`.env` 已被 Git 忽略，不应提交、分享或写入前端代码；`.env.example` 只保留示例值。

## 启动方式

在项目目录中启动 Flask：

```powershell
python app.py
```

服务监听 `5001` 端口。启动后访问：

```text
http://localhost:5001/
```

## API

### 会话 API

- `POST /api/conversations`：创建会话；
- `GET /api/conversations`：获取会话摘要列表；
- `GET /api/conversations/<id>`：获取一个会话及其消息；
- `PATCH /api/conversations/<id>`：重命名会话；
- `DELETE /api/conversations/<id>`：删除会话；
- `POST /api/conversations/<id>/messages`：在指定会话中发送消息；
- `PATCH /api/conversations/<id>/turns/<turn_id>`：修改一轮对话中的用户消息；
- `DELETE /api/conversations/<id>/turns/<turn_id>`：删除一轮用户消息和 AI 回复。

### 基础 API

- `GET /api/hello`：返回中文问候，用于检查 Flask 是否可用；
- `POST /api/messages`：创建一条独立问答记录；
- `GET /api/messages`：获取当前进程中的独立问答记录；
- `PATCH /api/messages/<id>`：修改一条独立问答记录的用户消息；
- `DELETE /api/messages/<id>`：删除一条独立问答记录。

### 数据结构

每个 conversation 包含唯一 `id`、`title` 和 `messages` 数组。数组中的每条消息包含唯一 `id`、所属轮次 `turn_id`、角色 `role` 和文本 `content`。`role` 为 `user` 时表示用户消息，为 `assistant` 时表示模型回复。

调用 DeepSeek 时，后端按顺序取出当前 conversation 的全部历史消息，转换为由 `role` 和 `content` 组成的 `messages` 数组，再把本次新问题作为最后一条 `user` 消息加入。其他 conversation 的内容不会进入本次请求。

## 数据持久化

会话数据保存在 `data/conversations.json`。文件最外层是一个 JSON 对象，其中 `conversations` 字段是会话数组；每个会话对象内部的 `messages` 字段保存按顺序排列的用户和 AI 消息。

Flask 启动时读取该文件，并根据已有数据计算后续会话、消息和轮次 ID。创建、重命名或删除会话，以及新增、修改或删除消息后，后端都会立即把最新数据写回文件，因此 Flask 重启后可以恢复会话和聊天内容。

## 简单 API 测试

确认服务已经启动后，可在 PowerShell 中检查问候接口：

```powershell
curl.exe http://localhost:5001/api/hello
```

创建一个会话：

```powershell
curl.exe -X POST http://localhost:5001/api/conversations -H "Content-Type: application/json" -d '{\"title\":\"测试会话\"}'
```

根据创建结果中的会话 ID 发送消息。下面以会话 ID `1` 为例：

```powershell
curl.exe -X POST http://localhost:5001/api/conversations/1/messages -H "Content-Type: application/json" -d '{\"message\":\"请用一句话介绍北京大学\"}'
```

该请求会调用 DeepSeek API，响应中包含当前会话的完整消息列表。
