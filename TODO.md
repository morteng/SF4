# TODO List

## Current Goals
1. Implement comprehensive test coverage for all form validation
   - Add test cases for all validation scenarios in StipendForm, TagForm, UserForm, BotForm, and OrganizationForm
   - Verify error messages match expected values across all forms
   - Test both HTMX and regular form submissions for all forms
   - Test edge cases for all field types (dates, URLs, text lengths, etc.)

2. Document validation rules and error handling patterns
   - Add documentation for all form validation rules
   - Include examples of valid/invalid inputs for each field type
   - Document error message formats and handling patterns
   - Add to project documentation in PROJECT.md

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

- Form Validation Patterns:
  * All forms use consistent validation patterns
  * CustomDateTimeField handles all date/time validation cases
  * URL fields validate proper URL format and protocols
  * Text fields have consistent length validation
  * Unique field validation (username, email, etc.) implemented consistently

- Template Structure:
  * Error messages displayed in div with id="<field_name>-error"
  * Each error wrapped in div with class="error-message"
  * Flash messages displayed in #flash-messages container
  * Consistent styling using Tailwind CSS classes

## Implementation Details
1. For form error handling:
   - All forms properly validate their fields
   - Routes propagate errors correctly in HTMX responses
   - Template structure in _form.html is consistent across all forms
   - field_errors are properly passed to templates
   - Error message rendering in templates is consistent

2. For date validation:
   - StipendForm.validate_application_deadline() includes comprehensive validation
   - CustomDateTimeField handles all date/time validation cases
   - Error messages are properly formatted and displayed in template
   - HTMX responses handle validation errors correctly

## Specific Tasks
1. Add test coverage for all forms:
   - Create test files for each form type
   - Add test cases for all validation scenarios
   - Verify error messages match expected values
   - Test both HTMX and regular form submissions
   - Test edge cases for each field type

2. Document validation rules:
   - Create VALIDATION.md documentation file
   - Document validation rules for each field type
   - Include examples of valid/invalid inputs
   - Document error message formats
   - Add to project documentation in PROJECT.md

3. Review error handling consistency:
   - Verify consistent error handling across all forms
   - Ensure all forms use proper field types (CustomDateTimeField for dates, etc.)
   - Check error message formatting in all templates
   - Verify HTMX error handling in all routes

