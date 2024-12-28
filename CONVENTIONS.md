## Coding Conventions
- All flash messages must use messages defined in app\constants.py
- Audit logging required for all CRUD operations
- CSRF tokens must be included in all forms and HTMX requests
- Rate limiting:
  - Admin: 200/day, 50/hour
  - CRUD: Create/Update (10/min), Delete (3/min)
  - Bot operations: 10/hour
  - Password resets: 5/hour

### Notification Badges
- All admin templates must include a notification badge
- Use NotificationType enum for all notification types
- Badge visible even when count is 0

### Audit Logging
- Required for all CRUD operations and system events
- Must include:
  - User ID (0 for system events)
  - Action type (create/update/delete/system_event)
  - Object type and ID
  - Timestamp (timezone-aware UTC)
  - IP address
  - Before/after state for updates

