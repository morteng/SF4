# Validation Rules
### CSRF Token Validation
- Validate CSRF tokens in all POST requests.
- Include CSRF token in form fields:
  ```html
  <input name="csrf_token" value="{{ csrf_token }}">
  ```
- For HTMX requests, include meta tag:
  ```html
  <meta name="csrf-token" content="{{ csrf_token() }}">
  ```
- Use `decode_csrf_token()` to properly verify tokens.

## CSRF Token Validation
- Validate CSRF tokens in all POST requests
- Include CSRF token in form fields: `<input name="csrf_token" value="{{ csrf_token }}">`
- For HTMX requests, include meta tag: `<meta name="csrf-token" content="{{ csrf_token() }}">`
- Use `decode_csrf_token()` to properly verify tokens

## Error Handling
- Rollback on error
- Return appropriate status codes:
  - 400 for validation/database errors
  - 200 for success
- For database errors:
  - Render templates directly
  - Set flash message with error details
  - Return 400 status
  - Pass flash messages explicitly in template context using `flash_messages` parameter
  - Ensure error messages follow format: "Error message: error details"
- Ensure validation errors are properly propagated to form errors
- Log details including error messages
- Use enums for user feedback with appended error details when needed
- Preserve form state
- Verify flash messages in response HTML after redirects

