# TODO List

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

## Specific Tasks
- [x] Fix HTMX handling in stipend update route (fixed status code and redirect behavior)
- [x] Update test for HTMX stipend update route
- [x] Verify HTMX stipend update route works with proper template rendering
- [x] Add explicit status code for HTMX responses
- [x] Add error handling for missing _stipend_row.html template
- [x] Create _stipend_row.html template with proper formatting
- [ ] Add more test coverage for HTMX routes
- [ ] Review other admin routes for similar HTMX issues
- [x] Fix redirect URL assertion in test_update_stipend_route
- [x] Investigate template rendering error in stipend update route
- [ ] Fix HTMX handling in stipend create route
- [ ] Update test for HTMX stipend create route
- [ ] Verify HTMX stipend create route works with proper template rendering

## Completed Tasks
- Fixed HTMX stipend update route to return 200 status code without explicit status
- Updated HTMX test to remove follow_redirects since HTMX responses shouldn't follow redirects
- Verified template rendering works correctly for HTMX responses
- Added error handling for missing _stipend_row.html template with fallback HTML

