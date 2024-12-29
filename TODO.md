# Updated TODO List

## Completed
- [x] Fix circular imports by refactoring shared functionality into `app/common/utils.py`.
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
