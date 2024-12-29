# Updated TODO List

## Completed
- [x] Fix `TypeError` in `CustomDateTimeField` caused by incorrect `format` usage.
- [x] Consolidate leap year validation logic in `CustomDateTimeField`.
- [x] Add tests for edge cases in date/time validation.
- [x] Standardize error messages using constants from `app/constants.py`.

## Next Session
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Add validation benchmarks for date/time fields.
- [ ] Expand test coverage for `BaseCrudController` and `BaseRouteController`.

## Long Term
- [ ] Refactor validation logic into reusable components.
- [ ] Improve test coverage for all form fields.
- [ ] Add integration tests for form validation.

## Medium Priority
- [ ] Optimize validation performance in `CustomDateTimeField`.
- [ ] Add validation benchmarks for date/time fields.
- [ ] Expand test coverage for `BaseCrudController` and `BaseRouteController`.

## Security Priority
- Implement rate limiting for API endpoints.
- Implement session expiration
- Add audit logging for admin actions
