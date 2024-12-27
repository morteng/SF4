## Coding Conventions
### Testing with CSRF
- Always use `app.test_request_context()` for form tests
- Initialize session with `client.get('/')` before form tests
- Use `client.session_transaction()` for session access
- Keep form creation and validation in same context
- Use `meta={'csrf': False}` to disable CSRF in tests when needed
- Verify error messages match actual implementation

### Security
- Validate all inputs
- CSRF tokens required in all forms (can be disabled in tests)
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling
- Always use form.validate() for validation (includes CSRF validation)
- Use test_request_context() for form testing
- For optional fields, handle empty values explicitly in custom validators
- Ensure test users remain bound to session during authentication tests

