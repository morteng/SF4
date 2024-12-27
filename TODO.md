# TODO List

## Current Goals
1. **Complete Admin System Refactoring**
   - [x] Fix bot route URL building issues
   - [ ] Implement caching for frequently accessed data
   - [ ] Add bulk actions (delete, update) for stipends, tags, and organizations
   - [ ] Add search and filtering functionality to index pages
   - [ ] Add export functionality (CSV, Excel) for all admin data
   - [ ] Implement audit logging for admin actions

## Knowledge & Memories
- **Form Validation**
  * Always return 400 status code for invalid form submissions
  * Ensure form errors are properly flashed to the user
  * Log form validation errors for debugging
  * Use consistent error message formatting
  * Test both valid and invalid form submissions
  * Verify status codes in route tests
  * Check for proper error handling in templates
  * Invalid form submissions should:
    - Return 400 status code
    - Display field-specific error messages
    - Log validation errors
    - Preserve form state
    - Use consistent error message formatting

- **Testing Best Practices**
  * Use fixtures for common test setup
  * Verify template rendering in route tests
  * Check for proper error handling
  * Test both success and failure cases
  * When testing forms, always include CSRF token
  * Use constants for flash messages to ensure consistency
  * Add tests for invalid form submissions
  * Verify status codes match expected values
  * Test edge cases for form validation
  * Verify proper error handling for database errors

## New Goals
1. **Improve Test Coverage**
   - Add more test cases for bot routes
   - Verify error handling for all admin routes
   - Test edge cases for form validation
   - Add tests for template rendering

