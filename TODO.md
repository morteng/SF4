# TODO List

## Completed Tasks
- Implemented comprehensive date validation system with client/server sync, error handling, and test coverage
- Added standardized error handling in utils.py with format_error_message() function
- Implemented HTMX-compatible error responses for form submissions

## Current Goals
1. [ ] Enhance error handling for all admin forms
   - Apply consistent error message formatting across all CRUD operations
   - Ensure proper error propagation for HTMX responses
   - Add field-specific error handling for all form fields
2. [ ] Improve test coverage for error scenarios
   - Add tests for edge cases in all form validations
   - Verify error message consistency across client/server
   - Test error handling for all HTTP methods (GET, POST, PUT, DELETE)

## Knowledge & Memories
- Windows 11 environment - use cmd.exe for commands
- Validation System Details:
  - Client-side (main.js):
    - Real-time validation using regex: /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/
    - Component validation for date/time ranges
    - Error display in #date-error div with is-invalid class
  - Server-side (StipendForm):
    - Uses datetime.strptime with format '%Y-%m-%d %H:%M:%S'
    - Future date validation: datetime.now() comparison
    - Date range validation: 5 year maximum future date
  - Error Handling:
    - Field-specific messages in #date-error div
    - is-invalid class for styling invalid inputs
    - 400 status code for all validation failures
    - HTMX-compatible error responses
    - Date field errors handled separately for clarity
    - Error message mapping for common validation scenarios
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
- Error Handling Implementation:
  - utils.py provides format_error_message() for consistent error formatting
  - HTMX responses include both error messages and field-specific errors
  - Date field errors are handled with specific message mapping
  - Form errors are propagated to templates with proper status codes

