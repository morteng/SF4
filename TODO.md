# TODO List

## Current Goals
1. [ ] Fix HTMX error handling in stipend routes
   - Update stipend_routes.py to properly propagate errors in HTMX responses
   - Ensure error messages are included in the response data
   - Add proper error container structure in templates
   - Steps:
     a. Modify create route to include field-specific errors
     b. Update _form.html template with error containers
     c. Ensure consistent error message formatting
     d. Verify error messages appear in correct HTML structure

2. [ ] Improve date validation consistency
   - Update validate_application_deadline in admin_forms.py
   - Add proper error handling for invalid date formats
   - Ensure consistent error messages across client and server
   - Steps:
     a. Add try-catch block for date parsing
     b. Standardize error messages
     c. Verify error handling for all edge cases
     d. Update tests to match new error messages

3. [ ] Update test_stipend_htmx.py
   - Modify tests to look for errors in correct locations
   - Add assertions for error container presence
   - Verify error message content matches expected format
   - Steps:
     a. Update test assertions to check specific error containers
     b. Add checks for error message formatting
     c. Verify status codes for different error cases
     d. Ensure tests match the updated error handling implementation

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  * utils.py provides format_error_message() for consistent error formatting
  * HTMX responses must include both error messages and field-specific errors
  * Date field errors require specific message mapping
  * Form errors must be propagated to templates with proper status codes
  * Error messages must be rendered in specific HTML structure for testability
- Validation System Details:
  * Client-side (main.js):
    - Real-time validation using regex: /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/
    - Component validation for date/time ranges
    - Error display in #date-error div with is-invalid class
  * Server-side (StipendForm):
    - Uses datetime.strptime with format '%Y-%m-%d %H:%M:%S'
    - Future date validation: datetime.now() comparison
    - Date range validation: 5 year maximum future date
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
- New Learnings:
  * HTMX responses must include error messages in the response data
  * Error containers must have consistent IDs for testability
  * Form validation errors must be properly propagated to templates
  * Date validation requires specific error handling for different cases
  * Tests must check for errors in specific HTML containers

