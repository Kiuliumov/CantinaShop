const chatToggle = document.getElementById('chat-toggle');
const chatBox = document.getElementById('chat-box');
const chatClose = document.getElementById('chat-close');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');
const adminAvatarUrl = "/static/images/admin.jpg";

const chatSocket = new WebSocket(
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
  window.location.host +
  '/ws/chat/'
);

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
  }, 300);
});

chatSocket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  const message = data.message;
  const username = data.username;
  const avatarUrl = data.avatar_url || adminAvatarUrl;
  if (username === "{{ user.username }}") {
    addUserMessage(message, avatarUrl);
  } else {
    addAdminMessage(message, avatarUrl);
  }
};

chatSocket.onclose = function(e) {
  console.error('Chat socket closed unexpectedly');
};

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  chatSocket.send(JSON.stringify({
    'message': message,
    'avatar_url': userAvatarUrl
  }));
  chatInput.value = '';
});

function addUserMessage(text, avatarUrl) {
  const bubble = document.createElement('div');
  bubble.className = 'flex items-start max-w-xs ml-auto self-end space-x-2';

  const avatar = document.createElement('img');
  avatar.src = avatarUrl;
  avatar.alt = "User avatar";
  avatar.className = 'w-8 h-8 rounded-full object-cover';

  const msgDiv = document.createElement('div');
  msgDiv.className = 'bg-indigo-100 text-gray-800 px-3 py-2 rounded-lg';
  msgDiv.textContent = text;

  bubble.appendChild(avatar);
  bubble.appendChild(msgDiv);

  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addAdminMessage(text, avatarUrl) {
  const bubble = document.createElement('div');
  bubble.className = 'flex items-start max-w-xs mr-auto self-start space-x-2';

  const avatar = document.createElement('img');
  avatar.src = avatarUrl;
  avatar.alt = "Admin avatar";
  avatar.className = 'w-8 h-8 rounded-full object-cover';

  const msgDiv = document.createElement('div');
  msgDiv.className = 'bg-gray-200 text-gray-900 px-3 py-2 rounded-lg';
  msgDiv.textContent = text;

  bubble.appendChild(avatar);
  bubble.appendChild(msgDiv);

  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
