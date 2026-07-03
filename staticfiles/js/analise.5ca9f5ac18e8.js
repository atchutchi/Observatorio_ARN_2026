// ==============================
// ANÁLISE JAVASCRIPT
// ==============================

document.addEventListener('DOMContentLoaded', function() {
    initializeAnalise();
});

function initializeAnalise() {
    initializeCharts();
    initializeFilters();
    initializeComparisons();
    initializeExportButtons();
}

// INICIALIZAÇÃO DOS GRÁFICOS
function initializeCharts() {
    // Get analysis data from the DOM
    const analysisDataElement = document.getElementById('analysis-data');
    if (!analysisDataElement) return;
    
    try {
        const analysisData = JSON.parse(analysisDataElement.textContent);
        
        // Create charts
        createAnnualOperatorChart(analysisData);
        createQuarterlyTotalChart(analysisData);
        
    } catch (error) {
        console.error('Erro ao carregar dados de análise:', error);
    }
}

function createAnnualOperatorChart(data) {
    const ctx = document.getElementById('annualOperatorChart');
    if (!ctx) return;
    
    const operators = Object.keys(data).filter(op => op !== 'TOTAL');
    const values = operators.map(op => {
        const annual = data[op].annual;
        return annual ? Object.values(annual).reduce((sum, val) => {
            const numVal = parseFloat(val) || 0;
            return sum + numVal;
        }, 0) : 0;
    });
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: operators,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#F0B90B', // Binance Yellow
                    '#4EAEFF', // Binance Blue
                    '#02C076', // Binance Green
                    '#F84060', // Binance Red
                    '#B7BDC6'  // Binance Gray
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
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            }
        }
    });
}

function createQuarterlyTotalChart(data) {
    const ctx = document.getElementById('quarterlyTotalChart');
    if (!ctx) return;
    
    const quarters = ['1', '2', '3', '4'];
    const totalData = data.TOTAL ? data.TOTAL.quarterly : {};
    
    const values = quarters.map(q => {
        const qData = totalData[q];
        if (!qData) return 0;
        
        return Object.values(qData).reduce((sum, val) => {
            const numVal = parseFloat(val) || 0;
            return sum + numVal;
        }, 0);
    });
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: quarters.map(q => `${q}º Trim`),
            datasets: [{
                label: 'Total do Mercado',
                data: values,
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
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#474D57'
                    },
                    ticks: {
                        color: '#F0F0F0',
                        font: {
                            family: 'Inter'
                        }
                    }
                },
                y: {
                    grid: {
                        color: '#474D57'
                    },
                    ticks: {
                        color: '#F0F0F0',
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            }
        }
    });
}

// FILTROS DA ANÁLISE
function initializeFilters() {
    const filterInputs = document.querySelectorAll('.analise-filter input, .analise-filter select');
    
    filterInputs.forEach(input => {
        input.addEventListener('change', applyFilters);
    });
}

function applyFilters() {
    const filters = {};
    
    // Collect filter values
    document.querySelectorAll('.analise-filter input, .analise-filter select').forEach(input => {
        if (input.value && input.value !== '') {
            filters[input.name] = input.value;
        }
    });
    
    // Apply filters to table
    filterAnalysisTable(filters);
}

function filterAnalysisTable(filters) {
    const table = document.querySelector('.analise-table tbody');
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        let shouldShow = true;
        
        for (const [filterName, filterValue] of Object.entries(filters)) {
            const cell = row.querySelector(`[data-filter="${filterName}"]`);
            if (cell) {
                const cellValue = cell.textContent.toLowerCase();
                if (!cellValue.includes(filterValue.toLowerCase())) {
                    shouldShow = false;
                    break;
                }
            }
        }
        
        row.style.display = shouldShow ? '' : 'none';
    });
}

// COMPARAÇÕES
function initializeComparisons() {
    const comparisonButtons = document.querySelectorAll('[data-comparison]');
    
    comparisonButtons.forEach(button => {
        button.addEventListener('click', function() {
            const comparisonType = this.dataset.comparison;
            showComparison(comparisonType);
        });
    });
}

function showComparison(type) {
    const comparisonModal = document.getElementById('comparisonModal');
    if (!comparisonModal) return;
    
    // Load comparison data based on type
    loadComparisonData(type).then(data => {
        renderComparison(data);
        // Show modal (using Bootstrap)
        const modal = new bootstrap.Modal(comparisonModal);
        modal.show();
    });
}

async function loadComparisonData(type) {
    try {
        const response = await fetch(`/api/comparison/${type}/`);
        return await response.json();
    } catch (error) {
        console.error('Erro ao carregar dados de comparação:', error);
        return null;
    }
}

function renderComparison(data) {
    const comparisonContainer = document.querySelector('.comparison-content');
    if (!comparisonContainer || !data) return;
    
    // Render comparison based on data structure
    comparisonContainer.innerHTML = `
        <div class="comparison-grid">
            ${Object.entries(data).map(([key, value]) => `
                <div class="comparison-item">
                    <div class="comparison-value">${formatValue(value)}</div>
                    <div class="comparison-label">${key}</div>
                </div>
            `).join('')}
        </div>
    `;
}

// EXPORTAÇÃO
function initializeExportButtons() {
    const exportButtons = document.querySelectorAll('[data-export]');
    
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const exportType = this.dataset.export;
            exportData(exportType);
        });
    });
}

function exportData(type) {
    switch (type) {
        case 'excel':
            exportToExcel();
            break;
        case 'pdf':
            exportToPDF();
            break;
        case 'csv':
            exportToCSV();
            break;
        default:
            console.log('Tipo de exportação não suportado:', type);
    }
}

function exportToExcel() {
    const table = document.querySelector('.analise-table');
    if (!table) return;
    
    // Simple table to Excel conversion
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = Array.from(cols).map(col => 
            '"' + col.textContent.replace(/"/g, '""') + '"'
        );
        csv.push(csvRow.join(','));
    });
    
    downloadFile(csv.join('\n'), 'analise.csv', 'text/csv');
}

function exportToPDF() {
    // This would require a PDF library like jsPDF
    console.log('Exportação para PDF - implementar com jsPDF');
    showNotification('Exportação para PDF será implementada em breve', 'info');
}

function exportToCSV() {
    exportToExcel(); // Same logic for CSV
}

// UTILITY FUNCTIONS
function formatValue(value) {
    if (typeof value === 'number') {
        return value.toLocaleString('pt-BR');
    }
    return value;
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

function showNotification(message, type = 'info') {
    // Use platform notification system
    if (window.showToast) {
        window.showToast(message, type);
    } else {
        alert(message);
    }
}

// ANIMATION HELPERS
function animateValue(element, start, end, duration = 1000) {
    const startTimestamp = performance.now();
    
    const step = (timestamp) => {
        const elapsed = timestamp - startTimestamp;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (end - start) * easeOutQuart(progress);
        element.textContent = Math.round(current).toLocaleString('pt-BR');
        
        if (progress < 1) {
            requestAnimationFrame(step);
        }
    };
    
    requestAnimationFrame(step);
}

function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

// Export functions for use in templates
window.AnaliseJS = {
    animateValue,
    showNotification,
    exportData,
    createAnnualOperatorChart,
    createQuarterlyTotalChart
};
