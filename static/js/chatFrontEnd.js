const chatToggle = document.getElementById('chat-toggle');
const chatBox = document.getElementById('chat-box');
const chatClose = document.getElementById('chat-close');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');
const adminAvatarUrl = "/static/images/admin.jpg";
const defaultAvatarUrlDefault = "/static/images/avatar.png";

console.log(userAvatarUrl);
const CHAT_HISTORY_KEY = 'chat_history';

const adminUsername = "admin";

const chatSocket = new WebSocket(
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
  window.location.host +
  '/ws/chat/'
);

window.addEventListener('load', () => {
  const history = JSON.parse(localStorage.getItem(CHAT_HISTORY_KEY)) || [];
  history.forEach(msg => {
    const avatarUrl = msg.avatarUrl || adminAvatarUrl;
    if (msg.username === currentUsername) {
      addUserMessage(msg.message, avatarUrl, msg.timestamp);
    } else if (msg.username === adminUsername) {
      addAdminMessage(msg.message, avatarUrl, msg.timestamp);
    } else {
      addAdminMessage(msg.message, avatarUrl, msg.timestamp);
    }
  });
});

chatToggle.addEventListener('click', () => {
  chatBox.classList.remove('opacity-0', 'invisible');
  chatBox.classList.add('opacity-100', 'visible');
  chatToggle.classList.add('hidden');
});

chatClose.addEventListener('click', () => {
  chatBox.classList.remove('opacity-100', 'visible');
  chatBox.classList.add('opacity-0', 'invisible');
  setTimeout(() => {
    chatToggle.classList.remove('hidden');
  }, 100);
});

chatSocket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  const message = data.message;
  const username = data.username;
  const timestamp = data.timestamp || new Date().toISOString();
  let avatarUrl;
  if (username === currentUsername) {
    avatarUrl = userAvatarUrl;
    addUserMessage(message, userAvatarUrl, timestamp);
  } else {
    avatarUrl = adminAvatarUrlDefault;
    addAdminMessage(message, adminAvatarUrlDefault, timestamp);
  }
  saveMessageToLocalStorage({ message, username, avatarUrl, timestamp });
};

chatSocket.onclose = function(e) {
  console.error('Chat socket closed unexpectedly');
};

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  const timestamp = new Date().toISOString();
  chatSocket.send(JSON.stringify({
    'username': currentUsername,
    'message': message,
    'avatar_url': userAvatarUrl,
    'timestamp': timestamp,
  }));
  chatInput.value = '';
});

function saveMessageToLocalStorage(msg) {
  let history = JSON.parse(localStorage.getItem(CHAT_HISTORY_KEY)) || [];
  history.push(msg);
  localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(history));
}

function addUserMessage(text, avatarUrl, timestamp) {
  const bubble = document.createElement('div');
  bubble.className = 'flex flex-col items-start max-w-xs mr-auto self-start space-y-1'; // left aligned

  const bubbleRow = document.createElement('div');
  bubbleRow.className = 'flex items-start space-x-2';

  const avatar = document.createElement('img');
  avatar.src = userAvatarUrl;
  avatar.alt = "User avatar";
  avatar.className = 'w-8 h-8 rounded-full object-cover';

  const msgDiv = document.createElement('div');
  msgDiv.className = 'bg-indigo-100 text-gray-800 px-3 py-2 rounded-lg';
  msgDiv.textContent = text;

  bubbleRow.appendChild(avatar);
  bubbleRow.appendChild(msgDiv);

  const timeDiv = document.createElement('div');
  timeDiv.className = 'text-xs text-gray-500';
  timeDiv.textContent = timestamp
    ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  bubble.appendChild(bubbleRow);
  bubble.appendChild(timeDiv);

  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addAdminMessage(text, avatarUrl, timestamp) {
  const bubble = document.createElement('div');
  bubble.className = 'flex flex-col items-end max-w-xs ml-auto self-end space-y-1'; // right aligned

  const bubbleRow = document.createElement('div');
  bubbleRow.className = 'flex items-start space-x-2';

  const msgDiv = document.createElement('div');
  msgDiv.className = 'bg-gray-200 text-gray-900 px-3 py-2 rounded-lg';
  msgDiv.textContent = text;

  const avatar = document.createElement('img');
  avatar.src = avatarUrl;
  avatar.alt = "Admin avatar";
  avatar.className = 'w-8 h-8 rounded-full object-cover';

  bubbleRow.appendChild(msgDiv);
  bubbleRow.appendChild(avatar);

  const timeDiv = document.createElement('div');
  timeDiv.className = 'text-xs text-gray-500';
  timeDiv.textContent = timestamp
    ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  bubble.appendChild(bubbleRow);
  bubble.appendChild(timeDiv);

  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
