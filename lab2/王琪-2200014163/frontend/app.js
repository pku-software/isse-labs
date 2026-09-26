const messagesEl = document.getElementById("messages");
const errorEl = document.getElementById("error");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");

function showError(text) {
  errorEl.textContent = text;
  errorEl.hidden = false;
}

function clearError() {
  errorEl.textContent = "";
  errorEl.hidden = true;
}

async function request(url, options) {
  const res = await fetch(url, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `请求失败 (${res.status})`);
  }
  return data;
}

async function loadMessages() {
  try {
    const messages = await request("/api/messages");
    render(messages);
    clearError();
  } catch (err) {
    showError(err.message);
  }
}

function render(messages) {
  messagesEl.innerHTML = "";
  if (messages.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "暂无聊天记录";
    messagesEl.appendChild(empty);
    return;
  }
  for (const m of messages) {
    messagesEl.appendChild(buildMessage(m));
  }
}

function buildMessage(m) {
  const item = document.createElement("div");
  item.className = "message";
  item.dataset.id = m.id;

  const userRow = document.createElement("div");
  userRow.className = "user-row";

  const userBubble = document.createElement("div");
  userBubble.className = "bubble user-bubble";
  userBubble.textContent = m.message;

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const editBtn = document.createElement("button");
  editBtn.type = "button";
  editBtn.className = "action-button edit-button";
  editBtn.textContent = "修改";

  const deleteBtn = document.createElement("button");
  deleteBtn.type = "button";
  deleteBtn.className = "action-button delete-button";
  deleteBtn.textContent = "删除";

  actions.appendChild(editBtn);
  actions.appendChild(deleteBtn);

  userRow.appendChild(userBubble);
  userRow.appendChild(actions);

  const replyBubble = document.createElement("div");
  replyBubble.className = "bubble reply-bubble";
  replyBubble.textContent = m.reply;

  item.appendChild(userRow);
  item.appendChild(replyBubble);

  editBtn.addEventListener("click", () => beginEdit(item, m));
  deleteBtn.addEventListener("click", () => beginDelete(item, m));

  return item;
}

function beginEdit(item, m) {
  const userBubble = item.querySelector(".user-bubble");
  const actions = item.querySelector(".message-actions");

  const editor = document.createElement("div");
  editor.className = "edit-editor";

  const input = document.createElement("input");
  input.type = "text";
  input.className = "edit-input";
  input.value = m.message;

  const saveBtn = document.createElement("button");
  saveBtn.type = "button";
  saveBtn.className = "action-button save-button";
  saveBtn.textContent = "保存";

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.className = "action-button cancel-button";
  cancelBtn.textContent = "取消";

  editor.appendChild(input);
  editor.appendChild(saveBtn);
  editor.appendChild(cancelBtn);

  userBubble.replaceWith(editor);
  actions.hidden = true;

  const restore = () => {
    editor.replaceWith(userBubble);
    actions.hidden = false;
  };

  cancelBtn.addEventListener("click", restore);

  saveBtn.addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) {
      showError("修改内容不能为空");
      return;
    }
    try {
      await request(`/api/messages/${m.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      await loadMessages();
    } catch (err) {
      showError(err.message);
    }
  });
}

function beginDelete(item, m) {
  const actions = item.querySelector(".message-actions");

  const confirmWrap = document.createElement("div");
  confirmWrap.className = "delete-confirm";

  const label = document.createElement("span");
  label.textContent = "确认删除？";

  const confirmBtn = document.createElement("button");
  confirmBtn.type = "button";
  confirmBtn.className = "action-button confirm-delete-button";
  confirmBtn.textContent = "确认";

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.className = "action-button cancel-button";
  cancelBtn.textContent = "取消";

  confirmWrap.appendChild(label);
  confirmWrap.appendChild(confirmBtn);
  confirmWrap.appendChild(cancelBtn);

  actions.replaceWith(confirmWrap);

  cancelBtn.addEventListener("click", () => {
    confirmWrap.replaceWith(actions);
  });

  confirmBtn.addEventListener("click", async () => {
    try {
      await request(`/api/messages/${m.id}`, { method: "DELETE" });
      await loadMessages();
    } catch (err) {
      showError(err.message);
    }
  });
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    showError("请输入消息内容");
    return;
  }
  try {
    await request("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    messageInput.value = "";
    await loadMessages();
  } catch (err) {
    showError(err.message);
  }
});

loadMessages();
