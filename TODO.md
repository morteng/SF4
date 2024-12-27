# TODO List
## High Priority
- [ ] Add remaining form validation tests
- [ ] Add CRUD integration tests
- [ ] Increase test coverage to 80%+

## Best Practices
- Ensure date parsing and logical validation are handled separately
- Verify date validation error propagation in form handling
- Ensure test data includes all required fields
- Implement proper error message handling for custom date fields
- Disable CSRF in tests when appropriate
- Test CSRF protection in all form submissions
- Verify proper error responses for invalid CSRF
- Ensure GET request before POST to establish session
- Add robust CSRF token extraction in tests
- Use enums consistently for error messages
- Ensure CSRF tokens match between form and session
- Ensure proper user initialization in authentication tests
- Verify login mechanism works correctly in test environment
- Use form.validate() instead of manual CSRF validation
- Verify UI & DB state in tests
- Ensure CSRF protection matches production environment
- Verify error messages match actual implementation
- Ensure validation errors return appropriate HTTP status codes (400 for validation errors)
- Clearly document field validation rules
- Handle empty values explicitly in custom validators
- Standardize CSRF error message handling across all endpoints
- Ensure datetime fields handle:
  - String input
  - Timezone-aware objects
  - Future date validation
  - Invalid date detection with consistent error messages
  - Missing/empty values with 'required' error message
  - Proper error state propagation in validation chain

