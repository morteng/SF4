# TODO List

## Current Goals
1. Ensure comprehensive test coverage for stipend form validation
   - Add test cases for all date validation scenarios in StipendForm
   - Verify error messages match expected values
   - Test both HTMX and regular form submissions
   - Test edge cases (leap years, month/day combinations)

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  * utils.py provides format_error_message() with error mapping for consistent error formatting
  * HTMX responses must include both error messages and field-specific errors
  * Form errors must be propagated to templates with proper status codes
  * Error messages must be rendered in specific HTML structure for testability
  * Key fixes implemented:
    - Error messages appear in HTMX responses
    - Template structure matches test expectations
    - Comprehensive date validation with edge case handling
    - Consistent error container structure (#<field_name>-error)

- Stipend Route Specifics:
  * Error handling returns 400 status code for invalid data
  * Form validation errors are properly propagated
  * HTMX responses have proper error container structure
  * Error messages match between client and server

## Implementation Details
1. For stipend route error handling:
   - StipendForm in admin_forms.py properly validates application_deadline
   - stipend_routes.py propagates errors correctly in HTMX responses
   - Template structure in admin/stipends/_form.html is correct
   - field_errors are properly passed to template
   - Error message rendering in template is consistent

## New Memories
- Completed implementation of application deadline validation
- CustomDateTimeField handles all date/time validation cases
- StipendForm.validate_application_deadline() includes comprehensive validation
- Error messages are properly formatted and displayed in template
- HTMX responses handle validation errors correctly

## Specific Tasks
1. Add comprehensive test coverage:
   - Add test cases for all date validation scenarios
   - Verify error messages match expected values
   - Test both HTMX and regular form submissions
   - Test edge cases (leap years, month/day combinations)
   - Test future date validation (must be future but not more than 5 years)
   - Test time component validation (hours, minutes, seconds)
   - Test invalid date combinations (e.g., Feb 30)

2. Document validation rules:
   - Add documentation for date/time validation rules
   - Include examples of valid/invalid dates
   - Document error message formats
   - Add to project documentation in PROJECT.md

3. Review error handling consistency:
   - Verify consistent error handling across all forms
   - Ensure all forms use CustomDateTimeField for date fields
   - Check error message formatting in all templates
   - Verify HTMX error handling in all routes

