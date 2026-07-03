document.addEventListener('DOMContentLoaded', function() {
    // Scroll to bottom of chat
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Suggestion buttons
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    const userInput = document.getElementById('user-input');
    
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            userInput.value = this.textContent;
            userInput.focus();
        });
    });
    
    // Form submission via AJAX
    const chatForm = document.getElementById('chat-form');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;
        
        // Adicionar mensagem do usuário ao chat
        addMessage(message, 'user-message');
        userInput.value = '';
        
        // Mostrar indicador de digitação
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        typingIndicator.id = 'typing-indicator';
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Enviar requisição para a API
        fetch('/dashboard/api/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ question: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na comunicação com o servidor');
            }
            return response.json();
        })
        .then(data => {
            // Remover indicador de digitação
            document.getElementById('typing-indicator').remove();
            
            // Adicionar resposta do chatbot
            addMessage(data.response, 'system-message');
        })
        .catch(error => {
            // Remover indicador de digitação
            if (document.getElementById('typing-indicator')) {
                document.getElementById('typing-indicator').remove();
            }
            
            // Mostrar mensagem de erro
            addMessage('Ocorreu um erro na comunicação. Por favor, tente novamente mais tarde.', 'system-message');
            console.error('Erro:', error);
        });
    });
    
    function addMessage(content, className) {
        const now = new Date();
        const time = now.getHours().toString().padStart(2, '0') + ':' + 
                     now.getMinutes().toString().padStart(2, '0');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + className + ' mb-3';
        messageDiv.innerHTML = `
            <div class="message-content">${content}</div>
            <div class="message-time">${time}</div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}); 