# TODO List

## Current Goals
1. **Template Improvements**
   - [ ] Add template inheritance tests
   - [ ] Verify proper error handling in all admin templates

2. **Form Validation Improvements**
   - [ ] Improve error message consistency
   - [ ] Add validation for bot description length

3. **Testing Improvements**
   - Add more test cases for organization routes
   - Verify error handling for all admin routes
   - Test edge cases for form validation
   - Add tests for template rendering

## New Goals
1. **Organization Route Testing**
   - Add tests for invalid form submissions
   - Test database error handling
   - Verify proper error message display

## Knowledge & Memories
- **Template Structure**
  * Admin templates must extend base.html directly
  * Use consistent block names (content for all pages)
  * Include _sidebar.html in all admin pages
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

