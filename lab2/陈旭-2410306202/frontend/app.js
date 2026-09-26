// 前端逻辑：用 fetch() 调用同一个 Flask 服务提供的 API。
// 所有请求都写成相对 URL（例如 "/api/messages"），浏览器会自动把它接到当前页面的地址上，
// 所以这里不需要（也不应该）写死 http://localhost:5001。

const chatList = document.getElementById("chat-list");
const emptyState = document.getElementById("empty-state");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const statusEl = document.getElementById("status");

// 当前页面里的聊天记录，内容来自后端 GET /api/messages
let messages = [];

// ---------- 小工具 ----------

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle("is-error", isError);
}

// 统一处理请求：解析 JSON，把非 2xx 的响应变成异常，交给调用处显示在页面上
async function request(url, options = {}) {
  const response = await fetch(url, options);

  let data = null;
  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }

  if (!response.ok) {
    const reason = data && data.error ? data.error : `请求失败（HTTP ${response.status}）`;
    throw new Error(reason);
  }

  return data;
}

function createBubble(className, text) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${className}`;

  const paragraph = document.createElement("p");
  paragraph.className = "bubble-text";
  // 用 textContent 而不是 innerHTML：用户输入的内容只作为文本显示，不会被当成 HTML 执行
  paragraph.textContent = text;

  bubble.appendChild(paragraph);
  return bubble;
}

function createButton(className, text) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `btn ${className}`;
  button.textContent = text;
  return button;
}

// ---------- 渲染 ----------

function renderMessages() {
  chatList.querySelectorAll(".message").forEach((node) => node.remove());

  if (messages.length === 0) {
    emptyState.hidden = false;
    return;
  }

  emptyState.hidden = true;
  messages.forEach((record) => {
    chatList.appendChild(createMessageElement(record));
  });
}

function createMessageElement(record) {
  const article = document.createElement("article");
  article.className = "message";
  article.dataset.id = record.id;

  article.appendChild(createBubble("bubble-user", record.message));
  article.appendChild(createBubble("bubble-reply", record.reply));

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const editButton = createButton("btn-edit", "修改");
  editButton.addEventListener("click", () => startEdit(article, record));

  const deleteButton = createButton("btn-delete", "删除");
  deleteButton.addEventListener("click", () => startDelete(article, record, actions));

  actions.appendChild(editButton);
  actions.appendChild(deleteButton);
  article.appendChild(actions);

  return article;
}

// ---------- 修改：改成页面内的编辑区，不用 prompt() ----------

function startEdit(article, record) {
  const actions = article.querySelector(".message-actions");
  actions.hidden = true;

  const editArea = document.createElement("div");
  editArea.className = "edit-area";

  const label = document.createElement("label");
  label.className = "edit-label";
  label.textContent = "修改这条提问";
  label.htmlFor = `edit-input-${record.id}`;

  const textarea = document.createElement("textarea");
  textarea.id = `edit-input-${record.id}`;
  textarea.className = "edit-input";
  textarea.rows = 2;
  textarea.value = record.message;

  const errorLine = document.createElement("p");
  errorLine.className = "edit-error";

  const editActions = document.createElement("div");
  editActions.className = "edit-actions";

  const saveButton = createButton("btn-primary", "保存");
  const cancelButton = createButton("btn-cancel", "取消");

  cancelButton.addEventListener("click", () => {
    editArea.remove();
    actions.hidden = false;
  });

  saveButton.addEventListener("click", async () => {
    const text = textarea.value.trim();
    if (!text) {
      errorLine.textContent = "修改后的内容不能为空";
      return;
    }

    saveButton.disabled = true;
    setStatus("正在保存…");

    try {
      const updated = await request(`/api/messages/${record.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      messages = messages.map((item) => (item.id === updated.id ? updated : item));
      renderMessages();
      setStatus(`已修改第 ${updated.id} 条记录`);
    } catch (error) {
      saveButton.disabled = false;
      errorLine.textContent = error.message;
      setStatus(`修改失败：${error.message}`, true);
    }
  });

  editActions.appendChild(saveButton);
  editActions.appendChild(cancelButton);
  editArea.appendChild(label);
  editArea.appendChild(textarea);
  editArea.appendChild(errorLine);
  editArea.appendChild(editActions);
  article.appendChild(editArea);

  textarea.focus();
}

// ---------- 删除：改成页面内的确认行，不用 confirm() ----------

function startDelete(article, record, actions) {
  actions.hidden = true;

  const row = document.createElement("div");
  row.className = "confirm-row";

  const question = document.createElement("span");
  question.textContent = `确定删除第 ${record.id} 条记录吗？`;

  const confirmButton = createButton("btn-danger", "确定删除");
  const cancelButton = createButton("btn-cancel", "取消");

  cancelButton.addEventListener("click", () => {
    row.remove();
    actions.hidden = false;
  });

  confirmButton.addEventListener("click", async () => {
    confirmButton.disabled = true;
    setStatus("正在删除…");

    try {
      await request(`/api/messages/${record.id}`, { method: "DELETE" });
      messages = messages.filter((item) => item.id !== record.id);
      renderMessages();
      setStatus(`已删除第 ${record.id} 条记录`);
    } catch (error) {
      confirmButton.disabled = false;
      setStatus(`删除失败：${error.message}`, true);
    }
  });

  row.appendChild(question);
  row.appendChild(confirmButton);
  row.appendChild(cancelButton);
  article.appendChild(row);
}

// ---------- 发送：调用 POST /api/messages ----------

async function sendMessage() {
  const text = messageInput.value.trim();
  if (!text) {
    setStatus("请先输入内容再发送", true);
    return;
  }

  sendButton.disabled = true;
  setStatus("发送中…");

  try {
    const record = await request("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    messages.push(record);
    messageInput.value = "";
    renderMessages();
    setStatus(`已添加第 ${record.id} 条记录`);
  } catch (error) {
    setStatus(`发送失败：${error.message}`, true);
  } finally {
    sendButton.disabled = false;
  }
}

// ---------- 页面打开时加载已有记录 ----------

async function loadMessages() {
  setStatus("正在加载聊天记录…");

  try {
    messages = await request("/api/messages");
    renderMessages();
    setStatus("");
  } catch (error) {
    setStatus(`加载失败：${error.message}`, true);
  }
}

sendButton.addEventListener("click", sendMessage);
loadMessages();
