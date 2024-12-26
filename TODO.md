# TODO List

## Completed Tasks
- Implemented comprehensive validation and error handling system with HTMX support
- Added test cases for invalid date formats in test_stipend_htmx.py

## Current Goals
1. [ ] Fix error message rendering in stipend routes
   - Ensure error messages are properly passed to templates
   - Verify error messages appear in correct HTML structure
   - Update tests to check for error messages in rendered HTML

2. [ ] Improve test coverage for stipend routes (currently 36%)
   - Add test cases for:
     - Successful stipend creation
     - Missing required fields
     - Boundary value testing
     - HTMX response handling
   - Verify error message consistency across all scenarios

3. [ ] Standardize error handling across all admin forms
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

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  - utils.py provides format_error_message() for consistent error formatting
  - HTMX responses include both error messages and field-specific errors
  - Date field errors are handled with specific message mapping
  - Form errors are propagated to templates with proper status codes
- Current Issues:
  - Error messages not appearing in response data as expected
  - Tests need to check for error messages in HTML structure
  - Stipend route coverage needs improvement (36%)
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

