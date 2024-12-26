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
- [ ] Add more test coverage for HTMX routes
- [ ] Review other admin routes for similar HTMX issues

## Completed Tasks
- Fixed HTMX stipend update route to return 200 status code without explicit status
- Updated HTMX test to remove follow_redirects since HTMX responses shouldn't follow redirects
- Verified template rendering works correctly for HTMX responses

