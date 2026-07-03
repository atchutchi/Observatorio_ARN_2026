document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    let outrosInvestimentosCount = 0;

    // Função para validar número
    function isValidNumber(value) {
        return !isNaN(value) && parseFloat(value) >= 0;
    }

    // Função para adicionar feedback de erro
    function addErrorFeedback(input, message) {
        input.classList.add('is-invalid');
        let feedback = input.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.classList.add('invalid-feedback');
            input.parentNode.insertBefore(feedback, input.nextSibling);
        }
        feedback.textContent = message;
    }

    // Função para remover feedback de erro
    function removeErrorFeedback(input) {
        input.classList.remove('is-invalid');
        const feedback = input.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.remove();
        }
    }

    // Função para validar um campo numérico
    function validateNumericField(input) {
        const value = input.value.trim();
        
        if (value === '') {
            addErrorFeedback(input, 'Este campo é obrigatório.');
            return false;
        }
        
        if (!isValidNumber(value)) {
            addErrorFeedback(input, 'Por favor, insira um número válido maior ou igual a zero.');
            return false;
        }
        
        removeErrorFeedback(input);
        return true;
    }

    // Validação no envio do formulário
    form.addEventListener('submit', function(event) {
        let isValid = true;
        const numericInputs = form.querySelectorAll('input[type="number"]');
        
        numericInputs.forEach(function(input) {
            if (!validateNumericField(input)) {
                isValid = false;
            }
        });

        if (!isValid) {
            event.preventDefault();
            event.stopPropagation();
            // Scroll para o primeiro campo com erro
            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });

    // Validação em tempo real
    form.querySelectorAll('input[type="number"]').forEach(function(input) {
        input.addEventListener('input', function() {
            validateNumericField(this);
            calcularTotais();
        });
    });

    // Adicionar novo campo de investimento
    const btnAddCampo = document.querySelector('#btn-add-investimento');
    if (btnAddCampo) {
        btnAddCampo.addEventListener('click', function() {
            const novoNome = document.querySelector('#novo_campo_nome');
            const novoValor = document.querySelector('#novo_campo_valor');
            
            if (novoNome.value && novoValor.value && isValidNumber(novoValor.value)) {
                adicionarCampoDinamico(novoNome.value, novoValor.value);
                novoNome.value = '';
                novoValor.value = '';
                calcularTotais();
            }
        });
    }

    // Função para calcular totais
    function calcularTotais() {
        let totalCorporeo = 0;
        let totalIncorporeo = 0;
        let totalOutros = 0;

        // Calcular total corpóreo
        const corpóreoInputs = document.querySelectorAll('.corporeo input[type="number"]');
        corpóreoInputs.forEach(input => {
            if (isValidNumber(input.value)) {
                totalCorporeo += parseFloat(input.value);
            }
        });

        // Calcular total incorpóreo
        const incorporeoInputs = document.querySelectorAll('.incorporeo input[type="number"]');
        incorporeoInputs.forEach(input => {
            if (isValidNumber(input.value)) {
                totalIncorporeo += parseFloat(input.value);
            }
        });

        // Calcular total outros
        const outrosInputs = document.querySelectorAll('.outros input[type="number"]');
        outrosInputs.forEach(input => {
            if (isValidNumber(input.value)) {
                totalOutros += parseFloat(input.value);
            }
        });

        // Atualizar os campos de total
        document.querySelector('#total-corporeo').textContent = totalCorporeo.toFixed(2);
        document.querySelector('#total-incorporeo').textContent = totalIncorporeo.toFixed(2);
        document.querySelector('#total-outros').textContent = totalOutros.toFixed(2);
        document.querySelector('#total-geral').textContent = (totalCorporeo + totalIncorporeo + totalOutros).toFixed(2);
    }

    // Inicializar cálculo de totais
    calcularTotais();
});