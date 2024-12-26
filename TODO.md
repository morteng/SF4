# TODO List

## Current Goals
1. [ ] Fix date validation error handling in stipend routes
   - Update error message handling in stipend_routes.py
   - Ensure proper error message passing to templates
   - Verify error message rendering in HTML response
   - Steps:
     a. Modify date error handling in create route
     b. Update form template to display errors correctly
     c. Add test cases for all date validation scenarios

2. [ ] Improve error handling test coverage
   - Add test cases in test_stipend_htmx.py for:
     * All date validation edge cases
     * Error message rendering location
     * Field-specific error styling
   - Steps:
     a. Add test cases for invalid dates/times
     b. Verify error message presence in response
     c. Check for proper error styling in HTML

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
    - Error message element presence (#application_deadline-error)
    - Form field focus after error display
    - Error message persistence across form submissions
    - Verify error messages appear in correct HTML structure
- Current Issues:
  * Date validation errors not appearing in response
  * Error messages not being passed to template correctly
  * Test assertions failing due to missing error messages

