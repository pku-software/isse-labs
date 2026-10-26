const messageList = document.getElementById("message-list");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const statusElement = document.getElementById("status");

function setStatus(text, isError = false) {
  statusElement.textContent = text;
  statusElement.className = isError ? "status error" : "status";
}

async function requestJSON(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.error || `请求失败（${response.status}）`);
  }
  return data;
}

function createMessageElement(record) {
  const item = document.createElement("li");
  item.className = "message";
  item.dataset.id = record.id;

  const content = document.createElement("div");
  content.className = "message-content";

  const userText = document.createElement("p");
  userText.className = "message-user";
  userText.textContent = record.message;

  const replyText = document.createElement("p");
  replyText.className = "message-reply";
  replyText.textContent = record.reply;

  content.append(userText, replyText);

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const editButton = document.createElement("button");
  editButton.type = "button";
  editButton.className = "edit-button";
  editButton.textContent = "修改";

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "delete-button";
  deleteButton.textContent = "删除";

  actions.append(editButton, deleteButton);
  item.append(content, actions);
  return item;
}

function renderMessages(records) {
  messageList.replaceChildren(
    ...records.map((record) => createMessageElement(record))
  );
}

async function loadMessages() {
  try {
    const records = await requestJSON("/api/messages");
    renderMessages(records);
    setStatus("");
  } catch (error) {
    setStatus(error.message, true);
  }
}

function enterEditMode(item) {
  const content = item.querySelector(".message-content");
  const currentMessage = item.querySelector(".message-user").textContent;

  content.replaceChildren();

  const input = document.createElement("input");
  input.type = "text";
  input.className = "edit-input";
  input.value = currentMessage;

  const saveButton = document.createElement("button");
  saveButton.type = "button";
  saveButton.textContent = "保存";

  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.textContent = "取消";

  content.append(input, saveButton, cancelButton);
  input.focus();

  saveButton.addEventListener("click", async () => {
    const newMessage = input.value.trim();
    if (!newMessage) {
      setStatus("消息不能为空", true);
      return;
    }

    try {
      await requestJSON(`/api/messages/${item.dataset.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newMessage }),
      });
      await loadMessages();
      setStatus("修改成功");
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  cancelButton.addEventListener("click", loadMessages);
}

function enterDeleteConfirm(item) {
  const actions = item.querySelector(".message-actions");
  actions.replaceChildren();

  const prompt = document.createElement("span");
  prompt.className = "confirm-text";
  prompt.textContent = "确认删除？";

  const confirmButton = document.createElement("button");
  confirmButton.type = "button";
  confirmButton.textContent = "确认";

  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.textContent = "取消";

  actions.append(prompt, confirmButton, cancelButton);

  confirmButton.addEventListener("click", async () => {
    try {
      await requestJSON(`/api/messages/${item.dataset.id}`, {
        method: "DELETE",
      });
      await loadMessages();
      setStatus("删除成功");
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  cancelButton.addEventListener("click", loadMessages);
}

messageList.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;

  const item = event.target.closest(".message");
  if (!item) return;

  if (button.classList.contains("edit-button")) {
    enterEditMode(item);
  } else if (button.classList.contains("delete-button")) {
    enterDeleteConfirm(item);
  }
});

async function sendMessage() {
  const message = messageInput.value.trim();
  if (!message) {
    setStatus("请输入消息", true);
    return;
  }

  setStatus("发送中...");
  try {
    await requestJSON("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    messageInput.value = "";
    await loadMessages();
    setStatus("发送成功");
  } catch (error) {
    setStatus(error.message, true);
  }
}

sendButton.addEventListener("click", sendMessage);
messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});

loadMessages();
