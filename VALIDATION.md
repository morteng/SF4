# Validation Rules
## Form Testing
- Always use `app.test_request_context()` for form tests
- Initialize session with `client.get('/')` before form tests
- Use `client.session_transaction()` for session access
- Use `meta={'csrf': False}` to disable CSRF in tests when needed
- Verify error messages match actual implementation
- Test both validation success and failure cases

## CSRF Token Validation
- Validate CSRF tokens in all forms
- Include CSRF token in form submissions
- Extract CSRF token from login page for tests
- Ensure CSRF protection is enabled in test config
- Verify token matching between form and session

## Error Handling
- Rollback on error
- Log details
- Use enums for user feedback
- Preserve form state
- Clearly document field validation rules
- Handle empty values explicitly in custom validators
- Ensure test users remain bound to session during authentication
- Verify consistent error messages for CSRF validation failures

