document.addEventListener('DOMContentLoaded', function() {
    const dataElement = document.getElementById('analysis-data');
    if (!dataElement) {
        console.error('Elemento de dados #analysis-data não encontrado.');
        return;
    }

    let analysisData;
    try {
        analysisData = JSON.parse(dataElement.textContent);
    } catch (e) {
        console.error('Erro ao parsear dados JSON:', e);
        return;
    }

    if (!analysisData || Object.keys(analysisData).length === 0) {
        console.warn('Dados de análise vazios ou inválidos.');
        return;
    }

    const operators = Object.keys(analysisData).filter(op => op !== 'TOTAL');
    const quarters = ['Q1', 'Q2', 'Q3', 'Q4'];

    // --- Chart 1: Annual Total per Operator --- 
    const annualOperatorCtx = document.getElementById('annualOperatorChart')?.getContext('2d');
    if (annualOperatorCtx) {
        const annualData = operators.map(op => {
            // Sum all total_* fields for the annual data of this operator
            const operatorAnnualData = analysisData[op]?.annual || {};
            return Object.values(operatorAnnualData).reduce((sum, val) => sum + (Number(val) || 0), 0);
        });
        
        new Chart(annualOperatorCtx, {
            type: 'bar',
            data: {
                labels: operators,
                datasets: [{
                    label: 'Total Anual Agregado',
                    data: annualData,
                    backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#dc3545'], // Example colors
                    borderColor: ['#0a58ca', '#146c43', '#ffb300', '#b02a37'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                 plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('pt-PT').format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }

    // --- Chart 2: Quarterly Total (Market) --- 
    const quarterlyTotalCtx = document.getElementById('quarterlyTotalChart')?.getContext('2d');
    if (quarterlyTotalCtx && analysisData['TOTAL']?.quarterly) {
        const quarterlyData = quarters.map(q => {
            // Sum all total_* fields for the quarterly data of TOTAL
            const quarterTotalData = analysisData['TOTAL']['quarterly'][q] || {};
             return Object.values(quarterTotalData).reduce((sum, val) => sum + (Number(val) || 0), 0);
        });

        new Chart(quarterlyTotalCtx, {
            type: 'line',
            data: {
                labels: quarters,
                datasets: [{
                    label: 'Total Trimestral (Mercado)',
                    data: quarterlyData,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
             options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                 plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('pt-PT').format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }

     // --- Utility Functions for Child Templates --- 
     window.createAnalysisChart = function(ctxId, chartType, labels, datasets, options = {}) {
         const ctx = document.getElementById(ctxId)?.getContext('2d');
         if (!ctx) {
             console.error(`Canvas com ID '${ctxId}' não encontrado.`);
             return null;
         }
         const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            scales: chartType !== 'pie' && chartType !== 'doughnut' ? {
                y: {
                    beginAtZero: true
                }
            } : undefined,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            let value = context.parsed.y ?? context.parsed;
                            if (value !== null) {
                                label += new Intl.NumberFormat('pt-PT').format(value);
                            }
                            return label;
                        }
                    }
                }
            }
         };
         const mergedOptions = {
             ...defaultOptions,
             ...options,
             plugins: { 
                 ...(defaultOptions.plugins || {}),
                 ...(options.plugins || {})
             }
         };

         return new Chart(ctx, {
             type: chartType,
             data: {
                 labels: labels,
                 datasets: datasets 
             },
             options: mergedOptions
         });
     };

    window.getAnalysisData = function() {
        return analysisData;
    };

    window.getOperatorColors = function() {
        // Define consistent colors for operators
        return {
            'ORANGE': '#fd7e14', // Bootstrap orange
            'TELECEL': '#ffc107',    // Bootstrap yellow
            'TELECEL': '#0d6efd', // Bootstrap primary blue
            'TOTAL': '#6c757d'  // Bootstrap secondary grey
        };
    };

}); 