## Coding Conventions
- All flash messages must use messages defined in app\constants.py - create new additions here when needed. All tests should evaluate the constant used, not the string itself.


### Testing with CSRF
- Enable CSRF in test config: `WTF_CSRF_ENABLED = True`
- Use `client.session_transaction()` for session access
- Extract CSRF token from form using pattern: `<input[^>]*id="csrf_token"[^>]*value="([^"]+)"`
- Ensure CSRF token is present in the HTML response before extraction
- Test both valid and invalid CSRF scenarios
- Verify error messages match actual implementation
- Always make a GET request before POST to establish session
- Handle CSRF token extraction errors gracefully
- For form validation errors, expect 400 status code
- Include CSRF token in both form data and headers:
  - Form data: `csrf_token` and `_csrf_token`
  - Header: `X-CSRFToken`
  - Header: `X-Requested-With: XMLHttpRequest`

### Security
- Validate all inputs, including leap year dates and invalid date combinations
- Leap year validation must explicitly check for February 29th in non-leap years with specific error message: 'Invalid date values (e.g., Feb 29 in non-leap years)'
- Date validation must handle both parsing errors and logical date validation separately
- CSRF tokens required in all POST requests (can be disabled in tests using meta={'csrf': False})
- Ensure validation errors are properly propagated to form errors and return appropriate HTTP status codes
- Custom fields must handle:
  - Timezone conversion
  - String formatting
  - Future date validation
  - Leap year validation (including Feb 29 in non-leap years) with specific error message
  - Invalid value detection with clear error messages
  - Missing/empty values with 'required' error message
  - Proper error state propagation in validation chain
- CSRF tokens required in all forms (can be disabled in tests using meta={'csrf': False})
- Always include required fields in test data
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling
- Always use form.validate() for validation (includes CSRF validation)
- Use test_request_context() for form testing
- For optional fields, handle empty values explicitly in custom validators
- Ensure test users are properly initialized with required fields
- Use application's actual login mechanism in tests instead of manual session manipulation
- Use consistent CSRF error messages across all endpoints
- Ensure datetime fields properly handle:
  - Timezone conversion
  - String formatting
  - Future date validation
  - Leap year validation (including Feb 29 in non-leap years)
  - Invalid date detection (e.g., Feb 30) with clear error messages

