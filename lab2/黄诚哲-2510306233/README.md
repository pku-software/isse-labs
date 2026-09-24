# AI 聊天 Web 应用

一个最小但完整的 AI 聊天 Web 应用：

- 前端使用 HTML + CSS + JavaScript；
- 后端使用 Python + Flask；
- 前端通过 `fetch()` 调用自己的 Flask API；
- Flask 后端调用 DeepSeek API 获得真实 AI 回复。

## 数据持久化

聊天记录保存在 `data/messages.json`。文件最外层是一个 JSON 数组，每个元素是一条记录：

```json
[
  {
    "id": 1,
    "message": "用户输入",
    "reply": "后端回复"
  }
]
```

每次创建、修改或删除记录后，后端都会把内存中的完整列表写回该文件；启动时再从这个文件读入内存，因此 Flask 重启后数据仍然保留。
