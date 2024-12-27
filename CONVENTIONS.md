## Coding Conventions
### Testing with CSRF
- Always initialize session with `client.get('/')` before form tests
- Verify CSRF token presence in session after form creation
- Keep form creation and validation in the same context
- Ensure test client maintains session state for CSRF validation
- Use `app.test_request_context()` when accessing session data
- Validate CSRF token matches between form and session
- Test both valid and invalid CSRF token scenarios
- Document session initialization requirements in test cases
- Use session_transaction() when verifying session state
- Verify CSRF token generation with form.csrf_token.current_token

### Security
- Validate all inputs
- CSRF tokens required in all forms
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling

