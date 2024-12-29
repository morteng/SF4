# Updated Validation Rules

## Date Validation
- Validate format before content
- Use fallback error messages
- Check for required fields first
- Validate time components separately

## Error Handling
- Centralize common error responses
- Use consistent error message format
- Log errors before returning responses

## Testing
- Test all error message variations
- Verify error message fallbacks
- Test edge cases in date validation

## Database Operations
- Pre-op validation in services
- Flexible date handling
- Error rollback
- Consistent validation patterns
- Post-op verification

## CSRF Validation
- Validate on all form submissions
- Test CSRF generation/validation
- Handle invalid CSRF gracefully

## Context Management
- Ensure proper cleanup
- Verify context state
- Handle context errors

