## Coding Conventions
### Testing
- Use type hints and docstrings
- Use fixtures for common setup
- Parameterize tests for multiple scenarios
- Verify both UI responses and database state
- Use `FlashMessages` and `FlashCategory` enums for assertions

### Security
- Validate all form inputs
- Use CSRF tokens for all forms
- Implement rate limiting for sensitive endpoints
- Use bleach for input sanitization

### Code Organization
- Keep CSS in app/static/css/main.css
- Keep JS in app/static/js/main.js
- Use Tailwind for styling
- Use HTMX for dynamic interactions
- Use FlashMessages and FlashCategory enums consistently

