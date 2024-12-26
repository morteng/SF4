# TODO List

## Nice to know
You're running on a windows 11 machine, should format all commands for that environment.

## Completed Tasks
- Resolved test file conflicts and syntax errors in stipend routes
- Fixed HTMX stipend creation issues including datetime validation and template path handling

## Things to remember about testing
- Always test both HTMX and non-HTMX cases separately
- Verify proper status codes (200 for success, 400 for errors)
- Test template rendering for HTMX responses
- Verify database state changes after successful operations
- Check for proper error handling and validation messages
- Test edge cases for form validation (empty fields, invalid formats)
- Verify CSRF token handling in form submissions
- Test datetime field validation thoroughly (past dates, invalid formats, far future dates)
- Verify error messages are properly displayed in templates
- Test form re-rendering with validation errors
- Ensure consistent error handling between HTMX and non-HTMX requests

## Things to remember about coding
- Keep HTMX and non-HTMX logic separate and explicit
- Add clear comments for HTMX-specific handling
- Use consistent status codes for API responses
- HTMX responses should return the partial template directly
- Ensure proper error handling and rollback for database operations
- Validate all form inputs before processing
- Use proper template paths for HTMX responses
- Maintain consistent flash message handling
- Ensure proper CSRF token validation in all forms
- Handle datetime fields carefully with proper validation and formatting
- Use proper error handling in form validation methods
- Ensure validation errors are properly propagated to templates
- Keep form validation logic consistent across routes
- Use proper error messages that are user-friendly and specific

## Current Issues
- [ ] Verify template error message rendering for HTMX stipend creation
  - Check that admin/stipends/_form.html properly displays form.errors
  - Ensure error messages are visible in the HTMX response
  - Test with various invalid inputs (empty fields, invalid formats)
  
- [ ] Add additional test cases for datetime validation
  - Test past dates
  - Test dates more than 5 years in future
  - Test invalid date formats
  - Test edge cases (leap years, month/day boundaries)

## Specific Tasks
1. Verify template error rendering:
   - Check admin/stipends/_form.html template
   - Add error message display section if missing
   - Test with invalid inputs to verify error visibility

2. Add datetime validation test cases:
   - Add test cases for past dates
   - Add test cases for far future dates
   - Add test cases for invalid formats
   - Add test cases for edge cases

## Knowledge & Memories
- Fixed datetime validation in StipendForm to handle string inputs
- Verified template path handling in stipend routes
- Confirmed proper CSRF token handling in HTMX requests
- Added debug logging for template verification
- Improved error handling for invalid date formats

