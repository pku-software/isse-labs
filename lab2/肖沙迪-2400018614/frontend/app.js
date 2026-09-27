/**
 * 前端脚本：通过相对 URL 调用同一个 Flask 服务提供的 API。
 *
 * 所有数据的读写都走 API，页面本身不保存数据；
 * 加载、错误和确认等反馈全部显示在页面元素中，不使用浏览器弹窗。
 */

const messageList = document.getElementById("message-list");
const composer = document.getElementById("composer");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const statusBar = document.getElementById("status");

/** 当前页面展示的聊天记录，与后端返回的数据保持一致 */
let records = [];
/** 是否正在等待上一次请求返回 */
let pending = false;

function setStatus(text, type) {
  statusBar.textContent = text;
  statusBar.className = type ? `status status-${type}` : "status";
}

/** 发送请求，成功时返回解析后的 JSON，失败时抛出带后端错误信息的异常 */
async function callApi(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();

  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch (error) {
      payload = null;
    }
  }

  if (!response.ok) {
    const reason =
      payload && payload.error ? payload.error : `请求失败（HTTP ${response.status}）`;
    throw new Error(reason);
  }
  return payload;
}

function jsonOptions(method, body) {
  return {
    method: method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}

function shortText(text, limit) {
  return text.length > limit ? `${text.slice(0, limit)}…` : text;
}

function createButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

/** 渲染记录列表 */
function render() {
  messageList.replaceChildren();

  if (records.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty-hint";
    empty.textContent = "还没有聊天记录，输入消息开始对话吧。";
    messageList.append(empty);
    return;
  }

  records.forEach((record) => {
    const item = document.createElement("li");
    item.className = "message-item";
    item.dataset.id = String(record.id);
    item.append(
      buildContentView(record),
      buildActionsView(record, item)
    );
    messageList.append(item);
  });
}

/** 正常状态的记录内容：用户消息 + 后端回复 */
function buildContentView(record) {
  const content = document.createElement("div");
  content.className = "message-content";

  const user = document.createElement("p");
  user.className = "message-user";
  user.textContent = record.message;

  const reply = document.createElement("p");
  reply.className = "message-reply";
  reply.textContent = record.reply;

  content.append(user, reply);
  return content;
}

function buildActionsView(record, item) {
  const actions = document.createElement("div");
  actions.className = "message-actions";
  actions.append(
    createButton("修改", "btn btn-edit", () => enterEditMode(record, item)),
    createButton("删除", "btn btn-delete", () => enterDeleteConfirm(record, item))
  );
  return actions;
}

/** 把一条记录切换成修改状态：内容变成输入框，按钮变成保存/取消 */
function enterEditMode(record, item) {
  const content = document.createElement("div");
  content.className = "message-content";

  const editInput = document.createElement("input");
  editInput.type = "text";
  editInput.className = "message-edit-input";
  editInput.value = record.message;

  const reply = document.createElement("p");
  reply.className = "message-reply";
  reply.textContent = record.reply;

  content.append(editInput, reply);

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const saveButton = createButton("保存", "btn btn-save", async () => {
    const value = editInput.value.trim();
    if (!value) {
      setStatus("消息内容不能为空。", "error");
      editInput.focus();
      return;
    }
    try {
      const updated = await callApi(
        `/api/messages/${record.id}`,
        jsonOptions("PATCH", { message: value })
      );
      records = records.map((item) => (item.id === updated.id ? updated : item));
      render();
      setStatus(`已修改第 ${updated.id} 条记录。`, "success");
    } catch (error) {
      setStatus(`修改失败：${error.message}`, "error");
    }
  });

  actions.append(saveButton, createButton("取消", "btn", () => render()));
  item.replaceChildren(content, actions);

  editInput.focus();
  editInput.select();
  editInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      saveButton.click();
    } else if (event.key === "Escape") {
      render();
    }
  });
}

/** 把一条记录切换成删除确认状态，确认过程完全在页面内完成 */
function enterDeleteConfirm(record, item) {
  const content = document.createElement("div");
  content.className = "message-content";

  const hint = document.createElement("p");
  hint.className = "message-user message-confirm";
  hint.textContent = `确定删除「${shortText(record.message, 20)}」这条记录吗？`;

  content.append(hint);

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const confirmButton = createButton("确认删除", "btn btn-delete", async () => {
    try {
      await callApi(`/api/messages/${record.id}`, { method: "DELETE" });
      records = records.filter((item) => item.id !== record.id);
      render();
      setStatus(`已删除第 ${record.id} 条记录。`, "success");
    } catch (error) {
      setStatus(`删除失败：${error.message}`, "error");
      render();
    }
  });

  actions.append(confirmButton, createButton("取消", "btn", () => render()));
  item.replaceChildren(content, actions);
}

/** 页面打开时读取已有的聊天记录 */
async function loadMessages() {
  setStatus("正在加载聊天记录…");
  try {
    const data = await callApi("/api/messages");
    records = Array.isArray(data) ? data : [];
    render();
    setStatus(
      records.length > 0 ? `共 ${records.length} 条聊天记录。` : "还没有聊天记录，输入消息开始对话吧。",
      "success"
    );
  } catch (error) {
    setStatus(`加载失败：${error.message}`, "error");
  }
}

composer.addEventListener("submit", async (event) => {
  event.preventDefault();

  const text = messageInput.value.trim();
  if (!text) {
    setStatus("请输入消息内容。", "error");
    messageInput.focus();
    return;
  }
  if (pending) {
    return;
  }

  pending = true;
  sendButton.disabled = true;
  setStatus("正在发送…");

  try {
    const created = await callApi("/api/messages", jsonOptions("POST", { message: text }));
    records.push(created);
    messageInput.value = "";
    render();
    setStatus(`发送成功，后端回复：${created.reply}`, "success");
  } catch (error) {
    setStatus(`发送失败：${error.message}`, "error");
  } finally {
    pending = false;
    sendButton.disabled = false;
    messageInput.focus();
  }
});

loadMessages();
