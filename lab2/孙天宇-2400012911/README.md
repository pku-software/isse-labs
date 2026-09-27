# AI 聊天 Web 应用

基于 HTML、CSS、JavaScript 和 Python Flask 的聊天应用。浏览器通过 Flask API 操作问答记录，Flask 调用 DeepSeek 生成回复，并将记录持久化到本机 JSON 文件。

## 项目功能

- 创建、查看、修改和删除问答记录。
- 修改提问时保留原回复；需要生成新回复时，重新发送问题。
- 编辑、删除确认、操作状态和错误提示均显示在页面内。
- 使用 DeepSeek `deepseek-flash` 生成回复，API Key 仅由后端加载。
- 支持 JSON 持久化，重启后可恢复已保存的问答。
- 当前为单个问答列表，每次模型调用只携带本次提问，不携带历史上下文；未提供多个会话管理功能。

## 安装依赖

需要 Python 3 和 pip。以下命令适用于 macOS 或 Linux。在仓库根目录进入个人项目，先将路径占位文字替换为自己的目录名：

```bash
cd "lab2/<姓名>-<学号>"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

依赖包括 Flask、python-dotenv 和 requests。已有虚拟环境时，只需激活环境并安装依赖。

## 环境配置

在 [DeepSeek 开放平台](https://platform.deepseek.com/)创建 API Key。首次配置时，将项目根目录中的 `.env.example` 复制为同目录下的 `.env`；已有 `.env` 时保留现有配置。编辑 `.env`，将示例值替换为自己的真实 Key：

```dotenv
DEEPSEEK_API_KEY=your_api_key_here
```

`.env` 被 `.gitignore` 忽略，不要将它加入 Git 或把真实 Key 写入前端、源码和对话记录。`.env.example` 仅含占位值，可以提交。

后端通过 `load_dotenv()` 加载与 `app.py` 同目录的 `.env`，再通过 `os.getenv("DEEPSEEK_API_KEY")` 取得配置。已有同名进程环境变量时优先使用该环境变量。修改 Key 后请重新启动 Flask。

## 启动方式

在个人项目目录中激活环境并运行：

```bash
source .venv/bin/activate
python app.py
```

浏览器访问 <http://localhost:5001/>。Flask 同时提供页面、静态资源和 API。运行期间保持终端打开；按 Ctrl+C 停止服务，再执行 `python app.py` 可重新启动。程序启用调试模式，用于本地开发。

## API 用法

API 基础地址为 `http://localhost:5001`，请求和响应采用 JSON。创建和修改时设置 `Content-Type: application/json`。

| 方法与路径 | 功能 | 成功响应 |
| --- | --- | --- |
| `GET /api/hello` | 检查服务响应 | `200`，包含 `message` |
| `POST /api/messages` | 接收提问，调用 DeepSeek，保存问答 | `201`，返回完整问答对象 |
| `GET /api/messages` | 获取全部记录 | `200`，返回问答对象数组 |
| `PATCH /api/messages/<id>` | 修改对应记录的提问，保留原回复 | `200`，返回更新后的完整对象 |
| `DELETE /api/messages/<id>` | 删除整条问答 | `200`，返回 `id` 和操作说明 `message` |

创建和修改接口接收：

```json
{"message": "请用一句话介绍北京大学"}
```

创建和查看时，每条问答包含 `id`、`message`、`reply`。`message` 必须是非空字符串；非法请求体返回 `400`，指定记录不存在时返回 `404`。保存失败返回 `500`；模型调用或响应异常返回 `502`，Key 缺失、限流或服务繁忙返回 `503`，模型请求超时返回 `504`。错误响应使用 `{"error": "错误说明"}` 格式。

### 最简单的接口测试

保持 Flask 运行，在另一个终端执行：

```bash
curl http://localhost:5001/api/hello
```

应返回 `{"message":"你好"}`。验证真实模型回复：

```bash
curl -X POST http://localhost:5001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

这一请求会调用 DeepSeek；成功时返回的 `reply` 为模型实际生成的内容。查看已有记录：

```bash
curl http://localhost:5001/api/messages
```

下面两个命令中的 `<id>` 需替换为实际返回的记录 ID。修改只改变提问，删除会移除该条问答：

```bash
curl -X PATCH "http://localhost:5001/api/messages/<id>" \
  -H "Content-Type: application/json" \
  -d '{"message":"修改后的问题"}'

curl -X DELETE "http://localhost:5001/api/messages/<id>"
```

浏览器验证时，可发送问题、刷新页面、修改提问和确认删除，观察对应的问答是否更新。

## 数据保存

聊天记录保存在项目目录下的 `data/messages.json`，文件路径相对于 `app.py` 确定，不受启动命令所在目录影响。应用使用单个 Flask 进程，在启动时加载已有记录。

JSON 文件最外层为数组，每个对象代表一次完整问答：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `id` | 正整数 | 聊天记录的唯一标识 |
| `message` | 字符串 | 用户提问 |
| `reply` | 字符串 | DeepSeek 生成的回复 |

创建记录时追加对象；修改提问时只更新对应记录的 `message`，保留原回复；删除时移除整条问答。上述操作成功时都会写回文件。查看记录不会改写文件。

文件不存在或为空时，应用从空记录开始，首次保存时自动创建数据目录与文件。启动时，新记录 ID 从已有最大 ID 之后继续分配。停止并重新启动 Flask 后，刷新网页即可加载已保存的记录。

写入使用同目录临时文件，完成后再替换原文件；写入失败时，接口返回错误，本次内存记录变更不生效。如果已有文件不是有效 JSON，或记录结构、ID 不合法，应用会停止启动并提示修复，保留原文件。
