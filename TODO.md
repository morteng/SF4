# TODO List

## Current Goals
1. [x] Add comprehensive test coverage for all form fields
   - Created test cases in test_stipend_htmx.py for:
     * Required field validation (name, summary, description)
     * Field length validation (max 100 chars for name, max 500 for summary)
     * URL format validation (homepage_url, application_procedure)
     * HTML escaping of user input
   - Implemented:
     a. Test cases for each form field with invalid data
     b. Error message consistency across all fields
     c. Field-specific error styling matching application_deadline pattern
     d. Error containers with unique IDs following pattern: <field_name>-error

2. [ ] Verify error handling consistency across all admin routes
   - Check error handling in:
     * Organization routes
     * Tag routes
     * User routes
     * Bot routes
   - Steps:
     a. Review each route's error handling pattern
     b. Ensure consistent use of format_error_message()
     c. Verify proper error container IDs in templates
     d. Check for consistent status code usage (400 for validation errors)

## New Knowledge
- Date validation error handling improvements:
  * Added specific error messages for invalid dates, times, and formats
  * Implemented future date validation with 5-year maximum
  * Added time component validation
  * Improved error message consistency between client and server
- Error propagation:
  * Ensured errors are properly flashed and rendered in templates
  * Added specific error containers for each field
  * Implemented consistent error styling with is-invalid class
- Test improvements:
  * Added assertions for error container presence
  * Verified error message content matches expected format
  * Ensured tests match the updated error handling implementation

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  * utils.py provides format_error_message() for consistent error formatting
  * HTMX responses include both error messages and field-specific errors
  * Date field errors are handled with specific message mapping
  * Form errors are propagated to templates with proper status codes
  * Error messages now rendered in specific HTML structure for better testability
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

