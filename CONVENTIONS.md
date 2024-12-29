# Updated Coding Conventions

## Service Layer
- BaseService handles CRUD
- Child services implement domain logic
- Standard method names
- Audit logging via user_id
- Consistent error handling

## Error Handling
- Use dict.get() with default messages for error handling
- Centralize common error responses
- Log errors with context before returning user-friendly messages
- Specific exceptions
- Rollback on errors
- Validate inputs
- Preserve exception types

## Updated Validation Conventions
- Use specific error messages for different validation scenarios
- Validate time components (hours, minutes, seconds) together
- Provide clear, user-friendly error messages
- Use consistent error message format across all fields
- Handle edge cases in time validation (e.g., 25:00:00)
- Ensure validation order: required → format → components → full parsing

## New Section: Validation Best Practices
1. **Date/Time Validation**:
   - Validate date and time components separately before full parsing.
   - Use specific error messages for different validation failures (e.g., invalid format, invalid time, invalid leap year).
   - Handle edge cases like February 29th in non-leap years.

2. **Error Messages**:
   - Always use error messages from `app/constants.py` instead of hardcoding them.
   - Provide clear, user-friendly error messages for validation failures.

3. **Testing**:
   - Test all error message variations for validation fields.
   - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).

## Testing
- Test both success and error cases
- Verify error messages in validation tests
- Use consistent test patterns for form validation
- Verify database state
- Use fixtures & base classes
- Test edge cases
- Keep tests isolated

