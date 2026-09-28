# AI 聊天 Web 应用

## 项目功能

这是一个使用 Flask 提供服务的 AI 聊天应用。浏览器中的前端通过同源 API 与 Flask 通信，Flask 调用 DeepSeek `deepseek-flash` 模型并管理聊天记录。聊天记录保存在本地 JSON 文件中，服务重启后可以恢复。

## 环境配置

需要 Python 3.10 或更高版本。进入个人项目目录后创建并启用虚拟环境，安装依赖：

```bash
cd "lab2/<姓名>-<学号>"
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

从示例文件创建本地配置：

```bash
cp .env.example .env
```

编辑 `.env`，将示例值替换为你自己的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=你的APIKey
```

`.env` 已加入 `.gitignore`，不要将真实 API Key 写入源代码或提交到 Git。

## 启动和访问

在个人项目目录中运行：

```bash
python app.py
```

浏览器访问 <http://localhost:5001/>。

## API

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `GET` | `/api/hello` | 返回问候 JSON |
| `POST` | `/api/messages` | 调用 DeepSeek 并创建一条问答记录 |
| `GET` | `/api/messages` | 读取全部问答记录 |
| `PATCH` | `/api/messages/<id>` | 修改指定记录的问题文本 |
| `DELETE` | `/api/messages/<id>` | 删除指定问答记录 |

创建记录时，请求体为 `{"message":"你的问题"}`。缺少问题或记录不存在时，API 会返回 JSON 错误和相应 HTTP 状态码。

## API 测试

在 Flask 服务运行时，可以在另一个终端测试问候接口和创建问答：

```bash
curl http://localhost:5001/api/hello

curl -X POST http://localhost:5001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

## 数据持久化

聊天记录保存在 `data/messages.json`。文件最外层是 JSON 数组，每条记录包含 `id`、`message` 和 `reply`。Flask 启动时读取该文件；创建记录会追加对象，修改会更新对应对象，删除会移除对应对象。每次变更都会写回文件，因此重启服务后仍可恢复记录。
