# Validation Rules
## CSRF Token Validation
- Validate CSRF tokens in all POST requests
- Include CSRF token in:
  - Form fields: `csrf_token` and `_csrf_token`
  - Meta tag: `<meta name="csrf-token" content="{{ csrf_token() }}">`
  - Headers: `X-CSRFToken` and `X-Requested-With: XMLHttpRequest`
  - HTMX requests: Add CSRF token via htmx:configRequest event

## Error Handling
- Rollback on error
- Return 400 status code for form validation errors
- Ensure validation errors are properly propagated to form errors
- Return appropriate HTTP status codes (400 for validation errors, 200 for successful form submissions with errors)
- Log details
- Use enums for user feedback
- Preserve form state

