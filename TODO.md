# TODO List

## Completed Tasks
- Fixed HTMX stipend creation and datetime validation issues

## Current Goals
1. [ ] Implement comprehensive date validation testing
   - Add test cases for edge dates (Feb 29, Dec 31, etc.)
   - Test timezone handling
   - Verify error messages for each test case
   - Add integration tests for form submission flow
   - Test with different browser date formats

2. [ ] Improve form error handling consistency
   - Create a shared error handling utility
   - Standardize error message formats across all forms
   - Add client-side validation for date fields
   - Implement real-time validation feedback

## Things to Remember About Testing
- Always test edge cases for date fields (leap years, month boundaries)
- Verify error messages are specific and helpful
- Check both server-side and client-side validation
- Test with different date formats and timezones
- Ensure error states are properly styled in the UI
- Verify that HTMX responses include proper error information

## Things to Remember About Coding
- Use specific error messages for validation failures
- Ensure consistent error handling across all forms
- Properly propagate errors to HTMX responses
- Use proper status codes for error responses (400 for validation errors)
- Maintain consistent field naming and error message formats
- Keep validation logic in forms, not in routes
- Use proper error styling in templates (is-invalid class)

## Current Issues
- Date validation error messages need to be more specific
- Error handling in HTMX responses needs improvement
- Test coverage for edge cases needs to be expanded
- Form error styling needs to be consistent across all forms
- Need better handling of timezone differences
- Need to implement client-side date validation

## Knowledge & Memories
- You're running on a windows 11 machine, should format all commands for that environment
- Date validation now handles both string and datetime inputs
- Error messages are properly propagated to HTMX responses
- Template rendering includes specific field error display
- Form validation includes comprehensive date component checks
- Added specific error messages for different date validation failures
- Implemented proper error message formatting in templates
- Added debug logging for form validation failures
- Confirmed proper CSRF token handling in all form submissions

