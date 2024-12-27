# Validation Rules

## Validation Principles
- Validate all form inputs client and server side
- Use Enum constants for consistent messages
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
- Use bleach to clean all user input
- Require CSRF token for all POST requests
- Implement rate limiting for admin routes
- Use FlashMessages and FlashCategory enums for consistent error/success messaging

