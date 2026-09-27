# AI 聊天 Web 应用

一个基于 Flask 与原生 HTML、CSS、JavaScript 构建的 AI 聊天 Web 应用。

## 数据持久化

聊天记录保存在 `data/messages.json` 中，最外层是一个数组，每个元素结构如下：

```json
{
  "id": 1,
  "message": "用户输入",
  "reply": "模型回复"
}
```
