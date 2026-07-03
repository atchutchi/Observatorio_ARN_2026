/**
 * JavaScript para configurar a tabela de tráfego originado com DataTables
 */
$(document).ready(function() {
    $('.table').DataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/Portuguese.json"
        },
        "order": [[0, "desc"], [1, "desc"]]
    });
}); 