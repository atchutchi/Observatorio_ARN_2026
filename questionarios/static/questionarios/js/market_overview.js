/**
 * Script para a visualização gráfica da visão geral do mercado
 * Este script recebe dados do Django e cria gráficos usando Chart.js
 */
function initMarketOverviewCharts(anos, assinantesData, receitaData, trafegoData, investimentosData) {
    // Gráfico de Assinantes
    const assinantesChart = new Chart(
        document.getElementById('assinantesChart'),
        {
            type: 'bar',
            data: {
                labels: anos,
                datasets: [{
                    label: 'Total de Assinantes',
                    data: assinantesData,
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: false,
                        text: 'Total de Assinantes por Ano'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    );
    
    // Gráfico de Receita
    const receitaChart = new Chart(
        document.getElementById('receitaChart'),
        {
            type: 'bar',
            data: {
                labels: anos,
                datasets: [{
                    label: 'Receita Total (milhões)',
                    data: receitaData,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: false,
                        text: 'Receita Total por Ano'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    );
    
    // Gráfico de Tráfego de Dados
    const trafegoChart = new Chart(
        document.getElementById('trafegoChart'),
        {
            type: 'bar',
            data: {
                labels: anos,
                datasets: [{
                    label: 'Tráfego de Dados (TB)',
                    data: trafegoData,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: false,
                        text: 'Tráfego de Dados por Ano'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    );
    
    // Gráfico de Investimentos
    const investimentosChart = new Chart(
        document.getElementById('investimentosChart'),
        {
            type: 'bar',
            data: {
                labels: anos,
                datasets: [{
                    label: 'Investimentos (milhões)',
                    data: investimentosData,
                    backgroundColor: 'rgba(255, 206, 86, 0.5)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: false,
                        text: 'Investimentos por Ano'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    );
} 