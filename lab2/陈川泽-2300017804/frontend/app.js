const messageList = document.querySelector("#message-list");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const feedback = document.querySelector("#feedback");

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

function makeExchange(record) {
  const exchange = document.createElement("article");
  exchange.className = "exchange";
  exchange.append(
    makeMessageRow("你", record.message, true),
    makeMessageRow("助手", record.reply, false),
  );

  const actions = document.createElement("div");
  actions.className = "record-actions";
  const editForm = document.createElement("form");
  editForm.className = "inline-panel";
  editForm.hidden = true;
  const editLabel = document.createElement("label");
  editLabel.textContent = "修改消息";
  const editInput = document.createElement("textarea");
  editInput.value = record.message;
  editInput.rows = 2;
  editInput.required = true;
  editLabel.append(editInput);
  const editControls = document.createElement("div");
  editControls.className = "inline-controls";
  const saveButton = document.createElement("button");
  saveButton.type = "submit";
  saveButton.className = "small-button";
  saveButton.textContent = "保存";
  editControls.append(
    saveButton,
    makeButton("取消", "text-button", () => { editForm.hidden = true; }),
  );
  editForm.append(editLabel, editControls);

  const deletePanel = document.createElement("div");
  deletePanel.className = "inline-panel";
  deletePanel.hidden = true;
  const deleteText = document.createElement("p");
  deleteText.textContent = "确定删除这条聊天记录吗？";
  const deleteControls = document.createElement("div");
  deleteControls.className = "inline-controls";
  deleteControls.append(
    makeButton("确认删除", "small-button delete-confirm", async () => {
      try {
        await apiRequest(`/api/messages/${record.id}`, { method: "DELETE" });
        await loadMessages();
        showFeedback("聊天记录已删除");
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
      await apiRequest(`/api/messages/${record.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      await loadMessages();
      showFeedback("聊天记录已修改");
    } catch (error) {
      showFeedback(error.message, true);
    }
  });

  exchange.append(actions, editForm, deletePanel);
  return exchange;
}

async function loadMessages() {
  const messages = await apiRequest("/api/messages");
  messageList.replaceChildren();
  if (messages.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "还没有聊天记录，发送一条消息开始吧。";
    messageList.append(empty);
    return;
  }
  messageList.append(...messages.map(makeExchange));
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    showFeedback("请输入消息", true);
    return;
  }

  const sendButton = messageForm.querySelector(".send-button");
  sendButton.disabled = true;
  showFeedback("正在发送……");
  try {
    await apiRequest("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    messageInput.value = "";
    await loadMessages();
    showFeedback("消息已发送");
  } catch (error) {
    showFeedback(error.message, true);
  } finally {
    sendButton.disabled = false;
  }
});

loadMessages().catch((error) => showFeedback(error.message, true));
