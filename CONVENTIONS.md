## Coding Conventions
### Testing
- Use enums for message types
- Verify UI & DB state
- Use fixtures & parameterized tests
- Include CSRF token validation in form tests
- CSRF enabled in testing environment

### Security
- Validate all inputs
- CSRF tokens required in all forms
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling

### Code Organization
- CSS: Tailwind in main.css
- JS: HTMX in main.js
- Constants: Use enums
- Forms: Use FlaskForm with CSRF protection

