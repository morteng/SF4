## Coding Conventions
### Testing with CSRF
- Initialize session with `client.get('/')` before form tests
- Verify CSRF token presence and value in session
- Keep form creation and validation in same context
- Use `app.test_request_context()` for session access
- Validate CSRF token matches between form and session

### Security
- Validate all inputs
- CSRF tokens required in all forms
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling

