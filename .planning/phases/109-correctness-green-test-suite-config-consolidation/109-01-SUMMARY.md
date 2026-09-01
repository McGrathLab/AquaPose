---
phase: 109-correctness-green-test-suite-config-consolidation
plan: "01"
subsystem: engine/config, training/run_manager
tags: [config, path-resolution, platform-neutrality, qa-03]
dependency_graph:
  requires: []
  provides: [unified-weights-path-resolution, model_path-alias-removed, forward-slash-weights-writes]
  affects: [src/aquapose/engine/config.py, src/aquapose/training/run_manager.py]
tech_stack:
  added: []
  patterns: [project_dir-relative path resolution, as_posix() forward-slash normalization]
key_files:
  created: []
  modified:
    - src/aquapose/engine/config.py
    - src/aquapose/training/run_manager.py
    - tests/unit/training/test_run_manager.py
decisions:
  - "D-04: Remove model_path alias from _RENAME_HINTS as a pre-1.0 clean break; model_path is now an ordinary unknown field rejected by _filter_fields"
  - "D-03: Layer 3.5 already resolves both det_kwargs and pose_kwargs weights_path relative to project_dir; absolute paths honored via is_absolute() guard — verified, no changes needed"
  - "D-07: as_posix() in update_config_weights ensures YAML writes use forward slashes on all platforms; backslash leak was the root cause of 2 Windows test failures"
metrics:
  duration: "~8 minutes"
  completed_date: "2026-09-01"
  tasks_completed: 2
  files_changed: 3
---

# Phase 109 Plan 01: Config Alias Removal & Weights-Path Unification Summary

**One-liner:** Removed the pre-1.0 `model_path` alias from `_RENAME_HINTS` and fixed `run_manager.update_config_weights` to write forward-slash weights paths via `as_posix()`, fixing 2 Windows path-separator test failures.

## What Was Built

### Task 1: Remove model_path alias and verify unified weights_path resolution (config.py)

- Deleted the `"model_path": "weights_path"` entry from `_RENAME_HINTS` in `config.py` (D-04). The `model_path` field is now rejected by `_filter_fields` as an ordinary unknown field — no "did you mean" hint emitted.
- Added a comment to `_RENAME_HINTS` explaining the intentional absence of `model_path`.
- Added a docstring paragraph to `load_config` documenting the unified D-03 path-resolution convention (relative paths resolve against `project_dir`; absolute paths pass through) and the D-04 alias removal.
- Verified that layer 3.5 of `load_config` already resolves both `det_kwargs["weights_path"]` and `pose_kwargs["weights_path"]` relative to `project_dir` via `is_absolute()` guard — no code changes needed for D-03.

### Task 2: Forward-slash normalization in run_manager (D-07)

- In `update_config_weights`, changed `config[section]["weights_path"] = str(weights_path)` to use `Path(weights_path).as_posix()` — the stored variable `posix_weights` is used for both the YAML write and the `click.echo` confirmation line.
- Updated `test_register_trained_model_autocreates_store` assertion from `str(best_weights)` to `best_weights.as_posix()` to match the now-correct behavior (config stores forward-slash paths regardless of OS).

## Root-Cause Notes (D-02 discipline)

**test_update_config_weights_obb / test_update_config_weights_pose (2 failures fixed):**
Root cause: `str(Path(...))` on Windows yields backslashes (`\new\best.pt`); the tests correctly expected forward-slash form (`/new/best.pt`). Genuine platform bug in production code — fixed via `as_posix()` in `update_config_weights`. No test assertions were weakened; production behavior was corrected.

**test_register_trained_model_autocreates_store (1 stale assertion updated):**
Root cause: This test used `str(best_weights)` to assert the config-written value, which was only coincidentally correct before (on Linux). After the D-07 fix the written value is always forward-slash; the assertion was updated to `best_weights.as_posix()` to match correct behavior. The store's internal `weights_path` column (asserted separately) was not affected.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Stale str() assertion in test_register_trained_model_autocreates_store**
- **Found during:** Task 2
- **Issue:** After normalizing `update_config_weights` to use `as_posix()`, the existing test `test_register_trained_model_autocreates_store` asserted `str(best_weights)` (backslashes on Windows) against the config-written value, causing it to fail.
- **Fix:** Changed assertion to `best_weights.as_posix()` — the config now correctly stores forward-slash paths.
- **Files modified:** tests/unit/training/test_run_manager.py
- **Commit:** f214301

## Verification Results

```
hatch run pytest tests/unit/engine tests/unit/training/test_run_manager.py -q
206 passed in 7.24s
```

- `model_path` occurrence count in config.py: 0 (alias removed)
- Both `test_update_config_weights_obb` and `test_update_config_weights_pose` pass
- Written weights paths use forward slashes (`/new/best.pt`)
- No `@pytest.mark.skip` or `xfail` added

## Self-Check: PASSED

- src/aquapose/engine/config.py exists and contains `def update_config_weights` — wait, that's in run_manager.py. config.py exists and layer 3.5 is intact.
- src/aquapose/training/run_manager.py exists and contains `def update_config_weights` with `as_posix()`.
- Commits b4d5838 and f214301 exist in git log.
