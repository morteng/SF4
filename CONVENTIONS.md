## Coding Conventions
- All flash messages must use messages defined in app\constants.py
- Audit logging required for all CRUD operations
- CSRF tokens must be included in:
  - All forms: `<input id="csrf_token" name="csrf_token" type="hidden" value="{{ csrf_token() }}">`
  - HTMX requests: Add meta tag `<meta name="csrf-token" content="{{ csrf_token() }}">` in base template
  - JavaScript: Include CSRF token in HTMX headers via htmx:configRequest event
- Rate limiting:
  - Admin endpoints: 100/hour
  - Sensitive operations: 10/minute

### Rate Limiting
- Admin endpoints: 100/hour
- Sensitive operations: 10/minute
- User creation: 10/minute
- User deletion: 3/minute
- Password resets: 5/hour

### CSRF Token Handling
- Use Flask-WTF for CSRF protection
- Include CSRF token in all forms via `{{ csrf_token }}` (not callable)
- Ensure `request` is imported from Flask when accessing form data
- Add CSRF meta tag in base template for HTMX
- Validate CSRF tokens in all POST requests
- Return 400 for invalid/missing CSRF tokens

### Notification Badges
- All admin templates must include a notification badge.
- The badge should display the count of unread notifications.
- Use `get_notification_count()` to retrieve the count.
- The badge should be visible even if the count is 0.

### Audit Logging
- Required for all CRUD operations
- Must include:
  - Timestamp (UTC)
  - User ID
  - IP address
  - Action type (create/update/delete)
  - Object type and ID
  - Details before/after changes
  - Operation status

### Testing with CSRF and Error Handling
- Enable CSRF in test config: `WTF_CSRF_ENABLED = True`
- Extract CSRF token from hidden input: `<input name="csrf_token" value="...">`
- Verify flash messages in response HTML (don't rely on redirects)
- For database errors:
  - Return 400 status code
  - Render template directly with error message
  - Pass flash messages explicitly in template context using `flash_messages` parameter
  - Ensure error messages are properly formatted with error details
- Test both valid and invalid CSRF scenarios
- Always make a GET request before POST to establish session
- For database error tests:
  - Verify flash messages directly in response
  - Expect 400 status code
  - Verify template is rendered directly
- For error scenarios:
  - Check response status codes (400 for errors)
  - Verify flash messages
  - Ensure redirects maintain error status codes

### Security
- Validate all inputs, including leap year dates and invalid date combinations
- Leap year validation must explicitly check for February 29th in non-leap years with specific error message: 'Invalid date values (e.g., Feb 29 in non-leap years)'
- Password strength requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character
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

