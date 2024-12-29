# Updated Validation Rules

## Updated Time Validation

### Best Practices
- Validate time components together (hours, minutes, seconds)
- Use specific error messages for different validation failures
- Handle edge cases in time validation (e.g., 25:00:00)
- Provide clear, user-friendly error messages
- Validate time values before full datetime parsing

### Error Handling
- Provide specific error messages for:
  - Invalid time formats
  - Out-of-range values
  - Missing required fields
  - Time values outside valid ranges
  - Malformed datetime strings
- Use configurable error messages
- Log validation errors with context

### Testing
- Test all error message variations
- Verify error message fallbacks
- Test edge cases in time validation
- Ensure consistent handling of empty/missing values

### Error Handling
- Provide specific error messages for:
  - Invalid date formats
  - Out-of-range values
  - Missing required fields
  - Invalid leap year dates
  - Invalid time components (hours, minutes, seconds)
  - Time values outside valid ranges
  - Malformed datetime strings
- Use configurable error messages
- Log validation errors with context

## Error Handling
- Centralize common error responses
- Use consistent error message format
- Always use configurable error messages
- Never hardcode error messages
- Log errors before returning responses
- Clear existing errors before new validation
- Use error_messages dictionary for all validation errors
- Handle required field validation first
- Return appropriate error messages for missing required fields
- Ensure consistent handling of empty/missing values

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

