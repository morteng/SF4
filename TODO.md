# TODO List

## Completed Tasks
- Implemented comprehensive date validation with client/server sync and error handling
- Added client-side date validation in main.js
- Enhanced test coverage in test_stipend_htmx.py
- Improved error handling in stipend routes and forms

## Current Goals
1. [ ] Standardize error handling in utils.py
   - Create format_error_message() function
   - Handle field-specific error formatting
   - Support HTMX error response structure
   - Add error message localization stubs
   - File: app/utils.py

## Knowledge & Memories
- Windows 11 environment - use cmd.exe for commands
- Current validation handles:
  - Format: YYYY-MM-DD HH:MM:SS
  - Date ranges: month 1-12, day 1-31
  - Time ranges: hour 0-23, minute 0-59, second 0-59
  - Future dates only (not in past)
  - Dates within 5 years
- Error handling specifics:
  - Field-specific messages in #date-error div
  - is-invalid class for styling
  - 400 status code for validation failures
  - HTMX-compatible error responses
  - Date field errors are handled separately for clearer messages
- Testing requirements:
  - Must test all edge cases including:
    - Leap years (2024-02-29)
    - Invalid month days (2023-04-31)
    - Invalid hours (24:00:00)
    - Missing time components
    - Past dates
    - Dates too far in future
  - Verify client/server message consistency
  - Check error styling in UI
  - Validate proper status codes
- Implementation details:
  - Client-side validation in main.js uses regex and component validation
  - Server-side validation in StipendForm uses datetime.strptime
  - Error messages are propagated through flash messages
  - Tests verify both error messages and UI state (is-invalid class)

