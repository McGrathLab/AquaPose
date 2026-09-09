---
phase: quick-260909-lkw
plan: 01
subsystem: testing
tags: [pytest, pseudo-labels, glob-ordering, test-defect]

# Dependency graph
requires:
  - phase: 113.1-06 / 113.2
    provides: prior OBB-label assertion in test_generates_merged_obb_and_separate_pose
      (first pinned to len==2, later relaxed to len>=1)
provides:
  - Deterministic named-file OBB label assertions in test_pseudo_label_cli.py
  - Closed, corrected diagnosis for the gap-fish platform-variance todo
affects: [pseudo-label-generation-tests, training-data-pipeline-todos]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Assert against named output files instead of glob(...)[0] when filenames
      are deterministic — Path.glob() does not guarantee order across filesystems."

key-files:
  created: []
  modified:
    - tests/unit/training/test_pseudo_label_cli.py
    - .planning/todos/done/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md

key-decisions:
  - "No src/ file was modified — the diagnosis found no production defect; only
    the test's unordered glob()[0] selection was wrong."
  - "Closed the mis-diagnosed todo with a Resolved section rather than deleting
    it, preserving the historical record and appending corrected evidence."

patterns-established:
  - "Pattern: Assert against named output files instead of glob(...)[0] when
    filenames are deterministic."

requirements-completed: []

# Metrics
duration: 12min
completed: 2026-09-09
---

# Quick Task 260909-lkw: Fix gap-fish pseudo-label test defect Summary

**Replaced an unordered `glob("*.txt"))[0]` file selection in a pseudo-label test with deterministic named-file assertions, and closed a todo that had wrongly diagnosed the resulting platform variance as a production bug.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-09-09T19:26:00Z (approx)
- **Completed:** 2026-09-09T19:38:31Z
- **Tasks:** 2/2 completed
- **Files modified:** 2

## Accomplishments
- `test_generates_merged_obb_and_separate_pose` now asserts exact line counts
  (`000000_cam1.txt` == 2 lines, `000000_cam0.txt` == 1 line) against named
  files instead of an unordered `glob(...)[0]` selection, restoring the merge
  coverage Phase 113.1-06 intended without reintroducing platform fragility.
- Kept and generalized the 9-token-per-line format check across both files,
  preserving the invariant that guards against the original whole-file
  `.split()` defect.
- Closed `.planning/todos/pending/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md`
  with a corrected diagnosis: the "platform variance" was `Path.glob()`
  non-determinism in the test, not a defect in
  `src/aquapose/training/pseudo_label_cli.py`. No production code was touched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Pin OBB label assertions to named files** - `4ddc447` (test)
2. **Task 2: Resolve the mis-diagnosed platform-variance todo** - `60ebfe2` (docs, git mv rename) + `602c6ea` (docs, closure content)

_Note: Task 2's git mv staged an empty-diff rename before the closure section
content was appended/fixed, so the content landed as a separate follow-up
commit (`602c6ea`) rather than being folded into `60ebfe2`. Both commits are
part of Task 2's atomic unit of work — the rename and its content are
inseparable in intent, just split across two commits due to staging order._

## Files Created/Modified
- `tests/unit/training/test_pseudo_label_cli.py` - Replaced `glob("*.txt"))[0]`
  selection with named-file reads (`000000_cam1.txt`, `000000_cam0.txt`),
  exact line-count assertions, and a 9-token-per-line format check looped over
  both files. Removed the stale comment referencing the now-closed todo.
- `.planning/todos/done/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md`
  (moved from `.planning/todos/pending/` via `git mv`) - Original Problem/Why
  it matters/Investigation/Solution/Notes body preserved verbatim; appended a
  `## Resolved` section with the real cause, disproving evidence, and an
  explicit non-defect statement for `pseudo_label_cli.py`.

## Deviations from Plan

None - plan executed exactly as written. The only note is a mechanical one:
Task 2's `git mv` staged the rename with the file's pre-closure content
(matching the pending file byte-for-byte, hence a 0-line diff), so the
appended `## Resolved` section and the mid-edit format fix landed in a
separate follow-up commit rather than in the rename commit itself. This does
not affect the plan's must-haves — both commits are present in history, the
file lives only under `.planning/todos/done/`, and the closure content is
fully intact at `HEAD`.

## Verification Results

- `hatch run test -k test_generates_merged_obb_and_separate_pose` - 1 passed
- `hatch run test` (full fast suite) - 1410 passed, 2 skipped, 17 deselected,
  0 failed
- `hatch run ruff format --check tests/unit/training/test_pseudo_label_cli.py` -
  clean (after one auto-format pass)
- `hatch run ruff check tests/unit/training/test_pseudo_label_cli.py` - clean
- `git status --porcelain` - confirmed zero files under `src/` touched at
  every commit boundary
- `grep -rn "gap-fish-pseudo-label-emission-varies-by-platform" tests/` -
  no matches (stale comment reference removed)
- Todo-closure automated check (path moved, `glob` and
  `not found to be defective` both present in closed file) - PASS

## Known Stubs

None.

## Self-Check: PASSED

- FOUND: tests/unit/training/test_pseudo_label_cli.py
- FOUND: .planning/todos/done/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md
- MISSING (expected): .planning/todos/pending/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md (moved, confirmed absent)
- FOUND commit 4ddc447 in `git log --oneline --all`
- FOUND commit 60ebfe2 in `git log --oneline --all`
- FOUND commit 602c6ea in `git log --oneline --all`

## Next Steps
- None required by this task. The corrected todo record is closed; no
  follow-up production investigation is warranted per its own Resolved
  section.
