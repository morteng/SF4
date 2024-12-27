## Coding Conventions
### Testing with CSRF
- Enable CSRF in test config: `WTF_CSRF_ENABLED = True`
- Use `client.session_transaction()` for session access
- Extract CSRF token from form or login page
- Test both valid and invalid CSRF scenarios
- Verify error messages match actual implementation

### Security
- Validate all inputs
- CSRF tokens required in all forms (can be disabled in tests using meta={'csrf': False})
- Always include required fields in test data
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling
- Always use form.validate() for validation (includes CSRF validation)
- Use test_request_context() for form testing
- For optional fields, handle empty values explicitly in custom validators
- Ensure test users remain bound to session during authentication tests
- Use consistent CSRF error messages across all endpoints
- Ensure datetime fields properly handle timezone conversion and string formatting

