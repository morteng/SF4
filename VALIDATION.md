# Validation Best Practices

## 1. Custom Field Implementation

1. **Handle All Arguments**  
   - Ensure that custom fields handle all arguments passed to them (e.g., `validators`).

2. **Default Validators**  
   - Provide default validators if none are passed:
     
     if validators is None:
         validators = [InputRequired()]
     

3. **Error Message Centralization**  
   - Use error messages from `app/constants.py` rather than hardcoded strings.  
   - Example:
     
     from app.constants import MISSING_REQUIRED_FIELD
     validators = [InputRequired(message=MISSING_REQUIRED_FIELD)]
     

4. **Example: CustomDateTimeField**  
   C
   from wtforms import Field
   from wtforms.validators import InputRequired
   from app.constants import MISSING_REQUIRED_FIELD

   class CustomDateTimeField(Field):
       def __init__(self, label=None, validators=None, **kwargs):
           if validators is None:
               validators = [InputRequired(message=MISSING_REQUIRED_FIELD)]
           super().__init__(label=label, validators=validators, **kwargs)
   

## 2. Date/Time Validation

1. **Data Type Awareness**  
   - Always verify the data type of form field inputs before applying validation logic (e.g., use `isinstance()` checks for `datetime` objects).

2. **Timezone Handling**  
   - Ensure all `datetime` objects are timezone-aware. For instance, use libraries such as `pytz` or ’s built-in `zoneinfo` to avoid naive datetimes.

3. **Future/Past Date Validation**  
   - Validate that dates are within acceptable ranges (e.g., future dates for deadlines).  
   - Use consistent timezone-aware checks such as `datetime.now(pytz.UTC)` for comparisons.

4. **Error Messages**  
   - Store and retrieve all error messages from `app/constants.py`.  
   - Provide specific messages for:
     - Invalid date/time formats  
     - Out-of-range values  
     - Missing required fields  
     - Invalid leap year dates (e.g., February 29 on a non-leap year)  
     - Invalid time components (e.g., 25:00:00)

5. **Allow Flexible Deadlines**  
   - Recognize that some deadlines (especially stipends) can be end-of-month, end-of-year, rolling, or otherwise indefinite.  
   - Implement logic to accommodate open-ended or approximate deadlines without rejecting submissions unnecessarily.

## 3. Error Handling

1. **Centralized Error Messages**  
   - Maintain a single source of truth for error messages in `app/constants.py`.

2. **Consistency**  
   - Use the constants defined in `app/constants.py` to ensure consistent messages and reduce the chance of typos.

3. **User-Friendly Messages**  
   - Provide clear, actionable error messages for validation failures.  
   - Log errors (with context) for easier debugging and troubleshooting.

4. **Specific Error Cases**  
   - Offer tailored messages for invalid date formats, out-of-range values, missing fields, leap year issues, and invalid time components.

## 4. Testing

1. **Edge Cases**  
   - Thoroughly test edge cases, particularly for date/time validation (e.g., February 29 on a non-leap year, 25:00:00, indefinite deadlines).  
   - Include tests for invalid or vague stipend deadlines.

2. **Mocking**  
   - Use `freezegun` (or equivalent) for deterministic time-based testing.  
   - Verify installation via `pip show freezegun` before running tests.

3. **Isolation**  
   - Ensure that database fixtures or other data states are reset between tests to prevent side effects.

4. **Comprehensive Coverage**  
   - Test all validation paths, including invalid formats, missing fields, and unusual time/date boundaries.

5. **Integration Testing**  
   - Consider adding end-to-end tests for form submission flows to confirm that error messages display correctly to end users.

## 5. Code Organization

1. **Modularity**  
   - Keep validation logic modular and reusable to facilitate maintenance and reduce duplication.

2. **Avoid Duplication**  
   - Utilize base classes and common utility functions to centralize shared validation logic.

3. **Documentation**  
   - Document validation rules, error messages, and any relevant constraints or edge cases in the codebase.  
   - Use docstrings to explain complex logic for future maintainers.

## 6. Property Implementation

1. **Define Properties Correctly**  
   - Use `@property` decorators for getters and `@<property>.setter` for setters.

2. **Validation in Setters**  
   - Include appropriate validation logic in property setters to maintain data integrity.

3. **Private Attributes**  
   - Rely on private attributes (e.g., `_property_name`) for internal storage when working with properties.

4. **Documentation**  
   - Provide clear docstrings explaining property behaviors and validation rules.  
   - Maintain consistency across the codebase for all property definitions.

## 7. General Validation

1. **Validation Logic**  
   - Always confirm that form field inputs match the expected data type before applying validation logic.  
   - Ensure compatibility with parent classes when overriding methods or attributes.  
   - Use centralized error messages from `app/constants.py`.

2. **Testing**  
   - Pay special attention to edge cases for date/time fields.  
   - Include mocking libraries (like `freezegun`) to ensure consistent time-based tests.

3. **Error Handling**  
   - Log validation errors with context to facilitate debugging and ensure thorough audit trails.  
   - Provide clear, user-friendly feedback for validation failures.

4. **Base Classes and Utilities**  
   - Use inheritance or shared utilities to keep validation logic consistent and reduce code duplication.

## 8. Stipend Deadlines

- Stipend application deadlines can be:
  - A specific date
  - A specific date and time  
  - End of a specific month or year  
  - A certain day of the month  
  - Continuous or rolling  
- Implement flexible logic to handle multiple deadline scenarios, including “no strict deadline,” while still providing meaningful validation feedback where possible.

## Blueprint Validation

1. **Blueprint Naming**:
   - Use consistent naming conventions for blueprints and endpoints.
   - Example: `admin_stipend_bp` for the blueprint and `admin_stipend.create` for the endpoint.

2. **Route Validation**:
   - Use `validate_blueprint_routes` to ensure all required routes are registered.
   - Example:
     ```python
     required_routes = ['admin_stipend.create', 'dashboard.dashboard']
     validate_blueprint_routes(app, required_routes)
     ```

3. **Error Handling**:
   - Log errors during blueprint registration.
   - Raise `RuntimeError` for missing routes.

## Application Context

1. **Context Management**:
   - Use `with app.app_context()` when accessing `current_app` or other context-dependent features.
   - Example:
     ```python
     with app.app_context():
         app.logger.debug("Debug message")
     ```

2. **Logging**:
   - Use `app.logger` instead of `current_app.logger` when `app` is explicitly available.
   - Example:
     ```python
     app.logger.error("Error message")
     ```

## 9. Key Takeaways

1. **Validation Logic**  
   - Consistently verify input data types, especially for date/time fields.  
   - Centralize error messages in `app/constants.py`.

2. **Testing**  
   - Exercise broad coverage of edge cases, particularly for date/time, including unusual or indefinite deadlines.  
   - Use mocking tools like `freezegun` to ensure deterministic time-dependent tests.

3. **Error Handling**  
   - Maintain user-friendly, clearly actionable error messages.  
   - Log errors in detail to aid debugging.

4. **Code Organization**  
   - Keep validation and property logic modular, well-documented, and consistent.  
   - Leverage base classes and utility functions to avoid duplication.

5. **Property Implementation**  
   - Define properties with correct `@property` and setter patterns, including validation.  
   - Use private attributes for data storage and public properties for validation and access control.

6. **Flexible Deadlines**  
   - Acknowledge that some deadlines (e.g., stipends) can be vague or rolling and adjust validation logic accordingly.

