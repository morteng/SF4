# TODO List

## Current Goals
1. Expand validation test coverage for edge cases
   - Add tests for timezone handling in date fields
   - Test form submission with mixed valid/invalid fields
   - Verify error message persistence across HTMX partial updates

2. Improve validation documentation
   - Add validation flow diagrams to VALIDATION.md
   - Document error message localization requirements
   - Add API documentation for validation endpoints

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  * utils.py format_error_message() handles date/time validation edge cases
  * HTMX responses require specific error message structure for client-side handling
  * Form templates use consistent error container IDs (#<field_name>-error)
  * Key validation patterns implemented:
    - Date/time validation with CustomDateTimeField
    - URL validation with protocol enforcement
    - Length validation with character counting
    - Unique field validation with database checks

- Template Structure:
  * Error messages use Tailwind CSS classes for consistent styling
  * Field-specific errors appear below each input
  * Flash messages appear in #flash-messages container
  * HTMX responses maintain form state during validation

## Implementation Details
1. Validation Patterns:
   - All forms use CustomDateTimeField for date/time fields
   - URL fields validate protocol and format
   - Text fields enforce length limits
   - Unique fields perform database checks

2. Error Handling:
   - format_error_message() in utils.py standardizes error messages
   - Templates render errors in consistent structure
   - HTMX responses include both field errors and flash messages
   - Date validation handles edge cases (leap years, timezones, etc.)

## Specific Tasks
1. Enhance date/time validation:
   - Add timezone support to CustomDateTimeField
   - Implement daylight saving time handling
   - Add tests for international date formats

2. Improve validation documentation:
   - Add validation flow diagrams to VALIDATION.md
   - Document error message localization requirements
   - Add API documentation for validation endpoints

3. Optimize validation performance:
   - Implement caching for repeated validation checks
   - Add rate limiting for form submissions
   - Optimize database queries during validation

