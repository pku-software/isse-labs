/**
 * 前端脚本。
 *
 * 当前阶段只完成页面结构和样式，这里暂时不调用后端 API，也不调用第三方 API，
 * 因此页面上的发送、修改、删除按钮点击后不会有任何效果。
 *
 * 后续会在这个文件中补上：
 * - 页面加载时通过 fetch("/api/messages") 读取历史记录
 * - 发送消息时通过 fetch("/api/messages", {method: "POST"}) 创建记录
 * - 修改记录时调用 PATCH /api/messages/<id>
 * - 删除记录时调用 DELETE /api/messages/<id>
 * - 把加载、错误和确认等状态反馈显示在页面元素里，而不是使用浏览器弹窗
 */
