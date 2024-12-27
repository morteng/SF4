# Validation Rules

## Validation Principles
- Validate all form inputs client and server side
- Centralize test utilities in tests/utils.py
- Use factory functions for test data
- Verify both success and failure scenarios

## Form Validation
### Organization Form
- **Name**: Required, max 100 chars
- **Homepage URL**: Optional, valid URL
- **Description**: Required, max 500 chars

## Error Handling Patterns
- Rollback session on error
- Log detailed error information
- Display user-friendly message
- Preserve form state

## Security Best Practices
- Use bleach for input sanitization
- Require CSRF tokens for all POST requests
- Implement rate limiting for sensitive endpoints
- Use FlashMessages and FlashCategory enums consistently

