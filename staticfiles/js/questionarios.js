// ==============================
// QUESTIONÁRIOS JAVASCRIPT
// ==============================

document.addEventListener('DOMContentLoaded', function() {
    initializeQuestionarios();
});

function initializeQuestionarios() {
    initializeFilters();
    initializeForms();
    initializeDataTables();
    initializeDeleteConfirmations();
}

// FILTROS
function initializeFilters() {
    const filterInputs = document.querySelectorAll('.filter-input');
    const filterSelects = document.querySelectorAll('.filter-select');
    
    // Add event listeners for real-time filtering
    filterInputs.forEach(input => {
        input.addEventListener('input', debounce(filterTable, 300));
    });
    
    filterSelects.forEach(select => {
        select.addEventListener('change', filterTable);
    });
}

function filterTable() {
    const table = document.querySelector('.questionario-table tbody');
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const filters = getActiveFilters();
    
    rows.forEach(row => {
        const shouldShow = matchesFilters(row, filters);
        row.style.display = shouldShow ? '' : 'none';
    });
    
    updateResultsCount();
}

function getActiveFilters() {
    const filters = {};
    
    // Text filters
    document.querySelectorAll('.filter-input').forEach(input => {
        if (input.value.trim()) {
            filters[input.dataset.column] = input.value.toLowerCase();
        }
    });
    
    // Select filters
    document.querySelectorAll('.filter-select').forEach(select => {
        if (select.value) {
            filters[select.dataset.column] = select.value;
        }
    });
    
    return filters;
}

function matchesFilters(row, filters) {
    for (const [column, value] of Object.entries(filters)) {
        const cell = row.querySelector(`[data-column="${column}"]`);
        if (!cell) continue;
        
        const cellText = cell.textContent.toLowerCase();
        if (!cellText.includes(value.toLowerCase())) {
            return false;
        }
    }
    return true;
}

function updateResultsCount() {
    const table = document.querySelector('.questionario-table tbody');
    if (!table) return;
    
    const visibleRows = table.querySelectorAll('tr:not([style*="display: none"])').length;
    const totalRows = table.querySelectorAll('tr').length;
    
    const countElement = document.querySelector('.results-count');
    if (countElement) {
        countElement.textContent = `${visibleRows} de ${totalRows} resultados`;
    }
}

// FORMULÁRIOS
function initializeForms() {
    const forms = document.querySelectorAll('.questionario-form');
    
    forms.forEach(form => {
        // Add form validation
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                showFormErrors(form);
            }
        });
        
        // Add real-time validation
        const inputs = form.querySelectorAll('.form-control-questionario');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(input);
            });
        });
    });
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            markFieldAsInvalid(field, 'Este campo é obrigatório');
            isValid = false;
        } else {
            markFieldAsValid(field);
        }
    });
    
    return isValid;
}

function validateField(field) {
    if (field.hasAttribute('required') && !field.value.trim()) {
        markFieldAsInvalid(field, 'Este campo é obrigatório');
        return false;
    }
    
    markFieldAsValid(field);
    return true;
}

function markFieldAsInvalid(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    // Add error message
    let errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        field.parentNode.appendChild(errorElement);
    }
    errorElement.textContent = message;
}

function markFieldAsValid(field) {
    field.classList.add('is-valid');
    field.classList.remove('is-invalid');
    
    // Remove error message
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

function showFormErrors(form) {
    const firstError = form.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

// TABELAS DE DADOS
function initializeDataTables() {
    const tables = document.querySelectorAll('.questionario-table');
    
    tables.forEach(table => {
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, header);
            });
        });
        
        // Add row selection functionality
        const checkboxes = table.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateBulkActions);
        });
    });
}

function sortTable(table, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const currentSort = header.dataset.sort || 'none';
    
    // Determine new sort direction
    let newSort;
    if (currentSort === 'none' || currentSort === 'desc') {
        newSort = 'asc';
    } else {
        newSort = 'desc';
    }
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));
        
        let comparison;
        if (!isNaN(aNum) && !isNaN(bNum)) {
            comparison = aNum - bNum;
        } else {
            comparison = aValue.localeCompare(bValue);
        }
        
        return newSort === 'asc' ? comparison : -comparison;
    });
    
    // Update table
    rows.forEach(row => tbody.appendChild(row));
    
    // Update header indicators
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        th.dataset.sort = 'none';
    });
    
    header.classList.add(`sort-${newSort}`);
    header.dataset.sort = newSort;
}

function updateBulkActions() {
    const selectedCheckboxes = document.querySelectorAll('.row-checkbox:checked');
    const bulkActions = document.querySelector('.bulk-actions');
    
    if (bulkActions) {
        bulkActions.style.display = selectedCheckboxes.length > 0 ? 'block' : 'none';
    }
}

// CONFIRMAÇÕES DE EXCLUSÃO
function initializeDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.btn-questionario-danger[data-action="delete"]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemName = button.dataset.itemName || 'este item';
            const deleteUrl = button.getAttribute('href');
            
            showDeleteConfirmation(itemName, deleteUrl);
        });
    });
}

function showDeleteConfirmation(itemName, deleteUrl) {
    const confirmed = confirm(`Tem certeza que deseja excluir ${itemName}? Esta ação não pode ser desfeita.`);
    
    if (confirmed) {
        // Create a form for DELETE request
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = deleteUrl;
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken.value;
            form.appendChild(csrfInput);
        }
        
        document.body.appendChild(form);
        form.submit();
    }
}

// UTILITY FUNCTIONS
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showNotification(message, type = 'info') {
    // Use the platform notification system
    if (window.showToast) {
        window.showToast(message, type);
    } else {
        alert(message); // Fallback
    }
}

// Export functions for use in templates
window.QuestionariosJS = {
    showNotification,
    validateForm,
    sortTable,
    filterTable
};
