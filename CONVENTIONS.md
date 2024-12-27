## Coding Conventions
### Testing
- Always use a request context (`app.test_request_context()`) when testing forms with CSRF tokens.
- Use `client.session_transaction()` to initialize and verify session data, including CSRF tokens.
- Ensure form creation and submission occur within the same context.
- Verify CSRF tokens are properly generated and added to the session.

### Testing with CSRF
- Always use an application context for form tests
- Ensure test client maintains session state
- Use `client.session_transaction()` to verify CSRF tokens
- Initialize session with a request (e.g., `client.get('/')`) before creating forms
- Verify CSRF token is present in session after form creation
- Use form-generated CSRF tokens in tests and ensure they are added to the session
- Include CSRF token in POST requests
- Keep form creation and POST requests within the same context
- Add debug logging for form validation errors and response status

### Form Testing with CSRF
- Always use a request context when testing forms with CSRF tokens
- Use `client.session_transaction()` to initialize CSRF tokens
- Ensure form creation and submission occur within the same context
- Ensure test client maintains session state
- Use form-generated CSRF tokens in tests and ensure they are added to the session
- Include CSRF token in POST requests
- Initialize session with a request (e.g., `client.get('/')`) before form creation
- Add assertions to verify CSRF token presence in session

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

