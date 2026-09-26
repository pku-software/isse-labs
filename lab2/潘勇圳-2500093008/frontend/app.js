// 前端通过 fetch() 调用同一个 Flask 服务提供的 API。
// 这里用的是以 / 开头的相对 URL，浏览器会基于当前页面的地址去解析它，
// 所以从 http://localhost:5001/ 打开页面时，请求也会发给这个服务。

const API_URL = "/api/messages";

// 页面状态：全部记录、正在编辑的记录 id、正在确认删除的记录 id
let records = [];
let editingId = null;
let pendingDeleteId = null;

const els = {};

document.addEventListener("DOMContentLoaded", () => {
  els.chat = document.querySelector("#chat");
  els.empty = document.querySelector("#empty");
  els.form = document.querySelector("#composer");
  els.input = document.querySelector("#message-input");
  els.sendButton = document.querySelector("#send-button");
  els.status = document.querySelector("#status");

  els.form.addEventListener("submit", handleSubmit);

  // 页面打开时先加载已有记录
  loadMessages();
});

/* ---------------- 与后端通信 ---------------- */

async function requestJson(url, options) {
  let response;
  try {
    response = await fetch(url, options);
  } catch (error) {
    throw new Error("连不上后端服务，请确认 Flask 正在运行。");
  }

  const body = await response.text();
  let data = null;
  if (body) {
    try {
      data = JSON.parse(body);
    } catch (error) {
      data = null;
    }
  }

  if (!response.ok) {
    throw new Error((data && data.error) || `请求失败（HTTP ${response.status}）`);
  }
  return data;
}

async function loadMessages() {
  try {
    records = await requestJson(API_URL);
    render();
  } catch (error) {
    showStatus(`加载聊天记录失败：${error.message}`);
  }
}

async function handleSubmit(event) {
  event.preventDefault();

  const text = els.input.value.trim();
  if (!text) {
    showStatus("请先输入内容，再点击发送。");
    return;
  }

  clearStatus();
  setSending(true);
  try {
    const record = await requestJson(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    records.push(record);
    els.input.value = "";
    render();
  } catch (error) {
    showStatus(error.message);
  } finally {
    setSending(false);
  }
}

async function saveMessage(id, value) {
  const text = value.trim();
  if (!text) {
    showStatus("消息内容不能为空。");
    return;
  }

  clearStatus();
  try {
    const updated = await requestJson(`${API_URL}/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    records = records.map((record) => (record.id === updated.id ? updated : record));
    editingId = null;
    render();
  } catch (error) {
    showStatus(error.message);
  }
}

async function removeMessage(id) {
  clearStatus();
  try {
    await requestJson(`${API_URL}/${id}`, { method: "DELETE" });
    records = records.filter((record) => record.id !== id);
    pendingDeleteId = null;
    render();
  } catch (error) {
    showStatus(error.message);
  }
}

/* ---------------- 页面渲染 ---------------- */

function render() {
  els.chat.replaceChildren();
  records.forEach((record) => {
    els.chat.append(buildCard(record));
  });
  els.empty.hidden = records.length > 0;

  // 进入编辑模式后，把光标直接放进输入框
  if (editingId !== null) {
    const input = els.chat.querySelector(".editor__input");
    if (input) {
      input.focus();
      input.select();
    }
  }
}

function buildCard(record) {
  const card = document.createElement("article");
  card.className = "message";

  const toolbar = document.createElement("div");
  toolbar.className = "message__toolbar";

  const index = document.createElement("span");
  index.className = "message__index";
  index.textContent = `#${record.id}`;

  const actions = document.createElement("div");
  actions.className = "message__actions";

  if (editingId === record.id) {
    actions.append(
      createButton("取消", "button button--ghost", () => {
        editingId = null;
        clearStatus();
        render();
      })
    );
  } else {
    actions.append(
      createButton("修改", "button button--ghost", () => {
        editingId = record.id;
        pendingDeleteId = null;
        clearStatus();
        render();
      }),
      createButton("删除", "button button--ghost", () => {
        pendingDeleteId = record.id;
        editingId = null;
        clearStatus();
        render();
      })
    );
  }

  toolbar.append(index, actions);
  card.append(toolbar);

  if (editingId === record.id) {
    card.append(buildEditor(record));
  } else {
    card.append(buildBubble(record.message, "user"));
  }

  card.append(buildBubble(record.reply, "reply"));

  if (pendingDeleteId === record.id) {
    card.append(buildDeleteConfirm(record));
  }

  return card;
}

function buildEditor(record) {
  const editor = document.createElement("div");
  editor.className = "editor";

  const input = document.createElement("input");
  input.className = "editor__input";
  input.type = "text";
  input.value = record.message;
  input.maxLength = 500;
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      saveMessage(record.id, input.value);
    } else if (event.key === "Escape") {
      editingId = null;
      clearStatus();
      render();
    }
  });

  editor.append(
    input,
    createButton("保存", "button button--primary", () => {
      saveMessage(record.id, input.value);
    })
  );
  return editor;
}

function buildDeleteConfirm(record) {
  const bar = document.createElement("div");
  bar.className = "confirm";

  const text = document.createElement("span");
  text.textContent = "确定要删除这条记录吗？";

  const actions = document.createElement("div");
  actions.className = "confirm__actions";
  actions.append(
    createButton("确认删除", "button button--danger", () => removeMessage(record.id)),
    createButton("取消", "button button--ghost", () => {
      pendingDeleteId = null;
      clearStatus();
      render();
    })
  );

  bar.append(text, actions);
  return bar;
}

function buildBubble(text, kind) {
  const bubble = document.createElement("p");
  bubble.className = kind === "user" ? "bubble bubble--user" : "bubble bubble--reply";
  bubble.textContent = text;
  return bubble;
}

function createButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

/* ---------------- 页面状态提示 ---------------- */

function showStatus(message) {
  els.status.textContent = message;
}

function clearStatus() {
  els.status.textContent = "";
}

function setSending(isSending) {
  els.sendButton.disabled = isSending;
  els.sendButton.textContent = isSending ? "发送中…" : "发送";
}
