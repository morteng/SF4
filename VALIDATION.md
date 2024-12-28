# Validation Rules

### Database Operations
- Validate inputs before database operations
- Handle constraint violations gracefully
- Rollback on errors
- Verify state after operations
- Refresh objects before validation

### CSRF Validation
- Validate CSRF tokens on all form submissions
- Test CSRF token generation and validation
- Handle invalid CSRF tokens gracefully
- Use session_transaction for CSRF token testing

### Context Management
- Ensure proper context cleanup
- Verify context state in tests
- Handle context errors gracefully
- Maintain consistent context hierarchy

