(function () {
  let chatSocket = null;
  let chatMessages, chatForm, chatInput, chatToggleBtn, chatBox;
  const wsChatUrl = `${window.chatConfig.wsProtocol}://${window.chatConfig.host}/ws/chat/user/${window.chatConfig.userId}/`;

  let currentUserId = window.chatConfig?.userId || null;

  function init() {
    chatMessages = document.getElementById('chat-messages');
    chatForm = document.getElementById('chat-form');
    chatInput = document.getElementById('chat-input');
    chatToggleBtn = document.getElementById('chat-toggle');
    chatBox = document.getElementById('chat-box');

    if (!currentUserId || !chatMessages || !chatForm || !chatInput) {
      console.error("Chat initialization failed: missing elements or user ID");
      return;
    }

    chatForm.addEventListener('submit', onSendMessage);
    chatToggleBtn?.addEventListener('click', toggleChat);
    document.getElementById('chat-close')?.addEventListener('click', toggleChat);

    loadChatMessages(currentUserId);
    connectSocket(currentUserId);
  }

  function toggleChat() {
    if (!chatBox) return;

    if (window.chatConfig.userIsStaffOrSuperuser) {
      window.location.href = `${window.location.protocol}//${window.location.host}/chat/admin`;
      return;
    }

    if (window.chatConfig.userIsChatBanned) {
      showChatBanAlert();
      return;
    }

    const isOpen = chatBox.classList.contains('opacity-100');
    if (isOpen) {
      chatBox.classList.remove('opacity-100', 'visible');
      chatBox.classList.add('opacity-0', 'invisible');
    } else {
      chatBox.classList.remove('opacity-0', 'invisible');
      chatBox.classList.add('opacity-100', 'visible');
    }
  }

  function clearChat() {
    chatMessages.innerHTML = '';
  }

  async function loadChatMessages(userId) {
    clearChat();
    try {
      const url = window.chatConfig.apiMessagesUrl.replace(/\/\d+\/$/, `/${userId}/`);
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch messages');
      const data = await res.json();

      const recentMessages = data.messages.slice(-100);
      recentMessages.forEach(msg => {
        addMessage({
          text: msg.message,
          username: msg.sender_username,
          avatarUrl: (msg.sender_id === 0 || msg.from_admin) ? window.chatConfig.adminAvatarUrl : (msg.avatar_url || window.chatConfig.defaultAvatarUrl),
          timestamp: msg.timestamp,
          fromAdmin: msg.sender_id === 0 || msg.from_admin,
          isBanMessage: msg.message.toLowerCase().includes('banned'),  // mark ban messages
        });
      });
    } catch (err) {
      console.error(err);
    }
  }

  function connectSocket(userId) {
    if (chatSocket) chatSocket.close();

    const baseWsUrl = wsChatUrl.replace(/\/\d+\/$/, `/${userId}/`);
    chatSocket = new WebSocket(baseWsUrl);

    chatSocket.onopen = () => {
      chatInput.disabled = false;
      const submitBtn = chatForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = false;
    };

    chatSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);

      // Special type from server for ban
      if (data.type === 'chat_banned') {
        showChatBanAlert(data.message || "You have been banned from chatting.");
        chatSocket.close();
        chatInput.disabled = true;
        const submitBtn = chatForm.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        return;
      }

      // If ban message comes as normal chat message, also show alert
      if (data.message && data.message.toLowerCase().includes("banned")) {
        showChatBanAlert(data.message);
      }

      addMessage({
        text: data.message,
        username: data.username,
        avatarUrl: data.avatar_url || window.chatConfig.defaultAvatarUrl,
        timestamp: data.timestamp,
        fromAdmin: data.from_admin,
        isBanMessage: data.message.toLowerCase().includes("banned"),
      });
    };

    chatSocket.onerror = (e) => {
      console.error("WebSocket error:", e);
      chatInput.disabled = true;
      const submitBtn = chatForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;
    };

    chatSocket.onclose = () => {
      chatInput.disabled = true;
      const submitBtn = chatForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;
    };
  }

  function onSendMessage(e) {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) {
      console.warn("Chat socket is not open.");
      return;
    }

    chatSocket.send(JSON.stringify({ message }));
    chatInput.value = '';
  }

  function addMessage({ text, username, avatarUrl, timestamp, fromAdmin, isBanMessage = false }) {
    const messageEl = document.createElement('div');
    messageEl.classList.add('chat-message');

    // Use special classes and no avatar if banned message
    if (isBanMessage) {
      messageEl.classList.add('chat-ban-message');
    } else {
      messageEl.classList.add(fromAdmin ? 'from-admin' : 'from-user');
    }

    if (!isBanMessage) {
      const avatar = document.createElement('img');
      avatar.src = avatarUrl;
      avatar.alt = username;
      avatar.classList.add('chat-avatar');
      messageEl.appendChild(avatar);
    }

    const content = document.createElement('div');
    content.classList.add('chat-content');

    const header = document.createElement('div');
    header.classList.add('chat-header');

    const userSpan = document.createElement('span');
    userSpan.classList.add('chat-username');
    userSpan.textContent = username;

    const timeSpan = document.createElement('span');
    timeSpan.classList.add('chat-timestamp');
    timeSpan.textContent = new Date(timestamp).toLocaleTimeString();

    header.appendChild(userSpan);
    header.appendChild(timeSpan);

    const messageText = document.createElement('div');
    messageText.classList.add('chat-text');
    messageText.textContent = text;

    content.appendChild(header);
    content.appendChild(messageText);

    messageEl.appendChild(content);

    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function showChatBanAlert(message) {
    const banMsg = message || "You have been banned from chatting due to excessive messaging. Please contact support.";
    const existingAlert = document.getElementById('chat-ban-alert');
    if (existingAlert) return;

    const alertBox = document.createElement('div');
    alertBox.id = 'chat-ban-alert';
    alertBox.style.position = 'fixed';
    alertBox.style.top = '20%';
    alertBox.style.left = '50%';
    alertBox.style.transform = 'translateX(-50%)';
    alertBox.style.backgroundColor = '#f44336'; // red background
    alertBox.style.color = 'white';
    alertBox.style.padding = '1rem 2rem';
    alertBox.style.borderRadius = '8px';
    alertBox.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    alertBox.style.zIndex = 9999;
    alertBox.style.fontSize = '1.1rem';
    alertBox.style.textAlign = 'center';
    alertBox.textContent = banMsg;

    document.body.appendChild(alertBox);

    setTimeout(() => {
      alertBox.remove();
    }, 7000);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
