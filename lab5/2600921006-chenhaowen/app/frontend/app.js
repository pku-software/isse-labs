const conversationList = document.querySelector("#conversation-list");
const newConversationForm = document.querySelector("#new-conversation-form");
const newConversationTitle = document.querySelector("#new-conversation-title");
const sidebarStatus = document.querySelector("#sidebar-status");
const conversationTitle = document.querySelector("#conversation-title");
const conversationStatus = document.querySelector("#conversation-status");
const renameStart = document.querySelector("#rename-start");
const renameForm = document.querySelector("#rename-form");
const renameInput = document.querySelector("#rename-input");
const deleteConversationStart = document.querySelector("#delete-conversation-start");
const deleteConversationPanel = document.querySelector("#delete-conversation-panel");
const deleteConversationConfirm = document.querySelector("#delete-conversation-confirm");
const messageList = document.querySelector("#message-list");
const emptyState = document.querySelector("#empty-state");
const messageTemplate = document.querySelector("#message-template");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const statusMessage = document.querySelector("#status-message");

let conversations = [];
let activeConversation = null;
let busy = false;

function showStatus(element, text, isError = false) {
  element.textContent = text;
  element.classList.toggle("error", isError);
}

async function apiRequest(url, options = {}) {
  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    throw new Error("无法连接后端，请确认 Flask 正在运行。");
  }

  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("后端未返回有效的 JSON，请确认页面由 Flask 提供。");
  }
  if (!response.ok) {
    throw new Error(data.error || `请求失败（${response.status}）。`);
  }
  return data;
}

function setBusy(value) {
  busy = value;
  document.querySelectorAll("button, input, textarea").forEach((control) => {
    control.disabled = value;
  });
  if (!activeConversation) {
    [messageInput, sendButton, renameStart, deleteConversationStart].forEach((control) => {
      control.disabled = true;
    });
  }
  messageList.setAttribute("aria-busy", String(value));
}

async function performAction(statusElement, pendingText, action) {
  if (busy) return false;
  setBusy(true);
  showStatus(statusElement, pendingText);
  try {
    await action();
    return true;
  } catch (error) {
    showStatus(statusElement, error.message, true);
    return false;
  } finally {
    setBusy(false);
  }
}

function updateEmptyState() {
  emptyState.classList.remove("error");
  emptyState.hidden = messageList.querySelector(".message-record") !== null;
  emptyState.textContent = activeConversation
    ? "这个会话还没有聊天记录，写下第一条消息开始吧。"
    : "请先在会话列表中选择或建立一个会话。";
}

function updateSummary(conversation) {
  const summary = {
    id: conversation.id,
    title: conversation.title,
    message_count: conversation.messages.length,
  };
  const index = conversations.findIndex((item) => item.id === conversation.id);
  if (index === -1) conversations.push(summary);
  else conversations[index] = summary;
  renderConversationList();
}

function renderConversationList() {
  conversationList.replaceChildren();
  for (const conversation of conversations) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "conversation-select";
    button.disabled = busy;
    button.setAttribute("aria-pressed", String(activeConversation?.id === conversation.id));

    const title = document.createElement("span");
    title.textContent = conversation.title;
    const count = document.createElement("span");
    count.className = "conversation-count";
    count.textContent = `${conversation.message_count} 条问答`;
    button.append(title, count);
    button.addEventListener("click", async () => {
      if (activeConversation?.id === conversation.id) return;
      const selected = await performAction(sidebarStatus, "正在加载会话……", async () => {
        const detail = await apiRequest(`/api/conversations/${conversation.id}`);
        displayConversation(detail);
        showStatus(sidebarStatus, "");
      });
      if (selected) messageInput.focus();
    });
    item.append(button);
    conversationList.append(item);
  }
}

function displayConversation(conversation) {
  activeConversation = conversation;
  conversationTitle.textContent = conversation ? conversation.title : "请选择一个会话";
  renameForm.hidden = true;
  deleteConversationPanel.hidden = true;
  messageInput.value = "";
  showStatus(conversationStatus, "");
  showStatus(statusMessage, "");
  messageList.replaceChildren(emptyState);
  if (conversation) {
    for (const record of conversation.messages) {
      messageList.append(createRecordElement(record, conversation.id));
    }
    updateSummary(conversation);
  } else {
    renderConversationList();
  }
  updateEmptyState();
  setBusy(busy);
}

function createRecordElement(record, conversationId) {
  const article = messageTemplate.content.firstElementChild.cloneNode(true);
  const question = article.querySelector(".question-text");
  const reply = article.querySelector(".reply-text");
  const editStart = article.querySelector(".edit-start");
  const deleteStart = article.querySelector(".delete-start");
  const editForm = article.querySelector(".edit-form");
  const editInput = editForm.querySelector("textarea");
  const deletePanel = article.querySelector(".delete-confirmation");
  const deleteConfirm = article.querySelector(".delete-confirm");
  const recordStatus = article.querySelector(".record-status");
  const recordUrl = `/api/conversations/${conversationId}/messages/${record.id}`;

  article.setAttribute("aria-label", `问答 ${record.id}`);
  article.querySelector(".record-label").textContent = `问答 #${record.id}`;
  question.textContent = record.message;
  reply.textContent = record.reply;

  editStart.addEventListener("click", () => {
    deletePanel.hidden = true;
    editInput.value = record.message;
    editForm.hidden = false;
    showStatus(recordStatus, "");
    editInput.focus();
  });
  article.querySelector(".edit-cancel").addEventListener("click", () => {
    editForm.hidden = true;
    showStatus(recordStatus, "");
    editStart.focus();
  });
  deleteStart.addEventListener("click", () => {
    editForm.hidden = true;
    deletePanel.hidden = false;
    showStatus(recordStatus, "");
    deleteConfirm.focus();
  });
  article.querySelector(".delete-cancel").addEventListener("click", () => {
    deletePanel.hidden = true;
    showStatus(recordStatus, "");
    deleteStart.focus();
  });

  editForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy) return;
    const message = editInput.value.trim();
    if (!message) {
      showStatus(recordStatus, "请输入非空消息。", true);
      editInput.focus();
      return;
    }
    const saved = await performAction(recordStatus, "正在保存……", async () => {
      record = await apiRequest(recordUrl, {
        method: "PATCH",
        body: JSON.stringify({ message }),
      });
      activeConversation.messages = activeConversation.messages.map((item) =>
        item.id === record.id ? record : item
      );
      question.textContent = record.message;
      reply.textContent = record.reply;
      editForm.hidden = true;
      showStatus(recordStatus, "已保存。");
    });
    if (saved) editStart.focus();
  });

  deleteConfirm.addEventListener("click", async () => {
    const deleted = await performAction(recordStatus, "正在删除……", async () => {
      await apiRequest(recordUrl, { method: "DELETE" });
      activeConversation.messages = activeConversation.messages.filter((item) => item.id !== record.id);
      article.remove();
      updateSummary(activeConversation);
      updateEmptyState();
      showStatus(statusMessage, "已删除记录。");
    });
    if (deleted) messageInput.focus();
  });

  return article;
}

newConversationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  const title = newConversationTitle.value.trim();
  if (!title) {
    showStatus(sidebarStatus, "请输入会话名称。", true);
    newConversationTitle.focus();
    return;
  }
  const created = await performAction(sidebarStatus, "正在建立会话……", async () => {
    const conversation = await apiRequest("/api/conversations", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
    displayConversation(conversation);
    newConversationTitle.value = "";
    showStatus(sidebarStatus, "会话已建立。");
  });
  if (created) messageInput.focus();
});

renameStart.addEventListener("click", () => {
  if (!activeConversation || busy) return;
  renameInput.value = activeConversation.title;
  renameForm.hidden = false;
  deleteConversationPanel.hidden = true;
  showStatus(conversationStatus, "");
  renameInput.focus();
});
document.querySelector("#rename-cancel").addEventListener("click", () => {
  renameForm.hidden = true;
  showStatus(conversationStatus, "");
  renameStart.focus();
});
renameForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!activeConversation || busy) return;
  const title = renameInput.value.trim();
  if (!title) {
    showStatus(conversationStatus, "请输入会话名称。", true);
    renameInput.focus();
    return;
  }
  const conversationId = activeConversation.id;
  const renamed = await performAction(conversationStatus, "正在保存名称……", async () => {
    const updated = await apiRequest(`/api/conversations/${conversationId}`, {
      method: "PATCH",
      body: JSON.stringify({ title }),
    });
    activeConversation.title = updated.title;
    conversationTitle.textContent = updated.title;
    updateSummary(activeConversation);
    renameForm.hidden = true;
    showStatus(conversationStatus, "会话名称已更新。");
  });
  if (renamed) renameStart.focus();
});

deleteConversationStart.addEventListener("click", () => {
  if (!activeConversation || busy) return;
  renameForm.hidden = true;
  deleteConversationPanel.hidden = false;
  showStatus(conversationStatus, "");
  deleteConversationConfirm.focus();
});
document.querySelector("#delete-conversation-cancel").addEventListener("click", () => {
  deleteConversationPanel.hidden = true;
  showStatus(conversationStatus, "");
  deleteConversationStart.focus();
});
deleteConversationConfirm.addEventListener("click", async () => {
  if (!activeConversation || busy) return;
  const conversationId = activeConversation.id;
  const deleted = await performAction(conversationStatus, "正在删除会话……", async () => {
    await apiRequest(`/api/conversations/${conversationId}`, { method: "DELETE" });
    conversations = conversations.filter((item) => item.id !== conversationId);
    displayConversation(null);
    showStatus(sidebarStatus, "会话已删除，请选择其他会话或建立新会话。");
  });
  if (deleted) newConversationTitle.focus();
});

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!activeConversation || busy) return;
  const message = messageInput.value.trim();
  if (!message) {
    showStatus(statusMessage, "请输入消息后再发送。", true);
    messageInput.focus();
    return;
  }
  const conversationId = activeConversation.id;
  const sent = await performAction(statusMessage, "正在等待 AI 回复……", async () => {
    const record = await apiRequest(`/api/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    activeConversation.messages.push(record);
    messageList.append(createRecordElement(record, conversationId));
    updateSummary(activeConversation);
    updateEmptyState();
    messageInput.value = "";
    showStatus(statusMessage, "消息已发送。");
  });
  if (sent) messageInput.focus();
});

async function loadConversations() {
  const loaded = await performAction(sidebarStatus, "正在加载会话……", async () => {
    conversations = await apiRequest("/api/conversations");
    if (conversations.length) {
      const detail = await apiRequest(`/api/conversations/${conversations[0].id}`);
      displayConversation(detail);
    } else {
      displayConversation(null);
    }
    showStatus(sidebarStatus, conversations.length ? "" : "还没有会话，请先建立一个。");
  });
  if (!loaded) {
    showStatus(emptyState, "会话加载失败，请刷新页面重试。", true);
  }
}

loadConversations();
