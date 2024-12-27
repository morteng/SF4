# Validation Rules
## CSRF Token Validation
- Validate CSRF tokens in all POST requests
- Include CSRF token in form fields: `<input name="csrf_token" value="{{ csrf_token }}">`
- Use `decode_csrf_token()` to properly verify tokens

## Error Handling
- Rollback on error
- Return 400 status code for form validation and database errors
- Ensure validation errors are properly propagated to form errors
- Return appropriate HTTP status codes (400 for validation/database errors)
- Log details including error messages
- Use enums for user feedback with appended error details when needed
- Preserve form state
- Verify flash messages in session using substring matching

