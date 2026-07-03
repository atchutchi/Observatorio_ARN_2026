document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    // Validação do formulário
    form.addEventListener('submit', function(event) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[type="number"], input[type="text"]');
        
        // Validação geral para todos os campos
        inputs.forEach(function(input) {
            removeError(input);
            
            if (input.hasAttribute('required') && !input.value) {
                isValid = false;
                showError(input, 'Este campo é obrigatório.');
            }
            
            if (input.type === 'number' && parseFloat(input.value) < 0) {
                isValid = false;
                showError(input, 'O valor deve ser maior ou igual a zero.');
            }

            if (input.name.includes('taxa_imposto')) {
                const taxaPattern = /^(TVA\s*19%(\s*\+\s*IET)?|19%)$/;
                if (!taxaPattern.test(input.value)) {
                    isValid = false;
                    showError(input, 'Formato inválido. Use "TVA 19%" ou "TVA 19% + IET"');
                }
            }

            if (input.classList.contains('currency-input') && input.value && isNaN(input.value)) {
                isValid = false;
                showError(input, 'Digite apenas números.');
            }
        });

        // Validações específicas para Orange
        if (form.classList.contains('orange-form')) {
            // Internet USB Pré-pago
            const prepaidFields = ['dongle_3g', 'dongle_4g', 'airbox_4g', 'flybox_4g', 'flybox_4g_plus'];
            prepaidFields.forEach(field => {
                const input = form.querySelector(`[name="${field}"]`);
                if (input && parseInt(input.value) < 0) {
                    isValid = false;
                    showError(input, 'O valor deve ser maior ou igual a zero.');
                }
            });

            // Pacotes de Internet
            const orangePassFields = [
                'pass_ilimite_1h', 'pass_ilimite_3h', 'pass_ilimite_8h',
                'pass_ilimite_dimanche', 'pass_ilimite_nuit', 'pass_jours_ferie',
                'pass_30_mo', 'pass_75_mo', 'pass_150_mo', 'pass_250_mo',
                'pass_500_mo', 'pass_600_mo', 'pass_1_5_go', 'pass_3_go',
                'pass_10_go', 'pass_18_go', 'pass_35_go', 'pass_100_go',
                'pass_400_mo', 'pass_1_go'
            ];
            
            orangePassFields.forEach(field => {
                const input = form.querySelector(`[name="${field}"]`);
                if (input && parseInt(input.value) < 0) {
                    isValid = false;
                    showError(input, 'O valor deve ser maior ou igual a zero.');
                }
            });

            // Validação de tarifas Orange
            const orangeTarifaFields = [
                'tarifa_orange_livre_6h_22h', 'tarifa_orange_livre_22h_6h',
                'tarifa_orange_jovem_vip_jovem', 'tarifa_orange_jovem_vip_6h_22h',
                'tarifa_orange_jovem_vip_22h_6h', 'tarifa_orange_intenso',
                'tarifa_offnet_orange_livre', 'tarifa_offnet_orange_jovem_vip',
                'tarifa_offnet_orange_intenso',
                'tarifa_zona1', 'tarifa_zona2', 'tarifa_zona3',
                'tarifa_zona4', 'tarifa_zona5', 'tarifa_zona6'
            ];

            orangeTarifaFields.forEach(field => {
                const input = form.querySelector(`[name="${field}"]`);
                if (input && parseFloat(input.value) < 0) {
                    isValid = false;
                    showError(input, 'A tarifa deve ser maior ou igual a zero.');
                }
            });
        }

        // Validações específicas para TELECEL
        if (form.classList.contains('telecel-form')) {
            const dataPacks = [
                'pacote_30mb', 'pacote_100mb', 'pacote_300mb',
                'pacote_1gb', 'pacote_650mb', 'pacote_1000mb'
            ];
            
            dataPacks.forEach(packName => {
                const input = form.querySelector(`[name="${packName}"]`);
                if (input && input.value && parseInt(input.value) <= 0) {
                    isValid = false;
                    showError(input, 'O valor do pacote deve ser maior que zero.');
                }
            });

            // Pacotes Y'ello
            const yelloFields = [
                'pacote_yello_350mb', 'pacote_yello_1_5gb', 
                'pacote_yello_1_5gb_7dias'
            ];

            yelloFields.forEach(field => {
                const input = form.querySelector(`[name="${field}"]`);
                if (input && parseInt(input.value) < 0) {
                    isValid = false;
                    showError(input, 'O valor deve ser maior ou igual a zero.');
                }
            });
        }

        if (!isValid) {
            event.preventDefault();
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });

    // Funções auxiliares
    function showError(input, message) {
        input.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.innerText = message;
        input.parentNode.appendChild(errorDiv);
    }

    function removeError(input) {
        input.classList.remove('is-invalid');
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // Formatação de campos monetários
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = this.value.replace(/[^\d.]/g, '');
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            if (parts[1] && parts[1].length > 2) {
                value = parts[0] + '.' + parts[1].slice(0, 2);
            }
            this.value = value;
        });
    });

    // Cálculos automáticos
    const calculateTotals = function() {
        if (form.classList.contains('orange-form')) {
            // Totais Orange
            const prepaidInputs = document.querySelectorAll('[name*="dongle"], [name*="airbox"], [name*="flybox"]');
            const totalPrepaid = Array.from(prepaidInputs)
                .reduce((sum, input) => sum + (parseFloat(input.value) || 0), 0);
            updateTotal('total-prepaid', totalPrepaid);

            const residencialInputs = document.querySelectorAll('[name*="casa_"], [name*="casabox_"]');
            const totalResidencial = Array.from(residencialInputs)
                .reduce((sum, input) => sum + (parseFloat(input.value) || 0), 0);
            updateTotal('total-residencial', totalResidencial);

            const passInputs = document.querySelectorAll('[name*="pass_"]');
            const totalPasses = Array.from(passInputs)
                .reduce((sum, input) => sum + (parseFloat(input.value) || 0), 0);
            updateTotal('total-passes', totalPasses);

        } else if (form.classList.contains('telecel-form')) {
            // Totais MTN
            const pacotesInputs = document.querySelectorAll('[name*="pacote_"]');
            const totalPacotes = Array.from(pacotesInputs)
                .reduce((sum, input) => sum + (parseFloat(input.value) || 0), 0);
            updateTotal('total-pacotes', totalPacotes);
        }
    };

    function updateTotal(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value.toFixed(2);
        }
    }

    // Event Listeners
    const numericInputs = form.querySelectorAll('input[type="number"]');
    numericInputs.forEach(input => {
        input.addEventListener('input', calculateTotals);
    });

    // Calcular totais iniciais
    calculateTotals();

    // Limpar campos quando mudar entre Orange e TELECEL
    const operadoraSelect = document.querySelector('[name="operadora"]');
    if (operadoraSelect) {
        operadoraSelect.addEventListener('change', function() {
            form.reset();
            document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        });
    }

    // Inicialização de gráficos (se existirem)
    if (typeof Chart !== 'undefined') {
        if (document.getElementById('orangeChart')) {
            initOrangeChart();
        }
        if (document.getElementById('telecelChart')) {
            initMTNChart();
        }
    }

    // Função para inicializar gráfico Orange
    function initOrangeChart() {
        const ctx = document.getElementById('orangeChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Pré-pago', 'Residencial', 'Passes'],
                datasets: [{
                    data: [
                        document.getElementById('total-prepaid')?.textContent || 0,
                        document.getElementById('total-residencial')?.textContent || 0,
                        document.getElementById('total-passes')?.textContent || 0
                    ],
                    backgroundColor: [
                        'rgba(255, 140, 0, 0.8)',
                        'rgba(255, 165, 0, 0.8)',
                        'rgba(255, 120, 0, 0.8)'
                    ],
                    borderColor: [
                        'rgb(255, 140, 0)',
                        'rgb(255, 165, 0)',
                        'rgb(255, 120, 0)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Função para inicializar gráfico MTN
    function initMTNChart() {
        const ctx = document.getElementById('telecelChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Pacotes'],
                datasets: [{
                    data: [
                        document.getElementById('total-pacotes')?.textContent || 0
                    ],
                    backgroundColor: ['rgba(255, 255, 0, 0.8)'],
                    borderColor: ['rgb(255, 255, 0)'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
});