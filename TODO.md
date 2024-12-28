# TODO List
## High Priority
- [x] Core CRUD & security
- [x] Implement password hashing using werkzeug.security
- [x] Fix remaining datetime.utcnow() deprecation warnings
- [ ] Ensure audit log details accurately reflect changes
- [x] Add username validation constants
- [x] Improve test isolation with unique credentials
- [x] Fix DetachedInstanceError in admin user tests
- [ ] Ensure IP address logging for all audit logs
- [x] Testing:
  - Admin routes
  - User request handling
  - HTMX integration
  - Rate limiting
- [x] Fix datetime.utcnow() deprecation warnings
- [ ] Ensure consistent timezone handling across all datetime operations
- [x] Complete CRUD test coverage
- [x] Add audit logging for all operations
- [x] Fix notification.user_id constraint issues
- [x] Implement blueprint factory pattern
- [x] Implement bot scheduling

## Best Practices
- Ensure CSRF protection matches production environment
- Standardize error message handling across all endpoints
- Verify error scenarios using response status codes and flash messages

