# Validation Rules

## Principles
- Validate client & server side
- Test success & failure cases
- Use FlashCategory and FlashMessages enums for message types

## Form Validation
- Required fields: Validate presence
- Length: Enforce max lengths
- Format: Validate URLs, dates
- Uniqueness: Check for duplicates

## Error Handling
- Rollback on error
- Log details
- Use FlashMessages for user feedback
- Preserve form state

## Security
- Sanitize with bleach
- CSRF tokens required
- Rate limit sensitive endpoints

