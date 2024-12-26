# TODO List

## Completed Tasks
- Implemented comprehensive date validation and error handling for stipend forms

## Current Goals
1. [ ] Add client-side date validation
   - Add JavaScript validation in main.js for date fields
   - Match server-side validation rules
   - Show real-time feedback using HTMX
   - Test with different browser date formats
   - File: app/static/js/main.js

2. [ ] Improve test coverage for edge cases
   - Add tests for leap years (Feb 29)
   - Test timezone handling (UTC vs local)
   - Verify error messages for each validation rule
   - Add integration tests for form submission flow
   - File: tests/app/routes/admin/test_stipend_htmx.py

## Things to Remember About Testing
- Always test edge cases for date fields (Feb 29, Dec 31, etc.)
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

## Knowledge & Memories
- Windows 11 environment - use cmd.exe for commands
- Date validation handles both string and datetime inputs
- Error messages are properly propagated to HTMX responses
- Template rendering includes specific field error display
- Form validation includes comprehensive date component checks
- Specific error messages for different validation failures
- Proper error message formatting in templates
- Debug logging for form validation failures
- CSRF token handling confirmed in all form submissions
- Current date validation handles:
  - Invalid formats (YYYY-MM-DD HH:MM:SS required)
  - Invalid dates (Feb 30, etc.)
  - Invalid times (25:61:61, etc.)
  - Missing time components
  - Past dates
  - Dates more than 5 years in future

