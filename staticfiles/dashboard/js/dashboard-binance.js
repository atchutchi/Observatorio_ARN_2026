// ==============================
// DASHBOARD BINANCE JAVASCRIPT
// ==============================

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    initializeKPIs();
    initializeDashboardCharts();
    initializeExportButtons();
    initializeFilters();
    initializeRealTimeUpdates();
}

// KPIs ANIMATION
function initializeKPIs() {
    const kpiValues = document.querySelectorAll('.kpi-value');
    
    // Animar valores dos KPIs quando entram na viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateKPIValue(entry.target);
            }
        });
    });
    
    kpiValues.forEach(value => observer.observe(value));
}

function animateKPIValue(element) {
    const finalValue = element.dataset.value || element.textContent.replace(/[^\d]/g, '');
    const duration = 2000;
    
    if (!finalValue || isNaN(finalValue)) return;
    
    const startValue = 0;
    const endValue = parseInt(finalValue);
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

// DASHBOARD CHARTS
function initializeDashboardCharts() {
    // Chart padrão para market share
    initializeMarketShareChart();
    
    // Chart de evolução temporal
    initializeEvolutionChart();
    
    // Chart de comparação de operadoras
    initializeOperatorComparisonChart();
    
    // Chart de tráfego
    initializeTrafficChart();
}

function initializeMarketShareChart() {
    const ctx = document.getElementById('marketShareChart');
    if (!ctx) return;
    
    const data = JSON.parse(document.getElementById('market-share-data')?.textContent || '{}');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
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

function initializeEvolutionChart() {
    const ctx = document.getElementById('evolutionChart');
    if (!ctx) return;
    
    const data = JSON.parse(document.getElementById('evolution-data')?.textContent || '[]');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.periodo),
            datasets: [{
                label: 'Evolução',
                data: data.map(item => item.valor),
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
        options: getDashboardChartOptions()
    });
}

function initializeOperatorComparisonChart() {
    const ctx = document.getElementById('operatorComparisonChart');
    if (!ctx) return;
    
    const data = JSON.parse(document.getElementById('operator-comparison-data')?.textContent || '{}');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Valores',
                data: Object.values(data),
                backgroundColor: [
                    '#DC3545', // MTN
                    '#FF6600', // Orange
                    '#DC3545', // Telecel
                ],
                borderColor: '#161A1E',
                borderWidth: 2
            }]
        },
        options: getDashboardChartOptions()
    });
}

function initializeTrafficChart() {
    const ctx = document.getElementById('trafficChart');
    if (!ctx) return;
    
    const data = JSON.parse(document.getElementById('traffic-data')?.textContent || '{}');
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['On-Net', 'Off-Net', 'Internacional', 'SMS', 'Dados'],
            datasets: Object.keys(data).map((operator, index) => ({
                label: operator,
                data: data[operator],
                backgroundColor: `rgba(${getOperatorColor(operator)}, 0.2)`,
                borderColor: getOperatorColor(operator, false),
                borderWidth: 2,
                pointBackgroundColor: getOperatorColor(operator, false),
                pointBorderColor: '#161A1E',
                pointBorderWidth: 2
            }))
        },
        options: {
            ...getDashboardChartOptions(),
            scales: {
                r: {
                    angleLines: { color: '#474D57' },
                    grid: { color: '#474D57' },
                    pointLabels: {
                        color: '#F0F0F0',
                        font: { family: 'Inter' }
                    },
                    ticks: {
                        color: '#F0F0F0',
                        font: { family: 'Inter' },
                        backdropColor: 'transparent'
                    }
                }
            }
        }
    });
}

function getDashboardChartOptions() {
    return {
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
    };
}

function getOperatorColor(operator, withAlpha = true) {
    const colors = {
        'ORANGE': withAlpha ? 'rgba(255, 102, 0, 0.8)' : '#FF6600',
        'TELECEL': withAlpha ? 'rgba(220, 53, 69, 0.8)' : '#DC3545'
    };
    return colors[operator.toUpperCase()] || (withAlpha ? 'rgba(240, 185, 11, 0.8)' : '#F0B90B');
}

// EXPORT FUNCTIONALITY
function initializeExportButtons() {
    const exportButtons = document.querySelectorAll('.btn-export');
    
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const format = this.dataset.format;
            const reportType = this.dataset.reportType || 'dashboard';
            
            exportDashboardData(format, reportType);
        });
    });
}

async function exportDashboardData(format, reportType) {
    try {
        showLoadingIndicator('Gerando relatório...');
        
        const formData = new FormData();
        formData.append('format', format);
        formData.append('report_type', reportType);
        formData.append('year', getCurrentYear());
        
        const response = await fetch('/dashboard/reports/generate/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        });
        
        if (response.ok) {
            if (format === 'csv') {
                // Download direto para CSV
                const blob = await response.blob();
                downloadBlob(blob, `dashboard_${reportType}_${getCurrentYear()}.csv`);
            } else {
                const data = await response.json();
                if (data.success) {
                    showNotification(`Relatório ${format.toUpperCase()} gerado com sucesso!`, 'success');
                } else {
                    showNotification(data.error || 'Erro ao gerar relatório', 'error');
                }
            }
        } else {
            throw new Error('Erro na resposta do servidor');
        }
        
    } catch (error) {
        showNotification('Erro ao exportar dados: ' + error.message, 'error');
    } finally {
        hideLoadingIndicator();
    }
}

// FILTERS
function initializeFilters() {
    const filterInputs = document.querySelectorAll('.dashboard-filter');
    
    filterInputs.forEach(input => {
        input.addEventListener('change', applyDashboardFilters);
    });
    
    // Filter trigger button
    const filterButton = document.getElementById('applyFilters');
    if (filterButton) {
        filterButton.addEventListener('click', applyDashboardFilters);
    }
}

function applyDashboardFilters() {
    const filters = {};
    
    document.querySelectorAll('.dashboard-filter').forEach(input => {
        if (input.value) {
            filters[input.name] = input.value;
        }
    });
    
    // Aplicar filtros aos dados
    updateDashboardWithFilters(filters);
}

async function updateDashboardWithFilters(filters) {
    try {
        const params = new URLSearchParams(filters);
        const response = await fetch(`/dashboard/api/reports/dashboard/?${params}`);
        const data = await response.json();
        
        // Atualizar KPIs
        updateKPIs(data.kpis_principais);
        
        // Atualizar gráficos
        updateDashboardCharts(data);
        
        showNotification('Filtros aplicados com sucesso!', 'success');
        
    } catch (error) {
        showNotification('Erro ao aplicar filtros', 'error');
    }
}

// REAL-TIME UPDATES
function initializeRealTimeUpdates() {
    // Atualizar dados a cada 5 minutos
    setInterval(refreshDashboardData, 5 * 60 * 1000);
}

async function refreshDashboardData() {
    try {
        const response = await fetch('/dashboard/api/reports/dashboard/');
        const data = await response.json();
        
        updateKPIs(data.kpis_principais);
        updateLastUpdateTime();
        
    } catch (error) {
        console.log('Erro ao atualizar dados em tempo real:', error);
    }
}

function updateKPIs(kpisData) {
    Object.keys(kpisData).forEach(kpiKey => {
        const element = document.querySelector(`[data-kpi="${kpiKey}"]`);
        if (element) {
            const valueElement = element.querySelector('.kpi-value');
            const changeElement = element.querySelector('.kpi-change');
            
            if (valueElement) {
                valueElement.textContent = kpisData[kpiKey].valor;
            }
            
            if (changeElement) {
                changeElement.textContent = kpisData[kpiKey].variacao;
                
                // Atualizar classe de cor baseada na variação
                changeElement.classList.remove('positive', 'negative', 'neutral');
                if (kpisData[kpiKey].variacao.includes('+')) {
                    changeElement.classList.add('positive');
                } else if (kpisData[kpiKey].variacao.includes('-')) {
                    changeElement.classList.add('negative');
                } else {
                    changeElement.classList.add('neutral');
                }
            }
        }
    });
}

function updateLastUpdateTime() {
    const updateElement = document.getElementById('lastUpdate');
    if (updateElement) {
        updateElement.textContent = new Date().toLocaleString('pt-BR');
    }
}

// UTILITY FUNCTIONS
function getCurrentYear() {
    return new Date().getFullYear();
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
}

function showLoadingIndicator(message = 'Carregando...') {
    // Implementar indicador de loading
    const loading = document.createElement('div');
    loading.id = 'loading-indicator';
    loading.innerHTML = `
        <div class="loading-backdrop">
            <div class="loading-content">
                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                <p>${message}</p>
            </div>
        </div>
    `;
    loading.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.7); z-index: 9999; display: flex;
        align-items: center; justify-content: center;
    `;
    loading.querySelector('.loading-content').style.cssText = `
        background: var(--binance-dark-light); padding: 2rem;
        border-radius: 12px; text-align: center; color: var(--binance-text);
    `;
    document.body.appendChild(loading);
}

function hideLoadingIndicator() {
    const loading = document.getElementById('loading-indicator');
    if (loading) loading.remove();
}

function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

function showNotification(message, type = 'info') {
    if (window.showToast) {
        window.showToast(message, type);
    } else {
        alert(message);
    }
}

function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

// Export functions for use in templates
window.DashboardJS = {
    updateKPIs,
    refreshDashboardData,
    exportDashboardData,
    showNotification
};
