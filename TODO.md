# TODO List

## Completed Tasks
- Implemented comprehensive date validation system with client/server sync, error handling, and test coverage

## Current Goals
1. [ ] Standardize error handling in utils.py
   - Create format_error_message() function in app/utils.py
   - Implement field-specific formatting:
     - Date fields: Use raw error message
     - Other fields: Format as "Field Label: Error"
   - Add HTMX response support:
     - Include error messages in response.data
     - Maintain 400 status code for validation failures
   - Add error message localization stubs for future i18n support

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

