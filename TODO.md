# TODO List
## High Priority
- [ ] Add remaining form validation tests
- [ ] Add CRUD integration tests
- [ ] Increase test coverage to 80%+

## Best Practices
- Validate & sanitize all inputs
- Test CSRF protection in all form submissions
- Verify proper error responses for invalid CSRF
- Use enums consistently for error messages
- Ensure CSRF tokens match between form and session
- Fix session binding issues in authentication tests
- Use form.validate() instead of manual CSRF validation
- Verify UI & DB state in tests
- Ensure CSRF protection matches production environment
- Verify error messages match actual implementation
- Clearly document field validation rules
- Handle empty values explicitly in custom validators
- Standardize CSRF error message handling across all endpoints

