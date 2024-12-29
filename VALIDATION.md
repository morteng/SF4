# Updated Validation Best Practices

## Custom Field Implementation

### Handle All Arguments
- Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
- Example:
  ```python
  class CustomDateTimeField(Field):
      def __init__(self, label=None, validators=None, **kwargs):
          if validators is None:
              validators = [InputRequired()]  # Default validator
          super().__init__(label=label, validators=validators, **kwargs)
  ```

### Default Validators
- Provide default validators if none are passed:
  ```python
  if validators is None:
      validators = [InputRequired()]
  ```

### Error Message Centralization
- Define all error messages in `app/constants.py`.
- Use constants instead of hardcoded strings for error messages.
  Example:
  ```python
  from app.constants import MISSING_REQUIRED_FIELD
  validators=[InputRequired(message=MISSING_REQUIRED_FIELD)]
  ```

### Testing
- Test edge cases thoroughly, especially for date/time validation.
- Use mocking libraries like `freezegun` to ensure deterministic test behavior.

## Key Takeaways

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Date/Time Validation
1. **Data Type Awareness**:
   - Always verify the data type of form field inputs before applying validation logic.
2. **Timezone Handling**:
   - Ensure all `datetime` objects are timezone-aware.
3. **Future/Past Date Validation**:
   - Validate that dates are within acceptable ranges (e.g., future dates for deadlines).
4. **Error Messages**:
   - Use centralized error messages from `app/constants.py` for consistency.

### Property Implementation
1. **Proper Property Definition**:
   - Always define properties with `@property` and `@<property>.setter`
   - Include validation in setters
   - Use private attributes for storage
2. **Best Practices**:
   - Document properties with clear docstrings
   - Avoid direct attribute access outside the class
   - Ensure consistent property patterns across the codebase

### General Validation
1. **Validation Logic**:
   - Always verify the data type of form field inputs before applying validation logic.
   - Ensure compatibility with parent classes when overriding attributes or methods.
   - Use centralized error messages from `app/constants.py` for consistency.
2. **Testing**:
   - Test edge cases thoroughly, especially for date/time validation.
   - Use mocking libraries like `freezegun` to ensure deterministic test behavior.
3. **Error Handling**:
   - Log validation errors with context for easier debugging.
   - Provide clear, user-friendly error messages for validation failures.
4. **Code Organization**:
   - Keep validation logic modular and reusable.
   - Avoid code duplication by using base classes and utilities.

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Date/Time Validation
1. **Data Type Awareness**:
   - Always verify the data type of form field inputs before applying validation logic.
2. **Timezone Handling**:
   - Ensure all `datetime` objects are timezone-aware.
3. **Future/Past Date Validation**:
   - Validate that dates are within acceptable ranges (e.g., future dates for deadlines).
4. **Error Messages**:
   - Use centralized error messages from `app/constants.py` for consistency.

### General Validation
1. **Validation Logic**:
   - Always verify the data type of form field inputs before applying validation logic.
   - Ensure compatibility with parent classes when overriding attributes or methods.
   - Use centralized error messages from `app/constants.py` for consistency.
2. **Testing**:
   - Test edge cases thoroughly, especially for date/time validation.
   - Use mocking libraries like `freezegun` to ensure deterministic test behavior.
3. **Error Handling**:
   - Log validation errors with context for easier debugging.
   - Provide clear, user-friendly error messages for validation failures.
4. **Code Organization**:
   - Keep validation logic modular and reusable.
   - Avoid code duplication by using base classes and utilities.

### Date/Time Validation
1. **Best Practices**:
   - Validate date and time components separately before full parsing.
   - Use specific error messages for different validation failures (e.g., invalid format, invalid time, invalid leap year).
   - Handle edge cases like February 29th in non-leap years.

2. **Error Handling**:
   - Provide specific error messages for:
     - Invalid date formats.
     - Out-of-range values.
     - Missing required fields.
     - Invalid leap year dates.
     - Invalid time components (hours, minutes, seconds).
   - Use configurable error messages from `app/constants.py`.

3. **Testing**:
   - Test all error message variations for date/time fields.
   - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).

## Key Takeaways

### Validation Logic
1. **Data Type Awareness**:
   - Always verify the data type of form field inputs before applying validation logic.
   - Use `isinstance()` to check for `datetime` objects when working with date/time fields.

2. **Timezone Handling**:
   - Ensure all `datetime` objects are timezone-aware.
   - Use `pytz.UTC.localize()` to add a timezone to naive `datetime` objects.

3. **Future/Past Date Validation**:
   - Validate that dates are within acceptable ranges (e.g., future dates for deadlines).
   - Use `datetime.now(pytz.UTC)` for consistent timezone-aware comparisons.

4. **Error Messages**:
   - Use centralized error messages from `app/constants.py` for consistency.
   - Provide clear, user-friendly error messages for validation failures.

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Testing
1. **Edge Cases**:
   - Test edge cases thoroughly, especially for date/time validation.
2. **Mocking**:
   - Use `freezegun` for deterministic time-based testing.
3. **Isolation**:
   - Ensure database fixtures are properly reset between tests to avoid side effects.

### Date/Time Validation
1. **Best Practices**:
   - Validate date and time components separately before full parsing.
   - Use specific error messages for different validation failures (e.g., invalid format, invalid time, invalid leap year).
   - Handle edge cases like February 29th in non-leap years.

2. **Error Handling**:
   - Provide specific error messages for:
     - Invalid date formats.
     - Out-of-range values.
     - Missing required fields.
     - Invalid leap year dates.
     - Invalid time components (hours, minutes, seconds).
   - Use configurable error messages from `app/constants.py`.

3. **Testing**:
   - Test all error message variations for date/time fields.
   - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### General Validation
1. **Validation Logic**:
   - Always verify the data type of form field inputs before applying validation logic.
   - Ensure compatibility with parent classes when overriding attributes or methods.
   - Use centralized error messages from `app/constants.py` for consistency.

2. **Testing**:
   - Test edge cases thoroughly, especially for date/time validation.
   - Use mocking libraries like `freezegun` to ensure deterministic test behavior.

3. **Error Handling**:
   - Log validation errors with context for easier debugging.
   - Provide clear, user-friendly error messages for validation failures.

4. **Code Organization**:
   - Keep validation logic modular and reusable.
   - Avoid code duplication by using base classes and utilities.

### Key Takeaways for Next Coding Session
1. **Validation Logic**:
   - Always verify the data type of form field inputs before applying validation logic.
   - Use centralized error messages from `app/constants.py` for consistency.

2. **Testing**:
   - Test edge cases thoroughly, especially for date/time validation.
   - Use mocking libraries like `freezegun` to ensure deterministic test behavior.

3. **Error Handling**:
   - Log validation errors with context for easier debugging.
   - Provide clear, user-friendly error messages for validation failures.

4. **Code Organization**:
   - Keep validation logic modular and reusable.
   - Avoid code duplication by using base classes and utilities.
1. **Best Practices**:
   - Validate date and time components separately before full parsing.
   - Use specific error messages from app/constants.py for different validation failures (e.g., invalid format, invalid time, invalid leap year).
   - Handle edge cases like February 29th in non-leap years.
   - Ensure CustomDateTimeField properly handles validators argument with default InputRequired().

2. **Error Handling**:
   - Provide specific error messages for:
     - Invalid date formats.
     - Out-of-range values.
     - Missing required fields.
     - Invalid leap year dates.
     - Invalid time components (hours, minutes, seconds).
   - Use configurable error messages from `app/constants.py`.

3. **Testing**:
   - Test all error message variations for date/time fields.
   - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Key Takeaways

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Date/Time Validation
1. **Data Type Awareness**:
   - Always verify the data type of form field inputs before applying validation logic.
2. **Timezone Handling**:
   - Ensure all `datetime` objects are timezone-aware.
3. **Future/Past Date Validation**:
   - Validate that dates are within acceptable ranges (e.g., future dates for deadlines).
4. **Error Messages**:
   - Use centralized error messages from `app/constants.py` for consistency.

### General Validation
1. **Validation Logic**:
   - Always verify the data type of form field inputs before applying validation logic.
   - Ensure compatibility with parent classes when overriding attributes or methods.
   - Use centralized error messages from `app/constants.py` for consistency.
2. **Testing**:
   - Test edge cases thoroughly, especially for date/time validation.
   - Use mocking libraries like `freezegun` to ensure deterministic test behavior.
3. **Error Handling**:
   - Log validation errors with context for easier debugging.
   - Provide clear, user-friendly error messages for validation failures.
4. **Code Organization**:
   - Keep validation logic modular and reusable.
   - Avoid code duplication by using base classes and utilities.

### Key Takeaways
1. **Validation Logic**:
   - Always verify the data type of form field inputs before applying validation logic.
   - Use centralized error messages from `app/constants.py` for consistency.

2. **Testing**:
   - Test edge cases thoroughly, especially for date/time validation.
   - Use mocking libraries like `freezegun` to ensure deterministic test behavior.

3. **Error Handling**:
   - Log validation errors with context for easier debugging.
   - Provide clear, user-friendly error messages for validation failures.

4. **Code Organization**:
   - Keep validation logic modular and reusable.
   - Avoid code duplication by using base classes and utilities.

