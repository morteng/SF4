# Coding Conventions

## Error Handling
- Use specific exceptions in try/except blocks
- Always rollback database transactions on errors
- Log errors with context using logger.error()
- Validate inputs before processing
- Preserve original exception types when re-raising

## Context Management
- Use Flask's context managers
- Ensure proper cleanup in tests
- Avoid manual context management

## Testing
- Test both success and error cases
- Verify database state after operations
- Use fixtures for setup/teardown
- Test edge cases and validation

