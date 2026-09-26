# AI 聊天 Web 应用

一个最小但完整的 AI 聊天 Web 应用：前端使用 HTML + CSS + JavaScript，后端使用 Python + Flask，
后端调用 DeepSeek API 生成回复，聊天记录支持创建、读取、修改和删除。

## 功能

- 在浏览器里与 DeepSeek 模型对话，回复由模型实时生成；
- 新建、重命名、删除会话，并在多个会话之间切换；
- 每个会话独立保存自己的多轮对话历史，切换回来后可以接着之前的话题继续聊；
- 每一轮问答都可以单独修改或删除；
- 会话和对话写入本地 JSON 文件，Flask 重启后数据仍然存在；
- 前端不使用 `alert()`、`prompt()`、`confirm()` 等弹窗，输入、确认和提示都在页面内完成。

## 环境与依赖

## 配置

## 启动方式

## API 说明

### 会话

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| `POST` | `/api/conversations` | 新建会话，请求体可省略，也可带 `{"title": "..."}` |
| `GET` | `/api/conversations` | 列出全部会话，每项含 `id`、`title`、`turn_count` |
| `GET` | `/api/conversations/<id>` | 读取某个会话的完整内容 |
| `PATCH` | `/api/conversations/<id>` | 重命名会话，请求体 `{"title": "..."}` |
| `DELETE` | `/api/conversations/<id>` | 删除会话及其全部对话 |

### 会话里的问答

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| `POST` | `/api/conversations/<id>/messages` | 在当前会话里提问，返回更新后的会话 |
| `PATCH` | `/api/conversations/<id>/turns/<turn_id>` | 修改某一轮问答的提问内容 |
| `DELETE` | `/api/conversations/<id>/turns/<turn_id>` | 删除某一轮问答 |

### 兼容接口

以下四个接口作用在“默认会话”上（没有会话时自动新建一个），路径和返回结构与单会话版本保持一致：

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| `POST` | `/api/messages` | 在默认会话里新增一轮问答，返回这一轮记录 |
| `GET` | `/api/messages` | 返回默认会话里的全部问答记录 |
| `PATCH` | `/api/messages/<id>` | 修改默认会话里某一轮问答的提问 |
| `DELETE` | `/api/messages/<id>` | 删除默认会话里某一轮问答 |

### 接口错误约定

请求体格式不对返回 `400`，指定的会话或问答不存在返回 `404`，DeepSeek 调用失败返回 `502`，响应体都是 `{"error": "..."}` 形式的 JSON，前端会把 `error` 的内容显示在页面底部的状态行里。

## 数据存储

会话和对话保存在项目目录下的 JSON 文件中，路径是 `data/conversations.json`（即 `lab2/<姓名>-<学号>/data/conversations.json`）。

文件最外层是一个数组，每个元素是一个会话：

```json
[
  {
    "id": 1,
    "title": "会话标题",
    "turns": [
      {
        "id": 1,
        "message": "用户的提问",
        "reply": "模型返回的回复"
      }
    ]
  }
]
```

- conversation 的 `id`：整数，由后端生成，在会话之间唯一；
- conversation 的 `title`：会话名称，可以重命名；
- conversation 的 `turns`：这个会话里的多轮问答；
- turn 的 `id`：整数，在同一个会话内唯一；
- turn 的 `message`：用户输入的问题；
- turn 的 `reply`：模型返回的回复文本。

后端启动时会读取该文件并把内容还原成内存中的列表；每次新建、修改或删除会话或问答之后，都会把当前完整数据重新写回文件（整体覆盖，不是追加）。文件不存在、为空或内容损坏时，服务会从空数据开始，不会启动失败。

## 传给 DeepSeek 的上下文

调用 DeepSeek 时，后端不会只发送这一次的新问题，而是把当前会话的历史一并带上。具体做法是把当前会话的 `turns` 展开成带 `role` 的数组，再加上新问题：

```json
{
  "model": "deepseek-chat",
  "messages": [
    { "role": "user", "content": "第一轮的提问" },
    { "role": "assistant", "content": "第一轮的回复" },
    { "role": "user", "content": "这一轮的新提问" }
  ],
  "stream": false
}
```

模型接口本身不保存任何对话状态，它只能看到本次请求里的 `messages`。带上当前会话的历史，模型才能接着上下文中回答（比如记住前面提到的信息）；只带当前会话的历史，则保证不同会话之间不会互相影响。

## API 测试示例

## 选做功能

两个选做任务都已完成：

1. **JSON 文件持久化**：会话和对话保存在 `data/conversations.json`，写入与读取规则见上面的“数据存储”；
2. **多个聊天会话**：支持新建、重命名、删除、切换会话，并且每个会话独立维护自己的多轮上下文，数据结构、接口设计和上下文组成分别见“数据存储”“API 说明”和“传给 DeepSeek 的上下文”。
