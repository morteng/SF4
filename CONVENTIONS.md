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
- Initialize error messages with defaults
- Use defensive programming in validation logic
- Validate format before content

## Testing
- Test both success and error cases
- Verify error messages in validation tests
- Use consistent test patterns for form validation
- Verify database state
- Use fixtures & base classes
- Test edge cases
- Keep tests isolated

