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
  - "Time is required. Please use YYYY-MM-DD HH:MM:SS"
  - "Invalid date format. Please use YYYY-MM-DD HH:MM:SS"
  - "Invalid date values (e.g., Feb 30)"
  - "Date is required"
  - "Time is required. Please use YYYY-MM-DD HH:MM:SS"

### Test Cases
1. Invalid date values (2023-13-32 99:99:99)
   - Expected Error: "Invalid date values (e.g., Feb 30)"
2. Invalid month/day combinations (2023-02-30 12:00:00)
   - Expected Error: "Invalid date values (e.g., Feb 30)"
3. Invalid time values (2023-01-01 25:61:61)
   - Expected Error: "Invalid time values (e.g., 25:61:61)"
4. Missing time components (2023-01-01)
   - Expected Error: "Time is required. Please use YYYY-MM-DD HH:MM:SS"
5. Invalid formats (invalid-date)
   - Expected Error: "Invalid date format. Please use YYYY-MM-DD HH:MM:SS"
6. Date range issues (2020-01-01 00:00:00)
   - Expected Error: "Application deadline must be a future date"
7. Edge cases (2023-02-29 12:00:00)
   - Expected Error: "Invalid date values (e.g., Feb 30)"
   
### Validation Improvements
- Fixed error message for invalid dates to show "Invalid date values (e.g., Feb 30)" instead of "Date is required"
- Improved error handling for invalid date/time combinations
- Added specific error handling for invalid date/time values
- Maintained proper error message hierarchy

### Timezone Handling
- **Input Type**: Must be a string or convertible to string
- **Default Value**: 'UTC'
- **Error Handling**:
  * If invalid type provided, converts to string
  * If None provided, defaults to 'UTC'
  * Properly converts string timezone to pytz timezone object
  * Handles UnknownTimeZoneError gracefully

- **Comparison Rules**:
  * All datetime comparisons must be between timezone-aware datetimes
  * Naive datetimes must be localized to UTC using pytz.UTC.localize()
  * Timezone-aware datetimes must be converted to UTC using astimezone(pytz.UTC)
  * Comparisons between naive and timezone-aware datetimes will raise TypeError

### Dependency Validation Improvements
- Added test cases for requirements-parser package
- Updated dependency validation to use RequirementsParser class
- Added error handling for missing requirements-parser package

### Dependency Validation Improvements
- Added test cases for requirements-parser package
- Updated dependency validation to use RequirementsParser class
- Added error handling for missing requirements-parser package

### Dependency Validation

**Required Packages**:
- Flask-Limiter must be installed and properly configured
- All packages in requirements.txt must be installed

**Test Cases**:
1. Verify Flask-Limiter is installed and importable
2. Verify all requirements.txt packages are installed
3. Verify rate limiting is working on admin endpoints

**Error Messages**:
- "Missing required package: Flask-Limiter"
- "Package version mismatch in requirements.txt"
- "Rate limiting not properly configured"

### Dependency Validation

**Required Packages**:
- Flask-Limiter must be installed and properly configured
- All packages in requirements.txt must be installed

**Test Cases**:
1. Verify Flask-Limiter is installed and importable
2. Verify all requirements.txt packages are installed
3. Verify rate limiting is working on admin endpoints

**Error Messages**:
- "Missing required package: Flask-Limiter"
- "Package version mismatch in requirements.txt"
- "Rate limiting not properly configured"

### Dependency Validation

**Required Packages**:
- Flask-Limiter must be installed and properly configured
- All packages in requirements.txt must be installed

**Test Cases**:
1. Verify Flask-Limiter is installed and importable
2. Verify all requirements.txt packages are installed
3. Verify rate limiting is working on admin endpoints

**Error Messages**:
- "Missing required package: Flask-Limiter"
- "Package version mismatch in requirements.txt"
- "Rate limiting not properly configured"

## Template Validation

### New Test Cases
1. Verify all admin templates extend base.html
2. Check for proper template inheritance chain
3. Validate template rendering for all admin routes

### Error Messages
- "Template not found: {template_name}"
- "Invalid template inheritance"
- "Missing required block: {block_name}"

### Examples
- Admin bot create template must extend base.html
- All templates must include required blocks (content, etc)
- Flash messages must use _flash_messages.html partial

### Timezone-aware Datetime Validation

**Test Cases**:
1. Compare timezone-aware datetime with UTC
2. Compare naive datetime with timezone-aware datetime (should convert naive to UTC)
3. Compare datetimes in different timezones (should convert both to UTC)
4. Validate future date with timezone conversion
5. Validate max future date (5 years) with timezone conversion
6. Validate leap year dates (2024-02-29)
7. Validate invalid dates (2023-02-30)
8. Validate invalid times (25:61:61)
9. Validate missing time components
10. Validate invalid formats

**Error Messages**:
- "Application deadline must be a future date"
- "Application deadline cannot be more than 5 years in the future"
- "Invalid timezone conversion"
- "Invalid date format. Please use YYYY-MM-DD HH:MM:SS"
- "Invalid date values (e.g., Feb 30)"
- "Invalid time values (e.g., 25:61:61)"
- "Date is required"
- "Time is required. Please use YYYY-MM-DD HH:MM:SS"

### Examples

**Valid Comparisons**:
- pytz.UTC.localize(datetime.now()) < datetime.now(pytz.UTC)
- datetime.now(pytz.timezone('America/New_York')).astimezone(pytz.UTC) < datetime.now(pytz.UTC)

**Invalid Comparisons**:
- datetime.now() < datetime.now(pytz.UTC)  # Raises TypeError

### Examples

**Valid Inputs**:
- "UTC"
- "America/New_York"
- SelectField object (will be converted to string)
- None (will default to 'UTC')
- "Invalid/Timezone" (will raise UnknownTimeZoneError)

### Dependency Validation

**Required Packages**:
- Flask-Limiter must be installed and properly configured
- All packages in requirements.txt must be installed

**Test Cases**:
1. Verify Flask-Limiter is installed and importable
2. Verify all requirements.txt packages are installed
3. Verify rate limiting is working on admin endpoints

**Error Messages**:
- "Missing required package: Flask-Limiter"
- "Package version mismatch in requirements.txt"
- "Rate limiting not properly configured"

### Examples

**Valid Inputs**:
- "2023-01-01 12:00:00"
- "2024-02-29 23:59:59" (leap year)

**Invalid Inputs**:
- "2023-13-32 99:99:99" (invalid date/time)
- "2023-02-30 12:00:00" (invalid date)
- "2023-01-01 25:61:61" (invalid time)
- "invalid-date" (invalid format)

## Bot Route Validation

### Test Cases
1. **Create Bot**
   - Valid input
   - Missing required fields
   - Invalid bot name (special characters)
   - Database error during creation
   - Template rendering validation

2. **Edit Bot**
   - Valid update
   - Invalid ID
   - Validation errors
   - Database error during update
   - Template rendering validation

3. **Delete Bot**
   - Valid deletion
   - Invalid ID
   - Database error during deletion
   - Template rendering validation

4. **Run Bot**
   - Successful run
   - Invalid ID
   - Bot runtime error
   - Template rendering validation

### Error Messages
- "Failed to create bot: {error}"
- "Bot not found"
- "Failed to update bot: {error}"
- "Failed to delete bot: {error}"
- "Failed to run bot: {error}"

### Validation Improvements
- Added proper error handling for bot creation
- Improved form validation with specific error messages
- Added status field validation
- Enhanced template error display

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

