## Coding Conventions
### Testing with CSRF
- Initialize session with `client.get('/')` before form tests
- Use `app.test_request_context()` for proper context
- Verify CSRF token presence in session
- Keep form creation and validation in same context
- Use `client.session_transaction()` for session access
- Use `meta={'csrf': False}` to disable CSRF in tests when needed

### Security
- Validate all inputs
- CSRF tokens required in all forms (can be disabled in tests)
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling
- Always use form.validate() for validation (includes CSRF validation)
- Use test_request_context() for form testing

