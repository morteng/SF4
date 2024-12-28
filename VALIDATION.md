# Validation Rules

## Test Isolation Validation
- Ensure tests use unique credentials to avoid conflicts
- Clean up test data before each test run
- Verify proper database state for each test
- Use proper context management for session handling
- Ensure session persistence for audit log verification

## Audit Log Validation
- Verify all CRUD operations and system events create audit logs with:
  - User ID (0 for system events)
  - Action type (create/update/delete/system_event)
  - Object type and ID
  - Timestamp (timezone-aware UTC)
  - IP address (required for all operations)
  - Operation details
  - Before/after state for updates
- Ensure related_object is a model instance, not a string
- Ensure consistent timezone handling in audit logs
- Verify audit logs create corresponding notifications
- Check logs contain:
  - user_id, action, object_type, object_id
  - timestamp, ip_address
  - details_before, details_after
- Ensure logs are created for both success and failure cases
- Validate audit log details field contains operation-specific information
- Verify object_type is always set (defaults to 'User' if not specified)

## Notification Handling
- notification_count must be passed to all admin templates
- Use get_notification_count() for count retrieval
- Handle errors gracefully (return 0 on error)
- Ensure real-time updates
- Validate user_id matches current user or system (0)
- Use NotificationType enum for all notification types
- Validate enum values match defined types:
  - BOT_SUCCESS, BOT_ERROR, USER_ACTION, SYSTEM
  - CRUD_CREATE, CRUD_UPDATE, CRUD_DELETE
  - USER_CREATED, USER_UPDATED, USER_DELETED
  - PASSWORD_RESET, AUDIT_LOG
  - STIPEND_CREATED, STIPEND_UPDATED, STIPEND_DELETED

## CSRF Token Validation
- Validate CSRF tokens in all POST requests
- Include CSRF token in all forms and HTMX requests
- Return 400 for invalid/missing tokens
- Ensure CSRF tokens are properly extracted in tests

## CSRF Token Validation
- Validate CSRF tokens in all POST requests
- Use Flask-WTF forms for automatic CSRF validation
- Include CSRF token in all forms and HTMX requests
- Ensure CSRF tokens are properly extracted in tests
- Handle missing/invalid CSRF tokens with 400 status
- Verify blueprint factory pattern implementation

## Rate Limiting
- Verify rate limits are enforced:
  - Admin: 100/hour (global)
  - Sensitive ops: 10/minute (per endpoint)
  - CRUD Operations:
    - Create/Update: 10/minute
    - Delete: 3/minute
    - View: No limit
  - Password resets: 5/hour
  - Bot operations: 10/hour
  - Bot scheduling: 5/hour

### Notification Badge Validation
- All admin templates must include a notification badge.
- The badge must display the correct count of unread notifications.
- The badge must be visible even if the count is 0.

## Form Validation
- Validate all form inputs using constants from app\constants.py
- Password validation:
  - Verify passwords are hashed using werkzeug.security.generate_password_hash()
  - Test password verification using check_password_hash()
  - Ensure no plain text passwords are stored
  - Verify password strength requirements are enforced
- Required validations:
    USERNAME_REQUIRED = "Username is required."
    USERNAME_LENGTH = "Username must be between 3 and 50 characters."
    USERNAME_FORMAT = "Username can only contain letters, numbers and underscores."
    FORM_VALIDATION_ERROR = "Form validation failed. Please check your input."

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
- Validate audit log details match actual changes
- Verify details_before and details_after are JSON serializable
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

