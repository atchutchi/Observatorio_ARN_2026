// ==============================
// ARN ASSISTANT JAVASCRIPT
// ==============================

class ARNAssistantInterface {
    constructor() {
        this.sessionId = null;
        this.isProcessing = false;
        this.messageHistory = [];
        
        // Elementos DOM
        this.chatMessages = null;
        this.chatInput = null;
        this.sendButton = null;
        this.loadingIndicator = null;
    }
    
    initialize() {
        this.initializeElements();
        this.setupEventListeners();
        this.initializeSession();
        this.checkAIStatus();
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendMessage');
        this.loadingIndicator = document.getElementById('chatLoading');
    }
    
    setupEventListeners() {
        // Send button
        this.sendButton?.addEventListener('click', () => this.sendMessage());
        
        // Enter key
        this.chatInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Suggestion buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn')) {
                const suggestion = e.target.dataset.suggestion || e.target.textContent;
                this.sendMessage(suggestion);
            }
        });
        
        // Quick actions
        document.addEventListener('click', (e) => {
            if (e.target.closest('.quick-action-btn')) {
                const action = e.target.closest('.quick-action-btn').dataset.action;
                this.handleQuickAction(action);
            }
        });
        
        // Example questions
        document.addEventListener('click', (e) => {
            if (e.target.closest('.example-category li')) {
                const question = e.target.textContent.replace(/['"]/g, '');
                this.sendMessage(question);
            }
        });
    }
    
    async initializeSession() {
        try {
            const response = await fetch('/dashboard/api/chatbot/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.session_id) {
                this.sessionId = data.session_id;
                
                // Se há histórico, carregar
                if (data.history && data.history.length > 0) {
                    this.loadChatHistory(data.history);
                }
            }
            
        } catch (error) {
            console.error('Erro ao inicializar sessão:', error);
            this.showErrorMessage('Erro ao conectar com o assistente. Recarregue a página.');
        }
    }
    
    async sendMessage(messageText = null) {
        const message = messageText || this.chatInput?.value?.trim();
        
        if (!message || this.isProcessing) return;
        
        // Limpar input
        if (this.chatInput) {
            this.chatInput.value = '';
        }
        
        // Adicionar mensagem do usuário
        this.addUserMessage(message);
        
        // Mostrar loading
        this.showLoading();
        this.isProcessing = true;
        
        try {
            const response = await fetch('/dashboard/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.addBotMessage(data);
                
                // Atualizar session_id se necessário
                if (data.session_id) {
                    this.sessionId = data.session_id;
                }
                
            } else {
                this.showErrorMessage(data.error || 'Erro ao processar mensagem');
            }
            
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            this.showErrorMessage('Erro de conexão. Verifique sua internet.');
        } finally {
            this.hideLoading();
            this.isProcessing = false;
        }
    }
    
    addUserMessage(message) {
        const messageElement = this.createMessageElement({
            type: 'user',
            text: message,
            timestamp: new Date().toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit' 
            })
        });
        
        this.chatMessages?.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    addBotMessage(data) {
        const messageElement = this.createMessageElement({
            type: 'bot',
            text: data.response,
            timestamp: new Date().toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit' 
            }),
            suggestions: data.suggestions,
            charts: data.charts,
            intent: data.intent,
            confidence: data.confidence,
            aiEnhanced: data.ai_enhanced
        });
        
        this.chatMessages?.appendChild(messageElement);
        
        // Adicionar gráficos se existirem
        if (data.charts && data.charts.length > 0) {
            this.renderCharts(data.charts, messageElement);
        }
        
        this.scrollToBottom();
    }
    
    createMessageElement(messageData) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `arn-message ${messageData.type}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = messageData.type === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = this.formatMessage(messageData.text);
        
        content.appendChild(textDiv);
        
        // Adicionar timestamp
        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = messageData.timestamp;
        content.appendChild(timestamp);
        
        // Adicionar indicador de IA avançada
        if (messageData.aiEnhanced) {
            const aiIndicator = document.createElement('div');
            aiIndicator.className = 'ai-enhanced-indicator';
            aiIndicator.innerHTML = '<i class="fas fa-brain me-1"></i>Resposta aprimorada com IA';
            aiIndicator.style.cssText = `
                font-size: 0.75rem; 
                color: var(--binance-success); 
                margin-top: 0.5rem;
            `;
            content.appendChild(aiIndicator);
        }
        
        // Adicionar sugestões
        if (messageData.suggestions && messageData.suggestions.length > 0) {
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.className = 'message-suggestions';
            
            messageData.suggestions.forEach(suggestion => {
                const btn = document.createElement('button');
                btn.className = 'suggestion-btn';
                btn.textContent = suggestion;
                btn.dataset.suggestion = suggestion;
                suggestionsDiv.appendChild(btn);
            });
            
            content.appendChild(suggestionsDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        return messageDiv;
    }
    
    formatMessage(text) {
        // Converter quebras de linha para <br>
        let formatted = text.replace(/\n/g, '<br>');
        
        // Converter números grandes para formato legível
        formatted = formatted.replace(/\b(\d{4,})\b/g, (match) => {
            return parseInt(match).toLocaleString('pt-BR');
        });
        
        // Destacar operadoras
        formatted = formatted.replace(/\b(TELECEL|Orange|TELECEL)\b/g, '<strong>$1</strong>');
        
        // Destacar percentuais
        formatted = formatted.replace(/(\d+\.?\d*)%/g, '<strong>$1%</strong>');
        
        return formatted;
    }
    
    renderCharts(charts, messageElement) {
        charts.forEach((chartData, index) => {
            const chartContainer = document.createElement('div');
            chartContainer.className = 'chat-chart-container';
            
            const chartTitle = document.createElement('h6');
            chartTitle.className = 'chat-chart-title';
            chartTitle.textContent = chartData.titulo || 'Gráfico';
            
            const canvas = document.createElement('canvas');
            canvas.id = `chatChart_${Date.now()}_${index}`;
            
            chartContainer.appendChild(chartTitle);
            chartContainer.appendChild(canvas);
            
            messageElement.querySelector('.message-content').appendChild(chartContainer);
            
            // Renderizar gráfico
            setTimeout(() => {
                this.createChart(canvas, chartData);
            }, 100);
        });
    }
    
    createChart(canvas, chartData) {
        if (!window.Chart) return;
        
        const ctx = canvas.getContext('2d');
        
        let config = {
            type: chartData.tipo || 'pie',
            data: this.prepareChartData(chartData),
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#F0F0F0',
                            usePointStyle: true,
                            padding: 15,
                            font: { family: 'Inter', size: 12 }
                        }
                    }
                }
            }
        };
        
        // Configurações específicas por tipo
        if (chartData.tipo === 'line' || chartData.tipo === 'bar') {
            config.options.scales = {
                x: {
                    grid: { color: '#474D57' },
                    ticks: { color: '#F0F0F0', font: { family: 'Inter' } }
                },
                y: {
                    grid: { color: '#474D57' },
                    ticks: { color: '#F0F0F0', font: { family: 'Inter' } }
                }
            };
        }
        
        new Chart(ctx, config);
    }
    
    prepareChartData(chartData) {
        const data = chartData.dados || [];
        
        if (chartData.tipo === 'pie' || chartData.tipo === 'doughnut') {
            return {
                labels: data.map(item => item.operadora || item.label),
                datasets: [{
                    data: data.map(item => item.total || item.value || item.percentual),
                    backgroundColor: [
                        '#F0B90B', // Binance Yellow
                        '#FF6600', // Orange
                        '#DC3545', // Blue
                        '#02C076', // Green
                        '#B7BDC6'  // Gray
                    ],
                    borderColor: '#161A1E',
                    borderWidth: 2
                }]
            };
        } else if (chartData.tipo === 'bar') {
            return {
                labels: data.map(item => item.label || item.operadora),
                datasets: [{
                    label: chartData.titulo || 'Valores',
                    data: data.map(item => item.value || item.total),
                    backgroundColor: '#F0B90B',
                    borderColor: '#D4A00A',
                    borderWidth: 1
                }]
            };
        }
        
        return { labels: [], datasets: [] };
    }
    
    showLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'flex';
        }
        
        this.sendButton.disabled = true;
        this.chatInput.disabled = true;
    }
    
    hideLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'none';
        }
        
        this.sendButton.disabled = false;
        this.chatInput.disabled = false;
        this.chatInput.focus();
    }
    
    scrollToBottom() {
        if (this.chatMessages) {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }
    
    showErrorMessage(errorText) {
        const errorElement = this.createMessageElement({
            type: 'bot',
            text: `❌ ${errorText}`,
            timestamp: new Date().toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit' 
            })
        });
        
        this.chatMessages?.appendChild(errorElement);
        this.scrollToBottom();
    }
    
    handleQuickAction(action) {
        switch (action) {
            case 'clear':
                this.clearChat();
                break;
            case 'history':
                this.openChatHistory();
                break;
            case 'export':
                this.exportChat();
                break;
        }
    }
    
    clearChat() {
        if (confirm('Tem certeza que deseja limpar a conversa atual?')) {
            // Manter apenas a mensagem de boas-vindas
            const messages = this.chatMessages?.querySelectorAll('.arn-message');
            if (messages) {
                for (let i = 1; i < messages.length; i++) {
                    messages[i].remove();
                }
            }
            
            // Iniciar nova sessão
            this.initializeSession();
        }
    }
    
    openChatHistory() {
        window.open('/dashboard/chatbot/history/', '_blank');
    }
    
    exportChat() {
        const messages = this.chatMessages?.querySelectorAll('.arn-message');
        if (!messages || messages.length <= 1) {
            alert('Nenhuma conversa para exportar.');
            return;
        }
        
        let exportText = `Conversa ARN Assistant - ${new Date().toLocaleString('pt-BR')}\n\n`;
        
        messages.forEach(msg => {
            const isUser = msg.classList.contains('user-message');
            const text = msg.querySelector('.message-text')?.textContent || '';
            const timestamp = msg.querySelector('.message-timestamp')?.textContent || '';
            
            exportText += `[${timestamp}] ${isUser ? 'Você' : 'Assistente'}: ${text}\n\n`;
        });
        
        // Download como arquivo
        const blob = new Blob([exportText], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversa_arn_${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        window.URL.revokeObjectURL(url);
    }
    
    loadChatHistory(history) {
        history.forEach(msg => {
            const messageElement = this.createMessageElement({
                type: msg.tipo,
                text: msg.mensagem,
                timestamp: new Date(msg.timestamp).toLocaleTimeString('pt-BR', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                }),
                intent: msg.intencao,
                confidence: msg.confianca
            });
            
            this.chatMessages?.appendChild(messageElement);
        });
        
        this.scrollToBottom();
    }
    
    async checkAIStatus() {
        // Verificar status dos serviços de IA
        try {
            // Teste simples para HuggingFace
            const hfStatus = await this.testAIService('huggingface');
            this.updateStatusIndicator('aiStatus', hfStatus);
            
            // Teste para DeepSeek
            const dsStatus = await this.testAIService('deepseek');
            this.updateStatusIndicator('deepseekStatus', dsStatus);
            
        } catch (error) {
            console.log('Erro ao verificar status da IA:', error);
        }
    }
    
    async testAIService(service) {
        try {
            const response = await fetch(`/dashboard/api/ai-status/${service}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            return response.ok;
        } catch (error) {
            return false;
        }
    }
    
    updateStatusIndicator(elementId, isOnline) {
        const indicator = document.getElementById(elementId);
        if (indicator) {
            indicator.className = `status-indicator ${isOnline ? 'online' : 'offline'}`;
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
               '';
    }
    
    // Utility methods
    showNotification(message, type = 'info') {
        if (window.showToast) {
            window.showToast(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    formatNumber(number) {
        return new Intl.NumberFormat('pt-BR').format(number);
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'XOF', // Franc CFA
            minimumFractionDigits: 0
        }).format(amount);
    }
}

// Funções globais para compatibilidade
window.sendChatMessage = function(message) {
    if (window.ARNAssistant) {
        window.ARNAssistant.sendMessage(message);
    }
};

window.clearChat = function() {
    if (window.ARNAssistant) {
        window.ARNAssistant.clearChat();
    }
};

// Auto-inicialização quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (!window.ARNAssistant) {
            window.ARNAssistant = new ARNAssistantInterface();
            window.ARNAssistant.initialize();
        }
    });
} else {
    // DOM já está pronto
    if (!window.ARNAssistant) {
        window.ARNAssistant = new ARNAssistantInterface();
        window.ARNAssistant.initialize();
    }
}
