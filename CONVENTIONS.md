## Coding Conventions
### Testing with CSRF
- Always initialize session with `client.get('/')` before form tests
- Verify CSRF token presence in session after form creation
- Keep form creation and validation in the same context
- Ensure test client maintains session state for CSRF validation

### Security
- Validate all inputs
- CSRF tokens required in all forms
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling

