# TODO List

## Current Goals
1. Fixed application deadline validation error handling in stipend routes
   - Error messages are properly propagated to HTMX responses
   - Template structure matches test expectations
   - Comprehensive date validation with edge case handling implemented
   - Test coverage for date validation edge cases complete

## Knowledge & Memories
- Windows 11 environment
- Error Handling Implementation:
  * utils.py provides format_error_message() with error mapping for consistent error formatting
  * HTMX responses must include both error messages and field-specific errors
  * Form errors must be propagated to templates with proper status codes
  * Error messages must be rendered in specific HTML structure for testability
  * Key fixes needed:
    - Ensure error messages appear in HTMX responses
    - Verify template structure matches test expectations
    - Maintain consistent error container structure (#<field_name>-error)

- Stipend Route Specifics:
  * Error handling needs to return 400 status code for invalid data
  * Form validation errors should be properly propagated
  * HTMX responses need proper error container structure
  * Error messages should match between client and server

## Implementation Details
1. For stipend route error handling:
   - Update StipendForm in admin_forms.py to properly validate application_deadline
   - Ensure stipend_routes.py propagates errors correctly in HTMX responses
   - Verify template structure in admin/stipends/_form.html
   - Ensure field_errors are properly passed to template
   - Verify error message rendering in template

## New Memories
- Discovered failing test for invalid application deadlines
- Need to ensure error messages appear in HTMX responses
- Current implementation in stipend_routes.py needs to properly propagate errors
- Test expects specific error messages for invalid dates/times
- Form validation needs to handle both string and datetime inputs

## Specific Tasks
1. Fix application deadline validation in StipendForm:
   - Add comprehensive validation for date components (month, day, year)
   - Add validation for time components (hour, minute, second)
   - Add validation for future date requirement
   - Add validation for maximum future date (5 years)
   - Ensure consistent error messages across all validation cases

2. Update stipend_routes.py error handling:
   - Ensure field_errors are properly passed to the template
   - Verify error messages are included in HTMX responses
   - Maintain consistent error container structure (#<field_name>-error)
   - Ensure proper status codes (400) for validation errors

3. Update template error rendering:
   - Verify error container structure matches test expectations
   - Ensure error messages are properly displayed for each field
   - Maintain consistent styling for error messages

4. Add comprehensive test coverage:
   - Add test cases for all date validation scenarios
   - Verify error messages match expected values
   - Test both HTMX and regular form submissions
   - Test edge cases (leap years, month/day combinations)

