# Coding Conventions
- Remember only stipend name is obligatory when creating stipends as a bot will search for and fill out other info later. that includes application deadline.

Deadlines should be flexible to handle various formats:
- Full datetime: "2023-12-31 23:59:59"
- Month/year: "August 2023" 
- Year only: "2023"
- Vague descriptions like "in August" should be converted to "August 2023"
The system must be flexible in handling stipend info, not strict.

TODO.md should be focused on tasks you have todo in the future, to remember doing them next coding session. Use this file to plan ahead and keep track of tasks that need to be completed. This can include refactoring, adding new features, or fixing bugs. It's a good practice to add a brief description of each task and any relevant context or dependencies.


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

