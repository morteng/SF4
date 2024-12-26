# TODO List

## Current Goals
1. [ ] Improve test coverage for stipend routes (currently 36%)
   - Add test cases in test_stipend_htmx.py for:
     * Successful stipend creation (test_create_stipend_success)
     * Missing required fields (test_create_stipend_missing_fields)
     * Boundary value testing (test_create_stipend_boundary_values)
     * HTMX response handling (test_create_stipend_htmx_response)
   - Verify error message consistency across all scenarios
   - Steps:
     a. Create new test functions in test_stipend_htmx.py
     b. Test both HTML and JSON responses
     c. Verify proper status codes (200, 400)
     d. Check error message formatting in responses

2. [ ] Standardize error handling across all admin forms
   - Create error_handler utility in utils.py to:
     * Format field-specific errors consistently
     * Handle HTMX responses with proper status codes
     * Map common validation errors to user-friendly messages
   - Implement in all admin routes:
     * Use error_handler in create/update endpoints
     * Ensure consistent error message formatting
     * Add proper error response templates
   - Add tests in test_utils.py:
     * Verify error message formatting (test_format_error_message)
     * Test HTMX response handling (test_error_handler_htmx)
     * Check status code consistency (test_error_handler_status_codes)
   - Steps:
     a. Create error_handler function in utils.py
     b. Update all admin routes to use error_handler
     c. Add test cases in test_utils.py
     d. Verify error handling in all admin forms

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  * utils.py provides format_error_message() for consistent error formatting
  * HTMX responses include both error messages and field-specific errors
  * Date field errors are handled with specific message mapping
  * Form errors are propagated to templates with proper status codes
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

