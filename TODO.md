# TODO List

## Current Goals
1. Complete organization routes implementation
   - Ensure consistent error display across all organization views
   - Implement proper error handling for organization operations
   - Add timezone handling for application deadlines

2. Enhance test coverage for organization routes
   - Add tests for HTMX responses in organization routes
   - Add integration tests for organization service interactions
   - Add tests for timezone conversion functionality

## Knowledge & Memories
- Organization model now includes application_deadline field with timezone support
- Timezone handling must be implemented in both forms and routes
- Application deadlines should be stored in UTC but displayed in user's local timezone
- Use pytz for timezone conversions
- Add validation to ensure application deadlines are in the future
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
- Fixed database error handling in organization edit route to properly set flash messages
- Updated organization form validation tests to expect field-specific error messages
- Fixed test_timezone_handling by adding missing application_deadline field

