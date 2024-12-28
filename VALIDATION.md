# Validation Rules

### Form Validation
- Validate all form inputs using constants from app\constants.py
- Ensure all required fields have validation messages
- SelectMultipleField must have valid choices defined
- Date validation must handle:
  - Past dates invalid
  - Future dates limited to 5 years
  - Leap year validation

### Audit Log Validation
- Verify all CRUD operations create audit logs
- Check logs contain required fields
- Ensure logs are created for both success and failure cases

### Notification Handling
- notification_count must be passed to all admin templates
- Handle errors gracefully (return 0 on error)
- Validate enum values match defined types

