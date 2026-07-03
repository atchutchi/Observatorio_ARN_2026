document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Inicializar popovers do Bootstrap
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Função para criar gráficos
    window.createChart = function(chartId, chartType, chartData, chartOptions) {
        const ctx = document.getElementById(chartId);
        if (!ctx) return;
        
        // Definir cores padrão para gráficos
        const defaultColors = [
            'rgba(52, 152, 219, 0.8)',    // Azul
            'rgba(243, 156, 18, 0.8)',    // Laranja
            'rgba(46, 204, 113, 0.8)',    // Verde
            'rgba(231, 76, 60, 0.8)',     // Vermelho
            'rgba(155, 89, 182, 0.8)',    // Roxo
            'rgba(52, 73, 94, 0.8)',      // Cinza escuro
            'rgba(22, 160, 133, 0.8)',    // Verde água
            'rgba(230, 126, 34, 0.8)',    // Laranja escuro
            'rgba(41, 128, 185, 0.8)',    // Azul escuro
            'rgba(44, 62, 80, 0.8)'       // Azul marinho
        ];
        
        const borderColors = defaultColors.map(color => color.replace('0.8', '1'));
        
        // Configurações padrão para gráficos
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        boxWidth: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    padding: 10,
                    cornerRadius: 4,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        };
        
        // Verificar se são dados para gráfico de linhas ou barras
        if (chartType === 'line' || chartType === 'bar') {
            defaultOptions.scales = {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            };
        }
        
        // Mesclar opções padrão com opções personalizadas
        const options = {...defaultOptions, ...chartOptions};
        
        // Adicionar cores padrão se não foram fornecidas
        if (chartData.datasets) {
            chartData.datasets.forEach((dataset, index) => {
                if (!dataset.backgroundColor) {
                    dataset.backgroundColor = defaultColors[index % defaultColors.length];
                }
                if (!dataset.borderColor && (chartType === 'line' || chartType === 'radar')) {
                    dataset.borderColor = borderColors[index % borderColors.length];
                }
            });
        }
        
        // Criar o gráfico
        return new Chart(ctx, {
            type: chartType,
            data: chartData,
            options: options
        });
    };
    
    // Adicionar classes de animação aos elementos
    const animElements = document.querySelectorAll('.anim-fade-in');
    animElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('fade-in');
        }, index * 100);
    });
    
    // Evento para alternar entre modo claro e escuro
    const themeToggler = document.getElementById('theme-toggler');
    if (themeToggler) {
        themeToggler.addEventListener('click', function() {
            document.body.classList.toggle('theme-dark');
            document.body.classList.toggle('theme-light');
            
            const isDark = document.body.classList.contains('theme-dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            // Atualizar o ícone
            const icon = this.querySelector('i');
            if (isDark) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        });
    }
    
    // Aplicar tema salvo
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.add(`theme-${savedTheme}`);
        document.body.classList.remove(`theme-${savedTheme === 'dark' ? 'light' : 'dark'}`);
        
        if (themeToggler) {
            const icon = themeToggler.querySelector('i');
            if (savedTheme === 'dark') {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }
        }
    }
    
    // Função para formatar números
    window.formatNumber = function(number, decimals = 0, decPoint = ',', thousandsSep = '.') {
        number = (number + '').replace(/[^0-9+\-Ee.]/g, '');
        const n = !isFinite(+number) ? 0 : +number;
        const prec = !isFinite(+decimals) ? 0 : Math.abs(decimals);
        const sep = (typeof thousandsSep === 'undefined') ? ',' : thousandsSep;
        const dec = (typeof decPoint === 'undefined') ? '.' : decPoint;
        let s = '';
        
        const toFixedFix = function (n, prec) {
            const k = Math.pow(10, prec);
            return '' + Math.round(n * k) / k;
        };
        
        s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
        if (s[0].length > 3) {
            s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
        }
        if ((s[1] || '').length < prec) {
            s[1] = s[1] || '';
            s[1] += new Array(prec - s[1].length + 1).join('0');
        }
        
        return s.join(dec);
    };
}); 