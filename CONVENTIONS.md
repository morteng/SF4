## Coding Conventions
- All flash messages must use messages defined in app\constants.py
- Audit logging required for all CRUD operations
- CSRF tokens must be included in all forms and HTMX requests
- Rate limiting:
  - Admin: 200/day, 50/hour
  - CRUD: Create/Update (10/min), Delete (3/min)
  - Bot operations: 10/hour
  - Password resets: 5/hour

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

