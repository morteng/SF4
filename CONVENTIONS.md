## Coding Conventions
### Testing with CSRF
- Always make an initial request (e.g., `client.get('/')`) before testing forms
- Verify CSRF token presence and value in session
- Keep form creation and validation in the same context
- Ensure test client maintains session state between requests

### Form Testing with CSRF
- Always make an initial request (e.g., `client.get('/')`) before form creation
- Verify CSRF token presence and value in session
- Keep form creation and submission in the same context
- Use `client.session_transaction()` to verify session state
- Compare form-generated CSRF token with session token

### Form Testing
- Always use an application context when testing forms
- Include CSRF token validation in form tests
- Use form-generated CSRF tokens in tests
- Ensure test client maintains session state for CSRF validation
- Add error handling to debug form validation failures

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

