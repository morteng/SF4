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

    if (toggleButton) {
        toggleButton.addEventListener('click', function () {
            if (document.body.classList.contains('dark')) {
                document.body.classList.remove('dark');
                localStorage.setItem('theme', '');
            } else {
                document.body.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
        });
    }

    // Mobile theme toggle functionality
    const toggleButtonMobile = document.getElementById('theme-toggle-mobile');
    if (toggleButtonMobile) {
        toggleButtonMobile.addEventListener('click', function () {
            if (document.body.classList.contains('dark')) {
                document.body.classList.remove('dark');
                localStorage.setItem('theme', '');
            } else {
                document.body.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
        });
    }

    // Mobile menu toggle functionality
    const navToggle = document.getElementById('nav-toggle');
    const mobileMenu = document.getElementById('mobile-menu');

    if (navToggle) {
        navToggle.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
        });
    }
});
