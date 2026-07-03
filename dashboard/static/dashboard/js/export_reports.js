/**
 * Sistema de Exportação de Relatórios ARN
 * Gerencia download de PDFs, Excel e CSV
 */

(function() {
    'use strict';
    
    // Configuração
    const CONFIG = {
        exportBaseUrl: '/dashboard/reports/export/',
        loadingClass: 'exporting',
        errorDisplayTime: 5000
    };
    
    /**
     * Inicializa o sistema de exportação
     */
    function initExportSystem() {
        // Adicionar event listeners aos botões de exportação
        document.querySelectorAll('.btn-export').forEach(button => {
            button.addEventListener('click', handleExportClick);
        });
        
        // Adicionar event listeners aos links de exportação rápida
        document.querySelectorAll('[data-export-report]').forEach(link => {
            link.addEventListener('click', handleQuickExportClick);
        });
    }
    
    /**
     * Manipula clique no botão de exportação
     */
    function handleExportClick(event) {
        event.preventDefault();
        
        const button = event.currentTarget;
        const format = button.dataset.format || 'pdf';
        const reportType = button.dataset.reportType || getCurrentReportType();
        
        // Obter ano da URL ou campo de filtro
        const year = getYearParameter();
        
        // Mostrar loading
        showLoading(button);
        
        // Construir URL de exportação
        const exportUrl = buildExportUrl(reportType, format, year);
        
        // Fazer download
        downloadFile(exportUrl, button);
    }
    
    /**
     * Manipula exportação rápida
     */
    function handleQuickExportClick(event) {
        event.preventDefault();
        
        const link = event.currentTarget;
        const report = link.dataset.exportReport;
        const format = link.dataset.exportFormat || 'pdf';
        const year = link.dataset.exportYear || new Date().getFullYear();
        
        showLoading(link);
        
        const exportUrl = buildExportUrl(report, format, year);
        downloadFile(exportUrl, link);
    }
    
    /**
     * Constrói URL de exportação
     */
    function buildExportUrl(reportType, format, year) {
        const url = `${CONFIG.exportBaseUrl}${reportType}/${format}/`;
        const params = new URLSearchParams({ year: year });
        return `${url}?${params.toString()}`;
    }
    
    /**
     * Faz download do arquivo
     */
    function downloadFile(url, triggerElement) {
        // Criar elemento temporário para download
        const link = document.createElement('a');
        link.href = url;
        link.style.display = 'none';
        document.body.appendChild(link);
        
        // Verificar se o download foi bem-sucedido
        fetch(url, { method: 'HEAD' })
            .then(response => {
                if (response.ok) {
                    link.click();
                    showSuccess(triggerElement);
                } else {
                    throw new Error('Erro ao exportar relatório');
                }
            })
            .catch(error => {
                showError(triggerElement, error.message);
            })
            .finally(() => {
                hideLoading(triggerElement);
                document.body.removeChild(link);
            });
    }
    
    /**
     * Obtém tipo de relatório atual da URL ou contexto
     */
    function getCurrentReportType() {
        const path = window.location.pathname;
        
        if (path.includes('/market/')) return 'market';
        if (path.includes('/executive/')) return 'executive';
        if (path.includes('/comparative/')) return 'comparative';
        
        // Default
        return 'market';
    }
    
    /**
     * Obtém parâmetro year da URL ou seletor
     */
    function getYearParameter() {
        // Tentar obter da URL
        const urlParams = new URLSearchParams(window.location.search);
        let year = urlParams.get('year');
        
        // Se não encontrar, tentar do seletor
        if (!year) {
            const yearSelect = document.querySelector('select[name="year"]');
            if (yearSelect) {
                year = yearSelect.value;
            }
        }
        
        // Se ainda não encontrar, usar ano atual
        if (!year) {
            year = new Date().getFullYear();
        }
        
        return year;
    }
    
    /**
     * Mostra indicador de loading
     */
    function showLoading(element) {
        element.classList.add(CONFIG.loadingClass);
        element.disabled = true;
        
        // Salvar conteúdo original
        element.dataset.originalContent = element.innerHTML;
        
        // Mostrar spinner
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exportando...';
    }
    
    /**
     * Esconde indicador de loading
     */
    function hideLoading(element) {
        element.classList.remove(CONFIG.loadingClass);
        element.disabled = false;
        
        // Restaurar conteúdo original
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }
    }
    
    /**
     * Mostra mensagem de sucesso
     */
    function showSuccess(element) {
        // Feedback visual temporário
        const originalBg = element.style.backgroundColor;
        element.style.backgroundColor = '#28a745';
        
        setTimeout(() => {
            element.style.backgroundColor = originalBg;
        }, 1000);
        
        // Mostrar toast/notificação
        showNotification('Relatório exportado com sucesso!', 'success');
    }
    
    /**
     * Mostra mensagem de erro
     */
    function showError(element, message) {
        console.error('Erro na exportação:', message);
        
        // Feedback visual temporário
        const originalBg = element.style.backgroundColor;
        element.style.backgroundColor = '#dc3545';
        
        setTimeout(() => {
            element.style.backgroundColor = originalBg;
        }, 1000);
        
        // Mostrar toast/notificação
        showNotification(`Erro ao exportar: ${message}`, 'error');
    }
    
    /**
     * Mostra notificação toast
     */
    function showNotification(message, type = 'info') {
        // Criar elemento de notificação
        const notification = document.createElement('div');
        notification.className = `export-notification export-notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
        `;
        
        // Adicionar ao body
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Remover após tempo
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, CONFIG.errorDisplayTime);
    }
    
    // Estilos para notificações
    function addNotificationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .export-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                transform: translateX(400px);
                transition: transform 0.3s ease;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }
            
            .export-notification.show {
                transform: translateX(0);
            }
            
            .export-notification-success {
                background: linear-gradient(135deg, #28a745, #20c997);
            }
            
            .export-notification-error {
                background: linear-gradient(135deg, #dc3545, #c82333);
            }
            
            .export-notification-info {
                background: linear-gradient(135deg, #17a2b8, #138496);
            }
            
            .btn-export.exporting {
                opacity: 0.7;
                cursor: not-allowed;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Inicializar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            addNotificationStyles();
            initExportSystem();
        });
    } else {
        addNotificationStyles();
        initExportSystem();
    }
    
})();

