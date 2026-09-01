---
phase: 109-correctness-green-test-suite-config-consolidation
reviewed: 2026-09-01T00:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - src/aquapose/engine/config.py
  - src/aquapose/training/run_manager.py
  - src/aquapose/training/store.py
  - src/aquapose/cli.py
  - pyproject.toml
  - tests/unit/training/test_run_manager.py
  - tests/unit/training/test_store.py
  - tests/unit/training/test_training_cli.py
  - tests/unit/evaluation/test_viz.py
  - tests/unit/training/test_reid_training.py
findings:
  critical: 0
  warning: 4
  info: 3
  total: 7
status: issues_found
---

# Phase 109: Code Review Report

**Reviewed:** 2026-09-01
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Reviewed the Phase 109 diff (base `b4d5838^`): the `model_path` alias removal and
weights-path resolution docs in `config.py`, forward-slash weights writes in
`run_manager.py`, the symlink→hardlink→copy fallback (`_link_or_copy`) plus
`list_models` ordering in `store.py`, utf-8 encoding fixes in `cli.py`, pyproject
URL corrections, and the associated test-fixture updates.

The core changes are correct in their intent. The `_link_or_copy` three-tier fallback
is sound: it correctly passes a relative target to `symlink_to` (relocatable) and the
absolute `src_abs` to `os.link`/`copy2`, catches the right exception classes, and
byte-equality holds for all three tiers. The `list_models` `rowid DESC` tiebreaker is
a legitimate determinism fix. No BLOCKER-level defects were found.

However, several correctness/quality gaps remain: an internal inconsistency where the
same weights path is persisted to the store with OS-native separators but to the config
YAML with POSIX separators (defeating the stated D-07 platform-neutrality goal for the
store record), a usability regression from the `model_path` removal, a silently-swallowed
copy fallback with no data-integrity verification, and two device-adaptive test fixtures
that convert an assertion-bearing test into a near-no-op path shape depending on hardware.

## Warnings

### WR-01: weights_path persisted inconsistently — store gets backslashes, config gets forward slashes

**File:** `src/aquapose/training/run_manager.py:252-253, 312, 320`
**Issue:** `update_config_weights` now normalizes the config YAML value with
`Path(weights_path).as_posix()` (forward slashes, D-07). But `register_trained_model`
registers the *same* weights file into the SampleStore with `weights_path=str(best_weights)`
(line 312), which yields backslashes on Windows. The two records for one physical file
therefore disagree on representation. This defeats the platform-neutrality goal of D-07 for
the store record, and any downstream code that cross-references the store's `weights_path`
against the config's `weights_path` (e.g. to detect "is this model already registered?")
will see a spurious mismatch on Windows. The fix normalized only one of the two write sites.
**Fix:**
```python
# run_manager.py register_trained_model — normalize before registering in store too
store.register_model(
    run_id=run_dir.name,
    weights_path=Path(best_weights).as_posix(),
    model_type=model_type,
    metrics=metrics,
    dataset_name=dataset_name,
    tag=tag,
)
```

### WR-02: `model_path` removal yields a non-actionable error instead of the documented migration hint

**File:** `src/aquapose/engine/config.py:595-601, 604-630`
**Issue:** The diff removed `"model_path": "weights_path"` from `_RENAME_HINTS` while
keeping the field out of every dataclass. Until this commit `model_path` was an accepted
alias; any project `config.yaml` still carrying `detection: {model_path: ...}` (or
`midline`/`pose`) will now fail `_filter_fields` via the generic `else` branch, producing
`DetectionConfig: unknown field 'model_path'` with no guidance. A "clean break" that
strands existing configs should still tell the user what to do. The docstring/comment
claim the break is intentional, but the removal simultaneously deletes the only mechanism
that would have made the break discoverable.
**Fix:** Keep a migration-only hint entry so the actionable message survives the removal:
```python
_RENAME_HINTS: dict[str, str] = {
    ...
    "model_path": "weights_path (alias removed in pre-1.0 clean break; rename the field)",
    ...
}
```
Alternatively, if the hint must be dropped, add a release-notes/CHANGELOG entry and a
targeted test asserting the error text guides migration.

### WR-03: copy fallback in `_link_or_copy` swallows both prior failures with no diagnostics or integrity check

**File:** `src/aquapose/training/store.py:52-64`
**Issue:** Both the symlink and hardlink attempts `pass` on `OSError` with no logging, and
the final `shutil.copy2` runs unconditionally as the catch-all. Three concerns:
(1) A genuine, non-recoverable error on the symlink attempt (e.g. `link_path` already exists
from a prior partial run, `FileExistsError` is an `OSError`) is silently reclassified as a
"no privilege" condition and masked; the operator gets no signal that the intended symlink
strategy was abandoned for every file in a large dataset. (2) The module now performs full
file copies (potentially thousands of images) silently — a materially different resource
profile from symlinking — with no `logger.debug`/`warning` breadcrumb. (3) If `copy2` itself
fails (e.g. disk full mid-dataset), the exception propagates from an arbitrary file leaving a
half-assembled dataset dir; `assemble` does not wrap the loop in cleanup.
**Fix:** Distinguish "privilege/cross-volume" fallbacks from unexpected errors and record which
tier was used:
```python
try:
    link_path.symlink_to(rel_target)
    return
except (OSError, NotImplementedError):
    pass
try:
    os.link(src_abs, link_path)
    return
except OSError:
    pass
logger.debug("Falling back to copy for %s (no symlink/hardlink)", link_path)
shutil.copy2(src_abs, link_path)
```
Consider logging once per `assemble()` call (which strategy was used) rather than per file.

### WR-04: device-adaptive reid fixtures change what the test actually exercises based on host hardware

**File:** `tests/unit/training/test_reid_training.py:493, 529`
**Issue:** `device="cuda" if torch.cuda.is_available() else "cpu"` makes the code path
under test hardware-dependent. On a GPU host the test runs the CUDA fine-tuning path; on a
CPU-only runner it runs the CPU path. These are different codepaths (dtype/device transfer,
autocast, pin_memory), so a passing result on one machine gives no assurance about the other,
and a regression that only manifests on CUDA (or only on CPU) can pass CI indefinitely. This
is acceptable for a `@pytest.mark.slow` smoke test but the two tests are the *only* end-to-end
coverage of `train_reid_end_to_end`; the non-determinism weakens the safety net. Note also
that these tests are `@slow` and thus excluded from `hatch run test`, so they contribute
nothing to the "green suite" gate on developer machines — the green-suite claim rests on CI
running them.
**Fix:** Either (a) pin `device="cpu"` and keep `crop_size=224` so the test deterministically
exercises one path everywhere (accepting the runtime cost, or shrinking `epochs`/`batch_size`
further), or (b) parametrize over available devices with an explicit
`pytest.mark.skipif(not torch.cuda.is_available())` CUDA variant so both paths are named and
their skip status is visible in the report, rather than silently collapsing to whichever the
host happens to have.

## Info

### IN-01: URL migration left a stale reference outside the reviewed scope

**File:** `pyproject.toml:47-50` (in scope) and `CODE_OF_CONDUCT.md:39` (out of scope)
**Issue:** The pyproject URLs were correctly updated to `McGrathLab/AquaPose`, but
`CODE_OF_CONDUCT.md:39` still points to the old `tlancaster6/aquapose/issues`. Not part of
the Phase 109 file set, but the URL migration is incomplete repo-wide.
**Fix:** Update the CODE_OF_CONDUCT reporting URL to `McGrathLab/AquaPose/issues` in a
follow-up.

### IN-02: layer 3.5 path resolution silently ignores the `segmentation` alias's own `weights_path` semantics

**File:** `src/aquapose/engine/config.py:694-698, 753-761`
**Issue:** The D-03 docstring names `detection.weights_path` and `midline.weights_path` as the
resolved fields. In practice YAML keys `segmentation`, `midline`, and `pose` all merge into
`pose_kwargs`, and `pose_kwargs["weights_path"]` is resolved — so the behavior is broader than
the docstring states (also resolves `segmentation.weights_path`, `pose.weights_path`). This is
harmless but the docstring undersells/mis-describes the actual coverage, which will mislead a
future maintainer reasoning about which keys resolve.
**Fix:** Update the D-03 docstring to say the resolved targets are `detection.weights_path` and
the pose bucket (`pose`/`midline`/`segmentation`).`weights_path`.

### IN-03: `_link_or_copy` docstring claims "cross-volume only" for copy, but copy also triggers on any hardlink OSError

**File:** `src/aquapose/training/store.py:38-40, 58-64`
**Issue:** The docstring says copy is "Used only when both symlink and hardlink are unavailable
(cross-volume paths)." In fact the `except OSError` around `os.link` catches *any* OSError
(permissions, unsupported FS, `FileExistsError`, ENOSPC transient, etc.), so copy is the
fallback for a broader set of conditions than "cross-volume." The comment overstates the
precision of the classification.
**Fix:** Reword to "Used when neither symlink nor hardlink succeed (cross-volume paths, or any
other hardlink failure)."

---

_Reviewed: 2026-09-01_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
