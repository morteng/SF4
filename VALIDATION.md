# Validation Rules

## Principles
- Validate client & server side
- Test success & failure cases
- Use enums consistently

## Organization Form
- Name: Required, ≤100 chars
- URL: Optional, valid
- Description: Required, ≤500 chars

## Error Handling
- Rollback on error
- Log details
- User-friendly messages
- Preserve form state

## Security
- Sanitize with bleach
- CSRF tokens required
- Rate limit sensitive endpoints

