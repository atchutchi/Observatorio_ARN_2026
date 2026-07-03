document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(event) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[type="number"]');
        
        inputs.forEach(function(input) {
            if (input.value === '') {
                isValid = false;
                input.classList.add('is-invalid');
                let feedbackDiv = input.nextElementSibling;
                if (!feedbackDiv || !feedbackDiv.classList.contains('invalid-feedback')) {
                    feedbackDiv = document.createElement('div');
                    feedbackDiv.classList.add('invalid-feedback');
                    input.parentNode.insertBefore(feedbackDiv, input.nextSibling);
                }
                feedbackDiv.textContent = 'Este campo é obrigatório.';
            } else if (parseInt(input.value) < 0) {
                isValid = false;
                input.classList.add('is-invalid');
                let feedbackDiv = input.nextElementSibling;
                if (!feedbackDiv || !feedbackDiv.classList.contains('invalid-feedback')) {
                    feedbackDiv = document.createElement('div');
                    feedbackDiv.classList.add('invalid-feedback');
                    input.parentNode.insertBefore(feedbackDiv, input.nextSibling);
                }
                feedbackDiv.textContent = 'O valor deve ser maior ou igual a zero.';
            } else {
                input.classList.remove('is-invalid');
                const feedbackDiv = input.nextElementSibling;
                if (feedbackDiv && feedbackDiv.classList.contains('invalid-feedback')) {
                    feedbackDiv.remove();
                }
            }
        });

        if (!isValid) {
            event.preventDefault();
            event.stopPropagation();
        }
    });

    // Limpar mensagens de erro quando o usuário começa a digitar
    form.querySelectorAll('input').forEach(function(input) {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            const feedbackDiv = this.nextElementSibling;
            if (feedbackDiv && feedbackDiv.classList.contains('invalid-feedback')) {
                feedbackDiv.remove();
            }
        });
    });
});