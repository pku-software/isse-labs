// 前端交互逻辑：会话管理与消息收发，所有数据操作都通过调用后端 API 完成

const conversationList = document.getElementById("conversation-list");
const newConversationBtn = document.getElementById("new-conversation");
const conversationTitle = document.getElementById("conversation-title");
const renameBtn = document.getElementById("rename-conversation");
const deleteBtn = document.getElementById("delete-conversation");
const chatArea = document.getElementById("chat-area");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const statusBar = document.getElementById("status-bar");

let conversations = []; // 当前已加载的全部会话
let selectedId = null;  // 当前选中的会话 id

// 在页面底部显示一条提示（成功为绿色、错误为红色），3 秒后自动消失
function showStatus(text, isError) {
  statusBar.textContent = text;
  statusBar.className = isError ? "status status-error" : "status status-ok";
  setTimeout(() => {
    statusBar.textContent = "";
    statusBar.className = "status";
  }, 3000);
}

// 当前选中的会话对象；未选中时返回 null
function selectedConversation() {
  return conversations.find((c) => c.id === selectedId) || null;
}

// 渲染左侧会话列表
function renderConversationList() {
  conversationList.innerHTML = "";
  for (const conv of conversations) {
    const item = document.createElement("li");
    item.className = "conversation-item" + (conv.id === selectedId ? " selected" : "");
    item.textContent = conv.title;
    item.addEventListener("click", () => selectConversation(conv.id));
    conversationList.appendChild(item);
  }
}

// 渲染一条消息（用户消息 + AI 回复）
function createRecordElement(msg) {
  const article = document.createElement("article");
  article.className = "chat-record";

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
  article.appendChild(body);
  return article;
}

// 渲染当前会话的消息
function renderMessages(messages) {
  const conv = selectedConversation();
  conversationTitle.textContent = conv ? conv.title : "选择或新建一个会话";
  chatArea.innerHTML = "";
  if (messages.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-tip";
    empty.textContent = "发送一条消息，开始这个会话吧～";
    chatArea.appendChild(empty);
    return;
  }
  for (const msg of messages) {
    chatArea.appendChild(createRecordElement(msg));
  }
}

// 未选中会话时的空状态
function renderEmptyState() {
  conversationTitle.textContent = "选择或新建一个会话";
  chatArea.innerHTML = "";
  const empty = document.createElement("div");
  empty.className = "empty-tip";
  empty.textContent = "点击左侧「＋ 新建会话」开始聊天";
  chatArea.appendChild(empty);
}

// 加载全部会话：GET /api/conversations
async function loadConversations() {
  try {
    const res = await fetch("/api/conversations");
    if (!res.ok) {
      throw new Error("HTTP " + res.status);
    }
    conversations = await res.json();
    if (conversations.length === 0) {
      selectedId = null;
      renderConversationList();
      renderEmptyState();
      return;
    }
    if (selectedId === null || !conversations.some((c) => c.id === selectedId)) {
      await selectConversation(conversations[0].id);
      return;
    }
    renderConversationList();
    renderMessages(selectedConversation().messages);
  } catch (e) {
    showStatus("加载会话失败：" + e.message, true);
  }
}

// 选中并打开一个会话：GET /api/conversations/<id>
async function selectConversation(id) {
  try {
    const res = await fetch(`/api/conversations/${id}`);
    if (!res.ok) {
      throw new Error("HTTP " + res.status);
    }
    const conv = await res.json();
    selectedId = conv.id;
    const idx = conversations.findIndex((c) => c.id === conv.id);
    if (idx >= 0) {
      conversations[idx] = conv;
    } else {
      conversations.push(conv);
    }
    renderConversationList();
    renderMessages(conv.messages);
  } catch (e) {
    showStatus("打开会话失败：" + e.message, true);
  }
}

// 新建会话：POST /api/conversations
newConversationBtn.addEventListener("click", async () => {
  try {
    const res = await fetch("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "新会话" })
    });
    if (!res.ok) {
      throw new Error("HTTP " + res.status);
    }
    const conv = await res.json();
    conversations.push(conv);
    renderConversationList();
    await selectConversation(conv.id);
    showStatus("会话已创建");
  } catch (e) {
    showStatus("创建会话失败：" + e.message, true);
  }
});

// 重命名：点击后标题变为页面内输入框（输入框 + 保存/取消）
function startRename(conv) {
  const editBox = document.createElement("div");
  editBox.className = "edit-box";

  const input = document.createElement("input");
  input.type = "text";
  input.value = conv.title;

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

  conversationTitle.replaceChildren(editBox);

  saveBtn.addEventListener("click", async () => {
    const newTitle = input.value.trim();
    if (!newTitle) {
      errorTip.textContent = "标题不能为空";
      return;
    }
    try {
      const res = await fetch(`/api/conversations/${conv.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle })
      });
      if (!res.ok) {
        const err = await res.json();
        errorTip.textContent = "重命名失败：" + (err.error || res.status);
        return;
      }
      const updated = await res.json();
      const idx = conversations.findIndex((c) => c.id === updated.id);
      if (idx >= 0) {
        conversations[idx] = updated;
      }
      renderConversationList();
      conversationTitle.textContent = updated.title;
      showStatus("重命名成功");
    } catch (e) {
      errorTip.textContent = "网络错误：" + e.message;
    }
  });

  cancelBtn.addEventListener("click", () => {
    conversationTitle.textContent = conv.title;
  });
}

renameBtn.addEventListener("click", () => {
  const conv = selectedConversation();
  if (!conv) {
    showStatus("请先选择一个会话", true);
    return;
  }
  startRename(conv);
});

// 删除：点击后按钮变为"确认删除/取消"，确认后才真正请求删除
function startDelete() {
  const actions = document.querySelector(".header-actions");
  actions.innerHTML = "";

  const confirmBtn = document.createElement("button");
  confirmBtn.className = "btn-delete-confirm";
  confirmBtn.type = "button";
  confirmBtn.textContent = "确认删除";

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.textContent = "取消";

  const errorTip = document.createElement("span");
  errorTip.className = "inline-error";

  actions.appendChild(confirmBtn);
  actions.appendChild(cancelBtn);
  actions.appendChild(errorTip);

  confirmBtn.addEventListener("click", async () => {
    const conv = selectedConversation();
    if (!conv) {
      errorTip.textContent = "没有选中的会话";
      return;
    }
    try {
      const res = await fetch(`/api/conversations/${conv.id}`, { method: "DELETE" });
      if (!res.ok) {
        const err = await res.json();
        errorTip.textContent = "删除失败：" + (err.error || res.status);
        return;
      }
      conversations = conversations.filter((c) => c.id !== conv.id);
      selectedId = null;
      showStatus("会话已删除");
      await loadConversations();
      renderHeaderActions();
    } catch (e) {
      errorTip.textContent = "网络错误：" + e.message;
    }
  });

  cancelBtn.addEventListener("click", renderHeaderActions);
}

// 恢复头部"重命名/删除"按钮
function renderHeaderActions() {
  const actions = document.querySelector(".header-actions");
  actions.innerHTML = "";
  actions.appendChild(renameBtn);
  actions.appendChild(deleteBtn);
}

deleteBtn.addEventListener("click", () => {
  if (!selectedConversation()) {
    showStatus("请先选择一个会话", true);
    return;
  }
  startDelete();
});

// 发送消息：POST /api/conversations/<id>/messages
chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    showStatus("请输入消息内容", true);
    return;
  }
  if (selectedId === null) {
    showStatus("请先选择或新建一个会话", true);
    return;
  }
  try {
    const res = await fetch(`/api/conversations/${selectedId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    if (!res.ok) {
      const err = await res.json();
      showStatus("发送失败：" + (err.error || res.status), true);
      return;
    }
    const conv = await res.json();
    const idx = conversations.findIndex((c) => c.id === conv.id);
    if (idx >= 0) {
      conversations[idx] = conv;
    }
    renderMessages(conv.messages);
    messageInput.value = "";
    showStatus("发送成功");
  } catch (e) {
    showStatus("网络错误：" + e.message, true);
  }
});

// 页面打开时加载会话列表
loadConversations();
