# Validation Rules
## Form Testing
- Initialize session with `client.get('/')` before form tests
- Verify CSRF token presence and value in session
- Keep form creation and validation in the same context

## Form Validation
- Validate CSRF tokens in all forms
- Include CSRF token in form submissions
- Use form-generated CSRF tokens in tests
- Ensure CSRF tokens are properly initialized in forms
- Add error handling to debug validation failures

### CSRF Token Validation
- Validate CSRF tokens in all forms
- Include CSRF token in form submissions
- Use form-generated CSRF tokens in tests
- Ensure CSRF tokens are properly initialized in forms
- Add error handling to debug validation failures

### CSRF Token Validation in Tests
- Use `client.session_transaction()` to initialize CSRF tokens
- Ensure form creation and submission occur within the same context
- Verify CSRF tokens are properly generated and validated
- Initialize session with a request (e.g., `client.get('/')`) before creating forms
- Verify CSRF token is present in session after form creation
- Verify the CSRF token value matches between form and session
- Ensure the session is initialized (e.g., via `client.get('/')`) before creating forms that rely on CSRF tokens
- Verify the CSRF token is present in the session after form creation
- Ensure test client maintains session state between requests
- Add assertions to verify CSRF token presence in session
- Ensure the session is initialized (e.g., via `client.get('/')`) before creating forms that rely on CSRF tokens
- Verify the CSRF token is present in the session after form creation
- Ensure all required fields are properly set
- Validate presence of required fields
- Enforce max lengths
- Validate URLs and dates
- Check for duplicates
- Use form-generated CSRF tokens

## Form Testing
- Ensure correct import paths for configuration (e.g., `from app.config import TestConfig`)
- Test both valid and invalid form submissions
- Verify validation messages
- Always use an application context for form tests
- Validate CSRF tokens in all form tests
- Ensure form submissions include all required fields
- Use form-generated CSRF tokens in tests
- Add debug logging for form validation errors
- Include response status and data in debug output
- Keep form creation and POST requests within the same context

### Session State
- Verify session maintains CSRF tokens
- Use `client.session_transaction()` to debug session issues
- Ensure test client preserves cookies between requests

## Form Validation Testing
- Test all required fields and constraints
- Verify error messages for invalid inputs
- Use `form.errors` to debug validation failures

## Error Handling
- Rollback on error
- Log details
- Use enums for user feedback
- Preserve form state

## Security
- Sanitize inputs
- CSRF tokens required in all forms
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling

