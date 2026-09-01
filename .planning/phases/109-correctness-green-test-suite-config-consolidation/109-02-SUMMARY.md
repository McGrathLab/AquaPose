---
phase: 109-correctness-green-test-suite-config-consolidation
plan: "02"
subsystem: training/store
tags: [windows-compat, symlink-fallback, determinism, D-09, D-02]
dependency_graph:
  requires: [109-01]
  provides: [store-assemble-windows-safe, list-models-deterministic]
  affects: [tests/unit/training/test_store.py, tests/unit/training/test_data_cli.py]
tech_stack:
  added: []
  patterns: [three-tier-link-fallback, rowid-tiebreaker]
key_files:
  created: []
  modified:
    - src/aquapose/training/store.py
    - tests/unit/training/test_store.py
decisions:
  - "D-09: symlink→hardlink→copy three-tier fallback in _link_or_copy() helper — fixes WinError 1314 on Windows without Developer Mode"
  - "D-02: list_models() ORDER BY rowid DESC tiebreaker — fixes non-determinism when created_at timestamps share the same second"
metrics:
  duration: ~15 minutes
  completed: "2026-09-01"
  tasks_completed: 2
  files_modified: 2
---

# Phase 109 Plan 02: Symlink Fallback and List Models Ordering Summary

Store assemble() now works on Windows without symlink privilege via hardlink/copy fallback; list_models() ordering is deterministic via rowid tiebreaker.

## Tasks Completed

### Task 1: Add symlink→hardlink→copy fallback in store.assemble() (D-09)

**Commit:** f6de5a5

Extracted a module-private `_link_or_copy(src_abs, link_path, rel_target)` helper with a Google-style docstring. The three-tier strategy:

1. `link_path.symlink_to(rel_target)` — relative symlink (existing behavior on privileged installs, keeps dataset relocatable)
2. `os.link(src_abs, link_path)` — hardlink on same volume (no data duplication; catches WinError 1314 / OSError)
3. `shutil.copy2(src_abs, link_path)` — copy only when both fail (cross-volume EXDEV)

Both `img_link.symlink_to` / `lbl_link.symlink_to` call sites in `assemble()` replaced with `_link_or_copy(...)`. Trust boundary identical to the original: targets are always `self.root`-relative store paths, never externally controlled input.

Added a one-line module note at the top of `store.py` that assemble degrades gracefully without symlink privilege.

### Task 2: Update test_symlinks_are_relative semantics and fix list_models ordering

**Commit:** aaef2e6

**test_symlinks_are_relative (D-09 semantics update):**
- Root cause (D-02 note): `symlink_to` raises `OSError` (WinError 1314) on Windows without `SeCreateSymbolicLinkPrivilege`. The original test called `os.readlink` unconditionally, which raises `OSError` on hardlinks — so the test always failed on stock Windows.
- Fix: detect entry type via `entry.is_symlink()`. On the symlink branch: assert relative target (existing privileged invariant preserved). On both branches: assert `entry.exists()` and `entry.read_bytes() == img_bytes` (correct content regardless of link type). Captures source bytes before `import_sample()` because the store renames files by UUID.

**test_assemble_creates_symlinks (tolerance fix):**
- Root cause (D-02 note): The assertion `f.is_symlink()` is correct only when symlink privilege is available. On Windows without Developer Mode all entries are hardlinks, which `is_symlink()` returns `False` for.
- Fix: assert `f.is_file()` instead — satisfied by symlinks, hardlinks, and copies. Comment documents the three accepted forms.

**list_models() ORDER BY tiebreaker (D-02 non-determinism fix):**
- Root cause (D-02 note): `ORDER BY created_at DESC` alone is non-deterministic when two `register_model()` calls share the same second-resolution SQLite timestamp (common in rapid sequential registrations in tests and scripts). SQLite returns rows in insertion order when the sort key is tied, but this is undefined/unstable behavior.
- Fix: `ORDER BY created_at DESC, rowid DESC` — `rowid` is the SQLite internal row identifier, monotonically increasing with insertion order. The last-inserted model (run_b) gets the highest rowid and sorts first, matching the test expectation.

## Verification

All 15 plan-scoped tests pass:

```
hatch run test ... -k "TestAssemble or TestDataAssemble or TestAssembleSplitMode or list_models or symlinks"
15 passed, 1300 deselected in 9.34s
```

Acceptance criteria:
- `grep -c "os.link" src/aquapose/training/store.py` → 2 (helper + import)
- `grep -c "shutil.copy2" src/aquapose/training/store.py` → 7 (includes existing uses + new fallback)
- `list_models()` ORDER BY includes `rowid DESC` tiebreaker
- No `@pytest.mark.skip` or `xfail` added to any test

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_symlinks_are_relative byte-comparison used wrong source path**
- **Found during:** Task 2 implementation
- **Issue:** Initial fix used `store.root / "images" / img.name` to get the stored copy for byte comparison, but the store renames images to `<uuid>.jpg` on import — the original filename does not exist in the store.
- **Fix:** Capture `img.read_bytes()` before calling `store.import_sample()` (before UUID rename), then compare the assembled entry bytes to those captured bytes.
- **Files modified:** tests/unit/training/test_store.py
- **Commit:** aaef2e6

## D-02 Root Cause Notes

Per D-02 discipline, one-line root-cause note per fixed test:

| Test | Classification | Root Cause |
|------|---------------|------------|
| `test_symlinks_are_relative` | Genuine regression | `symlink_to` → `OSError` (WinError 1314) on Windows without `SeCreateSymbolicLinkPrivilege`; `os.readlink` then raises on non-symlink entries |
| `test_assemble_creates_symlinks` | Stale assertion | `is_symlink()` assertion correct only with symlink privilege; hardlinks satisfy `is_file()` but not `is_symlink()` |
| `test_list_models_returns_all` | Genuine non-determinism bug | `ORDER BY created_at DESC` alone unstable when two models share a second-resolution timestamp; `rowid DESC` tiebreaker resolves insertion order |
| 9 other `TestAssemble*` / `TestDataAssemble*` | Genuine regression | `store.assemble()` raised `OSError` (WinError 1314) before reaching file-existence assertions |

## Threat Surface Scan

No new network endpoints, auth paths, or external-input surfaces introduced. The `_link_or_copy` helper operates strictly within the existing `self.root`-relative trust boundary — same scope as the original `symlink_to` call it replaces. T-109-02-01 mitigated as planned.

## Self-Check: PASSED

- `src/aquapose/training/store.py` — modified, exists
- `tests/unit/training/test_store.py` — modified, exists
- Commits f6de5a5 and aaef2e6 exist in git log
- 15 plan-scoped tests pass, 0 skip/xfail added
