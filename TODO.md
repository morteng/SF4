# TODO List

## Current Goals
1. **Template Improvements**
   - [x] Verify all admin templates extend base.html
   - [ ] Add template inheritance tests
   - [ ] Verify proper error handling in all admin templates

2. **Form Validation Improvements**
   - [ ] Add validation for bot status field
   - [ ] Improve error message consistency
   - [ ] Add validation for bot description length

## New Goals
1. **Improve Test Coverage**
   - Add more test cases for bot routes
   - Verify error handling for all admin routes
   - Test edge cases for form validation
   - Add tests for template rendering

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

