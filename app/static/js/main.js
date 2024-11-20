// Main JavaScript file for HTMX and other interactions

document.addEventListener('DOMContentLoaded', function() {
    // Example of adding an event listener to a button with HTMX
    document.querySelectorAll('[hx-post]').forEach(function(button) {
        button.addEventListener('htmx:afterRequest', function(event) {
            console.log('Request completed:', event);
        });
    });
});
