# Coding Conventions

## Service Layer
- BaseService handles CRUD
- Child services implement domain logic
- Standard method names
- Audit logging via user_id
- Consistent error handling

## Error Handling
- Specific exceptions
- Rollback on errors
- Log with context
- Validate inputs
- Preserve exception types

## Testing
- Test success & error cases
- Verify database state
- Use fixtures & base classes
- Test edge cases
- Keep tests isolated

