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

## Validation
- Always use configurable error messages via `error_messages`.
- Never use hardcoded error messages in validation logic.
- Initialize error messages with defaults.
- Use defensive programming in validation logic.
- Clear existing errors before new validation.
- Use consistent error message format across all fields.
- Validate date and time components separately.
- Add specific validation for time values (hours, minutes, seconds).
- Map error message keys consistently.
- Validate time components before full datetime parsing.
- Use specific error messages for each validation failure.
- Handle edge cases in time validation (e.g., 25:00:00).
- Ensure validation order: required → format → components → full parsing.
- Always check for required fields first.
- Handle empty/missing values consistently.
- Return appropriate error messages for missing required fields.

## Testing
- Test both success and error cases
- Verify error messages in validation tests
- Use consistent test patterns for form validation
- Verify database state
- Use fixtures & base classes
- Test edge cases
- Keep tests isolated

