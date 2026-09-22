const conversationList = document.querySelector("#conversation-list");
const newConversationForm = document.querySelector("#new-conversation-form");
const newConversationTitle = document.querySelector("#new-conversation-title");
const currentConversationTitle = document.querySelector("#current-conversation-title");
const conversationControls = document.querySelector("#conversation-controls");
const conversationPanel = document.querySelector("#conversation-panel");
const renameConversationButton = document.querySelector("#rename-conversation-button");
const deleteConversationButton = document.querySelector("#delete-conversation-button");
const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const feedback = document.querySelector("#form-feedback");
const connectionStatus = document.querySelector("#connection-status");

let conversationSummaries = [];
let currentConversation = null;

function setFeedback(text, isError = false) {
  feedback.textContent = text;
  feedback.classList.toggle("error-text", isError);
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `请求失败（${response.status}）`);
  }

  return data;
}

function createActionButton(label, className, handler) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", handler);
  return button;
}

function clearSelection() {
  currentConversation = null;
  currentConversationTitle.textContent = "请选择一个会话";
  conversationControls.classList.add("hidden");
  conversationPanel.replaceChildren();
  messageList.replaceChildren();
  messageInput.value = "";
  messageInput.disabled = true;
  sendButton.disabled = true;
  setFeedback("请先创建或选择一个会话。");
  renderConversationList();
}

function renderConversationList() {
  conversationList.replaceChildren();

  for (const summary of conversationSummaries) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "conversation-item";
    if (currentConversation?.id === summary.id) {
      button.classList.add("active");
    }

    const title = document.createElement("strong");
    title.textContent = summary.title;
    const count = document.createElement("span");
    count.textContent = `${Math.floor(summary.message_count / 2)} 轮对话`;
    button.append(title, count);
    button.addEventListener("click", () => selectConversation(summary.id));
    conversationList.append(button);
  }
}

function updateCurrentSummary() {
  if (!currentConversation) {
    return;
  }

  conversationSummaries = conversationSummaries.map((summary) => (
    summary.id === currentConversation.id
      ? {
          id: currentConversation.id,
          title: currentConversation.title,
          message_count: currentConversation.messages.length,
        }
      : summary
  ));
  renderConversationList();
}

async function loadConversations(preferredId = null) {
  connectionStatus.textContent = "正在连接";
  try {
    conversationSummaries = await requestJson("/api/conversations");
    renderConversationList();

    const currentId = preferredId ?? currentConversation?.id;
    const target = conversationSummaries.find((item) => item.id === currentId)
      || conversationSummaries[0];

    if (target) {
      await selectConversation(target.id);
    } else {
      clearSelection();
    }
    connectionStatus.textContent = "已连接";
  } catch (error) {
    connectionStatus.textContent = "连接失败";
    setFeedback(error.message, true);
  }
}

async function selectConversation(id) {
  try {
    currentConversation = await requestJson(`/api/conversations/${id}`);
    currentConversationTitle.textContent = currentConversation.title;
    conversationControls.classList.remove("hidden");
    conversationPanel.replaceChildren();
    messageInput.disabled = false;
    sendButton.disabled = false;
    renderConversationList();
    renderMessages();
    setFeedback("已加载当前会话。");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

function getTurns() {
  const turns = new Map();
  for (const message of currentConversation?.messages || []) {
    if (!turns.has(message.turn_id)) {
      turns.set(message.turn_id, { turnId: message.turn_id });
    }
    turns.get(message.turn_id)[message.role] = message;
  }
  return [...turns.values()];
}

function renderMessages() {
  messageList.replaceChildren();
  if (!currentConversation) {
    return;
  }

  for (const turn of getTurns()) {
    const card = document.createElement("article");
    card.className = "message-card";

    if (turn.user) {
      card.append(createMessageRow("你", turn.user.content, "user-message"));
    }
    if (turn.assistant) {
      card.append(createMessageRow("AI", turn.assistant.content, "assistant-message"));
    }

    const actions = document.createElement("div");
    actions.className = "message-actions";
    actions.append(
      createActionButton("修改", "secondary-button", () => showTurnEditor(card, turn)),
      createActionButton("删除", "danger-button", () => showTurnDelete(card, turn)),
    );
    card.append(actions);
    messageList.append(card);
  }
}

function createMessageRow(role, text, className) {
  const row = document.createElement("div");
  row.className = `message-row ${className}`;

  const roleLabel = document.createElement("span");
  roleLabel.className = "role";
  roleLabel.textContent = role;

  const content = document.createElement("p");
  content.textContent = text;
  row.append(roleLabel, content);
  return row;
}

function removeCardPanels(card) {
  card.querySelectorAll(".inline-editor, .delete-confirmation").forEach((panel) => panel.remove());
}

function showTurnEditor(card, turn) {
  removeCardPanels(card);
  const editor = document.createElement("div");
  editor.className = "inline-editor";

  const label = document.createElement("label");
  label.textContent = "修改用户消息（已有 AI 回复不会重新生成）";
  const input = document.createElement("textarea");
  input.rows = 3;
  input.value = turn.user?.content || "";
  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(
    createActionButton("取消", "secondary-button", () => editor.remove()),
    createActionButton("保存", "primary-button", () => updateTurn(turn.turnId, input.value)),
  );

  editor.append(label, input, actions);
  card.append(editor);
  input.focus();
}

function showTurnDelete(card, turn) {
  removeCardPanels(card);
  const confirmation = document.createElement("div");
  confirmation.className = "delete-confirmation";

  const text = document.createElement("p");
  text.textContent = "确定删除这一轮用户消息和 AI 回复吗？";
  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(
    createActionButton("取消", "secondary-button", () => confirmation.remove()),
    createActionButton("确认删除", "danger-button", () => deleteTurn(turn.turnId)),
  );
  confirmation.append(text, actions);
  card.append(confirmation);
}

async function updateTurn(turnId, message) {
  const trimmed = message.trim();
  if (!trimmed) {
    setFeedback("修改后的消息不能为空。", true);
    return;
  }

  try {
    currentConversation = await requestJson(
      `/api/conversations/${currentConversation.id}/turns/${turnId}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      },
    );
    renderMessages();
    setFeedback("消息已修改，原有 AI 回复保持不变。");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

async function deleteTurn(turnId) {
  try {
    currentConversation = await requestJson(
      `/api/conversations/${currentConversation.id}/turns/${turnId}`,
      { method: "DELETE" },
    );
    updateCurrentSummary();
    renderMessages();
    setFeedback("这一轮对话已删除。");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

function showRenameConversation() {
  conversationPanel.replaceChildren();
  const panel = document.createElement("div");
  panel.className = "inline-editor";
  const label = document.createElement("label");
  label.textContent = "新的会话名称";
  const input = document.createElement("input");
  input.type = "text";
  input.maxLength = 60;
  input.value = currentConversation.title;
  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(
    createActionButton("取消", "secondary-button", () => panel.remove()),
    createActionButton("保存", "primary-button", () => renameConversation(input.value)),
  );
  panel.append(label, input, actions);
  conversationPanel.append(panel);
  input.focus();
}

async function renameConversation(title) {
  const trimmed = title.trim();
  if (!trimmed) {
    setFeedback("会话名称不能为空。", true);
    return;
  }

  try {
    currentConversation = await requestJson(`/api/conversations/${currentConversation.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: trimmed }),
    });
    currentConversationTitle.textContent = currentConversation.title;
    conversationPanel.replaceChildren();
    updateCurrentSummary();
    setFeedback("会话已重命名。");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

function showDeleteConversation() {
  conversationPanel.replaceChildren();
  const panel = document.createElement("div");
  panel.className = "delete-confirmation";
  const text = document.createElement("p");
  text.textContent = `确定删除会话“${currentConversation.title}”及其中全部消息吗？`;
  const actions = document.createElement("div");
  actions.className = "inline-actions";
  actions.append(
    createActionButton("取消", "secondary-button", () => panel.remove()),
    createActionButton("确认删除", "danger-button", deleteConversation),
  );
  panel.append(text, actions);
  conversationPanel.append(panel);
}

async function deleteConversation() {
  try {
    await requestJson(`/api/conversations/${currentConversation.id}`, { method: "DELETE" });
    currentConversation = null;
    await loadConversations();
    setFeedback("会话已删除。");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

newConversationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = newConversationTitle.value.trim();
  if (!title) {
    setFeedback("请输入新会话名称。", true);
    newConversationTitle.focus();
    return;
  }

  try {
    const created = await requestJson("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    newConversationTitle.value = "";
    await loadConversations(created.id);
    setFeedback("新会话已创建。");
  } catch (error) {
    setFeedback(error.message, true);
  }
});

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentConversation) {
    setFeedback("请先选择一个会话。", true);
    return;
  }

  const message = messageInput.value.trim();
  if (!message) {
    setFeedback("请输入消息后再发送。", true);
    messageInput.focus();
    return;
  }

  sendButton.disabled = true;
  setFeedback("正在等待 AI 回复……");
  try {
    currentConversation = await requestJson(
      `/api/conversations/${currentConversation.id}/messages`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      },
    );
    messageInput.value = "";
    updateCurrentSummary();
    renderMessages();
    setFeedback("AI 已回复。");
  } catch (error) {
    setFeedback(error.message, true);
  } finally {
    sendButton.disabled = false;
  }
});

renameConversationButton.addEventListener("click", showRenameConversation);
deleteConversationButton.addEventListener("click", showDeleteConversation);

loadConversations();
