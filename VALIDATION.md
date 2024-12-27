# Validation Rules
## Form Testing
- Always use `app.test_request_context()` for form tests
- Include all required fields in test data
- Disable CSRF in tests using meta={'csrf': False} when appropriate
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
- Leap year validation must return specific error message for February 29th in non-leap years
- Ensure validation errors are properly propagated to form errors
- Validate leap year dates and return clear error messages
- Custom date fields must provide specific error messages for:
  - Invalid date formats
  - Leap year violations (including Feb 29 in non-leap years)
  - Timezone conversion errors
- Log details
- Use enums for user feedback
- Preserve form state
- Clearly document field validation rules
- Handle empty values explicitly in custom validators
- Ensure test users remain bound to session during authentication
- Verify consistent error messages for CSRF validation failures
- Ensure datetime fields properly handle:
  - Timezone conversion
  - Validation
  - Future date limits
  - Leap year validation (including Feb 29 in non-leap years)
  - Invalid date detection with clear error messages

