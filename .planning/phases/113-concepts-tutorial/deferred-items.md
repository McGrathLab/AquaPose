# Deferred Items — Phase 113

Out-of-scope discoveries logged during execution but not fixed (per executor
scope-boundary rule: only auto-fix issues directly caused by the current
task's changes).

## Plan 01, Task 2

- **`tests/unit/training/test_pseudo_label_cli.py::TestGenerateCommand::test_generates_merged_obb_and_separate_pose`**
  fails on `dev` independent of this plan's changes. Assertion
  `assert len(parts) == 9  # cls + 4 corners x 2` receives 18 parts instead of
  9 — an OBB label-content-format mismatch in `training/pseudo_label_cli.py`
  or its test fixture, unrelated to `pyproject.toml`'s wheel-index pin.
  Confirmed pre-existing by reverting the `pyproject.toml` edit and
  re-running the single test in isolation: identical failure before and
  after. Out of scope for a documentation phase; not fixed here.
