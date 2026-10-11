const list = document.querySelector("#conversation-list");
const messages = document.querySelector(".messages");
const composer = document.querySelector(".composer");
const input = document.querySelector("#message-input");
const title = document.querySelector("#conversation-title");
const status = document.querySelector(".status");
let conversations = [];
let activeId = null;

function setStatus(text, error = false) {
  status.textContent = text;
  status.style.color = error ? "#b91c1c" : "#6b7280";
}

function render() {
  list.replaceChildren();
  conversations.forEach((conversation) => {
    const item = document.createElement("div");
    item.className = `conversation-item${conversation.id === activeId ? " active" : ""}`;
    item.innerHTML = `<button type="button" data-id="${conversation.id}"></button><button type="button" data-delete="${conversation.id}">删除</button>`;
    item.querySelector("[data-id]").textContent = conversation.title;
    list.append(item);
  });
  const active = conversations.find((item) => item.id === activeId);
  title.textContent = active?.title || "AI 聊天助手";
  messages.replaceChildren();
  (active?.messages || []).forEach((item) => {
    const article = document.createElement("article");
    article.className = `message ${item.role === "user" ? "user-message" : "assistant-message"}`;
    article.innerHTML = `<div class="message-role">${item.role === "user" ? "用户" : "AI"}</div><p></p>`;
    article.querySelector("p").textContent = item.content;
    messages.append(article);
  });
}

async function load() {
  conversations = await (await fetch("/api/conversations")).json();
  if (!conversations.length) {
    const response = await fetch("/api/conversations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: "新会话" }) });
    conversations = [await response.json()];
  }
  if (!conversations.some((item) => item.id === activeId)) activeId = conversations[0].id;
  render();
}

document.querySelector("#new-conversation").addEventListener("click", async () => {
  const response = await fetch("/api/conversations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: "新会话" }) });
  const conversation = await response.json();
  conversations.push(conversation); activeId = conversation.id; render();
});

list.addEventListener("click", async (event) => {
  const deleteButton = event.target.closest("[data-delete]");
  if (deleteButton) await fetch(`/api/conversations/${deleteButton.dataset.delete}`, { method: "DELETE" });
  else {
    const selectButton = event.target.closest("[data-id]");
    if (selectButton) activeId = Number(selectButton.dataset.id);
  }
  await load();
});

composer.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || activeId === null) return setStatus("请选择会话并输入消息", true);
  const response = await fetch(`/api/conversations/${activeId}/messages`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message }) });
  if (!response.ok) return setStatus("发送失败", true);
  input.value = ""; setStatus("发送成功"); await load();
});

load().catch(() => setStatus("无法连接后端", true));
