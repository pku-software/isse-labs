// 前端交互逻辑：所有数据操作都通过调用后端 API 完成

const chatArea = document.getElementById("chat-area");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const statusBar = document.getElementById("status-bar");

// 在页面底部显示一条提示（成功为绿色、错误为红色），3 秒后自动消失
function showStatus(text, isError) {
  statusBar.textContent = text;
  statusBar.className = isError ? "status status-error" : "status status-ok";
  setTimeout(() => {
    statusBar.textContent = "";
    statusBar.className = "status";
  }, 3000);
}

// 创建一条聊天记录的 DOM 元素
function createRecordElement(msg) {
  const article = document.createElement("article");
  article.className = "chat-record";
  article.dataset.id = msg.id;

  const body = document.createElement("div");
  body.className = "record-body";

  const messageDiv = document.createElement("div");
  messageDiv.className = "record-message";
  messageDiv.textContent = msg.message;

  const replyDiv = document.createElement("div");
  replyDiv.className = "record-reply";
  replyDiv.textContent = msg.reply;

  body.appendChild(messageDiv);
  body.appendChild(replyDiv);

  const actions = document.createElement("div");
  actions.className = "record-actions";

  const editBtn = document.createElement("button");
  editBtn.className = "btn-edit";
  editBtn.type = "button";
  editBtn.textContent = "修改";
  editBtn.addEventListener("click", () => startEdit(article, msg));

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "btn-delete";
  deleteBtn.type = "button";
  deleteBtn.textContent = "删除";
  deleteBtn.addEventListener("click", () => startDelete(article, msg));

  actions.appendChild(editBtn);
  actions.appendChild(deleteBtn);

  article.appendChild(body);
  article.appendChild(actions);
  return article;
}

// 把全部聊天记录渲染到聊天区
function renderMessages(messages) {
  chatArea.innerHTML = "";
  if (messages.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-tip";
    empty.textContent = "还没有聊天记录，发送一条消息吧～";
    chatArea.appendChild(empty);
    return;
  }
  for (const msg of messages) {
    chatArea.appendChild(createRecordElement(msg));
  }
}

// 加载全部聊天记录：GET /api/messages
async function loadMessages() {
  try {
    const res = await fetch("/api/messages");
    if (!res.ok) {
      throw new Error("HTTP " + res.status);
    }
    const messages = await res.json();
    renderMessages(messages);
  } catch (e) {
    showStatus("加载记录失败：" + e.message, true);
  }
}

// 发送消息：POST /api/messages
async function sendMessage(text) {
  try {
    const res = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    if (!res.ok) {
      const err = await res.json();
      showStatus("发送失败：" + (err.error || res.status), true);
      return;
    }
    showStatus("发送成功");
    messageInput.value = "";
    await loadMessages();
  } catch (e) {
    showStatus("网络错误：" + e.message, true);
  }
}

// 点击“修改”：把消息内容替换为页面内的编辑框（输入框 + 保存/取消）
function startEdit(article, msg) {
  const body = article.querySelector(".record-body");

  const editBox = document.createElement("div");
  editBox.className = "edit-box";

  const input = document.createElement("input");
  input.type = "text";
  input.value = msg.message;

  const saveBtn = document.createElement("button");
  saveBtn.type = "button";
  saveBtn.textContent = "保存";

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.textContent = "取消";

  const errorTip = document.createElement("span");
  errorTip.className = "inline-error";

  editBox.appendChild(input);
  editBox.appendChild(saveBtn);
  editBox.appendChild(cancelBtn);
  editBox.appendChild(errorTip);

  // 用编辑框替换原内容
  body.replaceChildren(editBox);

  saveBtn.addEventListener("click", async () => {
    const newMessage = input.value.trim();
    if (!newMessage) {
      errorTip.textContent = "内容不能为空";
      return;
    }
    try {
      const res = await fetch(`/api/messages/${msg.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newMessage })
      });
      if (!res.ok) {
        const err = await res.json();
        errorTip.textContent = "修改失败：" + (err.error || res.status);
        return;
      }
      showStatus("修改成功");
      await loadMessages();
    } catch (e) {
      errorTip.textContent = "网络错误：" + e.message;
    }
  });

  cancelBtn.addEventListener("click", loadMessages);
}

// 点击“删除”：按钮变为“确认删除/取消”，确认后才真正请求删除
function startDelete(article, msg) {
  const actions = article.querySelector(".record-actions");
  actions.innerHTML = "";

  const confirmBtn = document.createElement("button");
  confirmBtn.className = "btn-delete-confirm";
  confirmBtn.type = "button";
  confirmBtn.textContent = "确认删除";

  const cancelBtn = document.createElement("button");
  cancelBtn.className = "btn-delete-cancel";
  cancelBtn.type = "button";
  cancelBtn.textContent = "取消";

  const errorTip = document.createElement("span");
  errorTip.className = "inline-error";

  actions.appendChild(confirmBtn);
  actions.appendChild(cancelBtn);
  actions.appendChild(errorTip);

  confirmBtn.addEventListener("click", async () => {
    try {
      const res = await fetch(`/api/messages/${msg.id}`, { method: "DELETE" });
      if (!res.ok) {
        const err = await res.json();
        errorTip.textContent = "删除失败：" + (err.error || res.status);
        return;
      }
      showStatus("删除成功");
      await loadMessages();
    } catch (e) {
      errorTip.textContent = "网络错误：" + e.message;
    }
  });

  cancelBtn.addEventListener("click", loadMessages);
}

// 提交表单：发送消息
chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    showStatus("请输入消息内容", true);
    return;
  }
  sendMessage(text);
});

// 页面打开时加载已有记录
loadMessages();
