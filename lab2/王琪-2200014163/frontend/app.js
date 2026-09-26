// 本阶段只包含页面结构相关的最小脚本，暂不调用后端或第三方 API。
// 后续会在这里通过 fetch() 调用 Flask 后端接口，并实现聊天记录的增删改查。

const messageForm = document.getElementById("message-form");

if (messageForm) {
  messageForm.addEventListener("submit", (event) => {
    // 暂时不做任何处理，避免页面刷新；后续会在这里发送消息。
    event.preventDefault();
  });
}
