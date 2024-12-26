# TODO List

## Current Goals
1. Enhance date/time validation edge cases
   - Add specific tests for leap years in tests/test_utils.py
   - Handle timezone transitions more gracefully in app/forms/fields.py
   - Add validation for historical dates (pre-1900) in CustomDateTimeField

2. Improve error message consistency
   - Standardize error message format across all forms using format_error_message()
   - Add more specific error messages for edge cases in app/utils.py
   - Ensure consistent error display in both full page and HTMX responses

3. Expand test coverage
   - Add tests for historical date validation in tests/test_utils.py
   - Create integration tests for timezone conversion scenarios
   - Add edge case tests for daylight saving time transitions

## Knowledge & Memories
- Current validation implementation:
  * CustomDateTimeField handles date/time parsing and validation with timezone support
  * format_error_message() in app/utils.py standardizes error display with specific error mapping
  * All forms use consistent validation patterns with detailed error messages
  * Error messages are displayed using Tailwind CSS classes

- Key validation patterns:
  * Date/time fields use CustomDateTimeField with strict format validation and timezone handling
  * URL fields enforce protocol (http/https) and format
  * Text fields have length limits enforced with specific error messages
  * Unique fields perform database checks for duplicates with custom error messages
  * UserForm requires an id field for edit operations

- Error handling details:
  * Errors are displayed below each field with consistent styling using format_error_message()
  * Flash messages appear in #flash-messages container with standardized formatting
  * HTMX responses maintain form state during validation with consistent error display
  * Date validation handles edge cases (leap years, timezones, etc.) with specific error messages

- Timezone handling:
  * Uses pytz for timezone management in app/forms/fields.py
  * Stores all dates in UTC but can display in user's timezone
  * Handles daylight saving time transitions with specific error messages

## Implementation Tasks
1. Date/time validation enhancements:
   - Add leap year validation to CustomDateTimeField._validate_date_components()
   - Add historical date validation (pre-1900) with specific error message
   - Improve daylight saving time transition handling in process_formdata()

2. Error message improvements:
   - Add more specific error messages for edge cases in format_error_message()
   - Standardize error message format across all forms using the error_map
   - Ensure consistent error display in both full page and HTMX responses

3. Test coverage expansion:
   - Add tests for historical date validation in tests/test_utils.py
   - Create integration tests for timezone conversion scenarios
   - Add edge case tests for daylight saving time transitions

## Recent Fixes
- Added id field to UserForm to fix template rendering error in admin user edit route

