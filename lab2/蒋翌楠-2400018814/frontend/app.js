const messagesArea = document.querySelector("#messages");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const feedback = document.querySelector("#feedback");

function showFeedback(text, isError = false) {
  feedback.textContent = text;
  feedback.classList.toggle("error", isError);
}

async function api(path, method = "GET", body) {
  let response;
  try {
    response = await fetch(path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new Error("无法连接后端，请确认 Flask 正在运行。");
  }
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "请求失败，请重试。");
  return data;
}

function createCard(record) {
  const card = document.createElement("article");
  card.className = "message-card";
  // 模板只包含固定 HTML；用户内容通过 textContent 或 value 写入。
  card.innerHTML = `
    <div class="message-heading">
      <span class="record-label"></span>
      <div class="record-actions">
        <button type="button" class="text-button edit-button">修改</button>
        <button type="button" class="text-button delete-button">删除</button>
      </div>
    </div>
    <p class="speaker">你</p>
    <p class="message-text question"></p>
    <div class="reply">
      <p class="speaker">AI</p>
      <p class="message-text answer"></p>
    </div>
    <div class="record-panel" hidden></div>`;
  card.querySelector(".record-label").textContent = `记录 #${record.id}`;
  card.querySelector(".question").textContent = record.message;
  card.querySelector(".answer").textContent = record.reply;
  const panel = card.querySelector(".record-panel");

  card.querySelector(".edit-button").addEventListener("click", () => {
    panel.hidden = false;
    panel.innerHTML = `
      <label>修改消息<textarea rows="3"></textarea></label>
      <button type="button" class="text-button save-button">保存</button>
      <button type="button" class="text-button cancel-button">取消</button>`;
    const editor = panel.querySelector("textarea");
    editor.value = record.message;
    editor.focus();
    panel.querySelector(".cancel-button").onclick = () => { panel.hidden = true; };
    panel.querySelector(".save-button").onclick = async (event) => {
      if (!editor.value.trim()) return showFeedback("消息不能为空。", true);
      const button = event.currentTarget;
      button.disabled = true;
      try {
        const updated = await api(`/api/messages/${record.id}`, "PATCH", { message: editor.value });
        card.replaceWith(createCard(updated));
        showFeedback("消息已修改。");
      } catch (error) {
        showFeedback(error.message, true);
      } finally {
        button.disabled = false;
      }
    };
  });

  card.querySelector(".delete-button").addEventListener("click", () => {
    panel.hidden = false;
    panel.innerHTML = `
      <p>确定删除这条问答吗？删除后无法恢复。</p>
      <button type="button" class="text-button confirm-delete delete-button">确认删除</button>
      <button type="button" class="text-button cancel-button">取消</button>`;
    panel.querySelector(".cancel-button").onclick = () => { panel.hidden = true; };
    panel.querySelector(".confirm-delete").onclick = async (event) => {
      const button = event.currentTarget;
      button.disabled = true;
      try {
        await api(`/api/messages/${record.id}`, "DELETE");
        card.remove();
        if (!messagesArea.children.length) showEmptyState();
        showFeedback("记录已删除。");
      } catch (error) {
        showFeedback(error.message, true);
      } finally {
        button.disabled = false;
      }
    };
  });
  return card;
}

function showEmptyState() {
  messagesArea.innerHTML = '<p class="empty-state">还没有聊天记录，写下第一个问题吧。</p>';
}

async function loadMessages() {
  try {
    const records = await api("/api/messages");
    messagesArea.replaceChildren(...records.map(createCard));
    if (!records.length) showEmptyState();
  } catch (error) {
    messagesArea.innerHTML = '<p class="empty-state">记录加载失败，请确认后端已启动后刷新页面。</p>';
    showFeedback(error.message, true);
  }
}

sendButton.addEventListener("click", async () => {
  if (!input.value.trim()) return showFeedback("请先输入消息。", true);
  sendButton.disabled = true;
  input.disabled = true;
  showFeedback("正在发送……");
  try {
    const record = await api("/api/messages", "POST", { message: input.value });
    messagesArea.querySelector(".empty-state")?.remove();
    messagesArea.append(createCard(record));
    input.value = "";
    showFeedback("消息已发送。");
  } catch (error) {
    showFeedback(error.message, true);
  } finally {
    sendButton.disabled = false;
    input.disabled = false;
    input.focus();
  }
});

loadMessages();
