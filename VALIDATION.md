# Validation Rules
## Form Testing
- Always initialize session with `client.get('/')` before form tests
- Verify CSRF token presence and value in session
- Keep form creation and validation in the same context
- Ensure test client maintains session state between requests
- Use `app.test_request_context()` when accessing session data
- Validate CSRF token matches between form and session

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

