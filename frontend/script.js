const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

let sessionId = null;

function appendMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    const bubbleDiv = document.createElement('div');
    bubbleDiv.classList.add('bubble');
    bubbleDiv.textContent = text;

    messageDiv.appendChild(bubbleDiv);
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function showTyping() {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'bot', 'typing');
    messageDiv.id = 'typing-indicator';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.classList.add('bubble', 'typing-indicator');
    bubbleDiv.innerHTML = '<span></span><span></span><span></span>';

    messageDiv.appendChild(bubbleDiv);
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function removeTyping() {
    const typingElement = document.getElementById('typing-indicator');
    if (typingElement) {
        typingElement.remove();
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    userInput.value = '';
    appendMessage(message, 'user');

    userInput.disabled = true;
    sendBtn.disabled = true;
    showTyping();

    try {
        const payload = { message: message };
        if (sessionId) {
            payload.session_id = sessionId;
        }

        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            removeTyping();
            appendMessage(data.answer, 'bot');
            if (data.session_id) {
                sessionId = data.session_id;
            }
        } else {
            removeTyping();
            appendMessage(`Error: ${data.detail || 'Something went wrong'}`, 'system');
        }

    } catch (error) {
        removeTyping();
        appendMessage('Error: Could not connect to server.', 'system');
        console.error(error);
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
