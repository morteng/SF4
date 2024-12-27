# TODO List

## Current Goals
1. **Template Improvements**
   - [ ] Add template inheritance tests
   - [ ] Verify proper error handling in all admin templates

2. **Form Validation Improvements**
   - [ ] Add validation for bot status field
   - [ ] Improve error message consistency
   - [ ] Add validation for bot description length

## Knowledge & Memories
- **Template Structure**
  * Admin templates must extend base.html directly
  * Use consistent block names (content for all pages)
  * Include admin/_sidebar.html in all admin pages
  * Use proper form error handling with invalid-feedback class
  * Admin templates should use flex layout with fixed sidebar width
  * Main content area should be flexible to fill remaining space

- **Testing Best Practices**
  * Verify template inheritance chain in tests
  * Check for proper error handling in templates
  * Test both success and failure cases
  * When testing forms, always include CSRF token
  * Use constants for flash messages to ensure consistency
  * Test template rendering for all admin routes
  * Verify proper error handling for database errors

- **Testing Best Practices**
  * Verify template inheritance chain in tests
  * Check for proper error handling in templates
  * Test both success and failure cases
  * When testing forms, always include CSRF token
  * Use constants for flash messages to ensure consistency

2. **Form Validation Improvements**
   - [ ] Add validation for bot status field
   - [ ] Improve error message consistency
   - [ ] Add validation for bot description length

## Knowledge & Memories
- **Form Validation**
  * Always return 400 status code for invalid form submissions
  * Ensure form errors are properly flashed to the user
  * Log form validation errors for debugging
  * Use consistent error message formatting
  * Test both valid and invalid form submissions
  * Verify status codes in route tests
  * Check for proper error handling in templates

- **Testing Best Practices**
  * Use fixtures for common test setup
  * Verify template rendering in route tests
  * Check for proper error handling
  * Test both success and failure cases
  * When testing forms, always include CSRF token
  * Use constants for flash messages to ensure consistency

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

1. **Template Improvements**
   - [ ] Create consistent admin template structure
   - [ ] Add template inheritance tests
   - [ ] Verify all admin templates extend base.html

## New Goals
1. **Improve Test Coverage**
   - Add more test cases for bot routes
   - Verify error handling for all admin routes
   - Test edge cases for form validation
   - Add tests for template rendering

