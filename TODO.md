# TODO List
## High Priority
- [x] Core CRUD & security
- [x] Testing:
  - Admin routes
  - User request handling
  - HTMX integration
  - Rate limiting
- [x] Fix datetime.utcnow() deprecation warnings
- [ ] Complete CRUD test coverage
- [x] Add audit logging for all operations
- [ ] Fix notification.user_id constraint issues
- [ ] Resolve view function endpoint conflicts using blueprint naming pattern

## Best Practices
- Ensure CSRF protection matches production environment
- Standardize error message handling across all endpoints
- Verify error scenarios using response status codes and flash messages

