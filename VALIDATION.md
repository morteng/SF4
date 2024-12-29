# Updated Validation Rules

## Updated Time Validation

### Best Practices
- Validate time components together (hours, minutes, seconds)
- Use specific error messages for different validation failures
- Handle edge cases in time validation (e.g., 25:00:00)
- Provide clear, user-friendly error messages
- Validate time values before full datetime parsing

## New Section: Date/Time Validation
1. **Best Practices**:
   - Validate date and time components separately before full parsing.
   - Use specific error messages for different validation failures (e.g., invalid format, invalid time, invalid leap year).
   - Handle edge cases like February 29th in non-leap years.

2. **Error Handling**:
   - Provide specific error messages for:
     - Invalid date formats.
     - Out-of-range values.
     - Missing required fields.
     - Invalid leap year dates.
     - Invalid time components (hours, minutes, seconds).
   - Use configurable error messages from `app/constants.py`.

3. **Testing**:
   - Test all error message variations for date/time fields.
   - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).

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
- **Centralized Error Messages**:
  - Always use error messages from `app/constants.py` for consistency.
  - Avoid hardcoding error messages in validation logic.
- **Field Initialization**:
  - Ensure parameters are not passed multiple times during field initialization.
  - Use consistent patterns for initializing custom fields.
- **Testing**:
  - Test all error message variations for validation fields.
  - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).

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

