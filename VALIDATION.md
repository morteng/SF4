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

### Date/Time Field
- **Required**: Yes
- **Type**: DateTime
- **Format**: YYYY-MM-DD HH:MM:SS
- **Timezone**: UTC (converted from user's local timezone)
- **Validation**:
  - Must be a valid date/time
  - Must be in the future (for future events)
  - Must handle daylight saving time transitions
  - Must be within valid ranges (1900-2100 for years)
- **Error Messages**:
  - "Invalid date format. Please use YYYY-MM-DD HH:MM:SS"
  - "Invalid timezone"
  - "Ambiguous time due to daylight saving transition"
  - "Date must be in the future"
  - "Date must be in the past"

### Examples

**Valid Inputs**:

{
    "name": "My Organization",
    "description": "A great organization",
    "homepage_url": "https://example.org"
}


**Invalid Inputs**:

{
    "name": "Org@123!",  // Contains special characters
    "description": "a" * 501,  // Too long
    "homepage_url": "not-a-url"  // Invalid URL format
}


### Error Handling
- Errors are displayed with the field label and error message
- Multiple errors are separated by line breaks
- Error messages are displayed in a consistent format:
<div class="error-message">
    <strong>Field Label</strong>: Error message
</div>

