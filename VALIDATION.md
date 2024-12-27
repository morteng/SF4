# Validation Rules
## Form Testing
- Initialize session with `client.get('/')` before form tests
- Verify CSRF token presence and value in session
- Keep form creation and validation in same context
- Use `app.test_request_context()` for session access

## CSRF Token Validation
- Validate CSRF tokens in all forms
- Include CSRF token in form submissions
- Use form-generated CSRF tokens in tests
- Ensure CSRF tokens are properly initialized in forms

## Error Handling
- Rollback on error
- Log details
- Use enums for user feedback
- Preserve form state

