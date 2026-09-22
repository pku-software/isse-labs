# AI 聊天 Web 应用

一个使用 HTML、CSS、JavaScript 和 Flask 构建的 AI 聊天 Web 应用。

## 功能

- 创建、查看、切换、重命名和删除聊天会话；
- 在每个会话中进行多轮 AI 对话；
- 修改或删除会话内的一轮问答；
- 由 Flask 后端安全调用 DeepSeek API，API Key 不进入浏览器。

## 安装依赖

待补充。

## 配置

待补充。

## 启动方式

待补充。

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

### 数据结构

每个 conversation 包含唯一 `id`、`title` 和 `messages` 数组。数组中的每条消息包含唯一 `id`、所属轮次 `turn_id`、角色 `role` 和文本 `content`。`role` 为 `user` 时表示用户消息，为 `assistant` 时表示模型回复。

调用 DeepSeek 时，后端按顺序取出当前 conversation 的全部历史消息，转换为由 `role` 和 `content` 组成的 `messages` 数组，再把本次新问题作为最后一条 `user` 消息加入。其他 conversation 的内容不会进入本次请求。
