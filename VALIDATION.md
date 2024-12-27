# Validation Rules
## Principles
- Validate client & server side
- Use enums for message types
- Test success & failure cases
- CSRF enabled in all environments
- Include CSRF validation in all form tests
- Use request context for form tests
- Use form-generated CSRF tokens in tests
- Ensure test client maintains session state

## Form Validation
- Validate CSRF tokens in all forms
- Include CSRF token in form submissions
- Use form-generated CSRF tokens in tests
- Ensure CSRF tokens are properly initialized in forms
- Add error handling to debug validation failures
- Ensure all required fields are properly set
- Validate presence of required fields
- Enforce max lengths
- Validate URLs and dates
- Check for duplicates
- Use form-generated CSRF tokens

## Form Testing
- Test both valid and invalid form submissions
- Verify validation messages
- Use `test_request_context` for CSRF-protected forms
- Validate CSRF tokens in all form tests
- Ensure form submissions include all required fields
- Use form-generated CSRF tokens in tests

## Form Validation Testing
- Test all required fields and constraints
- Verify error messages for invalid inputs
- Use `form.errors` to debug validation failures

## Error Handling
- Rollback on error
- Log details
- Use enums for user feedback
- Preserve form state

## Security
- Sanitize inputs
- CSRF tokens required in all forms
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling

