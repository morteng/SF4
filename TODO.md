# TODO List
## High Priority
- [x] Fix CSRF token initialization in form tests
- [x] Add session initialization checks in form tests
- [x] Verify CSRF token presence in session after form creation
- [x] Verify CSRF token value matches between form and session
- [ ] Add CRUD integration tests
- [ ] Increase test coverage to 80%+

## Best Practices
- Validate & sanitize all inputs
- Ensure session initialization in form tests
- Use enums consistently
- Verify UI & DB state in tests
- Ensure CSRF tokens in all forms
- Maintain CSRF protection in all environments
- Use form-generated CSRF tokens in tests
- Ensure test client maintains session state between requests
- Always use an application context for form tests

