## Coding Conventions
- **PEP 8**: Follow Python PEP 8 style
- **Modularity**: Keep code small and focused
- **Clear Separation**: Models, services, routes, and templates well-structured
- **Documentation**: Docstrings, comments, and meaningful names
- **Validation Messages**: Use constants from app\constants.py for all validation messages
- **Flash Messages**: Use FlashMessages enum from app\constants.py for all flash messages
- **CSRF Protection**: Include CSRF tokens in all forms and HTMX requests
- **Audit Logging**: Log all CRUD operations with user, action, and timestamp
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
  - CRUD: Create/Update (10/min;100/hour), Delete (3/min;30/hour)
  - Bot operations: 10/hour
  - Password resets: 5/hour
  - Login attempts: 3/min
- Bot implementations must:
  - Maintain proper status tracking
  - Create audit logs for all operations
  - Generate notifications for success/failure
  - Handle errors gracefully
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
  - Details field with human-readable description

