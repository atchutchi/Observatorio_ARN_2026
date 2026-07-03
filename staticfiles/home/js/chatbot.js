document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendMessageBtn = document.getElementById('send-message');
    const newConversationBtn = document.getElementById('new-conversation-btn');
    let currentSessionId = null; // Store session ID

    // Function to scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to add a message to the chat interface
    function addChatMessage(sender, text, source = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        const avatarIconClass = sender === 'user' ? 'fa-user' : 'fa-robot';
        const avatarBgClass = sender; 

        messageDiv.innerHTML = `
            <div class="chat-avatar ${avatarBgClass}">
                <i class="fas ${avatarIconClass}"></i>
            </div>
            <div class="chat-text"></div>
        `;
        
        // Set text content carefully to avoid XSS if text isn't sanitized server-side
        const textElement = messageDiv.querySelector('.chat-text');
        textElement.textContent = text; // Use textContent for security
        
        // You could re-enable link formatting here if needed, after sanitization
        // textElement.innerHTML = formatMessageWithLinks(text);

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot typing-indicator'; // Reuse styles
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="chat-avatar bot"><i class="fas fa-robot"></i></div>
            <div class="chat-text">
                <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Function to send message to backend
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addChatMessage('user', message);
        chatInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch('/chatbot/api/', { // Updated URL if changed
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(), // Ensure you have a function for this
                },
                body: JSON.stringify({ 
                    message: message,
                    session_id: currentSessionId // Send current session ID
                }),
            });

            removeTypingIndicator();

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Update session ID if provided by backend
            if (data.session_id) {
                currentSessionId = data.session_id;
                 console.log("Chatbot Session ID updated:", currentSessionId);
            }

            if (data.status === 'success') {
                addChatMessage('bot', data.message, data.source);
            } else {
                addChatMessage('bot', data.message || 'Ocorreu um erro.');
                console.error("Chatbot API Error:", data.error_type || 'Unknown');
            }

        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            removeTypingIndicator();
            addChatMessage('bot', 'Desculpe, ocorreu um erro de comunicação. Tente novamente.');
        }
    }

    // Function to get CSRF token (implement based on your setup)
    function getCSRFToken() {
        const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return csrfCookie ? csrfCookie.split('=')[1] : null;
    }
    
    // --- Event Listeners ---
    
    // Send message on button click
    sendMessageBtn.addEventListener('click', sendMessage);

    // Send message on Enter key press
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // New conversation button
    newConversationBtn.addEventListener('click', async () => {
        console.log("Iniciando nova conversa...");
        addChatMessage('system-info', 'Iniciando nova conversa...'); // Optional user feedback
        
        // Clear local display
        chatMessages.innerHTML = ''; 
        // Add back initial bot message
        addChatMessage('bot', 'Olá! Sou o assistente virtual... Como posso ajudar?'); 

        // Send reset command to backend
        try {
             await fetch('/chatbot/api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ 
                    message: '/reset', // Special command
                    session_id: currentSessionId 
                }),
            });
            // Backend handles resetting the cache via chatbot_instance.reset_conversation
            currentSessionId = null; // Reset local session ID, backend will generate new one
            console.log("Nova conversa iniciada.");
            chatInput.focus();

        } catch (error) {
             console.error('Erro ao reiniciar conversa no backend:', error);
             addChatMessage('system-info', 'Erro ao reiniciar a conversa no servidor.');
        }
    });

    // Initial scroll
    scrollToBottom();

}); 