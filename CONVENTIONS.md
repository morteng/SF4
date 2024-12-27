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
- Admin: 100/hour (global)
- Sensitive ops: 10/minute (per endpoint)
- Stipend CRUD:
  - Create/Update: 10/minute
  - Delete: 3/minute
- User CRUD:
  - Create: 10/minute
  - Delete: 3/minute
- Password resets: 5/hour
- Organization CRUD:
  - Create/Update: 10/minute
  - Delete: 3/minute
- Bot operations: 10/hour

### CSRF Token Handling
- Use Flask-WTF for CSRF protection
- Include CSRF token in all forms and HTMX requests
- Validate CSRF tokens in all POST requests
- Return 400 for invalid/missing CSRF tokens
- Add CSRF token to test requests

### Notification Badges
- All admin templates must include a notification badge.
- The badge should display the count of unread notifications.
- Use `get_notification_count()` to retrieve the count.
- The badge should be visible even if the count is 0.

### Audit Logging
- Required for all CRUD operations and system events
- Must include:
  - User ID (0 for system events)
  - Action type (create/update/delete/system_event)
  - Object type and ID
  - Timestamp (UTC)
  - IP address (if available)
  - Operation details
  - Before/after state for updates
- Must create notification for audit log creation
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

