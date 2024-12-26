# TODO List

## Current Goals
1. Improve error handling consistency across all admin routes
   - Verify error message formatting in bot, organization, and tag routes
   - Ensure all routes use format_error_message() consistently
   - Add HTMX response handling for form errors in all routes
   - Update test coverage for error handling in all routes

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  * utils.py provides format_error_message() with error mapping for consistent error formatting
  * HTMX responses must include both error messages and field-specific errors
  * Date field errors require specific message mapping
  * Form errors must be propagated to templates with proper status codes
  * Error messages must be rendered in specific HTML structure for testability
  * Key fixes needed:
    - Ensure error messages appear in HTMX responses
    - Verify template structure matches test expectations
    - Maintain consistent error container structure (#<field_name>-error)

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  * utils.py provides format_error_message() with error mapping for consistent error formatting
  * HTMX responses must include both error messages and field-specific errors
  * Date field errors require specific message mapping
  * Form errors must be propagated to templates with proper status codes
  * Error messages must be rendered in specific HTML structure for testability
  * Key fixes needed:
    - Ensure error messages appear in HTMX responses
    - Verify template structure matches test expectations
    - Maintain consistent error container structure (#<field_name>-error)
- Validation System Details:
  * Client-side (main.js):
    - Real-time validation using regex: /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/
    - Component validation for date/time ranges
    - Error display in #date-error div with is-invalid class
  * Server-side (StipendForm):
    - Handles both string and datetime inputs
    - Uses datetime.strptime with format '%Y-%m-%d %H:%M:%S' for string inputs
    - Comprehensive validation including:
      * Date component validation (year, month, day, hour, minute, second)
      * Future date validation: datetime.now() comparison
      * Date range validation: 5 year maximum future date
    - Specific error messages for:
      * Invalid date format
      * Invalid date values
      * Invalid time values
      * Missing time components
      * Past dates
      * Dates >5 years in future
- Testing Requirements:
  * Edge cases:
    - Leap years (2024-02-29)
    - Invalid month days (2023-04-31)
    - Invalid hours (24:00:00)
    - Missing time components
    - Past dates
    - Dates >5 years in future
  * Verification:
    - Client/server message consistency
    - Error styling in UI (is-invalid class)
    - Proper status codes (400 for failures)
    - Error message element presence (#<field_name>-error)
    - Form field focus after error display
    - Error message persistence across form submissions
    - Verify error messages appear in correct HTML structure
    - Specific test assertions for:
      * Error message content
      * Error container presence
      * Field error classes
      * Response status codes
- Current Issues:
  * test_create_stipend_with_invalid_application_deadline failing
    - Error messages not appearing in HTMX responses
    - Need to verify template structure in _form.html
    - Ensure field_errors are properly passed to template
    - Check format_error_message() implementation in utils.py
    - Verify error message rendering in template

