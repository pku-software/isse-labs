const messageList = document.querySelector("#message-list");
const emptyState = document.querySelector("#empty-state");
const messageTemplate = document.querySelector("#message-template");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const statusMessage = document.querySelector("#status-message");

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

function updateEmptyState() {
  emptyState.hidden = messageList.querySelector(".message-record") !== null;
}

function setRecordBusy(article, busy) {
  article.setAttribute("aria-busy", String(busy));
  article.querySelectorAll("button, textarea").forEach((control) => {
    control.disabled = busy;
  });
}

function createRecordElement(record) {
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

  article.setAttribute("aria-label", `问答 ${record.id}`);
  article.querySelector(".record-label").textContent = `问答 #${record.id}`;
  // 使用 textContent，把输入当作文本显示，不作为 HTML 执行。
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
    const message = editInput.value.trim();
    if (!message) {
      showStatus(recordStatus, "请输入非空消息。", true);
      editInput.focus();
      return;
    }

    setRecordBusy(article, true);
    showStatus(recordStatus, "正在保存……");
    try {
      record = await apiRequest(`/api/messages/${record.id}`, {
        method: "PATCH",
        body: JSON.stringify({ message }),
      });
      question.textContent = record.message;
      reply.textContent = record.reply;
      editForm.hidden = true;
      showStatus(recordStatus, "已保存。");
    } catch (error) {
      showStatus(recordStatus, error.message, true);
    } finally {
      setRecordBusy(article, false);
    }
    if (editForm.hidden) editStart.focus();
  });

  deleteConfirm.addEventListener("click", async () => {
    setRecordBusy(article, true);
    showStatus(recordStatus, "正在删除……");
    try {
      await apiRequest(`/api/messages/${record.id}`, { method: "DELETE" });
      article.remove();
      updateEmptyState();
      showStatus(statusMessage, "已删除记录。");
      messageInput.focus();
    } catch (error) {
      showStatus(recordStatus, error.message, true);
    } finally {
      setRecordBusy(article, false);
    }
  });

  return article;
}

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (sendButton.disabled) return;

  const message = messageInput.value.trim();
  if (!message) {
    showStatus(statusMessage, "请输入消息后再发送。", true);
    messageInput.focus();
    return;
  }

  sendButton.disabled = true;
  messageInput.disabled = true;
  showStatus(statusMessage, "正在发送……");
  try {
    const record = await apiRequest("/api/messages", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    messageList.append(createRecordElement(record));
    updateEmptyState();
    messageInput.value = "";
    showStatus(statusMessage, "消息已发送。");
  } catch (error) {
    showStatus(statusMessage, error.message, true);
  } finally {
    sendButton.disabled = false;
    messageInput.disabled = false;
    messageInput.focus();
  }
});

async function loadMessages() {
  try {
    const records = await apiRequest("/api/messages");
    for (const record of records) {
      messageList.append(createRecordElement(record));
    }
    emptyState.textContent = "还没有聊天记录，写下第一条消息开始吧。";
    updateEmptyState();
    sendButton.disabled = false;
  } catch (error) {
    showStatus(emptyState, `${error.message} 请刷新页面重试。`, true);
  } finally {
    messageList.setAttribute("aria-busy", "false");
  }
}

loadMessages();
