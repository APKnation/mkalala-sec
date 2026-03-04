// Initialize tooltips
$(document).ready(function(){
    // Enable tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Enable popovers
    $('[data-bs-toggle="popover"]').popover();
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // CSRF setup for AJAX
    const csrftoken = document.querySelector('[name=csrf-token]').content;
    $.ajaxSetup({
        headers: { 'X-CSRFToken': csrftoken }
    });
    
    // Any other global JS functionality
});

// Global function for confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}