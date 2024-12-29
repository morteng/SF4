# Updated TODO List

## Completed
- [x] Fix `CustomDateTimeField` initialization to handle `validators` argument correctly with default `InputRequired()`.
- [x] Install `pytest` and verify installation with `pip show pytest`.
- [x] Add `pytest` to `requirements.txt` for future environments.
- [x] Add pre-test dependency verification in `tests/test_dependencies.py`.
- [x] Document pytest installation and verification steps in `CONVENTIONS.md`.
- [x] Refactor shared functionality into `app/common/utils.py` to avoid circular imports.
- [x] Centralize error messages in `app/constants.py` for date/time validation.
- [x] Implement proper property handling in `BaseService` with getters and setters.
- [x] Add comprehensive tests for edge cases in date/time validation.
- [x] Document property implementation best practices in `CONVENTIONS.md`.

## Next Session
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Verify timezone handling in all date/time fields.
- [ ] Refactor validation logic in other forms to ensure consistency with `StipendForm`.
- [ ] Add property implementation tests for all service classes.
- [ ] Add integration tests for form validation.

## Long Term
- [ ] Automate dependency verification during test execution.
- [ ] Improve test coverage for all form fields.
- [ ] Refactor other shared functionality into `app/common`.
- [ ] Document property implementation patterns across the codebase.
- [ ] Add performance benchmarks for validation logic.
- [ ] Create a developer onboarding guide with setup instructions.
- [x] Fix `CustomDateTimeField` initialization to handle `validators` argument with default `InputRequired()`:
  - Added default validator when none provided
  - Updated form implementations to avoid duplicate validators
- [x] Install `pytest` and verify installation with `pip show pytest`
- [x] Add `pytest` to `requirements.txt` for future environments
- [x] Document pytest installation and verification steps in CONVENTIONS.md
- [x] Refactor shared functionality into `app/common/utils.py` to avoid circular imports.
- [x] Centralized error messages in `app/constants.py` for date/time validation.
- [x] Add pre-test dependency verification
- [x] Document setup process in CONVENTIONS.md

## Next Session
- [ ] Add comprehensive tests for edge cases in date/time validation.
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Verify timezone handling in all date/time fields.
- [ ] Refactor validation logic in other forms to ensure consistency with `StipendForm`.

## Long Term
- [ ] Automate dependency verification during test execution.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.
- [ ] Refactor other shared functionality into `app/common`.
- [ ] Add comprehensive tests for edge cases in date/time validation.
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Verify timezone handling in all date/time fields.
- [ ] Refactor validation logic in other forms to ensure consistency with `StipendForm`.

## Long Term
- [ ] Automate dependency verification during test execution.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.
- [ ] Refactor other shared functionality into `app/common`.

## Completed
- [x] Fix `CustomDateTimeField` initialization to handle `validators` argument with default `InputRequired()`.
- [x] Install `pytest` and verify installation with `pip show pytest`.
- [x] Add `pytest` to `requirements.txt` for future environments.
- [x] Document pytest installation and verification steps in CONVENTIONS.md.
- [x] Refactor shared functionality into `app/common/utils.py` to avoid circular imports.
- [x] Centralized error messages in `app/constants.py` for date/time validation.

## Next Session
- [ ] Add comprehensive tests for edge cases in date/time validation.
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Verify timezone handling in all date/time fields.
- [ ] Refactor validation logic in other forms to ensure consistency with `StipendForm`.

## Long Term
- [ ] Automate dependency verification during test execution.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.
- [ ] Refactor other shared functionality into `app/common`.
- [x] Fix `CustomDateTimeField` initialization to handle `validators` argument with default InputRequired().
- [x] Install `pytest` and verify installation with `pip show pytest`.
- [x] Add `pytest` to `requirements.txt` for future environments.
- [x] Refactor shared functionality into `app/common/utils.py` to avoid circular imports.
- [x] Centralized error messages in app/constants.py for date/time validation

## Next Session
- [x] Install `pytest` and `freezegun`
- [x] Add dependency verification test
- [x] Fix `CustomDateTimeField` initialization
- [x] Refactor circular imports
- [x] Add edge case tests for date/time validation
- [ ] Add comprehensive tests for edge cases in date/time validation.
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Verify timezone handling in all date/time fields.
- [ ] Refactor validation logic in other forms to ensure consistency with `StipendForm`.

## Long Term
- [ ] Automate dependency verification during test execution.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.
- [ ] Refactor other shared functionality into `app/common`.
- [x] Fix circular imports by refactoring shared functionality into `app/common/utils.py`.
- [x] Add comprehensive pytest installation and verification steps to documentation.
- [x] Add `__init__.py` to `app/forms` to make it a valid package.
- [x] Refactor `create_limit` into a proper property with a getter and setter.
- [x] Add a pre-test dependency verification script.
- [x] Install missing dependencies (`pytest`, `freezegun`, `Flask`).
- [x] Add pytest installation instructions to documentation.
- [x] Refactor `verify_dependencies()` to skip tests instead of failing the suite.
- [x] Fix `CustomDateTimeField` initialization to handle `validators` argument.
- [x] Install `pytest` and verify dependencies.
- [x] Refactor shared functionality into `app/common/utils.py`.

## Next Session
- [ ] Ensure all error messages are centralized in `app/constants.py` and used consistently.
- [ ] Add comprehensive tests for edge cases in date/time validation.
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Verify timezone handling in all date/time fields.
- [ ] Refactor validation logic in other forms to ensure consistency with `StipendForm`.

## Long Term
- [ ] Automate dependency verification during test execution.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.
- [ ] Refactor other shared functionality into `app/common`.
- [ ] Add comprehensive tests for `BaseService` properties.
- [ ] Verify time-based tests with `freezegun`.
- [ ] Add validation benchmarks for date/time fields.
- [ ] Expand test coverage for `BaseCrudController` and `BaseRouteController`.
- [ ] Ensure all error messages are centralized in `app/constants.py` and used consistently.
- [ ] Add comprehensive tests for edge cases in date/time validation.
- [ ] Optimize validation performance in `CustomDateTimeField`.

## Long Term
- [ ] Automate dependency verification during test execution.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.
- [ ] Refactor other shared functionality into `app/common`.
- [ ] Add comprehensive tests for `BaseService` properties.
- [ ] Verify time-based tests with `freezegun`.
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Add more comprehensive tests for timezone handling in date/time fields.
- [ ] Add validation benchmarks for date/time fields.
- [ ] Expand test coverage for `BaseCrudController` and `BaseRouteController`.
- [ ] Add more comprehensive tests for date/time validation in `StipendForm`.
- [ ] Verify timezone handling in all date/time fields.
- [ ] Refactor validation logic in other forms to ensure consistency with `StipendForm`.
