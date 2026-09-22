// 前端逻辑骨架
// 注意：本阶段仅展示静态界面与占位交互，暂不调用后端 API

document.addEventListener('DOMContentLoaded', () => {
    console.log('静态前端页面加载完成');

    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // 本阶段暂时不发送网络请求
            console.log('输入内容：', userInput.value);
        });
    }
});
