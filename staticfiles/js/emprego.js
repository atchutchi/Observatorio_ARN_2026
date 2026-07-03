document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    // Validação do formulário
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Validação de campos numéricos
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
                calcularTotais();
            });
        });

        // Função para calcular totais
        function calcularTotais() {
            // Cálculo do total geral
            const empregoDirecto = parseInt(form.querySelector('[name="emprego_direto_total"]').value) || 0;
            const empregoIndireto = parseInt(form.querySelector('[name="emprego_indireto"]').value) || 0;
            const totalGeral = empregoDirecto + empregoIndireto;
            document.getElementById('total-geral').textContent = totalGeral;

            // Cálculo dos percentuais por gênero
            const nacionaisTotal = parseInt(form.querySelector('[name="nacionais_total"]').value) || 0;
            const homens = parseInt(form.querySelector('[name="nacionais_homem"]').value) || 0;
            const mulheres = parseInt(form.querySelector('[name="nacionais_mulher"]').value) || 0;

            if (nacionaisTotal > 0) {
                const percentualHomens = (homens / nacionaisTotal * 100).toFixed(1);
                const percentualMulheres = (mulheres / nacionaisTotal * 100).toFixed(1);
                document.getElementById('percentual-homens').textContent = percentualHomens;
                document.getElementById('percentual-mulheres').textContent = percentualMulheres;

                // Validação do total de nacionais
                if (homens + mulheres !== nacionaisTotal) {
                    form.querySelector('[name="nacionais_total"]').classList.add('is-invalid');
                    form.querySelector('[name="nacionais_homem"]').classList.add('is-invalid');
                    form.querySelector('[name="nacionais_mulher"]').classList.add('is-invalid');
                } else {
                    form.querySelector('[name="nacionais_total"]').classList.remove('is-invalid');
                    form.querySelector('[name="nacionais_homem"]').classList.remove('is-invalid');
                    form.querySelector('[name="nacionais_mulher"]').classList.remove('is-invalid');
                }
            }
        }

        // Calcular totais iniciais
        calcularTotais();
    }

    // Inicialização do DataTable
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
});