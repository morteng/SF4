## Coding Conventions
- All flash messages must use messages defined in app\constants.py
- Audit logging required for all CRUD operations including:
  - User ID, Action type, Object type, Object ID
  - Timestamp (UTC), IP address, HTTP method, Endpoint
  - Before/after state for updates (JSON serialized)
- Notifications must:
  - Use NotificationType enum values
  - Include user_id and related_object
  - Use proper priority levels
- CSRF tokens must be included in all forms and HTMX requests
- Rate limiting:
  - Admin: 200/day, 50/hour
  - CRUD: Create/Update (10/min), Delete (3/min)
  - Bot operations: 10/hour
  - Password resets: 5/hour
  - Login attempts: 3/min
- Notification system must:
  - Use NotificationType enum values
  - Include user_id and related_object
  - Use proper priority levels
- Date/Time handling:
  - Use CustomDateTimeField for all datetime inputs
  - Store all timestamps in UTC
  - Validate date formats and ranges

### Form Validation
- SelectMultipleField must have valid choices defined
- Date validation must handle:
  - Past dates invalid
  - Future dates limited to 5 years
  - Leap year validation

### Audit Logging
- Required for all CRUD operations and system events
- Must include:
  - User ID (0 for system events)
  - Action type (create/update/delete/system_event)
  - Object type and ID
  - Timestamp (timezone-aware UTC)
  - IP address
  - HTTP method and endpoint
  - Before/after state for updates (where applicable)

