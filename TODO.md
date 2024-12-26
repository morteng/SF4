# TODO List

## Current Goals
1. Fix bot route error handling [COMPLETED]
   - Updated test_create_bot_route_with_invalid_data to expect 400 status code
   - Ensured error messages appear in HTMX responses
   - Verified template structure matches test expectations
   - Maintained consistent error container structure (#<field_name>-error)

2. Improve error handling consistency across all admin routes
   - Verify error message formatting in bot, organization, and tag routes
   - Ensure all routes use format_error_message() consistently
   - Add HTMX response handling for form errors in all routes
   - Update test coverage for error handling in all routes

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  * utils.py provides format_error_message() with error mapping for consistent error formatting
  * HTMX responses must include both error messages and field-specific errors
  * Form errors must be propagated to templates with proper status codes
  * Error messages must be rendered in specific HTML structure for testability
  * Key fixes needed:
    - Ensure error messages appear in HTMX responses
    - Verify template structure matches test expectations
    - Maintain consistent error container structure (#<field_name>-error)

- Bot Route Specifics:
  * Error handling needs to return 400 status code for invalid data
  * Form validation errors should be properly propagated
  * HTMX responses need proper error container structure
  * Error messages should match between client and server

## Implementation Details
1. For bot route error handling:
   - Update test to expect 400 status code for invalid data
   - Ensure bot_routes.py returns 400 status code for form validation errors
   - Verify error messages appear in HTMX responses
   - Check template structure in admin/bots/_create_form.html
   - Ensure field_errors are properly passed to template
   - Verify error message rendering in template

2. For general error handling:
   - Review all admin routes for consistent error handling
   - Ensure format_error_message() is used consistently
   - Add HTMX response handling for form errors
   - Update test coverage for error handling

