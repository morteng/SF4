# TODO List

## Completed Tasks
- Implemented comprehensive validation and error handling system with HTMX support

## Current Goals
1. [ ] Standardize error handling across all admin forms
   - Create error_handler utility in utils.py to:
     - Format field-specific errors consistently
     - Handle HTMX responses with proper status codes
     - Map common validation errors to user-friendly messages
   - Implement in all admin routes:
     - Use error_handler in create/update endpoints
     - Ensure consistent error message formatting
     - Add proper error response templates
   - Add tests in test_utils.py:
     - Verify error message formatting
     - Test HTMX response handling
     - Check status code consistency

2. [ ] Enhance test coverage for edge cases
   - Add test cases for:
     - Invalid date formats (test_stipend_htmx.py)
     - Missing required fields (test_utils.py)
     - Boundary value testing (test_stipend_htmx.py)
   - Verify error message consistency:
     - Between client and server
     - Across different HTTP methods
     - In both HTML and JSON responses

## Knowledge & Memories
- Windows 11 environment - use cmd.exe for commands
- Error Handling Implementation:
  - utils.py provides format_error_message() for consistent error formatting
  - HTMX responses include both error messages and field-specific errors
  - Date field errors are handled with specific message mapping
  - Form errors are propagated to templates with proper status codes
- Validation System Details:
  - Client-side (main.js):
    - Real-time validation using regex: /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/
    - Component validation for date/time ranges
    - Error display in #date-error div with is-invalid class
  - Server-side (StipendForm):
    - Uses datetime.strptime with format '%Y-%m-%d %H:%M:%S'
    - Future date validation: datetime.now() comparison
    - Date range validation: 5 year maximum future date
- Testing Requirements:
  - Edge cases:
    - Leap years (2024-02-29)
    - Invalid month days (2023-04-31)
    - Invalid hours (24:00:00)
    - Missing time components
    - Past dates
    - Dates >5 years in future
  - Verification:
    - Client/server message consistency
    - Error styling in UI (is-invalid class)
    - Proper status codes (400 for failures)
    - Error message element presence (#application_deadline-error)
    - Form field focus after error display
    - Error message persistence across form submissions

