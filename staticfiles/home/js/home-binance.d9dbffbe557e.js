// ==============================
// HOME BINANCE JAVASCRIPT
// ==============================

document.addEventListener('DOMContentLoaded', function() {
    initializeHome();
});

function initializeHome() {
    initializeHomeAnimations();
    initializeHomeCharts();
    initializeQuickActions();
}

// ANIMAÇÕES DA HOME
function initializeHomeAnimations() {
    // Animar valores das estatísticas
    const statValues = document.querySelectorAll('.home-stat-value');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStatValue(entry.target);
            }
        });
    });
    
    statValues.forEach(value => observer.observe(value));
    
    // Animar entrada dos cards
    animateFeatureCards();
}

function animateStatValue(element) {
    const finalValue = element.textContent.replace(/[^\d]/g, '');
    if (!finalValue || isNaN(finalValue)) return;
    
    const startValue = 0;
    const endValue = parseInt(finalValue);
    const duration = 2000;
    const startTime = performance.now();
    
    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.round(startValue + (endValue - startValue) * easeOutQuart(progress));
        
        // Manter formato original do texto
        const originalText = element.textContent;
        const newText = originalText.replace(/[\d,]+/, currentValue.toLocaleString('pt-BR'));
        element.textContent = newText;
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }
    
    requestAnimationFrame(updateValue);
}

function animateFeatureCards() {
    const cards = document.querySelectorAll('.home-feature-card');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
    });
}

// GRÁFICOS SIMPLES DA HOME
function initializeHomeCharts() {
    initializeAssinantesChart();
    initializeReceitasChart();
}

function initializeAssinantesChart() {
    const ctx = document.getElementById('homeAssinantesChart');
    if (!ctx) return;
    
    // Dados de exemplo baseados no context
    const assinantesData = window.assinantesData || [];
    
    if (assinantesData.length === 0) return;
    
    const labels = assinantesData.map(item => item.operadora);
    const data = assinantesData.map(item => item.assinantes);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#F0B90B', // Binance Yellow
                    '#FF6600', // Orange
                    '#DC3545', // Blue
                    '#02C076', // Green
                ],
                borderColor: '#161A1E',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#F0F0F0',
                        usePointStyle: true,
                        padding: 20,
                        font: { family: 'Inter' }
                    }
                }
            }
        }
    });
}

function initializeReceitasChart() {
    const ctx = document.getElementById('homeReceitasChart');
    if (!ctx) return;
    
    // Dados de evolução de receitas (exemplo)
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    const receitas = [3800, 3900, 4000, 4100, 4200, 4000, 4150, 4300, 4250, 4400, 4350, 4500]; // Exemplo
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: meses,
            datasets: [{
                label: 'Receitas Mensais (M FCFA)',
                data: receitas,
                borderColor: '#F0B90B',
                backgroundColor: 'rgba(240, 185, 11, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#F0B90B',
                pointBorderColor: '#161A1E',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#F0F0F0',
                        font: { family: 'Inter' }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: '#474D57' },
                    ticks: {
                        color: '#F0F0F0',
                        font: { family: 'Inter' }
                    }
                },
                y: {
                    grid: { color: '#474D57' },
                    ticks: {
                        color: '#F0F0F0',
                        font: { family: 'Inter' }
                    }
                }
            }
        }
    });
}

// AÇÕES RÁPIDAS
function initializeQuickActions() {
    const quickActionButtons = document.querySelectorAll('.home-feature-link, .home-cta-btn');
    
    quickActionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
}

// UTILITY FUNCTIONS
function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

function showWelcomeMessage() {
    const userName = document.querySelector('.user-avatar')?.textContent || 'Usuário';
    
    if (window.showToast) {
        window.showToast(`Bem-vindo à ARN Platform, ${userName}!`, 'success');
    }
}

// Initialize welcome message after load
setTimeout(showWelcomeMessage, 1000);

// Export functions for use in templates
window.HomeJS = {
    animateStatValue,
    showWelcomeMessage
};
