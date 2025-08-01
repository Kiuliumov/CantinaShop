(async function () {
  let adminAvatarUrl = '/static/images/admin.jpg';
  let defaultAvatarUrl = '/static/images/avatar.png';
  let messagesApiUrlBase = '/api/messages/';
  let websocketBaseUrl = (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host;

  try {
    const res = await fetch('/api/chat-config/');
    if (!res.ok) throw new Error('Failed to load chat config');
    const config = await res.json();

    adminAvatarUrl = config.adminAvatarUrl || adminAvatarUrl;
    defaultAvatarUrl = config.defaultAvatarUrl || defaultAvatarUrl;
    messagesApiUrlBase = config.apiMessagesUrl.replace(/\/\d+\/?$/, '/');
    const wsProtocol = config.wsProtocol || (window.location.protocol === "https:" ? "wss" : "ws");
    const host = config.host || window.location.host;
    websocketBaseUrl = ${wsProtocol}://${host};
  } catch (err) {
    console.error('Failed to load chat config:', err);
  }

  let currentChatUserId = null;
  let chatSocket = null;
  let chatHeader, userList, chatMessages, chatForm, chatInput, userSearchInput;
  const recentMessagesSet = new Set();
  const unreadCounts = new Map();

  function init() {
    chatHeader = document.getElementById('chat-header');
    userList = document.getElementById('user-list');
    chatMessages = document.getElementById('chat-messages');
    chatForm = document.getElementById('chat-form');
    chatInput = document.getElementById('chat-input');
    userSearchInput = document.getElementById('user-search');

    userList.querySelectorAll('button[data-user-id]').forEach(button => {
      let badge = document.createElement('span');
      badge.className = 'unread-badge hidden ml-auto bg-red-700 text-white rounded-full text-sm w-6 h-6 flex items-center justify-center shadow-lg';
      badge.style.fontWeight = 'bold';
      badge.style.position = 'absolute';
      badge.style.top = '6px';
      badge.style.right = '6px';
      button.style.position = 'relative';
      button.appendChild(badge);
    });

    userSearchInput.addEventListener('input', onUserSearch);
    userList.addEventListener('click', onUserSelect);
    chatForm.addEventListener('submit', onSendMessage);

    chatInput.disabled = true;
    chatForm.querySelector('button[type="submit"]').disabled = true;
  }

  function updateUnreadBadge(userId, count) {
    const btn = userList.querySelector(button[data-user-id="${userId}"]);
    if (!btn) return;
    const badge = btn.querySelector('.unread-badge');
    if (!badge) return;
    if (count > 0) {
      badge.textContent = count > 9 ? '9+' : count;
      badge.classList.remove('hidden');
    } else {
      badge.textContent = '';
      badge.classList.add('hidden');
    }
  }

  function clearUnread(userId) {
    unreadCounts.set(userId, 0);
    updateUnreadBadge(userId, 0);
  }

  function onUserSearch() {
    const query = userSearchInput.value.toLowerCase();
    const userButtons = userList.querySelectorAll('button[data-username]');
    userButtons.forEach(btn => {
      const username = btn.getAttribute('data-username').toLowerCase();
      btn.parentElement.style.display = username.includes(query) ? '' : 'none';
    });
  }

  function clearChat() {
    chatMessages.innerHTML = '';
    recentMessagesSet.clear();
  }

  function messageKey(msg) {
    return ${msg.timestamp}|${msg.sender_id}|${msg.text};
  }

  function addMessageSafe(msg) {
    const key = messageKey(msg);
    if (recentMessagesSet.has(key)) return;
    recentMessagesSet.add(key);
    if (recentMessagesSet.size > 500) {
      const keys = Array.from(recentMessagesSet).slice(-250);
      recentMessagesSet.clear();
      keys.forEach(k => recentMessagesSet.add(k));
    }
    addMessage(msg);
  }

  function addMessage({ text, username, avatarUrl, timestamp, fromAdmin }) {
    const bubble = document.createElement('div');
    bubble.className = 'flex flex-col space-y-1 max-w-xs ' + (fromAdmin ? 'mr-auto items-start' : 'ml-auto items-end');
    const bubbleRow = document.createElement('div');
    bubbleRow.className = 'flex items-start space-x-2';
    const avatar = document.createElement('img');
    avatar.src = avatarUrl || defaultAvatarUrl;
    avatar.alt = username;
    avatar.className = 'w-8 h-8 rounded-full object-cover';
    const msgDiv = document.createElement('div');
    msgDiv.className = fromAdmin
      ? 'bg-indigo-600 text-white px-3 py-2 rounded-lg break-words'
      : 'bg-gray-700 text-gray-100 px-3 py-2 rounded-lg break-words';
    msgDiv.style.wordBreak = 'break-word';
    msgDiv.textContent = text;
    if (fromAdmin) {
      bubbleRow.appendChild(avatar);
      bubbleRow.appendChild(msgDiv);
    } else {
      bubbleRow.appendChild(msgDiv);
      bubbleRow.appendChild(avatar);
    }
    const timeDiv = document.createElement('div');
    timeDiv.className = 'text-xs text-gray-400';
    timeDiv.textContent = timestamp
      ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : '';
    bubble.appendChild(bubbleRow);
    bubble.appendChild(timeDiv);
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function moveUserToTop(userId) {
    const btn = userList.querySelector(button[data-user-id="${userId}"]);
    if (!btn) return;
    const parent = btn.parentElement;
    if (parent.firstChild === btn) return;
    parent.prepend(btn);
  }

  async function loadChatMessages(userId) {
    clearChat();
    try {
      const url = ${messagesApiUrlBase}${userId}/?limit=100;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch messages');
      const data = await res.json();
      data.messages.forEach(msg => {
        addMessageSafe({
          text: msg.message,
          username: msg.sender_username,
          avatarUrl: (msg.sender_id === 0 || msg.from_admin) ? adminAvatarUrl : (msg.avatar_url || defaultAvatarUrl),
          timestamp: msg.timestamp,
          fromAdmin: msg.sender_id === 0 || msg.from_admin,
          sender_id: msg.sender_id.toString(),
        });
      });
      clearUnread(userId);
      await markMessagesRead(userId);
      moveUserToTop(userId);
    } catch (err) {
      console.error(err);
    }
  }

  async function markMessagesRead(userId) {
    try {
      await fetch(/api/mark-read/${userId}/, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
        },
      });
    } catch (err) {
      console.error('Failed to mark messages as read:', err);
    }
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function connectSocket(userId) {
    if (chatSocket) {
      chatSocket.close();
    }
    chatSocket = new WebSocket(
      ${websocketBaseUrl}/ws/chat/admin/${userId}/
    );
    chatSocket.onopen = () => {
      chatInput.disabled = false;
      chatForm.querySelector('button[type="submit"]').disabled = false;
    };
    chatSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      const fromAdmin = data.from_admin;
      const senderId = data.sender_id.toString();

      if (fromAdmin) {
        if (senderId === currentChatUserId) {
          addMessageSafe({
            text: data.message,
            username: data.username || 'Admin',
            avatarUrl: adminAvatarUrl,
            timestamp: data.timestamp,
            fromAdmin: true,
            sender_id: senderId,
          });
          moveUserToTop(senderId);
        }
        return;
      }

      if (senderId === currentChatUserId) {
        addMessageSafe({
          text: data.message,
          username: data.username || 'User',
          avatarUrl: data.avatar_url || defaultAvatarUrl,
          timestamp: data.timestamp,
          fromAdmin: false,
          sender_id: senderId,
        });
        clearUnread(senderId);
        markMessagesRead(senderId);
        moveUserToTop(senderId);
      } else {
        let currentCount = unreadCounts.get(senderId) || 0;
        unreadCounts.set(senderId, currentCount + 1);
        updateUnreadBadge(senderId, unreadCounts.get(senderId));
      }
    };
    chatSocket.onclose = () => {
      chatInput.disabled = true;
      chatForm.querySelector('button[type="submit"]').disabled = true;
    };
  }

  function onUserSelect(e) {
    const btn = e.target.closest('button[data-user-id]');
    if (!btn) return;
    currentChatUserId = btn.getAttribute('data-user-id');
    const username = btn.getAttribute('data-username');
    chatHeader.textContent = Chat with ${username};
    chatInput.value = '';
    chatInput.focus();
    clearUnread(currentChatUserId);
    loadChatMessages(currentChatUserId);
    connectSocket(currentChatUserId);
  }

  function onSendMessage(e) {
    e.preventDefault();
    if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) return;
    const message = chatInput.value.trim();
    if (!message) return;
    addMessageSafe({
      text: message,
      username: 'Admin',
      avatarUrl: adminAvatarUrl,
      timestamp: new Date().toISOString(),
      fromAdmin: true,
      sender_id: '0',
    });
    chatSocket.send(JSON.stringify({ message }));
    chatInput.value = '';
    moveUserToTop(currentChatUserId);
  }

  window.chatApp = {
    init,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();