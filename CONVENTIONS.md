## Coding Conventions
### Testing with CSRF
- Always make an initial request (e.g., `client.get('/')`) before testing forms
- Verify CSRF token presence and value in session
- Keep form creation and validation in the same context

### Form Testing with CSRF
- Always use a request context when testing forms with CSRF tokens
- Use `client.session_transaction()` to initialize CSRF tokens
- Ensure form creation and submission occur within the same context
- Ensure test client maintains session state
- Use form-generated CSRF tokens in tests and ensure they are added to the session
- Include CSRF token in POST requests
- Initialize session with a request (e.g., `client.get('/')`) before form creation
- Add assertions to verify CSRF token presence in session
- Verify the CSRF token value matches between form and session

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

