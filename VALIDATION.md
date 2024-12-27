# Validation Rules
## CSRF Token Validation
- Validate CSRF tokens in all POST requests
- Include CSRF token in:
  - Form fields: `csrf_token` and `_csrf_token`
  - Meta tag: `<meta name="csrf-token" content="{{ csrf_token() }}">`
  - Headers: `X-CSRFToken` and `X-Requested-With: XMLHttpRequest`
  - HTMX requests: Add CSRF token via htmx:configRequest event
- Ensure CSRF token is present in HTML response before extraction
- Verify token matching between form and session

## Error Handling
- Rollback on error
- Date parsing errors must be handled separately from logical date validation
- Return 400 status code for form validation errors
- Ensure validation errors are properly propagated to form errors
- Return appropriate HTTP status codes (400 for validation errors, 200 for successful form submissions with errors)
- Validate leap year dates and return clear error messages
- Custom date fields must provide specific error messages for:
  - Invalid date formats
  - Leap year violations (including Feb 29 in non-leap years)
  - Timezone conversion errors
  - Missing/empty values
  - Proper error state propagation in validation chain
- Log details
- Use enums for user feedback
- Preserve form state
- Clearly document field validation rules
- Handle empty values explicitly in custom validators
- Initialize test users with all required fields
- Use application's actual login flow in tests
- Verify CSRF token handling in authentication tests
- Verify consistent error messages for CSRF validation failures
- Ensure datetime fields properly handle:
  - Timezone conversion
  - Validation
  - Future date limits
  - Invalid date detection with clear error messages

