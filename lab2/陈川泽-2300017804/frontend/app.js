const conversationForm = document.querySelector("#conversation-form");
const conversationTitleInput = document.querySelector("#conversation-title");
const conversationList = document.querySelector("#conversation-list");
const activeTitle = document.querySelector("#active-title");
const activeCount = document.querySelector("#active-count");
const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = messageForm.querySelector(".send-button");
const feedback = document.querySelector("#feedback");

let summaries = [];
let activeConversationId = null;
let selectionVersion = 0;

function showFeedback(text, isError = false) {
  feedback.textContent = text;
  feedback.classList.toggle("feedback-error", isError);
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `请求失败（${response.status}）`);
  }
  return data;
}

function jsonOptions(method, data) {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  };
}

function makeButton(text, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = text;
  button.addEventListener("click", onClick);
  return button;
}

function makeMessageRow(speaker, content, isUser) {
  const row = document.createElement("div");
  row.className = `message-row ${isUser ? "user-row" : "assistant-row"}`;
  if (!isUser) {
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "AI";
    avatar.setAttribute("aria-hidden", "true");
    row.append(avatar);
  }
  const wrapper = document.createElement("div");
  wrapper.className = "message-content";
  const name = document.createElement("span");
  name.className = "speaker";
  name.textContent = speaker;
  const bubble = document.createElement("p");
  bubble.className = `bubble ${isUser ? "user-bubble" : "assistant-bubble"}`;
  bubble.textContent = content;
  wrapper.append(name, bubble);
  row.append(wrapper);
  return row;
}

function makeTurn(userMessage, assistantMessage) {
  const exchange = document.createElement("article");
  exchange.className = "exchange";
  exchange.append(makeMessageRow("你", userMessage.content, true));
  if (assistantMessage) {
    exchange.append(makeMessageRow("助手", assistantMessage.content, false));
  }

  const conversationId = activeConversationId;
  const turnId = userMessage.turn_id;
  const actions = document.createElement("div");
  actions.className = "record-actions";

  const editForm = document.createElement("form");
  editForm.className = "inline-panel";
  editForm.hidden = true;
  const editLabel = document.createElement("label");
  editLabel.textContent = "修改消息";
  const editInput = document.createElement("textarea");
  editInput.rows = 2;
  editInput.required = true;
  editInput.value = userMessage.content;
  editLabel.append(editInput);
  const editControls = document.createElement("div");
  editControls.className = "inline-controls";
  const saveButton = document.createElement("button");
  saveButton.type = "submit";
  saveButton.className = "small-button";
  saveButton.textContent = "保存";
  editControls.append(saveButton, makeButton("取消", "text-button", () => {
    editForm.hidden = true;
  }));
  editForm.append(editLabel, editControls);

  const deletePanel = document.createElement("div");
  deletePanel.className = "inline-panel";
  deletePanel.hidden = true;
  const deleteText = document.createElement("p");
  deleteText.textContent = "确定删除这一轮问答吗？";
  const deleteControls = document.createElement("div");
  deleteControls.className = "inline-controls";
  deleteControls.append(
    makeButton("确认删除", "small-button delete-confirm", async () => {
      try {
        await apiRequest(`/api/conversations/${conversationId}/messages/${turnId}`, { method: "DELETE" });
        await refreshConversationList(activeConversationId);
        showFeedback("这一轮问答已删除");
      } catch (error) {
        showFeedback(error.message, true);
      }
    }),
    makeButton("取消", "text-button", () => { deletePanel.hidden = true; }),
  );
  deletePanel.append(deleteText, deleteControls);

  actions.append(
    makeButton("修改", "text-button", () => {
      deletePanel.hidden = true;
      editForm.hidden = false;
      editInput.focus();
    }),
    makeButton("删除", "text-button danger-button", () => {
      editForm.hidden = true;
      deletePanel.hidden = false;
    }),
  );

  editForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = editInput.value.trim();
    if (!message) {
      showFeedback("消息不能为空", true);
      return;
    }
    try {
      await apiRequest(
        `/api/conversations/${conversationId}/messages/${turnId}`,
        jsonOptions("PATCH", { message }),
      );
      await refreshConversationList(activeConversationId);
      showFeedback("消息已修改");
    } catch (error) {
      showFeedback(error.message, true);
    }
  });

  exchange.append(actions, editForm, deletePanel);
  return exchange;
}

function renderMessages(conversation) {
  activeTitle.textContent = conversation.title;
  const userMessages = conversation.messages.filter((item) => item.role === "user");
  activeCount.textContent = `${userMessages.length} 轮问答`;
  messageList.replaceChildren();
  if (userMessages.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "这个会话还没有消息，发送第一条消息吧。";
    messageList.append(empty);
    return;
  }
  const replies = new Map(
    conversation.messages.filter((item) => item.role === "assistant")
      .map((item) => [item.turn_id, item]),
  );
  messageList.append(...userMessages.map((item) => makeTurn(item, replies.get(item.turn_id))));
}

function clearSelection() {
  activeConversationId = null;
  activeTitle.textContent = "请选择或创建会话";
  activeCount.textContent = "";
  messageList.replaceChildren();
  messageInput.disabled = true;
  sendButton.disabled = true;
}

async function selectConversation(id) {
  const version = ++selectionVersion;
  const conversation = await apiRequest(`/api/conversations/${id}`);
  if (version !== selectionVersion) return;
  activeConversationId = id;
  messageInput.disabled = false;
  sendButton.disabled = false;
  renderMessages(conversation);
  renderConversations();
}

function renderConversations() {
  conversationList.replaceChildren();
  if (summaries.length === 0) {
    const empty = document.createElement("p");
    empty.className = "conversation-meta";
    empty.textContent = "还没有会话，先创建一个。";
    conversationList.append(empty);
    return;
  }

  for (const summary of summaries) {
    const item = document.createElement("article");
    item.className = `conversation-item${summary.id === activeConversationId ? " active" : ""}`;
    const selectButton = makeButton(summary.title, "conversation-select", () => {
      selectConversation(summary.id).catch((error) => showFeedback(error.message, true));
    });
    const count = document.createElement("p");
    count.className = "conversation-meta";
    count.textContent = `${summary.message_count} 轮问答`;

    const renamePanel = document.createElement("form");
    renamePanel.className = "inline-panel";
    renamePanel.hidden = true;
    const renameLabel = document.createElement("label");
    renameLabel.textContent = "会话名称";
    const renameInput = document.createElement("input");
    renameInput.type = "text";
    renameInput.required = true;
    renameInput.value = summary.title;
    renameLabel.append(renameInput);
    const renameControls = document.createElement("div");
    renameControls.className = "inline-controls";
    const saveButton = document.createElement("button");
    saveButton.type = "submit";
    saveButton.className = "small-button";
    saveButton.textContent = "保存";
    renameControls.append(saveButton, makeButton("取消", "text-button", () => {
      renamePanel.hidden = true;
    }));
    renamePanel.append(renameLabel, renameControls);
    renamePanel.addEventListener("submit", async (event) => {
      event.preventDefault();
      const title = renameInput.value.trim();
      if (!title) {
        showFeedback("会话标题不能为空", true);
        return;
      }
      try {
        await apiRequest(`/api/conversations/${summary.id}`, jsonOptions("PATCH", { title }));
        await refreshConversationList(activeConversationId);
        showFeedback("会话已重命名");
      } catch (error) {
        showFeedback(error.message, true);
      }
    });

    const deletePanel = document.createElement("div");
    deletePanel.className = "inline-panel";
    deletePanel.hidden = true;
    const deleteText = document.createElement("p");
    deleteText.textContent = "确定删除这个会话及其全部消息吗？";
    const deleteControls = document.createElement("div");
    deleteControls.className = "inline-controls";
    deleteControls.append(
      makeButton("确认删除", "small-button delete-confirm", async () => {
        try {
          await apiRequest(`/api/conversations/${summary.id}`, { method: "DELETE" });
          await refreshConversationList(activeConversationId === summary.id ? null : activeConversationId);
          showFeedback("会话已删除");
        } catch (error) {
          showFeedback(error.message, true);
        }
      }),
      makeButton("取消", "text-button", () => { deletePanel.hidden = true; }),
    );
    deletePanel.append(deleteText, deleteControls);

    const actions = document.createElement("div");
    actions.className = "conversation-actions";
    actions.append(
      makeButton("重命名", "text-button", () => {
        deletePanel.hidden = true;
        renamePanel.hidden = false;
        renameInput.focus();
      }),
      makeButton("删除", "text-button danger-button", () => {
        renamePanel.hidden = true;
        deletePanel.hidden = false;
      }),
    );
    item.append(selectButton, count, actions, renamePanel, deletePanel);
    conversationList.append(item);
  }
}

async function refreshConversationList(preferredId = activeConversationId) {
  summaries = await apiRequest("/api/conversations");
  const targetId = summaries.some((item) => item.id === preferredId)
    ? preferredId : summaries[0]?.id;
  if (targetId === undefined) {
    ++selectionVersion;
    clearSelection();
    renderConversations();
    return;
  }
  await selectConversation(targetId);
}

conversationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = conversationTitleInput.value.trim();
  if (!title) {
    showFeedback("请输入会话名称", true);
    return;
  }
  try {
    const conversation = await apiRequest("/api/conversations", jsonOptions("POST", { title }));
    conversationTitleInput.value = "";
    await refreshConversationList(conversation.id);
    showFeedback("会话已创建");
  } catch (error) {
    showFeedback(error.message, true);
  }
});

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (activeConversationId === null) return;
  const message = messageInput.value.trim();
  if (!message) {
    showFeedback("请输入消息", true);
    return;
  }
  const conversationId = activeConversationId;
  sendButton.disabled = true;
  showFeedback("正在等待 AI 回复……");
  try {
    await apiRequest(
      `/api/conversations/${conversationId}/messages`,
      jsonOptions("POST", { message }),
    );
    messageInput.value = "";
    await refreshConversationList(activeConversationId);
    showFeedback("消息已发送");
  } catch (error) {
    showFeedback(error.message, true);
  } finally {
    sendButton.disabled = activeConversationId === null;
  }
});

refreshConversationList().catch((error) => showFeedback(error.message, true));
