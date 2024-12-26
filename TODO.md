# TODO List

## Current Goals
1. Implement comprehensive timezone handling
   - Add timezone selection to CustomDateTimeField in app/forms/fields.py
   - Store all dates in UTC but display in user's timezone
   - Handle daylight saving time transitions in date validation

2. Enhance validation error handling
   - Add specific error messages for each validation failure case
   - Standardize error message format across all forms
   - Ensure consistent error display in both full page and HTMX responses

3. Improve test coverage
   - Add tests for timezone handling in tests/test_utils.py
   - Create integration tests for form validation scenarios
   - Add edge case tests for date/time validation

## Knowledge & Memories
- Current validation implementation:
  * CustomDateTimeField handles date/time parsing and validation
  * format_error_message() in app/utils.py standardizes error display
  * All forms use consistent validation patterns
  * Error messages are displayed using Tailwind CSS classes

- Key validation patterns:
  * Date/time fields use CustomDateTimeField with strict format validation
  * URL fields enforce protocol (http/https) and format
  * Text fields have length limits enforced
  * Unique fields perform database checks for duplicates

- Error handling details:
  * Errors are displayed below each field with consistent styling
  * Flash messages appear in #flash-messages container
  * HTMX responses maintain form state during validation
  * Date validation handles edge cases (leap years, timezones, etc.)

## Implementation Tasks
1. Timezone handling:
   - Add timezone selection dropdown to forms
   - Modify CustomDateTimeField to handle timezone conversion
   - Update date validation to account for timezone differences

2. Error message standardization:
   - Create error message templates in app/utils.py
   - Ensure consistent error message format across all forms
   - Add support for localized error messages

3. Test coverage expansion:
   - Add timezone handling tests to tests/test_utils.py
   - Create form validation integration tests
   - Add edge case tests for date/time validation

