# Validation Rules

## Date/Time Field Validation

### Required Fields
- **Required**: Yes
- **Error Messages**:
  - "Date is required"

### Format Validation
- **Format**: YYYY-MM-DD HH:MM:SS
- **Error Messages**:
  - "Invalid date format. Please use YYYY-MM-DD HH:MM:SS"

### Date Validation
- **Valid Date Range**:
  - Year: 1900-2100
  - Month: 1-12
  - Day: 1-31 (month-dependent)
- **Error Messages**:
  - "Invalid date values (e.g., Feb 30)"

### Time Validation
- **Valid Time Range**:
  - Hour: 0-23
  - Minute: 0-59
  - Second: 0-59
- **Error Messages**:
  - "Invalid time values (e.g., 25:61:61)"

### Timezone Handling
- **Input Type**: Must be a string
- **Default Value**: 'UTC'
- **Error Handling**:
  * If invalid type provided, defaults to 'UTC'
  * Properly converts string timezone to pytz timezone object
  * Handles UnknownTimeZoneError gracefully

### Examples

**Valid Inputs**:
- "UTC"
- "America/New_York"
- "Europe/London"

**Invalid Inputs**:
- UnboundField objects (will default to 'UTC')
- None (will default to 'UTC')
- "Invalid/Timezone" (will raise UnknownTimeZoneError)

### Examples

**Valid Inputs**:
- "2023-01-01 12:00:00"
- "2024-02-29 23:59:59" (leap year)

**Invalid Inputs**:
- "2023-13-32 99:99:99" (invalid date/time)
- "2023-02-30 12:00:00" (invalid date)
- "2023-01-01 25:61:61" (invalid time)
- "invalid-date" (invalid format)

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

### Database Error Handling
- **Scenario**: Database error during update
- **Expected Behavior**:
  * User should be redirected back to edit page
  * Flash message should be displayed with database error
  * Form should retain previously entered values
  * Error message should be: "Database error while updating organization."
  * Test Case: test_update_organization_with_database_error
  * Implementation Details:
    - SQLAlchemyError should be caught and handled
    - Database session should be rolled back
    - User should be redirected to edit page with error message
    - Form should maintain its state
    - Flash message must be set before redirect
    - Error handling follows consistent pattern across all routes
    - Database errors are logged for debugging
    - Form state is preserved during error handling
    - Consistent error message format is maintained

