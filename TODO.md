# TODO List
## High Priority
- [x] Core CRUD & security
- [ ] Implement password hashing using werkzeug.security
- [x] Fix datetime.utcnow() deprecation warnings
- [x] Add username validation constants
- [x] Improve test isolation with unique credentials
- [ ] Fix DetachedInstanceError in admin user tests
- [x] Testing:
  - Admin routes
  - User request handling
  - HTMX integration
  - Rate limiting
- [x] Fix datetime.utcnow() deprecation warnings
- [x] Complete CRUD test coverage
- [x] Add audit logging for all operations
- [x] Fix notification.user_id constraint issues
- [x] Implement blueprint factory pattern
- [x] Implement bot scheduling

## Best Practices
- Ensure CSRF protection matches production environment
- Standardize error message handling across all endpoints
- Verify error scenarios using response status codes and flash messages

