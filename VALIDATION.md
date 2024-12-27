# Validation Rules

## Notification Handling
- notification_count must be passed to all admin templates
- notification_count should be retrieved using get_notification_count()
- Handle notification_count errors gracefully (return 0 on error)
- Ensure notification_count is updated in real-time

## CSRF Token Validation
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
- Use Flask-WTF forms for automatic CSRF validation
- Include CSRF token in all forms and HTMX requests
- Ensure CSRF tokens are properly extracted in tests using `extract_csrf_token()`
- Handle missing/invalid CSRF tokens with 400 status

## Rate Limiting
- Admin endpoints: 100 requests/hour
- Sensitive operations: 10 requests/minute
- User creation: 10 requests/minute
- User deletion: 3 requests/minute
- Password resets: 5 requests/hour

### Notification Badge Validation
- All admin templates must include a notification badge.
- The badge must display the correct count of unread notifications.
- The badge must be visible even if the count is 0.

## Error Handling
- Rollback on error
- Audit log all CRUD operations with:
  - Timestamp (UTC)
  - User ID
  - IP address
  - Action type (create/update/delete)
  - Object type and ID
  - Before/after state for updates
  - Success/failure status

## Audit Log Validation
- Verify all CRUD operations create audit logs
- Check logs contain required fields
- Ensure logs are created for both success and failure cases
- Validate audit log details field contains operation-specific information
- Ensure notification_count is passed to all admin templates
- Store audit logs in separate database table
- Include audit log reference in error responses
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

