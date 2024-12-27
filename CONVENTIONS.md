## Coding Conventions
### Testing
- Use enums for message types
- Verify UI & DB state
- Use fixtures & parameterized tests
- Include CSRF token validation in form tests
- CSRF enabled in testing environment
- Use request context for form tests
- When testing forms, always use the form's generated CSRF token
- Ensure test client maintains session state for CSRF validation

### Testing with CSRF
- Use `test_request_context` for CSRF-protected forms
- Ensure test client maintains session state
- Use `client.session_transaction()` to verify CSRF tokens
- Use form-generated CSRF tokens in tests
- Include CSRF token in POST requests
- Keep form creation and POST requests within the same context
- Add debug logging for form validation errors and response status

### Form Testing
- Always use `test_request_context` when testing forms
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

