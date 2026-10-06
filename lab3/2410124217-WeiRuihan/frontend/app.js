const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message");
const messageList = document.querySelector("#message-list");
const status = document.querySelector("#status");

function showStatus(text, isError = false) {
  status.textContent = text;
  status.classList.toggle("error", isError);
}

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (response.status === 204) {
    return null;
  }

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

function createButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  if (className) {
    button.className = className;
  }
  button.addEventListener("click", onClick);
  return button;
}

function renderMessages(records) {
  messageList.replaceChildren();

  if (records.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "还没有聊天记录。发送第一条消息吧。";
    messageList.append(empty);
    return;
  }

  for (const record of records) {
    const card = document.createElement("article");
    card.className = "message-card";

    const content = document.createElement("div");
    const userLabel = document.createElement("p");
    userLabel.className = "message-label";
    userLabel.textContent = "用户";
    const userMessage = document.createElement("p");
    userMessage.textContent = record.message;
    const aiLabel = document.createElement("p");
    aiLabel.className = "message-label ai-label";
    aiLabel.textContent = "AI";
    const reply = document.createElement("p");
    reply.textContent = record.reply;
    content.append(userLabel, userMessage, aiLabel, reply);

    const actions = document.createElement("div");
    actions.className = "message-actions";
    actions.append(
      createButton("修改", "", () => showEditForm(record, card)),
      createButton("删除", "danger", () => showDeleteConfirmation(record, card)),
    );
    card.append(content, actions);
    messageList.append(card);
  }
}

function showEditForm(record, card) {
  const editor = document.createElement("form");
  editor.className = "inline-form";
  const input = document.createElement("textarea");
  input.rows = 2;
  input.value = record.message;
  input.setAttribute("aria-label", "修改消息");
  const save = document.createElement("button");
  save.type = "submit";
  save.textContent = "保存";
  const cancel = createButton("取消", "secondary", () => loadMessages());
  editor.append(input, save, cancel);
  card.append(editor);
  input.focus();

  editor.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await request(`/api/messages/${record.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input.value }),
      });
      showStatus("消息已修改。");
      await loadMessages();
    } catch (error) {
      showStatus(error.message, true);
    }
  });
}

function showDeleteConfirmation(record, card) {
  const confirmation = document.createElement("div");
  confirmation.className = "confirmation";
  const text = document.createElement("span");
  text.textContent = "确定删除这条记录吗？";
  const confirmButton = createButton("确认删除", "danger", async () => {
    try {
      await request(`/api/messages/${record.id}`, { method: "DELETE" });
      showStatus("消息已删除。");
      await loadMessages();
    } catch (error) {
      showStatus(error.message, true);
    }
  });
  const cancelButton = createButton("取消", "secondary", () => confirmation.remove());
  confirmation.append(text, confirmButton, cancelButton);
  card.append(confirmation);
}

async function loadMessages() {
  try {
    const records = await request("/api/messages");
    renderMessages(records);
  } catch (error) {
    showStatus(error.message, true);
  }
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await request("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: messageInput.value }),
    });
    messageInput.value = "";
    showStatus("消息已发送，AI 回复为“你好”。");
    await loadMessages();
  } catch (error) {
    showStatus(error.message, true);
  }
});

loadMessages();
