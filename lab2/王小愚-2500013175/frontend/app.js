const conversationList = document.querySelector("#conversation-list");
const newConversationButton = document.querySelector("#new-conversation");
const activeConversationTitle = document.querySelector(
  "#active-conversation-title",
);
const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const feedback = document.querySelector("#feedback");
const submitButton = messageForm.querySelector("button[type='submit']");

let conversations = [];
let activeConversation = null;
let renamingConversationId = null;
let deletingConversationId = null;
let editingMessageId = null;
let deletingMessageId = null;

function setFeedback(text = "", kind = "") {
  feedback.textContent = text;
  feedback.dataset.kind = kind;
}

function makeButton(label, className, action, id) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.dataset.action = action;
  if (id !== undefined) button.dataset.id = id;
  button.textContent = label;
  return button;
}

function updateComposerState() {
  const disabled = activeConversation === null;
  messageInput.disabled = disabled;
  submitButton.disabled = disabled;
  activeConversationTitle.textContent = activeConversation
    ? activeConversation.title
    : "请选择或新建会话";
}

function renderConversationInlinePanel(conversation) {
  const panel = document.createElement("div");
  panel.className = "conversation-inline-panel";

  if (renamingConversationId === conversation.id) {
    const form = document.createElement("form");
    form.dataset.conversationId = conversation.id;
    form.className = "rename-conversation-form";

    const input = document.createElement("input");
    input.name = "title";
    input.value = conversation.title;
    input.required = true;
    input.setAttribute("aria-label", "新会话名称");

    const actions = document.createElement("div");
    actions.className = "panel-actions";
    actions.append(
      makeButton("取消", "secondary-button", "cancel-rename", conversation.id),
    );
    const save = document.createElement("button");
    save.type = "submit";
    save.className = "primary-button";
    save.textContent = "保存";
    actions.append(save);

    form.append(input, actions);
    panel.append(form);
  } else {
    const text = document.createElement("p");
    text.textContent = "确定删除该会话及其所有消息吗？";
    const actions = document.createElement("div");
    actions.className = "panel-actions";
    actions.append(
      makeButton(
        "取消",
        "secondary-button",
        "cancel-conversation-delete",
        conversation.id,
      ),
      makeButton(
        "确认删除",
        "danger-button",
        "confirm-conversation-delete",
        conversation.id,
      ),
    );
    panel.append(text, actions);
  }

  return panel;
}

function renderConversations() {
  conversationList.replaceChildren();

  if (conversations.length === 0) {
    const empty = document.createElement("div");
    empty.className = "conversation-empty";
    empty.textContent = "还没有会话，请先新建一个。";
    conversationList.append(empty);
    return;
  }

  for (const conversation of conversations) {
    const item = document.createElement("article");
    item.className = "conversation-item";
    if (activeConversation?.id === conversation.id) {
      item.classList.add("is-active");
    }

    const select = makeButton(
      conversation.title,
      "conversation-select",
      "select-conversation",
      conversation.id,
    );
    const meta = document.createElement("span");
    meta.className = "conversation-meta";
    meta.textContent = `${conversation.message_count} 条消息`;
    select.append(meta);

    const actions = document.createElement("div");
    actions.className = "conversation-actions";
    actions.append(
      makeButton("重命名", "secondary-button", "rename-conversation", conversation.id),
      makeButton("删除", "danger-button", "delete-conversation", conversation.id),
    );
    item.append(select, actions);

    if (
      renamingConversationId === conversation.id ||
      deletingConversationId === conversation.id
    ) {
      item.append(renderConversationInlinePanel(conversation));
    }
    conversationList.append(item);
  }
}

function createMessageBubble(message) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${
    message.role === "user" ? "user-message" : "assistant-message"
  }`;

  const badge = document.createElement("span");
  badge.className = "message-label";
  badge.textContent = message.role === "user" ? "你" : "AI";

  const content = document.createElement("p");
  content.textContent = message.content;
  wrapper.append(badge, content);
  return wrapper;
}

function createMessageEditPanel(message) {
  const form = document.createElement("form");
  form.className = "edit-panel message-edit-form";
  form.dataset.messageId = message.id;

  const label = document.createElement("label");
  label.htmlFor = `edit-message-${message.id}`;
  label.textContent = "修改用户消息";

  const input = document.createElement("textarea");
  input.id = `edit-message-${message.id}`;
  input.name = "message";
  input.required = true;
  input.value = message.content;

  const actions = document.createElement("div");
  actions.className = "panel-actions";
  actions.append(
    makeButton("取消", "secondary-button", "cancel-message-edit", message.id),
  );
  const save = document.createElement("button");
  save.type = "submit";
  save.className = "primary-button";
  save.textContent = "保存";
  actions.append(save);
  form.append(label, input, actions);
  return form;
}

function createMessageDeletePanel(message) {
  const panel = document.createElement("div");
  panel.className = "delete-panel";
  const text = document.createElement("p");
  text.textContent = "确定删除这一轮问答吗？";
  const actions = document.createElement("div");
  actions.className = "panel-actions";
  actions.append(
    makeButton("取消", "secondary-button", "cancel-message-delete", message.id),
    makeButton("确认删除", "danger-button", "confirm-message-delete", message.id),
  );
  panel.append(text, actions);
  return panel;
}

function renderMessages() {
  messageList.replaceChildren();
  updateComposerState();

  if (!activeConversation) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "从左侧选择一个会话，或新建会话开始聊天。";
    messageList.append(empty);
    return;
  }

  if (activeConversation.messages.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "这个会话还没有消息。";
    messageList.append(empty);
    return;
  }

  for (let index = 0; index < activeConversation.messages.length; index += 1) {
    const message = activeConversation.messages[index];
    if (message.role !== "user") continue;

    const article = document.createElement("article");
    article.className = "chat-record";
    article.append(createMessageBubble(message));

    const reply = activeConversation.messages[index + 1];
    if (reply?.role === "assistant") {
      article.append(createMessageBubble(reply));
    }

    const actions = document.createElement("div");
    actions.className = "record-actions";
    actions.append(
      makeButton("修改", "secondary-button", "edit-message", message.id),
      makeButton("删除", "danger-button", "delete-message", message.id),
    );
    article.append(actions);

    if (editingMessageId === message.id) {
      article.append(createMessageEditPanel(message));
    }
    if (deletingMessageId === message.id) {
      article.append(createMessageDeletePanel(message));
    }
    messageList.append(article);
  }
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "请求失败，请稍后重试");
  }
  return data;
}

async function refreshConversationSummaries() {
  conversations = await requestJson("/api/conversations");
  renderConversations();
}

async function selectConversation(id) {
  setFeedback("正在加载会话……");
  try {
    activeConversation = await requestJson(`/api/conversations/${id}`);
    editingMessageId = null;
    deletingMessageId = null;
    renderMessages();
    renderConversations();
    setFeedback();
  } catch (error) {
    setFeedback(error.message, "error");
  }
}

async function loadConversations() {
  setFeedback("正在加载会话……");
  try {
    await refreshConversationSummaries();
    if (conversations.length > 0) {
      await selectConversation(conversations[0].id);
    } else {
      renderMessages();
      setFeedback();
    }
  } catch (error) {
    renderMessages();
    setFeedback(error.message, "error");
  }
}

newConversationButton.addEventListener("click", async () => {
  newConversationButton.disabled = true;
  setFeedback("正在新建会话……");
  try {
    const created = await requestJson("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "新对话" }),
    });
    await refreshConversationSummaries();
    await selectConversation(created.id);
    setFeedback("会话已创建。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  } finally {
    newConversationButton.disabled = false;
  }
});

conversationList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const id = Number(button.dataset.id);
  const action = button.dataset.action;

  if (action === "select-conversation") {
    await selectConversation(id);
    return;
  }
  if (action === "rename-conversation") {
    renamingConversationId = id;
    deletingConversationId = null;
  } else if (action === "cancel-rename") {
    renamingConversationId = null;
  } else if (action === "delete-conversation") {
    deletingConversationId = id;
    renamingConversationId = null;
  } else if (action === "cancel-conversation-delete") {
    deletingConversationId = null;
  } else if (action === "confirm-conversation-delete") {
    button.disabled = true;
    setFeedback("正在删除会话……");
    try {
      await requestJson(`/api/conversations/${id}`, { method: "DELETE" });
      if (activeConversation?.id === id) activeConversation = null;
      deletingConversationId = null;
      await refreshConversationSummaries();
      if (!activeConversation && conversations.length > 0) {
        await selectConversation(conversations[0].id);
      } else {
        renderMessages();
      }
      setFeedback("会话已删除。", "success");
    } catch (error) {
      setFeedback(error.message, "error");
    }
  }

  renderConversations();
});

conversationList.addEventListener("submit", async (event) => {
  const form = event.target.closest(".rename-conversation-form");
  if (!form) return;
  event.preventDefault();

  const id = Number(form.dataset.conversationId);
  const title = new FormData(form).get("title").trim();
  if (!title) return;

  const saveButton = form.querySelector("button[type='submit']");
  saveButton.disabled = true;
  try {
    const updated = await requestJson(`/api/conversations/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    if (activeConversation?.id === id) activeConversation.title = updated.title;
    renamingConversationId = null;
    await refreshConversationSummaries();
    renderMessages();
    setFeedback("会话已重命名。", "success");
  } catch (error) {
    saveButton.disabled = false;
    setFeedback(error.message, "error");
  }
});

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!activeConversation) return;

  const message = messageInput.value.trim();
  if (!message) {
    setFeedback("请先输入消息。", "error");
    return;
  }

  submitButton.disabled = true;
  setFeedback("正在等待 AI 回复……");
  try {
    const created = await requestJson(
      `/api/conversations/${activeConversation.id}/messages`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      },
    );
    activeConversation.messages.push(
      created.user_message,
      created.assistant_message,
    );
    messageInput.value = "";
    await refreshConversationSummaries();
    renderMessages();
    setFeedback("消息已发送。", "success");
  } catch (error) {
    setFeedback(error.message, "error");
  } finally {
    submitButton.disabled = false;
    messageInput.focus();
  }
});

messageList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || !activeConversation) return;

  const id = Number(button.dataset.id);
  const action = button.dataset.action;

  if (action === "edit-message") {
    editingMessageId = id;
    deletingMessageId = null;
  } else if (action === "cancel-message-edit") {
    editingMessageId = null;
  } else if (action === "delete-message") {
    deletingMessageId = id;
    editingMessageId = null;
  } else if (action === "cancel-message-delete") {
    deletingMessageId = null;
  } else if (action === "confirm-message-delete") {
    button.disabled = true;
    setFeedback("正在删除问答……");
    try {
      await requestJson(
        `/api/conversations/${activeConversation.id}/messages/${id}`,
        { method: "DELETE" },
      );
      activeConversation = await requestJson(
        `/api/conversations/${activeConversation.id}`,
      );
      deletingMessageId = null;
      await refreshConversationSummaries();
      renderMessages();
      setFeedback("问答已删除。", "success");
    } catch (error) {
      setFeedback(error.message, "error");
    }
  }

  renderMessages();
});

messageList.addEventListener("submit", async (event) => {
  const form = event.target.closest(".message-edit-form");
  if (!form || !activeConversation) return;
  event.preventDefault();

  const id = Number(form.dataset.messageId);
  const message = new FormData(form).get("message").trim();
  if (!message) {
    setFeedback("修改后的消息不能为空。", "error");
    return;
  }

  const saveButton = form.querySelector("button[type='submit']");
  saveButton.disabled = true;
  try {
    const updated = await requestJson(
      `/api/conversations/${activeConversation.id}/messages/${id}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      },
    );
    activeConversation.messages = activeConversation.messages.map((item) =>
      item.id === id ? updated : item,
    );
    editingMessageId = null;
    renderMessages();
    setFeedback("用户消息已修改。", "success");
  } catch (error) {
    saveButton.disabled = false;
    setFeedback(error.message, "error");
  }
});

loadConversations();
