# Validation Rules
## Form Testing
- Use `app.test_request_context()` for proper context
- Initialize session with `client.get('/')` before form tests
- Use `client.session_transaction()` for session access
- Use `meta={'csrf': False}` to disable CSRF in tests when needed
- Verify error messages match actual implementation

## CSRF Token Validation
- Validate CSRF tokens in all forms
- Include CSRF token in form submissions
- Use form-generated CSRF tokens in tests
- Ensure CSRF protection is enabled in test config
- Verify CSRF token presence in session

## Error Handling
- Rollback on error
- Log details
- Use enums for user feedback
- Preserve form state

