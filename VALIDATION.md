# Updated Validation Rules

## Date & Time Validation
- Validate format before content
- Use fallback error messages
- Check for required fields first
- Validate date and time components separately
- Specific validation for:
  - Hours (0-23)
  - Minutes (0-59)
  - Seconds (0-59)
- Clear error messages before new validation
- Use consistent error message format

## Error Handling
- Centralize common error responses
- Use consistent error message format
- Always use configurable error messages
- Never hardcode error messages
- Log errors before returning responses
- Clear existing errors before new validation
- Use error_messages dictionary for all validation errors

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

