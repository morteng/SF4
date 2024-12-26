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

    // Date validation for application deadline
    document.addEventListener('input', function(e) {
        if (e.target.name === 'application_deadline') {
            const input = e.target;
            const value = input.value.trim();
            const errorDiv = document.getElementById('date-error');
            
            if (!value) {
                errorDiv.textContent = 'Date is required';
                input.classList.add('is-invalid');
                return;
            }

            // Validate format
            const regex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/;
            if (!regex.test(value)) {
                errorDiv.textContent = 'Invalid format. Use YYYY-MM-DD HH:MM:SS';
                input.classList.add('is-invalid');
                return;
            }

            // Validate date components
            const [datePart, timePart] = value.split(' ');
            const [year, month, day] = datePart.split('-').map(Number);
            const [hour, minute, second] = timePart.split(':').map(Number);

            if (month < 1 || month > 12 || day < 1 || day > 31 ||
                hour > 23 || minute > 59 || second > 59) {
                errorDiv.textContent = 'Invalid date or time values';
                input.classList.add('is-invalid');
                return;
            }

            // If all validations pass
            errorDiv.textContent = '';
            input.classList.remove('is-invalid');
        }
    });

    // Reinitialize any scripts after HTMX swap
    document.body.addEventListener('htmx:afterSwap', (event) => {
        if (event.detail.target.id === 'stipends tbody') {
            console.log("Pagination content swapped!");
            // Reinitialize any scripts if needed
        }
    });
});
