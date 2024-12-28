## Coding Conventions

### Error Handling
- Use try/except blocks for database operations
- Always rollback on errors
- Log errors with context using logger.error()
- Use specific exception types

### Context Management
- Use Flask's built-in context managers
- Avoid manual context management in tests
- Use `with` statements for resource management

### Testing
- Test both success and error cases
- Verify database state after operations
- Use fixtures for test setup/teardown
- Test CSRF token validation

