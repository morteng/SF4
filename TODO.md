# TODO List

## Current Goals
1. Fix application deadline validation error handling in stipend routes
   - Ensure error messages are properly propagated to HTMX responses
   - Verify template structure matches test expectations
   - Add comprehensive date validation with edge case handling
   - Update test coverage for date validation edge cases

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

- Stipend Route Specifics:
  * Error handling needs to return 400 status code for invalid data
  * Form validation errors should be properly propagated
  * HTMX responses need proper error container structure
  * Error messages should match between client and server

## Implementation Details
1. For stipend route error handling:
   - Update StipendForm in admin_forms.py to properly validate application_deadline
   - Ensure stipend_routes.py propagates errors correctly in HTMX responses
   - Verify template structure in admin/stipends/_form.html
   - Ensure field_errors are properly passed to template
   - Verify error message rendering in template

2. For general error handling:
   - Review all admin routes for consistent error handling
   - Ensure format_error_message() is used consistently
   - Add HTMX response handling for form errors
   - Update test coverage for error handling

## New Memories
- Discovered failing test for invalid application deadlines
- Need to ensure error messages appear in HTMX responses
- Current implementation in stipend_routes.py needs to properly propagate errors
- Test expects specific error messages for invalid dates/times
- Form validation needs to handle both string and datetime inputs

