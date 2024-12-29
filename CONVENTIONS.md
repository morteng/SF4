# Coding Conventions

## Service Layer
- BaseService handles CRUD operations
- Child services implement domain-specific logic
- Standard method names across all services
- Audit logging via user_id
- Custom validation hooks in child services
- Consistent error handling patterns

## Stipend Handling
- Only stipend name is required when creating stipends
- Bots will search for and fill out other info later
- Handle flexible deadline formats:
  - Full datetime: "2023-12-31 23:59:59"
  - Month/year: "August 2023"
  - Year only: "2023"
  - Convert vague descriptions like "in August" to "August 2023"

## Error Handling
- Use specific exceptions in try/except blocks
- Always rollback database transactions on errors
- Log errors with context using logger.error()
- Validate inputs before processing
- Preserve original exception types when re-raising

## Testing
- Test both success and error cases
- Verify database state after operations
- Use fixtures for setup/teardown
- Test edge cases and validation
- Keep tests isolated and independent

