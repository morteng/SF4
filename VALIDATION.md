# Validation Rules

### Form Validation
- Validate all form inputs using constants from app\constants.py
- Ensure all required fields have DataRequired and Length(min=1) validators
- Select fields must have choices set before validation
- SelectMultipleField must have valid choices defined
- Date validation must handle:
  - Past dates invalid
  - Future dates limited to 5 years
  - Leap year validation
  - Proper date format (YYYY-MM-DD HH:MM:SS)
  - Timezone awareness (convert to UTC)

### Audit Log Validation
- Validate required fields: user_id, action, object_type, object_id
- Verify timestamps are UTC and properly formatted
- Check JSON serialization of before/after states
- Ensure rollback occurs on audit log failure
  - Details field with human-readable description
- Ensure logs are created for both success and failure cases
- Validate JSON serialization of complex data
- Verify commit flag works as expected
- Check timezone handling for timestamps

### Notification Validation
- Validate NotificationType enum values
- Ensure related_object exists
- Validate user_id exists
- Validate message length (max 255 chars)

### Bot Validation
- Verify proper status tracking (running, completed, error)
- Check audit logs for all bot operations
- Validate notifications for bot success/failure
- Ensure proper error handling and logging
- Verify rate limiting for bot operations

### Notification Handling
- notification_count must be passed to all admin templates
- Handle errors gracefully (return 0 on error)
- Validate enum values match defined types
- Ensure notifications are marked as read when viewed

