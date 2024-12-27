# TODO List
## High Priority
- [ ] Add CRUD integration tests
- [ ] Increase test coverage to 80%+

## Best Practices
- Validate & sanitize all inputs
- Ensure CSRF protection is enabled in test config
- Verify session initialization in form tests
- Use enums consistently
- Use form.validate() instead of manual CSRF validation
- Verify UI & DB state in tests
- Ensure CSRF protection matches production environment
- Add CSRF token validation tests for all forms
- Document session initialization requirements
- Use session_transaction() for session verification
- Verify CSRF token generation with form.csrf_token.current_token

