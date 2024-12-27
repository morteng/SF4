# Validation Rules
## Form Testing
- Initialize session with `client.get('/')` before form tests
- Verify CSRF token presence in session
- Use form.validate() for validation (includes CSRF validation)
- Keep form creation and validation in same context
- Use `app.test_request_context()` for session access

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

