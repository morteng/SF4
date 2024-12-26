# TODO List

## Nice to know
- You're running on a windows 11 machine, should format all commands for that environment.

## Completed Tasks
- Resolved test file conflicts and syntax errors in stipend routes
- Fixed HTMX stipend creation issues including datetime validation and template path handling

## Things to remember about testing
1. Always test both HTMX and non-HTMX cases separately
2. Verify proper status codes (200 for success, 400 for errors)
3. Test template rendering for HTMX responses
4. Verify database state changes after successful operations
5. Check for proper error handling and validation messages
6. Test edge cases for form validation (empty fields, invalid formats)
7. Verify CSRF token handling in form submissions
8. Test datetime field validation thoroughly (past dates, invalid formats, far future dates)
9. Verify error messages are properly displayed in templates
10. Test form re-rendering with validation errors
11. Ensure consistent error handling between HTMX and non-HTMX requests
12. Test for proper error message propagation in form submissions
13. Verify validation error messages are specific and helpful
14. Test for proper handling of invalid date formats
15. Ensure error messages are visible in both full page and HTMX responses

## Things to remember about coding
1. Keep HTMX and non-HTMX logic separate and explicit
2. Add clear comments for HTMX-specific handling
3. Use consistent status codes for API responses
4. HTMX responses should return the partial template directly
5. Ensure proper error handling and rollback for database operations
6. Validate all form inputs before processing
7. Use proper template paths for HTMX responses
8. Maintain consistent flash message handling
9. Ensure proper CSRF token validation in all forms
10. Handle datetime fields carefully with proper validation and formatting
11. Use proper error handling in form validation methods
12. Ensure validation errors are properly propagated to templates
13. Keep form validation logic consistent across routes
14. Use proper error messages that are user-friendly and specific
15. Add specific validation for date fields including format and range checks
16. Ensure error messages are properly formatted for display in templates
17. Use consistent error message formatting across all forms
18. Add proper error handling for invalid date formats in forms

## Current Issues
1. [ ] Fix HTMX error message rendering for invalid date formats
   - Ensure error messages appear in HTMX responses
   - Verify proper error message formatting in templates
   - Test with various invalid date formats

2. [ ] Add comprehensive date validation tests
   - Test past dates
   - Test dates more than 5 years in future
   - Test invalid date formats (e.g., 2023-13-32 99:99:99)
   - Test edge cases (leap years, month/day boundaries)
   - Test empty date fields
   - Test valid date formats

3. [ ] Improve error message handling in forms
   - Ensure consistent error message display across all forms
   - Verify error messages are properly formatted for display
   - Test error message propagation in both HTMX and non-HTMX responses

4. [ ] Update form validation to handle edge cases
   - Add specific validation for date fields
   - Ensure proper error messages for invalid inputs
   - Test validation with various edge cases

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

