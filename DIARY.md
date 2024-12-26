# Project Diary
A log of interesting things tought, learned, discovered, and done.

### Day 1
- Learned about the project and its goals, started this project diary.

### Day 2
- Fixed error message rendering in stipend routes:
  * Updated error handling in stipend_routes.py to properly pass field-specific errors
  * Enhanced format_error_message in utils.py for consistent error formatting
  * Modified test_stipend_htmx.py to check for error messages in correct HTML structure
- Improved test coverage for date validation edge cases

### Day 3
- Completed error handling improvements for stipend routes:
  * Implemented consistent error message formatting using format_error_message utility
  * Added field-specific error rendering in templates
  * Updated tests to verify error handling behavior
  * Ensured proper HTMX response handling for error cases
- Key learnings:
  * Error messages should be rendered in specific HTML structure for testability
  * Field labels should be used in error messages for better UX
  * HTMX responses need proper status codes and error handling

### Day 4
- Fixed date validation error handling issues:
  * Standardized error handling using format_error_message utility
  * Improved date validation error messages in utils.py
  * Updated test_stipend_htmx.py with specific error location checks
  * Ensured error messages appear in correct HTML structure
- Key learnings:
  * Specific error containers are crucial for reliable testing
  * Consistent error message formatting improves maintainability
  * Detailed test assertions help catch rendering issues

### Day 5
- Completed date validation error handling fixes:
  * Removed duplicate validate_application_deadline method
  * Enhanced error propagation in stipend_routes.py
  * Updated test assertions to be more specific about error locations
  * Improved error message formatting in utils.py
- Key learnings:
  * Error messages must match exactly between client and server
  * Template structure must align with test expectations
  * Field-specific error containers improve test reliability

### Day 6
- Completed template error rendering verification:
  * Added specific error container div with id="application_deadline-error"
  * Implemented support for both field_errors and form.errors
  * Improved flash messages container spacing
  * Ensured consistent error message structure
- Key learnings:
  * Error containers must have consistent IDs for testability
  * Both field_errors and form.errors need to be handled
  * Proper spacing improves error message readability
  * Consistent structure makes testing more reliable

