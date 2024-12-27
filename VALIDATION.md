# Validation Rules
## Principles
- Validate client & server side
- Use enums for message types
- Test success & failure cases
- Include CSRF validation

## Form Validation
- Required fields: Validate presence
- Length: Enforce max lengths
- Format: Validate URLs, dates
- Uniqueness: Check for duplicates
- CSRF: Validate token in all forms

## Error Handling
- Rollback on error
- Log details
- Use enums for user feedback
- Preserve form state

## Security
- Sanitize inputs
- CSRF tokens required in all forms
- Rate limit sensitive endpoints
- Use Flask-WTF for form handling

