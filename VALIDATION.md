# Validation Rules

## Organization Form

### Name Field
- **Required**: Yes
- **Type**: String
- **Max Length**: 100 characters
- **Allowed Characters**: Letters, numbers, and spaces
- **Error Messages**:
  - "This field is required."
  - "Name must contain only letters, numbers, and spaces."
  - "Field must be between 1 and 100 characters long."

### Description Field
- **Required**: No
- **Type**: String
- **Max Length**: 500 characters
- **Error Messages**:
  - "Field must be between 0 and 500 characters long."

### Homepage URL Field
- **Required**: No
- **Type**: URL
- **Validation**:
  - Must be a valid URL if provided
  - Must start with http:// or https://
- **Error Messages**:
  - "Invalid URL format."

### Examples

**Valid Inputs**:
```json
{
    "name": "My Organization",
    "description": "A great organization",
    "homepage_url": "https://example.org"
}
```

**Invalid Inputs**:
```json
{
    "name": "Org@123!",  // Contains special characters
    "description": "a" * 501,  // Too long
    "homepage_url": "not-a-url"  // Invalid URL format
}
```

### Error Handling
- Errors are displayed with the field label and error message
- Multiple errors are separated by line breaks
- Error messages are displayed in a consistent format:
```html
<div class="error-message">
    <strong>Field Label</strong>: Error message
</div>
```
