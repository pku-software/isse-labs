const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const feedback = document.querySelector("#form-feedback");
const connectionStatus = document.querySelector("#connection-status");

let messages = [];

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

function renderMessages() {
  messageList.replaceChildren();

  for (const record of messages) {
    const card = document.createElement("article");
    card.className = "message-card";

    const userRow = createMessageRow("你", record.message, "user-message");
    const assistantRow = createMessageRow("AI", record.reply, "assistant-message");
    const actions = document.createElement("div");
    actions.className = "message-actions";
    actions.append(
      createActionButton("修改", "secondary-button", () => showEditor(card, record)),
      createActionButton("删除", "danger-button", () => showDeleteConfirmation(card, record)),
    );

    card.append(userRow, assistantRow, actions);
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

function removeInlinePanels(card) {
  card.querySelectorAll(".inline-editor, .delete-confirmation").forEach((panel) => panel.remove());
}

function showEditor(card, record) {
  removeInlinePanels(card);

  const editor = document.createElement("div");
  editor.className = "inline-editor";
  editor.innerHTML = `
    <label for="edit-message-${record.id}">修改消息</label>
    <textarea id="edit-message-${record.id}" rows="3"></textarea>
    <div class="inline-actions"></div>
  `;

  const input = editor.querySelector("textarea");
  input.value = record.message;
  const inlineActions = editor.querySelector(".inline-actions");
  inlineActions.append(
    createActionButton("取消", "secondary-button", () => editor.remove()),
    createActionButton("保存", "primary-button", () => updateMessage(record.id, input.value)),
  );

  card.append(editor);
  input.focus();
}

function showDeleteConfirmation(card, record) {
  removeInlinePanels(card);

  const confirmation = document.createElement("div");
  confirmation.className = "delete-confirmation";

  const text = document.createElement("p");
  text.textContent = "确定删除这条聊天记录吗？";

  const inlineActions = document.createElement("div");
  inlineActions.className = "inline-actions";
  inlineActions.append(
    createActionButton("取消", "secondary-button", () => confirmation.remove()),
    createActionButton("确认删除", "danger-button", () => deleteMessage(record.id)),
  );

  confirmation.append(text, inlineActions);
  card.append(confirmation);
}

async function loadMessages() {
  connectionStatus.textContent = "正在连接";
  try {
    messages = await requestJson("/api/messages");
    renderMessages();
    connectionStatus.textContent = "已连接";
    setFeedback("聊天记录已加载。");
  } catch (error) {
    connectionStatus.textContent = "连接失败";
    setFeedback(error.message, true);
  }
}

async function createMessage(message) {
  const record = await requestJson("/api/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  messages.push(record);
  renderMessages();
}

async function updateMessage(id, message) {
  const trimmedMessage = message.trim();
  if (!trimmedMessage) {
    setFeedback("修改后的消息不能为空。", true);
    return;
  }

  try {
    const updated = await requestJson(`/api/messages/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmedMessage }),
    });
    messages = messages.map((item) => (item.id === id ? updated : item));
    renderMessages();
    setFeedback("聊天记录已修改。");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

async function deleteMessage(id) {
  try {
    await requestJson(`/api/messages/${id}`, { method: "DELETE" });
    messages = messages.filter((item) => item.id !== id);
    renderMessages();
    setFeedback("聊天记录已删除。");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();

  if (!message) {
    setFeedback("请输入消息后再发送。", true);
    messageInput.focus();
    return;
  }

  sendButton.disabled = true;
  setFeedback("正在发送……");
  try {
    await createMessage(message);
    messageInput.value = "";
    setFeedback("消息已发送。");
  } catch (error) {
    setFeedback(error.message, true);
  } finally {
    sendButton.disabled = false;
  }
});

loadMessages();
