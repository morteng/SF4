# TODO List

## Current Goals
1. Complete date/time validation implementation
   - Add comprehensive tests for all date/time validation scenarios
   - Ensure consistent error messages across all date/time fields

2. Enhance test coverage for stipend routes
   - Add tests for HTMX responses in stipend routes
   - Add integration tests for stipend service interactions

## Knowledge & Memories
- CustomDateTimeField validation rules:
  * Uses strptime for format validation
  * Validates individual date/time components
  * Handles timezone conversion
  * Provides specific error messages for different validation failures
  * Error messages must match test expectations exactly

- Organization model includes basic fields: name, description, homepage_url
- When handling database errors:
  * Always set flash message before redirect
  * Rollback database session
  * Redirect back to edit page to preserve form state
  * Use consistent error message format from FLASH_MESSAGES
- Organization routes implementation details:
  * Uses consistent CRUD pattern with admin. prefix
  * Supports both full page and HTMX responses
  * Uses format_error_message() for consistent error display
  * Follows Flask-Login and admin_required decorator patterns
  * Template structure:
    * Main templates in admin/organizations/ directory must extend admin/layout.html
    * admin/layout.html extends base.html
    * HTMX partial templates should use _ prefix
    * Follows consistent naming conventions (index.html, create.html, edit.html)
    * Template paths must match route references exactly

- Error handling patterns:
  * Errors are displayed below each field with consistent styling
  * Flash messages appear in #flash-messages container
  * HTMX responses maintain form state during validation
  * Database errors are caught and handled gracefully
  * Invalid form submissions should return 302 redirects
  * Database errors during updates should redirect back to edit page with flash message

## Implementation Tasks
1. Organization routes improvements:
   - Implement proper error handling for organization operations
   - Add validation tests for organization forms
   - Ensure consistent error display across all organization views

2. Test coverage expansion:
   - Add tests for HTMX responses in organization routes
   - Create edge case tests for organization operations
   - Add integration tests for organization service interactions

## Recent Fixes
- Removed application_deadline field and related timezone handling code
- Updated Organization model and form to remove deadline-related fields
- Updated organization tests to remove deadline-related test cases
- Fixed database error handling in organization edit route to properly set flash messages and redirect
- Updated organization form validation tests to expect field-specific error messages
- Improved error message formatting in organization edit route to use field labels
- Fixed database error handling to properly redirect back to edit page with flash message
- Fixed test_update_organization_with_database_error by ensuring proper flash message is set
  * Now properly sets flash message before redirect
  * Maintains form state during database errors
  * Follows consistent error handling pattern
  * Ensures database session is rolled back on error
  * Preserves form state during error handling

