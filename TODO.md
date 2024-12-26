# TODO List

## Nice to know
You're running on a windows 11 machine, should format all commands for that environment.

## Things to remember about testing
- Ensure all tests pass
- When fixing HTMX routes, test both HTMX and non-HTMX cases
- Verify proper status codes (200 for success, 400 for errors)
- HTMX responses should not follow redirects

## Things to remember about coding
- Keep HTMX and non-HTMX logic separate and explicit
- Add clear comments for HTMX-specific handling
- Use consistent status codes for API responses
- HTMX responses should return the partial template directly

## Current Issues
- [x] Fix test file path conflict in test_stipend_routes.py
  - [x] Remove duplicate test file at tests/routes/admin/test_stipend_routes.py
  - [x] Keep only tests/app/routes/admin/test_stipend_routes.py
  - [x] Remove __pycache__/.pyc files
  - [x] Verify pytest can collect tests correctly after cleanup

## Specific Tasks
- [x] Remove duplicate test file tests/routes/admin/test_stipend_routes.py
- [x] Verify all tests pass after cleanup

