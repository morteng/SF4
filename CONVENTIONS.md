## Coding Conventions
### Testing with CSRF
- Initialize session with `client.get('/')` before form tests
- Ensure `WTF_CSRF_ENABLED=True` in test config
- Verify CSRF token presence in session
- Keep form creation and validation in same context
- Use `app.test_request_context()` for session access
- Use form-generated CSRF token in test submissions

### Security
- Validate all inputs
- CSRF tokens required in all forms (can be disabled in tests)
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling
- Always use form.validate() for validation (includes CSRF validation)
- Use test_request_context() for form testing

