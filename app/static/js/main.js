// Main JavaScript file for HTMX and other interactions

document.addEventListener('DOMContentLoaded', function() {
    // HTMX indicator
    document.body.addEventListener('htmx:configRequest', () => {
        document.getElementById('htmx-indicator').style.display = 'block';
    });
    document.body.addEventListener('htmx:afterRequest', () => {
        document.getElementById('htmx-indicator').style.display = 'none';
    });

   
    // Theme toggle functionality
    const toggleButton = document.getElementById('theme-toggle');
    let currentTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.add(currentTheme);

    toggleButton.addEventListener('click', function () {
        if (document.body.classList.contains('dark')) {
            document.body.classList.remove('dark');
            localStorage.setItem('theme', '');
        } else {
            document.body.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    });
});
