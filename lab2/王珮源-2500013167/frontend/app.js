// 前端脚本（当前阶段只有页面结构，没有任何网络请求）
//
// 后续阶段会在这里补充：
//   - 页面打开时用 GET /api/messages 加载并渲染已有记录
//   - 发送消息时用 POST /api/messages 创建记录
//   - 修改记录用 PATCH /api/messages/<id>，删除记录用 DELETE /api/messages/<id>
//   - 所有提示都写到页面内的 #status-text，不使用 alert()/prompt()/confirm()
//
// 但调用后端属于下一个阶段的任务，现在先保持空实现。

const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const statusText = document.getElementById("status-text");

// 暂时只拦掉表单默认的整页刷新，避免点击“发送”后页面跳转
chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  statusText.textContent = "当前阶段只有静态页面，还没有接入后端接口。";
});

// 消息输入框、修改和删除按钮本阶段都不绑定任何逻辑
messageInput.addEventListener("input", () => {
  statusText.textContent = "";
});
