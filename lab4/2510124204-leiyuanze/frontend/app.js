"use strict";

const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const newConversationButton = document.querySelector("#new-conversation-button");
const conversationList = document.querySelector("#conversation-list");
const messageList = document.querySelector("#message-list");
const messageCount = document.querySelector("#message-count");
const activeConversationTitle = document.querySelector(
  "#active-conversation-title",
);
const activeConversationSubtitle = document.querySelector(
  "#active-conversation-subtitle",
);
const feedback = document.querySelector("#feedback");
const connectionStatus = document.querySelector("#connection-status");

let conversations = [];
let activeConversation = null;
let editingConversationId = null;
let confirmingConversationDeleteId = null;
let editingMessageId = null;
let confirmingMessageDeleteId = null;
let isSending = false;
let isCreatingConversation = false;

function setFeedback(message = "", tone = "") {
  feedback.textContent = message;

  if (tone) {
    feedback.dataset.tone = tone;
  } else {
    delete feedback.dataset.tone;
  }
}

function setConnectionState(state, label) {
  connectionStatus.dataset.state = state;
  connectionStatus.textContent = label;
}

async function readResponse(response) {
  let payload = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message = payload?.error || `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }

  return payload;
}

function createElement(tagName, className, textContent) {
  const element = document.createElement(tagName);

  if (className) {
    element.className = className;
  }

  if (textContent !== undefined) {
    element.textContent = textContent;
  }

  return element;
}

function createAuthorElement(author, isAssistant = false) {
  const className = isAssistant
    ? "message-author message-author--assistant"
    : "message-author";
  return createElement("span", className, author);
}

function renderConversationList() {
  conversationList.replaceChildren();

  if (conversations.length === 0) {
    conversationList.append(
      createElement("p", "sidebar-empty", "还没有会话，点击“新建”开始。"),
    );
    return;
  }

  conversations.forEach((conversation) => {
    const item = createElement("div", "conversation-item");
    item.dataset.conversationId = String(conversation.id);

    if (activeConversation?.id === conversation.id) {
      item.classList.add("conversation-item--active");
    }

    if (editingConversationId === conversation.id) {
      const form = createElement("form", "conversation-rename-form");
      const input = createElement("input", "rename-input");
      input.type = "text";
      input.maxLength = 80;
      input.required = true;
      input.value = conversation.title;
      input.setAttribute("aria-label", "会话名称");

      const actions = createElement("div", "conversation-inline-actions");
      const cancelButton = createElement("button", "secondary-button", "取消");
      cancelButton.type = "button";
      cancelButton.dataset.action = "cancel-rename";

      const saveButton = createElement("button", "save-button", "保存");
      saveButton.type = "submit";

      actions.append(cancelButton, saveButton);
      form.append(input, actions);
      item.append(form);
    } else if (confirmingConversationDeleteId === conversation.id) {
      const confirmation = createElement(
        "div",
        "conversation-delete-confirmation",
      );
      confirmation.append(
        createElement("p", "confirmation-text", "确定删除这个会话？"),
      );

      const actions = createElement("div", "conversation-inline-actions");
      const cancelButton = createElement("button", "secondary-button", "取消");
      cancelButton.type = "button";
      cancelButton.dataset.action = "cancel-delete-conversation";

      const deleteButton = createElement(
        "button",
        "danger-button",
        "确认删除",
      );
      deleteButton.type = "button";
      deleteButton.dataset.action = "confirm-delete-conversation";

      actions.append(cancelButton, deleteButton);
      confirmation.append(actions);
      item.append(confirmation);
    } else {
      const selectButton = createElement("button", "conversation-select");
      selectButton.type = "button";
      selectButton.dataset.action = "select-conversation";

      const title = createElement(
        "span",
        "conversation-title",
        conversation.title,
      );
      const meta = createElement(
        "span",
        "conversation-meta",
        `${conversation.messageCount} 条消息`,
      );
      selectButton.append(title, meta);

      const actions = createElement("div", "conversation-actions");
      const renameButton = createElement("button", "text-button", "改名");
      renameButton.type = "button";
      renameButton.dataset.action = "rename-conversation";

      const deleteButton = createElement(
        "button",
        "text-button text-button--danger",
        "删除",
      );
      deleteButton.type = "button";
      deleteButton.dataset.action = "delete-conversation";

      actions.append(renameButton, deleteButton);
      item.append(selectButton, actions);
    }

    conversationList.append(item);
  });
}

function renderMessage(record) {
  const card = createElement("article", "message-card");
  card.dataset.messageId = String(record.id);

  const userRow = createElement("div", "message-row");
  userRow.append(createAuthorElement("你"));

  if (editingMessageId === record.id) {
    userRow.classList.add("message-row--editing");

    const form = createElement("form", "edit-form");
    const input = createElement("textarea", "edit-input");
    input.name = "message";
    input.maxLength = 2000;
    input.required = true;
    input.value = record.message;

    const actions = createElement("div", "edit-actions");
    const cancelButton = createElement("button", "secondary-button", "取消");
    cancelButton.type = "button";
    cancelButton.dataset.action = "cancel-edit";

    const saveButton = createElement("button", "save-button", "保存");
    saveButton.type = "submit";

    actions.append(cancelButton, saveButton);
    form.append(input, actions);
    userRow.append(form);
  } else if (confirmingMessageDeleteId === record.id) {
    userRow.classList.add("message-row--editing");

    const confirmation = createElement("div", "delete-confirmation");
    confirmation.append(
      createElement("span", "confirmation-text", "确定删除这条记录？"),
    );

    const cancelButton = createElement("button", "secondary-button", "取消");
    cancelButton.type = "button";
    cancelButton.dataset.action = "cancel-message-delete";

    const deleteButton = createElement(
      "button",
      "danger-button",
      "确认删除",
    );
    deleteButton.type = "button";
    deleteButton.dataset.action = "confirm-message-delete";

    confirmation.append(cancelButton, deleteButton);
    userRow.append(confirmation);
  } else {
    userRow.append(createElement("p", "message-text", record.message));

    const actions = createElement("div", "message-actions");
    const editButton = createElement("button", "text-button", "修改");
    editButton.type = "button";
    editButton.dataset.action = "edit-message";

    const deleteButton = createElement(
      "button",
      "text-button text-button--danger",
      "删除",
    );
    deleteButton.type = "button";
    deleteButton.dataset.action = "delete-message";

    actions.append(editButton, deleteButton);
    userRow.append(actions);
  }

  const replyRow = createElement(
    "div",
    "message-row message-row--reply",
  );
  replyRow.append(
    createAuthorElement("AI", true),
    createElement("p", "message-text", record.reply),
  );

  card.append(userRow, replyRow);
  messageList.append(card);
}

function renderMessages() {
  messageList.replaceChildren();

  if (!activeConversation) {
    activeConversationTitle.textContent = "未选择会话";
    activeConversationSubtitle.textContent = "选择或新建一个会话";
    messageCount.textContent = "0 条消息";
    messageInput.disabled = true;
    sendButton.disabled = true;
    messageList.append(
      createElement("p", "empty-state", "选择或新建一个会话，然后开始聊天。"),
    );
    return;
  }

  activeConversationTitle.textContent = activeConversation.title;
  activeConversationSubtitle.textContent = "同一会话会携带最近对话上下文";
  messageCount.textContent = `${activeConversation.messages.length} 条消息`;
  messageInput.disabled = isSending;
  sendButton.disabled = isSending;
  messageInput.placeholder = "输入消息...";

  if (activeConversation.messages.length === 0) {
    messageList.append(
      createElement("p", "empty-state", "还没有消息，发送第一条开始对话。"),
    );
    return;
  }

  activeConversation.messages.forEach(renderMessage);
}

function renderAll() {
  renderConversationList();
  renderMessages();
}

function syncActiveConversationSummary() {
  if (!activeConversation) {
    return;
  }

  const summary = conversations.find(
    (conversation) => conversation.id === activeConversation.id,
  );
  if (!summary) {
    return;
  }

  summary.title = activeConversation.title;
  summary.messageCount = activeConversation.messages.length;
  summary.lastMessage = activeConversation.messages.at(-1)?.message || null;
  summary.updatedAt = activeConversation.updatedAt;
  conversations.sort((left, right) =>
    right.updatedAt.localeCompare(left.updatedAt),
  );
}

async function refreshConversationList() {
  const response = await fetch("/api/conversations");
  const payload = await readResponse(response);

  if (!Array.isArray(payload)) {
    throw new Error("会话接口返回了无效的数据格式");
  }

  conversations = payload;
}

async function selectConversation(conversationId) {
  try {
    const response = await fetch(`/api/conversations/${conversationId}`);
    activeConversation = await readResponse(response);
    editingConversationId = null;
    confirmingConversationDeleteId = null;
    editingMessageId = null;
    confirmingMessageDeleteId = null;
    renderAll();
    setFeedback();
  } catch (error) {
    setFeedback(error.message, "error");
  }
}

async function initializeConversations() {
  conversationList.setAttribute("aria-busy", "true");

  try {
    await refreshConversationList();
    setConnectionState("online", "服务已连接");
    setFeedback();

    if (conversations.length > 0) {
      await selectConversation(conversations[0].id);
    } else {
      renderAll();
    }
  } catch (error) {
    setConnectionState("offline", "服务不可用");
    setFeedback(error.message, "error");
    renderAll();
  } finally {
    conversationList.setAttribute("aria-busy", "false");
  }
}

async function createConversation() {
  if (isCreatingConversation) {
    return;
  }

  isCreatingConversation = true;
  newConversationButton.disabled = true;

  try {
    const response = await fetch("/api/conversations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    });
    const conversation = await readResponse(response);

    await refreshConversationList();
    await selectConversation(conversation.id);
    setFeedback("会话已创建。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  } finally {
    isCreatingConversation = false;
    newConversationButton.disabled = false;
  }
}

async function renameConversation(conversationId, title) {
  try {
    const response = await fetch(`/api/conversations/${conversationId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title }),
    });
    await readResponse(response);

    editingConversationId = null;
    await refreshConversationList();

    if (activeConversation?.id === conversationId) {
      activeConversation.title = title;
      activeConversation.updatedAt = new Date().toISOString();
      syncActiveConversationSummary();
    }

    renderAll();
    setFeedback("会话名称已更新。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  }
}

async function deleteConversation(conversationId) {
  const wasActive = activeConversation?.id === conversationId;

  try {
    const response = await fetch(`/api/conversations/${conversationId}`, {
      method: "DELETE",
    });
    await readResponse(response);

    confirmingConversationDeleteId = null;
    if (wasActive) {
      activeConversation = null;
    }

    await refreshConversationList();

    if (!activeConversation && conversations.length > 0) {
      await selectConversation(conversations[0].id);
    } else {
      renderAll();
    }

    setFeedback("会话已删除。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  }
}

async function createMessage(event) {
  event.preventDefault();

  if (!activeConversation) {
    setFeedback("请先选择或新建一个会话。", "error");
    return;
  }

  const message = messageInput.value.trim();
  if (!message) {
    setFeedback("请输入消息内容。", "error");
    messageInput.focus();
    return;
  }

  isSending = true;
  renderMessages();
  setFeedback("正在等待 DeepSeek 回复...");

  try {
    const response = await fetch(
      `/api/conversations/${activeConversation.id}/messages`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      },
    );
    const record = await readResponse(response);

    activeConversation.messages.push(record);
    activeConversation.updatedAt = record.createdAt;
    messageInput.value = "";
    syncActiveConversationSummary();
    renderAll();
    setFeedback("消息已发送。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  } finally {
    isSending = false;
    renderMessages();
    messageInput.focus();
  }
}

async function updateMessage(messageId, message) {
  if (!activeConversation) {
    return;
  }

  try {
    const response = await fetch(
      `/api/conversations/${activeConversation.id}/messages/${messageId}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      },
    );
    const updatedRecord = await readResponse(response);

    activeConversation.messages = activeConversation.messages.map((record) =>
      record.id === messageId ? updatedRecord : record,
    );
    activeConversation.updatedAt = new Date().toISOString();
    editingMessageId = null;
    syncActiveConversationSummary();
    renderAll();
    setFeedback("消息已更新。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  }
}

async function deleteMessage(messageId) {
  if (!activeConversation) {
    return;
  }

  try {
    const response = await fetch(
      `/api/conversations/${activeConversation.id}/messages/${messageId}`,
      {
        method: "DELETE",
      },
    );
    await readResponse(response);

    activeConversation.messages = activeConversation.messages.filter(
      (record) => record.id !== messageId,
    );
    activeConversation.updatedAt = new Date().toISOString();
    confirmingMessageDeleteId = null;
    syncActiveConversationSummary();
    renderAll();
    setFeedback("消息已删除。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  }
}

messageForm.addEventListener("submit", createMessage);
newConversationButton.addEventListener("click", createConversation);

conversationList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }

  const item = button.closest(".conversation-item");
  const conversationId = Number(item.dataset.conversationId);

  if (button.dataset.action === "select-conversation") {
    void selectConversation(conversationId);
  } else if (button.dataset.action === "rename-conversation") {
    editingConversationId = conversationId;
    confirmingConversationDeleteId = null;
    renderConversationList();
  } else if (button.dataset.action === "cancel-rename") {
    editingConversationId = null;
    renderConversationList();
  } else if (button.dataset.action === "delete-conversation") {
    confirmingConversationDeleteId = conversationId;
    editingConversationId = null;
    renderConversationList();
  } else if (button.dataset.action === "cancel-delete-conversation") {
    confirmingConversationDeleteId = null;
    renderConversationList();
  } else if (button.dataset.action === "confirm-delete-conversation") {
    void deleteConversation(conversationId);
  }
});

conversationList.addEventListener("submit", (event) => {
  if (!event.target.matches(".conversation-rename-form")) {
    return;
  }

  event.preventDefault();
  const item = event.target.closest(".conversation-item");
  const conversationId = Number(item.dataset.conversationId);
  const title = event.target.querySelector(".rename-input").value.trim();

  if (!title) {
    setFeedback("会话名称不能为空。", "error");
    return;
  }

  void renameConversation(conversationId, title);
});

messageList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || !activeConversation) {
    return;
  }

  const card = button.closest(".message-card");
  const messageId = Number(card.dataset.messageId);

  if (button.dataset.action === "edit-message") {
    editingMessageId = messageId;
    confirmingMessageDeleteId = null;
    renderMessages();
  } else if (button.dataset.action === "cancel-edit") {
    editingMessageId = null;
    renderMessages();
  } else if (button.dataset.action === "delete-message") {
    confirmingMessageDeleteId = messageId;
    editingMessageId = null;
    renderMessages();
  } else if (button.dataset.action === "cancel-message-delete") {
    confirmingMessageDeleteId = null;
    renderMessages();
  } else if (button.dataset.action === "confirm-message-delete") {
    void deleteMessage(messageId);
  }
});

messageList.addEventListener("submit", (event) => {
  if (!event.target.matches(".edit-form")) {
    return;
  }

  event.preventDefault();
  const card = event.target.closest(".message-card");
  const messageId = Number(card.dataset.messageId);
  const message = event.target.querySelector(".edit-input").value.trim();

  if (!message) {
    setFeedback("消息内容不能为空。", "error");
    return;
  }

  void updateMessage(messageId, message);
});

void initializeConversations();
