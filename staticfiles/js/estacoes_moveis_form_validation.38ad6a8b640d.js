document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form.needs-validation');
    
    form.addEventListener('submit', function(event) {
        if (!form.checkValidity() || !validateCustomLogic()) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.classList.add('was-validated');
    });

    // Validação básica de números negativos
    const numberInputs = form.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
                showError(this, 'O valor não pode ser negativo.');
            } else {
                clearError(this);
            }
        });
    });

    // Validação de campos decimais
    const decimalInputs = form.querySelectorAll('input[type="text"][step="0.01"]');
    decimalInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9.]/g, '');
            if (this.value.split('.').length > 2) {
                this.value = this.value.replace(/\.+$/, '');
            }
        });
    });

    // Validações específicas para 3G e 4G
    const campos3G = [
        'id_utilizadores_servico_3g_upgrades',
        'id_utilizadores_acesso_internet_3g',
        'id_utilizadores_3g_placas_box',
        'id_utilizadores_3g_placas_usb'
    ];

    const campos4G = [
        'id_utilizadores_servico_4g',
        'id_utilizadores_acesso_internet_4g',
        'id_utilizadores_4g_placas_box',
        'id_utilizadores_4g_placas_usb'
    ];

    // Adicionar validações em tempo real
    [...campos3G, ...campos4G].forEach(function(fieldId) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('blur', function() {
                validateBandaLargaFields();
            });
        }
    });

    // Função para validar lógica customizada
    function validateCustomLogic() {
        let isValid = true;

        // Validar 3G - placas não podem ser maiores que acesso à internet
        const acesso3G = parseInt(document.getElementById('id_utilizadores_acesso_internet_3g')?.value || 0);
        const placasBox3G = parseInt(document.getElementById('id_utilizadores_3g_placas_box')?.value || 0);
        const placasUSB3G = parseInt(document.getElementById('id_utilizadores_3g_placas_usb')?.value || 0);

        if (placasBox3G > acesso3G) {
            showError(document.getElementById('id_utilizadores_3g_placas_box'), 
                'Placas Box (3G) não pode ser maior que utilizadores de acesso à Internet (3G)');
            isValid = false;
        }

        if (placasUSB3G > acesso3G) {
            showError(document.getElementById('id_utilizadores_3g_placas_usb'), 
                'Placas USB (3G) não pode ser maior que utilizadores de acesso à Internet (3G)');
            isValid = false;
        }

        if ((placasBox3G + placasUSB3G) > acesso3G) {
            showError(document.getElementById('id_utilizadores_3g_placas_usb'), 
                'Total de placas (3G) não pode ser maior que utilizadores de acesso à Internet (3G)');
            isValid = false;
        }

        // Validar 4G - placas não podem ser maiores que acesso à internet
        const acesso4G = parseInt(document.getElementById('id_utilizadores_acesso_internet_4g')?.value || 0);
        const placasBox4G = parseInt(document.getElementById('id_utilizadores_4g_placas_box')?.value || 0);
        const placasUSB4G = parseInt(document.getElementById('id_utilizadores_4g_placas_usb')?.value || 0);

        if (placasBox4G > acesso4G) {
            showError(document.getElementById('id_utilizadores_4g_placas_box'), 
                'Placas Box (4G) não pode ser maior que utilizadores de acesso à Internet (4G)');
            isValid = false;
        }

        if (placasUSB4G > acesso4G) {
            showError(document.getElementById('id_utilizadores_4g_placas_usb'), 
                'Placas USB (4G) não pode ser maior que utilizadores de acesso à Internet (4G)');
            isValid = false;
        }

        if ((placasBox4G + placasUSB4G) > acesso4G) {
            showError(document.getElementById('id_utilizadores_4g_placas_usb'), 
                'Total de placas (4G) não pode ser maior que utilizadores de acesso à Internet (4G)');
            isValid = false;
        }

        // Validar Mobile Money - somas devem fazer sentido
        const totalUtilizadores = parseInt(document.getElementById('id_numero_utilizadores')?.value || 0);
        const utilizadoresMulher = parseInt(document.getElementById('id_numero_utilizadores_mulher')?.value || 0);
        const utilizadoresHomem = parseInt(document.getElementById('id_numero_utilizadores_homem')?.value || 0);

        if ((utilizadoresMulher + utilizadoresHomem) > totalUtilizadores) {
            showError(document.getElementById('id_numero_utilizadores_homem'), 
                'Soma de utilizadores por gênero não pode ser maior que o total');
            isValid = false;
        }

        return isValid;
    }

    // Validar campos de banda larga em tempo real
    function validateBandaLargaFields() {
        // Limpar erros anteriores
        campos3G.concat(campos4G).forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) clearError(field);
        });

        // Revalidar
        validateCustomLogic();
    }

    // Função para mostrar erro
    function showError(field, message) {
        if (!field) return;
        
        field.classList.add('is-invalid');
        let feedbackElement = field.parentNode.querySelector('.invalid-feedback');
        if (!feedbackElement) {
            feedbackElement = document.createElement('div');
            feedbackElement.classList.add('invalid-feedback');
            field.parentNode.appendChild(feedbackElement);
        }
        feedbackElement.textContent = message;
    }

    // Função para limpar erro
    function clearError(field) {
        if (!field) return;
        
        field.classList.remove('is-invalid');
        const feedbackElement = field.parentNode.querySelector('.invalid-feedback');
        if (feedbackElement) {
            feedbackElement.textContent = '';
        }
    }

    // Função para formatar números grandes
    function formatLargeNumber(number) {
        return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    // Aplicar formatação aos campos numéricos grandes
    const largeNumberInputs = form.querySelectorAll('.large-number');
    largeNumberInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value) {
                const formattedValue = formatLargeNumber(this.value);
                this.value = formattedValue;
            }
        });

        input.addEventListener('focus', function() {
            this.value = this.value.replace(/\./g, '');
        });
    });

    // Adicionar tooltips informativos
    const tooltips = {
        'id_utilizadores_3g_placas_box': 'Número de utilizadores que acedem à Internet 3G através de placas Box',
        'id_utilizadores_3g_placas_usb': 'Número de utilizadores que acedem à Internet 3G através de placas USB',
        'id_utilizadores_4g_placas_box': 'Número de utilizadores que acedem à Internet 4G através de placas Box',
        'id_utilizadores_4g_placas_usb': 'Número de utilizadores que acedem à Internet 4G através de placas USB'
    };

    Object.keys(tooltips).forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.setAttribute('title', tooltips[fieldId]);
            field.setAttribute('data-bs-toggle', 'tooltip');
        }
    });

    // Inicializar tooltips Bootstrap se disponível
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});