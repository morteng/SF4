# Validation Rules
## CSRF Token Validation
- Validate CSRF tokens in all POST requests
- Include CSRF token in form fields: `<input name="csrf_token" value="{{ csrf_token }}">`
- Verify raw CSRF token matches session token directly

## Error Handling
- Rollback on error
- Return 400 status code for form validation errors
- Ensure validation errors are properly propagated to form errors
- Return appropriate HTTP status codes (400 for validation errors, 200 for successful form submissions with errors)
- Log details
- Use enums for user feedback
- Preserve form state

