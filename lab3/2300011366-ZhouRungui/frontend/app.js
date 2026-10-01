const messagesElement = document.querySelector("#messages");
const countElement = document.querySelector("#message-count");
const form = document.querySelector("#message-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const statusElement = document.querySelector("#status");

function setStatus(text, isError = false) {
  statusElement.textContent = text;
  statusElement.classList.toggle("error", isError);
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (response.status === 204) return null;

  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "请求失败");
  return data;
}

function makeButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

function renderMessage(record) {
  const card = document.createElement("article");
  card.className = "message-card";

  function addRow(labelText, text, extraClass = "") {
    const row = document.createElement("div");
    row.className = `message-row ${extraClass}`;
    const label = document.createElement("span");
    label.className = "label";
    label.textContent = labelText;
    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    row.append(label, paragraph);
    card.append(row);
    return paragraph;
  }

  const messageText = addRow("你", record.message);
  addRow("AI", record.reply, "assistant-row");

  const actions = document.createElement("div");
  actions.className = "message-actions";

  function showActions() {
    actions.replaceChildren(editButton, deleteButton);
  }

  const editButton = makeButton("修改", "text-button", () => {
    actions.replaceChildren();
    const editor = document.createElement("textarea");
    editor.className = "inline-editor";
    editor.value = record.message;
    editor.setAttribute("aria-label", "修改消息内容");

    const saveButton = makeButton("保存", "text-button", async () => {
      if (!editor.value.trim()) {
        setStatus("消息不能为空", true);
        return;
      }
      saveButton.disabled = true;
      try {
        const updated = await api(`/api/messages/${record.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: editor.value }),
        });
        record.message = updated.message;
        messageText.textContent = updated.message;
        setStatus("记录已修改");
        showActions();
      } catch (error) {
        setStatus(error.message, true);
        saveButton.disabled = false;
      }
    });
    const cancelButton = makeButton("取消", "text-button", showActions);
    actions.append(editor, saveButton, cancelButton);
    editor.focus();
  });

  const deleteButton = makeButton("删除", "text-button danger", () => {
    actions.replaceChildren(
      document.createTextNode("确定删除这条记录？"),
      makeButton("确定删除", "text-button danger", async () => {
        try {
          await api(`/api/messages/${record.id}`, { method: "DELETE" });
          card.remove();
          updateCount();
          setStatus("记录已删除");
        } catch (error) {
          setStatus(error.message, true);
          showActions();
        }
      }),
      makeButton("取消", "text-button", showActions),
    );
  });

  showActions();
  card.append(actions);
  return card;
}

function updateCount() {
  const count = messagesElement.querySelectorAll(".message-card").length;
  countElement.textContent = `${count} 条记录`;
  if (count === 0) {
    messagesElement.innerHTML = '<p class="empty-state">还没有聊天记录，发送一条消息开始吧。</p>';
  } else {
    messagesElement.querySelector(".empty-state")?.remove();
  }
}

async function loadMessages() {
  try {
    const records = await api("/api/messages");
    messagesElement.replaceChildren(...records.map(renderMessage));
    updateCount();
  } catch (error) {
    setStatus(error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) {
    setStatus("请输入消息", true);
    return;
  }

  sendButton.disabled = true;
  setStatus("正在发送……");
  try {
    const record = await api("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    messagesElement.querySelector(".empty-state")?.remove();
    messagesElement.append(renderMessage(record));
    input.value = "";
    updateCount();
    setStatus("消息已发送");
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    sendButton.disabled = false;
  }
});

loadMessages();
