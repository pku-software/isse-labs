// 本阶段前端只负责渲染页面结构，不调用后端或第三方 API。

const PLACEHOLDER_MESSAGES = [
  {
    id: 1,
    message: "你好，我想了解一下这个应用。",
    reply: "你好！这是一条示例回复，用来展示聊天记录的样式。",
  },
  {
    id: 2,
    message: "每条记录都带有修改和删除入口。",
    reply: "它们现在还没有实际效果，等后端接通后才会真正生效。",
  },
];

function renderMessages(messages) {
  const list = document.getElementById("message-list");
  list.textContent = "";

  messages.forEach((item) => {
    const wrapper = document.createElement("article");
    wrapper.className = "message";
    wrapper.dataset.id = item.id;

    const userBubble = document.createElement("p");
    userBubble.className = "bubble bubble-user";
    userBubble.textContent = item.message;

    const replyBubble = document.createElement("p");
    replyBubble.className = "bubble bubble-reply";
    replyBubble.textContent = item.reply;

    const actions = document.createElement("div");
    actions.className = "message-actions";

    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "link-button";
    editButton.textContent = "修改";

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "link-button danger";
    deleteButton.textContent = "删除";

    actions.append(editButton, deleteButton);
    wrapper.append(userBubble, replyBubble, actions);
    list.appendChild(wrapper);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderMessages(PLACEHOLDER_MESSAGES);

  // 阻止表单默认提交导致的页面刷新；真实发送逻辑后续再接。
  document.getElementById("composer").addEventListener("submit", (event) => {
    event.preventDefault();
  });
});
