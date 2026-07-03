// ==============================
// ARN PLATFORM JAVASCRIPT
// ==============================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize platform components
    initializeSidebar();
    initializeNotificationSystem();
    initializeToastCleanup();
});

// SIDEBAR FUNCTIONALITY
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-open');
        });
    }
}

// NOTIFICATION SYSTEM
class NotificationSystem {
    constructor() {
        this.loadNotifications();
        this.setupEventListeners();
        // Check for new notifications every 30 seconds
        setInterval(() => this.loadNotifications(), 30000);
    }
    
    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications/');
            const data = await response.json();
            
            this.updateBadge(data.unread_count);
            this.renderNotifications(data.notifications);
        } catch (error) {
            console.error('Erro ao carregar notificações:', error);
        }
    }
    
    updateBadge(count) {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        }
    }
    
    renderNotifications(notifications) {
        const container = document.getElementById('notificationsList');
        if (!container) return;
        
        if (notifications.length === 0) {
            container.innerHTML = `
                <div class="p-3 text-center" style="color: var(--binance-text-muted);">
                    <i class="fas fa-bell-slash fa-2x mb-2"></i>
                    <p class="mb-0">Nenhuma notificação</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = notifications.map(notification => `
            <li class="notification-item ${!notification.is_read ? 'unread' : ''}" data-id="${notification.id}">
                <div class="p-3 border-bottom notification-item-content" data-notification-id="${notification.id}">
                    <div class="d-flex">
                        <div class="me-3">
                            <i class="fas fa-${this.getTypeIcon(notification.type)}" 
                               style="color: ${this.getTypeColor(notification.type)};"></i>
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="mb-1 notification-title">
                                ${notification.title}
                            </h6>
                            <p class="mb-1 notification-message">
                                ${notification.message}
                            </p>
                            <small class="notification-time">${notification.created_at}</small>
                        </div>
                        ${!notification.is_read ? '<div class="ms-2"><div class="notification-dot"></div></div>' : ''}
                    </div>
                </div>
            </li>
        `).join('');
        
        // Add click event listeners
        container.querySelectorAll('.notification-item-content').forEach(item => {
            item.addEventListener('click', () => {
                const notificationId = item.dataset.notificationId;
                this.markAsRead(parseInt(notificationId));
            });
        });
    }
    
    getTypeIcon(type) {
        const icons = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    getTypeColor(type) {
        const colors = {
            'info': 'var(--binance-info)',
            'success': 'var(--binance-success)',
            'warning': 'var(--binance-warning)',
            'error': 'var(--binance-danger)'
        };
        return colors[type] || 'var(--binance-info)';
    }
    
    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Erro ao marcar notificação como lida:', error);
        }
    }
    
    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Erro ao marcar todas as notificações como lidas:', error);
        }
    }
    
    setupEventListeners() {
        const markAllBtn = document.getElementById('markAllReadBtn');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', () => this.markAllAsRead());
        }
    }
    
    getCSRFToken() {
        // Try multiple ways to get CSRF token
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput) return tokenInput.value;
        
        const tokenMeta = document.querySelector('meta[name=csrf-token]');
        if (tokenMeta) return tokenMeta.getAttribute('content');
        
        // Try to get from cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return value;
        }
        
        return '';
    }
}

// Initialize notification system
function initializeNotificationSystem() {
    window.notificationSystem = new NotificationSystem();
}

// TOAST CLEANUP
function initializeToastCleanup() {
    // Auto-hide toast notifications
    const toastContainer = document.querySelector('.notification-container');
    if (toastContainer) {
        setTimeout(() => {
            const notifications = toastContainer.querySelectorAll('.notification');
            notifications.forEach(notification => {
                notification.style.animation = 'slideIn 0.3s ease reverse';
                setTimeout(() => {
                    notification.remove();
                }, 300);
            });
        }, 5000);
    }
}

// UTILITY FUNCTIONS
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.notification-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `notification notification-${type}`;
    toast.innerHTML = `
        <div>
            <i class="fas fa-${getToastIcon(type)}"></i>
        </div>
        <div>
            <strong>${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
            <p class="mb-0 mt-1">${message}</p>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'notification-container';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    const icons = {
        'info': 'info-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'error': 'times-circle'
    };
    return icons[type] || 'info-circle';
}
