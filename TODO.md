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

## Things to remember about coding
- Keep HTMX and non-HTMX logic separate and explicit
- Add clear comments for HTMX-specific handling
- Use consistent status codes for API responses
- HTMX responses should return the partial template directly
- Ensure proper error handling and rollback for database operations
- Validate all form inputs before processing
- Use proper template paths for HTMX responses
- Maintain consistent flash message handling

## Current Issues
- [x] Fix test file path conflict in test_stipend_routes.py
  - [x] Remove duplicate test file at tests/routes/admin/test_stipend_routes.py
  - [x] Keep only tests/app/routes/admin/test_stipend_routes.py
  - [x] Remove __pycache__/.pyc files
  - [x] Verify pytest can collect tests correctly after cleanup
- [x] Fix SyntaxError in stipend_routes.py
  - [x] Identify invalid syntax around line 93
  - [x] Fix try/except block structure
  - [ ] Verify tests pass after fix
- [ ] Fix HTMX stipend creation test failure
  - [ ] Investigate 400 status code in test_create_stipend_route_htmx
  - [ ] Verify template path handling in stipend_routes.py
  - [ ] Check form validation and error handling
  - [ ] Ensure proper database commit/rollback behavior

## Specific Tasks
- [x] Remove duplicate test file tests/routes/admin/test_stipend_routes.py
- [x] Verify all tests pass after cleanup
- [ ] Fix HTMX stipend creation functionality

