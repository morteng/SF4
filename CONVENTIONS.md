## Coding Conventions

### Error Handling
- Use try/except with specific exceptions
- Always rollback on database errors
- Log errors with context using logger.error()
- Validate inputs before processing

### Context Management
- Use Flask's context managers
- Ensure proper cleanup in tests
- Avoid manual context management

### Testing
- Test success and error cases
- Verify database state
- Use fixtures for setup/teardown
- Test edge cases and validation

