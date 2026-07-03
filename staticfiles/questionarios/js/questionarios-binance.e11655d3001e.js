// ==============================
// QUESTIONÁRIOS BINANCE JAVASCRIPT
// ==============================

document.addEventListener('DOMContentLoaded', function() {
    initializeQuestionarios();
});

function initializeQuestionarios() {
    initializeFilters();
    initializeForms();
    initializeDataTables();
    initializeDeleteConfirmations();
    initializeBulkActions();
    initializeEmptyStateLinks();
}

// FILTROS DOS QUESTIONÁRIOS
function initializeFilters() {
    const filterInputs = document.querySelectorAll('.filter-input');
    const filterSelects = document.querySelectorAll('.filter-select');
    
    // Add event listeners for real-time filtering
    filterInputs.forEach(input => {
        input.addEventListener('input', debounceFilter);
    });
    
    filterSelects.forEach(select => {
        select.addEventListener('change', filterQuestionarioTable);
    });
}

const debounceFilter = debounce(filterQuestionarioTable, 300);

function filterQuestionarioTable() {
    const table = document.querySelector('.questionario-table tbody');
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const filters = getActiveFilters();
    
    let visibleCount = 0;
    
    rows.forEach(row => {
        const shouldShow = matchesFilters(row, filters);
        row.style.display = shouldShow ? '' : 'none';
        if (shouldShow) visibleCount++;
    });
    
    updateResultsCount(visibleCount, rows.length);
}

function getActiveFilters() {
    const filters = {};
    
    // Text filters
    document.querySelectorAll('.filter-input').forEach(input => {
        if (input.value.trim()) {
            filters[input.dataset.column || 'all'] = input.value.toLowerCase();
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
        if (column === 'all') {
            // Search in all cells
            const allText = Array.from(row.cells).map(cell => 
                cell.textContent.toLowerCase()
            ).join(' ');
            
            if (!allText.includes(value.toLowerCase())) {
                return false;
            }
        } else {
            const cell = row.querySelector(`[data-column="${column}"]`) || 
                        row.cells[getColumnIndex(column)];
            
            if (cell) {
                const cellText = cell.textContent.toLowerCase();
                if (!cellText.includes(value.toLowerCase())) {
                    return false;
                }
            }
        }
    }
    return true;
}

function getColumnIndex(columnName) {
    const headerRow = document.querySelector('.questionario-table thead tr');
    if (!headerRow) return -1;
    
    const headers = Array.from(headerRow.cells);
    return headers.findIndex(header => 
        header.textContent.toLowerCase().includes(columnName.toLowerCase())
    );
}

function updateResultsCount(visible, total) {
    const countElement = document.querySelector('.results-count');
    if (countElement) {
        countElement.textContent = `${visible} de ${total} resultado(s)`;
    }
}

// FORMULÁRIOS
function initializeForms() {
    const forms = document.querySelectorAll('.questionario-form');
    
    forms.forEach(form => {
        // Add form validation
        form.addEventListener('submit', function(e) {
            if (!validateQuestionarioForm(form)) {
                e.preventDefault();
                showFormErrors(form);
            }
        });
        
        // Add real-time validation
        const inputs = form.querySelectorAll('.form-control-questionario');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateQuestionarioField(input);
            });
            
            input.addEventListener('input', function() {
                clearFieldErrors(input);
            });
        });
    });
}

function validateQuestionarioForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateQuestionarioField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateQuestionarioField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    
    // Required validation
    if (field.hasAttribute('required') && !value) {
        markFieldAsInvalid(field, 'Este campo é obrigatório');
        return false;
    }
    
    // Number validation
    if (fieldType === 'number' && value) {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        const numValue = parseFloat(value);
        
        if (isNaN(numValue)) {
            markFieldAsInvalid(field, 'Deve ser um número válido');
            return false;
        }
        
        if (min !== null && numValue < parseFloat(min)) {
            markFieldAsInvalid(field, `Valor mínimo: ${min}`);
            return false;
        }
        
        if (max !== null && numValue > parseFloat(max)) {
            markFieldAsInvalid(field, `Valor máximo: ${max}`);
            return false;
        }
    }
    
    // Email validation
    if (fieldType === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            markFieldAsInvalid(field, 'Email inválido');
            return false;
        }
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

function clearFieldErrors(field) {
    if (field.value.trim()) {
        field.classList.remove('is-invalid');
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }
}

function showFormErrors(form) {
    const firstError = form.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
        
        showNotification('Por favor, corrija os erros no formulário', 'error');
    }
}

// TABELAS DE DADOS
function initializeDataTables() {
    const tables = document.querySelectorAll('.questionario-table');
    
    tables.forEach(table => {
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.addEventListener('click', function() {
                sortQuestionarioTable(table, header);
            });
        });
        
        // Add row selection functionality
        const checkboxes = table.querySelectorAll('input[type="checkbox"].row-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateBulkActions);
        });
    });
}

function sortQuestionarioTable(table, header) {
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
            comparison = aValue.localeCompare(bValue, 'pt-BR');
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
    
    showNotification(`Tabela ordenada por ${header.textContent.trim()}`, 'info');
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
    const confirmed = confirm(
        `⚠️ CONFIRMAÇÃO DE EXCLUSÃO\n\n` +
        `Tem certeza que deseja excluir ${itemName}?\n\n` +
        `Esta ação não pode ser desfeita e todos os dados relacionados serão perdidos.`
    );
    
    if (confirmed) {
        // Create a form for POST request
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

// AÇÕES EM MASSA
function initializeBulkActions() {
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.row-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActions();
        });
    }
}

function updateBulkActions() {
    const selectedCheckboxes = document.querySelectorAll('.row-checkbox:checked');
    const bulkActions = document.querySelector('.bulk-actions');
    
    if (bulkActions) {
        bulkActions.style.display = selectedCheckboxes.length > 0 ? 'block' : 'none';
    }
    
    // Update select all checkbox
    const selectAllCheckbox = document.getElementById('selectAll');
    const allCheckboxes = document.querySelectorAll('.row-checkbox');
    
    if (selectAllCheckbox && allCheckboxes.length > 0) {
        selectAllCheckbox.checked = selectedCheckboxes.length === allCheckboxes.length;
        selectAllCheckbox.indeterminate = selectedCheckboxes.length > 0 && 
                                          selectedCheckboxes.length < allCheckboxes.length;
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
        // Create simple toast if platform system not available
        const toast = document.createElement('div');
        toast.className = `alert-questionario alert-questionario-${type}`;
        toast.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 4000);
    }
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
}

// AUTO-SAVE FUNCTIONALITY
function initializeAutoSave() {
    const forms = document.querySelectorAll('.questionario-form[data-autosave]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                saveFormData(form);
            });
        });
    });
}

function saveFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    // Save to localStorage
    const formId = form.id || 'questionario-form';
    localStorage.setItem(`questionario-draft-${formId}`, JSON.stringify(data));
    
    // Show save indicator
    showSaveIndicator();
}

function loadFormData(form) {
    const formId = form.id || 'questionario-form';
    const savedData = localStorage.getItem(`questionario-draft-${formId}`);
    
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            });
            
            showNotification('Dados do rascunho carregados', 'info');
        } catch (error) {
            console.error('Erro ao carregar dados salvos:', error);
        }
    }
}

function clearSavedFormData(form) {
    const formId = form.id || 'questionario-form';
    localStorage.removeItem(`questionario-draft-${formId}`);
}

function showSaveIndicator() {
    const indicator = document.getElementById('save-indicator') || createSaveIndicator();
    indicator.style.display = 'block';
    
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 2000);
}

function createSaveIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'save-indicator';
    indicator.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        Rascunho salvo
    `;
    indicator.style.cssText = `
        position: fixed; top: 1rem; right: 1rem; z-index: 1050;
        background: var(--binance-success); color: white;
        padding: 0.5rem 1rem; border-radius: 6px;
        font-size: 0.875rem; display: none;
    `;
    document.body.appendChild(indicator);
    return indicator;
}

// EMPTY STATE LINKS
function initializeEmptyStateLinks() {
    // Configurar botão do empty state para usar a mesma URL do header
    const emptyStateBtn = document.getElementById('emptyStateCreateBtn');
    const headerCreateBtn = document.querySelector('.questionario-actions .btn-binance');
    
    if (emptyStateBtn && headerCreateBtn) {
        emptyStateBtn.href = headerCreateBtn.href;
        
        // Adicionar event listener para feedback visual
        emptyStateBtn.addEventListener('click', function(e) {
            if (this.href === '#' || !this.href) {
                e.preventDefault();
                showNotification('URL de criação não configurada', 'warning');
            }
        });
    }
}

// Export functions for use in templates
window.QuestionariosJS = {
    showNotification,
    validateQuestionarioForm,
    sortQuestionarioTable,
    filterQuestionarioTable,
    saveFormData,
    loadFormData,
    clearSavedFormData,
    initializeEmptyStateLinks
};
