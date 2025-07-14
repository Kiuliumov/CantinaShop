const chatToggle = document.getElementById('chat-toggle');
const chatBox = document.getElementById('chat-box');
const chatClose = document.getElementById('chat-close');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');

chatToggle.addEventListener('click', () => {
  chatBox.classList.toggle('hidden');
});

chatClose.addEventListener('click', () => {
  chatBox.classList.add('hidden');
});

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (message === '') return;
  const bubble = document.createElement('div');
  bubble.className = 'bg-indigo-100 text-gray-800 px-3 py-2 rounded-lg max-w-xs self-end ml-auto';
  bubble.textContent = message;
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  chatInput.value = '';
});
