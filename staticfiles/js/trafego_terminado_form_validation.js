document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(event) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('input[required], select[required]');
        
        requiredFields.forEach(function(field) {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        const numberFields = form.querySelectorAll('input[type="number"]');
        numberFields.forEach(function(field) {
            if (field.value && parseInt(field.value) < 0) {
                isValid = false;
                field.classList.add('is-invalid');
                alert('Os valores numéricos não podem ser negativos.');
            }
        });

        if (!isValid) {
            event.preventDefault();
            alert('Por favor, preencha todos os campos obrigatórios corretamente.');
        }
    });
});