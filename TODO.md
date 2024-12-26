# TODO List

## Things to remember about testing
- Ensure all tests pass
- When fixing HTMX routes, test both HTMX and non-HTMX cases
- Verify proper status codes (200 for success, 400 for errors)

## Things to remember about coding
- Keep HTMX and non-HTMX logic separate and explicit
- Add clear comments for HTMX-specific handling
- Use consistent status codes for API responses

## Specific Tasks
- [x] Fix HTMX handling in stipend update route (fixed status code and redirect behavior)
- [x] Update test for HTMX stipend update route
- [x] Verify HTMX stipend update route works with proper template rendering
- [ ] Add more test coverage for HTMX routes
- [ ] Review other admin routes for similar HTMX issues

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
