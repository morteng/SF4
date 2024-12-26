# TODO List

## Nice to know
You're running on a windows 11 machine, should format all commands for that environment.

## Things to remember about testing
- Ensure all tests pass
- When fixing HTMX routes, test both HTMX and non-HTMX cases
- Verify proper status codes (200 for success, 400 for errors)
- HTMX responses should not follow redirects
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
- [x] Fix test file path conflict in test_stipend_routes.py
  - [x] Remove duplicate test file at tests/routes/admin/test_stipend_routes.py
  - [x] Keep only tests/app/routes/admin/test_stipend_routes.py
  - [x] Remove __pycache__/.pyc files
  - [x] Verify pytest can collect tests correctly after cleanup
- [x] Fix SyntaxError in stipend_routes.py
  - [x] Identify invalid syntax around line 93
  - [x] Fix try/except block structure
  - [x] Verify tests pass after fix
- [ ] Fix HTMX stipend creation test failure
  - [x] Investigate 400 status code in test_create_stipend_route_htmx
  - [x] Verify template path handling in stipend_routes.py
  - [x] Check form validation and error handling
  - [x] Ensure proper database commit/rollback behavior
  - [x] Verify CSRF token handling in HTMX requests
  - [x] Test datetime field validation and formatting
  - [x] Added debug logging to verify template path and existence
  - [x] Confirmed template path is correct
  - [x] Fixed datetime validation in StipendForm
  - [ ] Verify error messages are properly displayed in templates
  - [ ] Test form re-rendering with validation errors

## Specific Tasks
- [x] Remove duplicate test file tests/routes/admin/test_stipend_routes.py
- [x] Verify all tests pass after cleanup
- [ ] Fix HTMX stipend creation functionality
  - [x] Update datetime validation in StipendForm
  - [ ] Verify template error message rendering
  - [ ] Add additional test cases for datetime validation

