/**
 * Lab 2 - 前端脚本
 * 任务 1：仅初始化页面元素与事件占位，不调用任何后端。
 * 任务 2 起：与 Flask 后端 API 对接，实现真实 CRUD。
 */

(function () {
  "use strict";

  const dom = {
    form: document.getElementById("chat-form"),
    input: document.getElementById("message-input"),
    sendButton: document.getElementById("send-button"),
    chatWindow: document.getElementById("chat-window"),
    emptyHint: document.getElementById("empty-hint"),
    status: document.getElementById("status-text"),
  };

  function setStatus(text, isError) {
    dom.status.textContent = text || "";
    dom.status.classList.toggle("error", Boolean(isError));
  }

  function renderEmpty() {
    if (dom.emptyHint) dom.emptyHint.style.display = "";
  }

  /**
   * 任务 1：仅打印提示，告诉用户"按钮暂无效果"。
   * 任务 2：改为调用 POST /api/messages 发送消息并刷新聊天区。
   */
  function handleSend(event) {
    event.preventDefault();
    const text = dom.input.value.trim();
    if (!text) {
      setStatus("请输入内容后再发送", true);
      return;
    }
    console.log("[任务1] 发送占位:", text);
    setStatus("任务 1 暂未连接后端：消息尚未发送");
  }

  /**
   * 任务 1：占位实现。任务 2 起会真正调用后端修改 / 删除接口。
   */
  function bindMessageActions(container) {
    container.querySelectorAll("[data-action='edit']").forEach((btn) => {
      btn.addEventListener("click", () =>
        setStatus("任务 1 暂未连接后端：修改功能尚未实现")
      );
    });
    container.querySelectorAll("[data-action='delete']").forEach((btn) => {
      btn.addEventListener("click", () =>
        setStatus("任务 1 暂未连接后端：删除功能尚未实现")
      );
    });
  }

  function bindEvents() {
    dom.form.addEventListener("submit", handleSend);
    dom.input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        dom.form.requestSubmit();
      }
    });
    bindMessageActions(dom.chatWindow);
  }

  function init() {
    renderEmpty();
    bindEvents();
    setStatus("任务 1：前端骨架就绪，等待连接后端");
  }

  document.addEventListener("DOMContentLoaded", init);
})();
