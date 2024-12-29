# Updated TODO List

## Completed
- [x] Fix circular imports by refactoring shared functionality into `app/common/utils.py`.
- [x] Fix property implementation in `BaseService`.
- [x] Install missing dependencies (`freezegun`).
- [x] Ensure `app/common` is recognized as a package by adding `__init__.py`.
- [x] Install `freezegun` for time-based testing.
- [x] Add installation verification steps to documentation.
- [x] Add a script to verify all dependencies listed in `requirements.txt` are installed.
- [x] Resolve circular imports by refactoring shared functionality into a separate module.
- [x] Install `freezegun` for time-based testing.
- [x] Add installation verification steps to documentation.
- [x] Consolidate leap year validation logic in `CustomDateTimeField`.
- [x] Add tests for edge cases in date/time validation.
- [x] Standardize error messages using constants from `app/constants.py`.
- [x] Improve validation error reporting for better debugging.
- [x] Add comprehensive test coverage for date/time validation.
- [x] Add a script to verify all dependencies listed in `requirements.txt` are installed.

## Next Session
- [ ] Add comprehensive tests for `BaseService` properties.
- [ ] Verify time-based tests with `freezegun`.
- [ ] Refactor other shared functionality into `app/common`.
- [x] Add comprehensive tests for property getters and setters.
- [x] Verify that all dependencies listed in `requirements.txt` are installed during test execution.
- [x] Add a pre-test dependency verification script to ensure all required packages are installed.
- [ ] Resolve circular imports by refactoring shared functionality into a separate module.
- [ ] Install missing dependencies (e.g., `freezegun`) and verify their installation.
- [x] Add comprehensive tests for property getters and setters.
- [x] Verify that all dependencies listed in `requirements.txt` are installed during test execution.
- [x] Add a pre-test dependency verification script to ensure all required packages are installed.
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Add more comprehensive tests for timezone handling in date/time fields.
- [ ] Add validation benchmarks for date/time fields.
- [ ] Expand test coverage for `BaseCrudController` and `BaseRouteController`.
- [ ] Add more comprehensive tests for date/time validation in `StipendForm`.
- [ ] Verify timezone handling in all date/time fields.
- [ ] Refactor validation logic in other forms to ensure consistency with `StipendForm`.

## Long Term
- [ ] Automate dependency verification during test execution.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.
- [ ] Refactor validation logic into reusable components.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.

## Security Priority
- [ ] Implement rate limiting for API endpoints.
- [ ] Implement session expiration.
- [ ] Add audit logging for admin actions.
- [ ] Automate dependency verification during test execution to ensure all required packages are installed.

## Long Term
- [ ] Automate dependency verification during test execution.
- [ ] Refactor validation logic into reusable components.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.

## Security Priority
- [ ] Implement rate limiting for API endpoints.
- [ ] Implement session expiration.
- [ ] Add audit logging for admin actions.
- [ ] Implement dependency verification during test execution to ensure all required packages are installed.
