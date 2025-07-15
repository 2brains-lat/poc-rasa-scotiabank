// Generar un UUID simple (v4)
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Crear input para el UUID de la conversación
const uuidContainer = document.createElement('div');
uuidContainer.style.marginBottom = '10px';
const uuidLabel = document.createElement('label');
uuidLabel.textContent = 'ID de conversación: ';
uuidLabel.style.fontSize = '0.95em';
const uuidInput = document.createElement('input');
uuidInput.type = 'text';
uuidInput.placeholder = 'UUID automático';
uuidInput.style.width = '220px';
uuidInput.style.fontSize = '0.95em';
uuidInput.style.marginLeft = '6px';
uuidInput.style.borderRadius = '6px';
uuidInput.style.border = '1px solid var(--primary)';
uuidInput.style.padding = '2px 8px';
uuidContainer.appendChild(uuidLabel);
uuidContainer.appendChild(uuidInput);

const chatbotWindow = document.getElementById('chatbot-window');
chatbotWindow.appendChild(uuidContainer);

const chatList = document.createElement('div');
chatList.className = 'chat-list';
chatList.style.display = 'flex';
chatList.style.flexDirection = 'column';
chatList.style.overflowY = 'auto';
chatList.style.height = '260px';
chatbotWindow.appendChild(chatList);

const inputBox = document.createElement('input');
inputBox.type = 'text';
inputBox.placeholder = 'Escribe tu mensaje...';
inputBox.className = 'chat-input';
const sendBtn = document.createElement('button');
sendBtn.textContent = 'Enviar';
sendBtn.className = 'chat-send-btn';
chatbotWindow.appendChild(inputBox);
chatbotWindow.appendChild(sendBtn);

// UUID de sesión (por defecto)
let senderId = generateUUID();
console.log('UUID de sesión del chatbot:', senderId);

function getSenderId() {
  const val = uuidInput.value.trim();
  if (val) return val;
  return senderId;
}

function addMessage(text, from) {
  const msg = document.createElement('div');
  msg.className = 'chat-msg ' + (from === 'user' ? 'user' : 'bot');
  msg.textContent = text;
  msg.style.fontSize = '0.93em'; // Achica la letra
  chatList.appendChild(msg);
  chatList.scrollTop = chatList.scrollHeight;
}

function sendMessage() {
  const text = inputBox.value.trim();
  if (!text) return;
  addMessage(text, 'user');
  inputBox.value = '';
  fetch('http://localhost:5005/webhooks/rest/webhook', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sender: getSenderId(), message: text })
  })
    .then(res => res.json())
    .then(data => {
      if (Array.isArray(data)) {
        data.forEach(msg => {
          if (msg.text) addMessage(msg.text, 'bot');
        });
      }
    })
    .catch(() => addMessage('Error de conexión con el bot.', 'bot'));
}

sendBtn.onclick = sendMessage;
inputBox.addEventListener('keydown', e => {
  if (e.key === 'Enter') sendMessage();
});

// Estilos para los mensajes
const style = document.createElement('style');
style.textContent = `
  .chat-list { min-height: 220px; margin-bottom: 12px; }
  .chat-msg { margin: 6px 0; padding: 8px 14px; border-radius: 16px; max-width: 80%; word-break: break-word; font-size: 0.93em; }
  .chat-msg.user { background: var(--primary); color: #fff; align-self: flex-end; margin-left: 20%; }
  .chat-msg.bot { background: #e2f3f6; color: var(--secondary); align-self: flex-start; margin-right: 20%; }
  .chat-input { width: 70%; padding: 8px; border-radius: 8px; border: 1px solid var(--primary); margin-right: 8px; }
  .chat-send-btn { background: var(--primary); color: #fff; border: none; border-radius: 8px; padding: 8px 18px; cursor: pointer; }
  .chat-send-btn:hover { background: var(--secondary); }
`;
document.head.appendChild(style);