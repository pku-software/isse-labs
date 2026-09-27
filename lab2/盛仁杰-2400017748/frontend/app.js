const messagesElement = document.querySelector(".messages");
const composer = document.querySelector(".composer");
const input = document.querySelector("#message-input");
const statusElement = document.querySelector(".status");

function setStatus(message, isError = false) {
  statusElement.textContent = message;
  statusElement.style.color = isError ? "#b91c1c" : "#6b7280";
}

function renderMessages(messages) {
  messagesElement.replaceChildren();
  for (const record of messages) {
    const userMessage = document.createElement("article");
    userMessage.className = "message user-message";
    userMessage.innerHTML = `
      <div class="message-role">用户</div>
      <p></p>
      <div class="message-actions">
        <button type="button" data-action="edit" data-id="${record.id}">修改</button>
        <button type="button" data-action="delete" data-id="${record.id}">删除</button>
      </div>`;
    userMessage.querySelector("p").textContent = record.message;

    const assistantMessage = document.createElement("article");
    assistantMessage.className = "message assistant-message";
    assistantMessage.innerHTML = '<div class="message-role">AI</div><p></p>';
    assistantMessage.querySelector("p").textContent = record.reply;
    messagesElement.append(userMessage, assistantMessage);
  }
}

async function loadMessages() {
  const response = await fetch("/api/messages");
  if (!response.ok) throw new Error("加载聊天记录失败");
  renderMessages(await response.json());
}

composer.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) {
    setStatus("请输入消息", true);
    return;
  }

  const response = await fetch("/api/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!response.ok) {
    setStatus("发送失败", true);
    return;
  }
  input.value = "";
  setStatus("发送成功");
  await loadMessages();
});

messagesElement.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = button.dataset.id;

  if (button.dataset.action === "edit") {
    const card = button.closest(".message");
    const paragraph = card.querySelector("p");
    const editor = document.createElement("textarea");
    editor.rows = 2;
    editor.value = paragraph.textContent;
    const save = document.createElement("button");
    save.type = "button";
    save.textContent = "保存";
    save.dataset.action = "save";
    save.dataset.id = id;
    const cancel = document.createElement("button");
    cancel.type = "button";
    cancel.textContent = "取消";
    cancel.dataset.action = "cancel";
    paragraph.replaceWith(editor);
    button.replaceWith(save);
    save.after(cancel);
    return;
  }

  if (button.dataset.action === "save") {
    const card = button.closest(".message");
    const message = card.querySelector("textarea").value.trim();
    if (!message) {
      setStatus("消息不能为空", true);
      return;
    }
    const response = await fetch(`/api/messages/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!response.ok) setStatus("修改失败", true);
  } else if (button.dataset.action === "cancel") {
    await loadMessages();
    return;
  } else {
    const response = await fetch(`/api/messages/${id}`, { method: "DELETE" });
    if (!response.ok) setStatus("删除失败", true);
  }
  await loadMessages();
});

loadMessages().catch(() => setStatus("无法连接后端", true));
