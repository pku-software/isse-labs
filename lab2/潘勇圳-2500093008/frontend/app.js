// 当前阶段只搭建页面结构和样式，脚本暂时不调用后端或任何第三方 API。
// 下一阶段会在这里用 fetch() 调用 Flask 的 /api/messages 接口，
// 把返回的聊天记录渲染到页面上，并接上修改、删除和错误提示。

document.addEventListener("DOMContentLoaded", () => {
  const composer = document.querySelector(".composer");

  if (composer) {
    // 暂时只阻止表单默认提交，避免点击「发送」时刷新页面。
    composer.addEventListener("submit", (event) => {
      event.preventDefault();
      // TODO: 下一阶段在这里调用 POST /api/messages 创建聊天记录。
    });
  }
});
