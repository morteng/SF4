# Updated Validation Rules

## Date & Time Validation

### General Principles
- Validate format before content.
- Use fallback error messages.
- Check for required fields first.
- Clear error messages before new validation.
- Use consistent error message format.
- Handle specific `ValueError` cases explicitly.
- Ensure date format strings are properly initialized.
- Remove duplicate validation code.

### Component Validation
- Validate date and time components separately
- Specific validation for:
  - Hours (0-23)
  - Minutes (0-59)
  - Seconds (0-59)
  - Leap years (February 29th)

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

