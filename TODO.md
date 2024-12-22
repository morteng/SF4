# TODO List

## General
- [x] Resolve import file mismatch error for tests/app/routes/test_user_routes.py.
- [x] Rename or move `tests/app/routes/admin/test_user_routes.py` to avoid naming conflicts with `tests/app/routes/test_user_routes.py`.
- [x] Ensure all test files have unique basenames to prevent import mismatches.

## Specific Tasks
- [ ] Use session.get() instead of query.get() in tests.
- [ ] Ensure all flash message assertions use constants.
