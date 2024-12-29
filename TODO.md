## Completed
- [x] Fix `CustomDateTimeField` initialization to handle `validators` argument correctly with default `InputRequired()`.
- [x] Install `pytest` and verify installation with `pip show pytest`.
- [x] Add `pytest` to `requirements.txt` for future environments.
- [x] Add pre-test dependency verification in `tests/test_dependencies.py`.
- [x] Refactor shared functionality into `app/common/utils.py` to avoid circular imports.
- [x] Centralize error messages in `app/constants.py` for date/time validation.
- [x] Implement proper property handling in `BaseService` with getters and setters.
- [x] Add comprehensive tests for edge cases in date/time validation.

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
