const conversationListEl = document.getElementById("conversation-list");
const newConversationBtn = document.getElementById("new-conversation");
const currentTitleEl = document.getElementById("current-title");
const renameBtn = document.getElementById("rename-button");
const deleteBtn = document.getElementById("delete-conversation");
const messagesEl = document.getElementById("messages");
const errorEl = document.getElementById("error");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");

let currentConversationId = null;
let sending = false;

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

async function loadConversations() {
  try {
    const conversations = await request("/api/conversations");
    renderConversationList(conversations);
    clearError();
  } catch (err) {
    showError(err.message);
  }
}

function renderConversationList(conversations) {
  conversationListEl.innerHTML = "";
  if (conversations.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "暂无会话";
    conversationListEl.appendChild(empty);
    return;
  }
  for (const conv of conversations) {
    const item = document.createElement("li");
    item.className = "conversation-item";
    item.dataset.id = conv.id;
    item.textContent = conv.title;
    if (conv.id === currentConversationId) {
      item.classList.add("active");
    }
    item.addEventListener("click", () => selectConversation(conv.id));
    conversationListEl.appendChild(item);
  }
}

async function selectConversation(id) {
  try {
    const conv = await request(`/api/conversations/${id}`);
    currentConversationId = id;
    currentTitleEl.textContent = conv.title;
    renameBtn.hidden = false;
    deleteBtn.hidden = false;
    renderMessages(conv.messages);
    await loadConversations();
    clearError();
  } catch (err) {
    showError(err.message);
  }
}

function renderMessages(messages) {
  messagesEl.innerHTML = "";
  if (messages.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "发送一条消息开始对话";
    messagesEl.appendChild(empty);
    return;
  }
  for (const m of messages) {
    messagesEl.appendChild(buildMessageElement(m));
  }
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function buildMessageElement(m) {
  const item = document.createElement("div");
  item.className = "message";
  item.dataset.id = m.id;

  const bubble = document.createElement("div");
  bubble.className = "bubble " + (m.role === "user" ? "user" : "assistant");
  bubble.textContent = m.content;

  if (m.role === "user") {
    const userRow = document.createElement("div");
    userRow.className = "user-row";

    const actions = document.createElement("div");
    actions.className = "message-actions";

    const editBtn = document.createElement("button");
    editBtn.type = "button";
    editBtn.className = "action-button";
    editBtn.textContent = "修改";

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = "action-button delete";
    deleteBtn.textContent = "删除";

    actions.appendChild(editBtn);
    actions.appendChild(deleteBtn);

    userRow.appendChild(bubble);
    userRow.appendChild(actions);
    item.appendChild(userRow);

    editBtn.addEventListener("click", () => beginEditMessage(userRow, m));
    deleteBtn.addEventListener("click", () => beginDeleteMessage(userRow, m));
  } else {
    item.appendChild(bubble);
  }

  return item;
}

function beginEditMessage(userRow, m) {
  const bubble = userRow.querySelector(".bubble");
  const actions = userRow.querySelector(".message-actions");

  const input = document.createElement("textarea");
  input.className = "edit-input";
  input.rows = 3;
  input.value = m.content;

  const buttons = document.createElement("div");
  buttons.className = "message-actions";

  const saveBtn = document.createElement("button");
  saveBtn.type = "button";
  saveBtn.className = "action-button";
  saveBtn.textContent = "保存";

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.className = "action-button";
  cancelBtn.textContent = "取消";

  buttons.appendChild(saveBtn);
  buttons.appendChild(cancelBtn);

  bubble.replaceWith(input);
  actions.replaceWith(buttons);

  const restore = () => {
    input.replaceWith(bubble);
    buttons.replaceWith(actions);
  };

  cancelBtn.addEventListener("click", restore);

  saveBtn.addEventListener("click", async () => {
    const content = input.value.trim();
    if (!content) {
      showError("内容不能为空");
      return;
    }
    saveBtn.disabled = true;
    cancelBtn.disabled = true;
    try {
      await request(`/api/conversations/${currentConversationId}/messages/${m.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });
      await selectConversation(currentConversationId);
    } catch (err) {
      showError(err.message);
    } finally {
      saveBtn.disabled = false;
      cancelBtn.disabled = false;
    }
  });
}

function beginDeleteMessage(userRow, m) {
  const actions = userRow.querySelector(".message-actions");

  const confirmWrap = document.createElement("div");
  confirmWrap.className = "delete-confirm";

  const label = document.createElement("span");
  label.textContent = "确认删除？";

  const confirmBtn = document.createElement("button");
  confirmBtn.type = "button";
  confirmBtn.className = "action-button";
  confirmBtn.textContent = "确认";
  confirmBtn.style.color = "#e11d48";

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.className = "action-button";
  cancelBtn.textContent = "取消";

  confirmWrap.appendChild(label);
  confirmWrap.appendChild(confirmBtn);
  confirmWrap.appendChild(cancelBtn);

  actions.replaceWith(confirmWrap);

  const restore = () => {
    confirmWrap.replaceWith(actions);
  };

  cancelBtn.addEventListener("click", restore);

  confirmBtn.addEventListener("click", async () => {
    try {
      await request(`/api/conversations/${currentConversationId}/messages/${m.id}`, { method: "DELETE" });
      await selectConversation(currentConversationId);
    } catch (err) {
      showError(err.message);
    }
  });
}

async function createConversation() {
  try {
    const conv = await request("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    await loadConversations();
    await selectConversation(conv.id);
  } catch (err) {
    showError(err.message);
  }
}

function beginRename() {
  if (currentConversationId === null) return;

  const title = currentTitleEl.textContent;
  const editor = document.createElement("div");
  editor.className = "rename-editor";

  const input = document.createElement("input");
  input.type = "text";
  input.className = "rename-input";
  input.value = title;

  const saveBtn = document.createElement("button");
  saveBtn.type = "button";
  saveBtn.className = "header-button";
  saveBtn.textContent = "保存";

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.className = "header-button";
  cancelBtn.textContent = "取消";

  editor.appendChild(input);
  editor.appendChild(saveBtn);
  editor.appendChild(cancelBtn);

  currentTitleEl.replaceWith(editor);
  renameBtn.hidden = true;
  deleteBtn.hidden = true;

  const restore = () => {
    editor.replaceWith(currentTitleEl);
    renameBtn.hidden = false;
    deleteBtn.hidden = false;
  };

  cancelBtn.addEventListener("click", restore);

  saveBtn.addEventListener("click", async () => {
    const newTitle = input.value.trim();
    if (!newTitle) {
      showError("标题不能为空");
      return;
    }
    try {
      await request(`/api/conversations/${currentConversationId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle }),
      });
      currentTitleEl.textContent = newTitle;
      restore();
      await loadConversations();
    } catch (err) {
      showError(err.message);
    }
  });
}

function beginDelete() {
  if (currentConversationId === null) return;

  const headerActions = document.querySelector(".header-actions");
  const confirmWrap = document.createElement("div");
  confirmWrap.className = "delete-confirm";

  const label = document.createElement("span");
  label.textContent = "确认删除当前会话？";

  const confirmBtn = document.createElement("button");
  confirmBtn.type = "button";
  confirmBtn.className = "action-button";
  confirmBtn.textContent = "确认";
  confirmBtn.style.color = "#e11d48";

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.className = "action-button";
  cancelBtn.textContent = "取消";

  confirmWrap.appendChild(label);
  confirmWrap.appendChild(confirmBtn);
  confirmWrap.appendChild(cancelBtn);

  headerActions.replaceWith(confirmWrap);

  cancelBtn.addEventListener("click", () => {
    confirmWrap.replaceWith(headerActions);
  });

  confirmBtn.addEventListener("click", async () => {
    try {
      await request(`/api/conversations/${currentConversationId}`, { method: "DELETE" });
      currentConversationId = null;
      currentTitleEl.textContent = "选择一个会话开始聊天";
      messagesEl.innerHTML = "";
      confirmWrap.replaceWith(headerActions);
      renameBtn.hidden = true;
      deleteBtn.hidden = true;
      await loadConversations();
      clearError();
    } catch (err) {
      showError(err.message);
    }
  });
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (sending) return;
  if (currentConversationId === null) {
    showError("请先选择一个会话");
    return;
  }
  const text = messageInput.value.trim();
  if (!text) {
    showError("请输入消息内容");
    return;
  }
  sending = true;
  sendButton.disabled = true;
  messageInput.disabled = true;
  try {
    await request(`/api/conversations/${currentConversationId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    messageInput.value = "";
    await selectConversation(currentConversationId);
    clearError();
  } catch (err) {
    showError(err.message);
  } finally {
    sending = false;
    sendButton.disabled = false;
    messageInput.disabled = false;
  }
});

newConversationBtn.addEventListener("click", createConversation);
renameBtn.addEventListener("click", beginRename);
deleteBtn.addEventListener("click", beginDelete);

loadConversations();
