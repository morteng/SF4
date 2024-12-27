# Validation Rules

## Validation Principles
1. **Input Validation**
   - All user input validated client and server side
   - Sanitize using bleach with specific allowed tags:
     - Text: No HTML
     - Descriptions: p, br, strong, em
     - URLs: No HTML
   - Validate URLs using Flask-WTF URL validator
   - Use `Enum` for constants to ensure type safety

2. **Error Handling**
   - Provide clear, user-friendly error messages using `FlashMessages`
   - Log detailed error information for debugging using `logger`
   - Handle database errors gracefully with try-except blocks
   - Rollback database sessions on errors

3. **Security**
   - Use CSRF tokens for all forms
   - Implement rate limiting for sensitive endpoints
   - Validate and sanitize all URLs
   - Use type hints for better code clarity and IDE support

## Form Validation

### Organization Form
- **Name**:
  - Required
  - Max length: 100 characters
  - Error messages:
    - "Name is required"
    - "Name must be between 1 and 100 characters"
    
- **Homepage URL**:
  - Optional
  - Must be valid URL if provided
  - Must start with http:// or https://
  - Validated using validate_url utility

- **Description**:
  - Required
  - Max length: 500 characters
  - Error messages:
    - "Description is required"
    - "Description must be less than 500 characters"

- **Homepage URL**:
  - Optional
  - Must be valid URL if provided
  - Must start with http:// or https://
  - Error messages:
    - "Invalid URL format"

### Test Cases
1. **Valid Inputs**:
   - Name: "Test Organization"
   - Description: "Test description"
   - Homepage URL: "https://example.org"

2. **Invalid Inputs**:
   - Name: "" (empty)
   - Name: "Org@123!" (special characters)
   - Description: "a" * 501 (too long)
   - Homepage URL: "invalid-url"

## Error Handling Patterns

### Database Errors
- Rollback session on error
- Log detailed error information
- Display user-friendly message
- Preserve form state

### Form Validation Errors
- Display field-specific messages
- Highlight invalid fields
- Preserve valid input
- Log validation errors

## Security Best Practices

### Input Sanitization
- Use bleach to clean all user input
- Strip whitespace from text fields
- Validate URLs before processing

### CSRF Protection
- Require CSRF token for all POST requests
- Validate token on server side
- Generate new token for each form

### Rate Limiting
- Implement rate limiting for admin routes
- Use Flask-Limiter for configuration
- Log rate limit violations

