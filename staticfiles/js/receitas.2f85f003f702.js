document.addEventListener('DOMContentLoaded', function() {
    // Validação do formulário
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Validação de valores negativos
        const numberInputs = form.querySelectorAll('input[type="number"]');
        numberInputs.forEach(function(input) {
            input.addEventListener('input', function() {
                if (this.value < 0) {
                    this.value = 0;
                    this.classList.add('is-invalid');
                    let feedbackElement = this.nextElementSibling;
                    if (!feedbackElement || !feedbackElement.classList.contains('invalid-feedback')) {
                        feedbackElement = document.createElement('div');
                        feedbackElement.classList.add('invalid-feedback');
                        this.parentNode.insertBefore(feedbackElement, this.nextSibling);
                    }
                    feedbackElement.textContent = 'O valor não pode ser negativo.';
                } else {
                    this.classList.remove('is-invalid');
                    let feedbackElement = this.nextElementSibling;
                    if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                        feedbackElement.textContent = '';
                    }
                }
            });
        });

        // Formatação de valores monetários
        const moneyInputs = form.querySelectorAll('input[type="number"][step="0.01"]');
        moneyInputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                if (this.value) {
                    this.value = parseFloat(this.value).toFixed(2);
                }
            });
        });
    }

    // Inicialização do DataTable na lista
    const table = document.querySelector('.table');
    if (table && typeof $.fn.DataTable !== 'undefined') {
        $(table).DataTable({
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/Portuguese.json"
            },
            "order": [[1, "desc"], [2, "desc"]],
            "pageLength": 25
        });
    }

    // Função para calcular totais em tempo real
    function calcularTotais() {
        if (!form) return;

        const retalhistas = Array.from(form.querySelectorAll('[name*="retalhistas"]'))
            .reduce((sum, input) => sum + (parseFloat(input.value) || 0), 0);
        const grossistas = Array.from(form.querySelectorAll('[name*="grossistas"]'))
            .reduce((sum, input) => sum + (parseFloat(input.value) || 0), 0);

        document.getElementById('total-retalhistas').textContent = retalhistas.toFixed(2);
        document.getElementById('total-grossistas').textContent = grossistas.toFixed(2);
        document.getElementById('total-geral').textContent = (retalhistas + grossistas).toFixed(2);
    }

    // Adicionar listeners para cálculo em tempo real
    const inputsCalculo = document.querySelectorAll('input[type="number"]');
    inputsCalculo.forEach(input => {
        input.addEventListener('input', calcularTotais);
    });

    // Calcular totais iniciais
    calcularTotais();
});