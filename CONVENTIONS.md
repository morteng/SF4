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

## Testing
- Test both success and error cases
- Verify error messages in validation tests
- Use consistent test patterns for form validation
- Verify database state
- Use fixtures & base classes
- Test edge cases
- Keep tests isolated

