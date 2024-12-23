// Main JavaScript file for HTMX and other interactions

document.addEventListener('DOMContentLoaded', function() {
    // HTMX indicator
    document.body.addEventListener('htmx:beforeRequest', () => {
        document.getElementById('htmx-indicator').style.display = 'block';
    });
    document.body.addEventListener('htmx:afterRequest', () => {
        document.getElementById('htmx-indicator').style.display = 'none';
    });

   
    let currentTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.add(currentTheme);

    const themeToggleCheckbox = document.getElementById('theme-toggle');
    if (themeToggleCheckbox) {
        // If the theme is dark, keep the checkbox checked
        themeToggleCheckbox.checked = (currentTheme === 'dark');

        themeToggleCheckbox.addEventListener('change', function () {
            if (themeToggleCheckbox.checked) {
                document.body.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark');
                localStorage.setItem('theme', '');
            }
        });
    }

    // Reinitialize any scripts after HTMX swap
    document.body.addEventListener('htmx:afterSwap', (event) => {
        if (event.detail.target.id === 'stipends tbody') {
            console.log("Pagination content swapped!");
            // Reinitialize any scripts if needed
        }
    });
});
