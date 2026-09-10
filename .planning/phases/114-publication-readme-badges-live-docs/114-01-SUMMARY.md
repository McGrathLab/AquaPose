---
phase: 114-publication-readme-badges-live-docs
plan: 01
subsystem: docs
tags: [readme, repo-hygiene, requirements-tracking, zenodo, todos]

# Dependency graph
requires:
  - phase: 111-example-dataset-reference-outputs
    provides: Zenodo tutorial deposit (10.5281/zenodo.22264079) naming the hero-media source assets
  - phase: 113-concepts-tutorial
    provides: DOI backfill (113-06) that made the stale Zenodo-upload todo obsolete
provides:
  - Two visitor-facing GitHub URLs (CODE_OF_CONDUCT.md, docs/contributing.md) pointing at McGrathLab/AquaPose instead of the tlancaster6 rename redirect
  - README-03 recorded as deferred (not silently dropped) in REQUIREMENTS.md and ROADMAP.md, with original criterion/requirement text preserved
  - A backlog todo naming the two existing hero-media source assets and the GitHub-embed format constraints for whoever picks README-03 back up
  - Stale Zenodo-upload todo retired to todos/done/ with a closure note
affects: [114-04-readme-rewrite, 114-07-pass-b-doi-backfill]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Deferral bookkeeping: annotate ROADMAP/REQUIREMENTS with an indented italic sub-bullet naming the backlog todo, never delete or rewrite the original criterion text"

key-files:
  created:
    - .planning/todos/pending/2026-09-09-readme-hero-media-3d-reconstruction.md
  modified:
    - CODE_OF_CONDUCT.md
    - docs/contributing.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/todos/done/2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md (moved from pending/ via git mv)

key-decisions:
  - "Also corrected docs/contributing.md's `cd aquapose` to `cd AquaPose` to match the new clone URL's casing — a case-sensitive filesystem (Linux/macOS) would fail the cd after cloning McGrathLab/AquaPose.git otherwise (Rule 1 bug fix, not in the plan's literal action text)"
  - "CHANGELOG.md's ~829 historical tlancaster6 links left untouched per D-13 — historical record, GitHub redirects renamed repos"

patterns-established:
  - "Requirement deferral bookkeeping: keep bullet/checkbox verbatim, append inline deferral annotation naming the todo filename; traceability table status cell gets free-text deferral note matching existing DOCS-07/DATA-02/QA-06 style"

requirements-completed: [README-03]

# Metrics
duration: 12min
completed: 2026-09-10
---

# Phase 114 Plan 01: URL Hygiene and README-03 Deferral Bookkeeping Summary

**Fixed the two visitor-facing tlancaster6 GitHub URLs and recorded README-03's hero-media deferral across REQUIREMENTS.md, ROADMAP.md, and a new backlog todo, while retiring a stale, already-completed Zenodo-upload todo.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-09-10T12:38:00Z (approx)
- **Completed:** 2026-09-10T12:50:19Z
- **Tasks:** 2 completed
- **Files modified:** 6 (2 URL fixes, 2 requirements-tracking files, 1 new todo, 1 moved+annotated todo)

## Accomplishments

- `CODE_OF_CONDUCT.md` and `docs/contributing.md` now point at `https://github.com/McGrathLab/AquaPose` — no visitor-facing page routes through the reclaimable `tlancaster6/aquapose` rename redirect (D-13, T-114-01-01/02 mitigated).
- README-03 is verifiably deferred, not dropped: `.planning/REQUIREMENTS.md`'s bullet, checkbox, and traceability row are unchanged in substance and carry a deferral annotation; `.planning/ROADMAP.md`'s Phase 114 success criterion 3 keeps its original text with a `DEFERRED` sub-bullet beneath it.
- A new backlog todo (`2026-09-09-readme-hero-media-3d-reconstruction.md`) names the two existing Zenodo deposit assets (`reference_outputs/animation_3d.html`, `reference_outputs/overlay_mosaic.mp4`) and the GitHub `<iframe>`-stripping / PyPI absolute-URL constraints a future implementer needs.
- The superseded `2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md` todo is moved to `todos/done/` via `git mv` (history preserved) with a closure note naming plan `113-06` and DOI `10.5281/zenodo.22264079`.

## Task Commits

1. **Task 1: Point the two visitor-facing GitHub URLs at McGrathLab/AquaPose** - `bca5e2c` (fix)
2. **Task 2: Record README-03's deferral in REQUIREMENTS, ROADMAP, and a backlog todo** - `2eb116c` (docs)

## Files Created/Modified

- `CODE_OF_CONDUCT.md` - enforcement-contact URL now `https://github.com/McGrathLab/AquaPose/issues`
- `docs/contributing.md` - clone URL now `https://github.com/McGrathLab/AquaPose.git`; `cd` target corrected to match casing
- `.planning/REQUIREMENTS.md` - README-03 bullet + traceability row annotated deferred
- `.planning/ROADMAP.md` - Phase 114 success criterion 3 annotated `DEFERRED` beneath unchanged criterion text
- `.planning/todos/pending/2026-09-09-readme-hero-media-3d-reconstruction.md` - new backlog todo, created
- `.planning/todos/done/2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md` - moved from `pending/` via `git mv`, closure note appended

## Decisions Made

- Extended the `docs/contributing.md` fix to also correct `cd aquapose` → `cd AquaPose` beyond the plan's literal two-URL scope, because leaving the old lowercase `cd` target would break the documented setup flow on case-sensitive filesystems after the clone URL casing changed (Rule 1 auto-fix — a bug directly caused by this task's own edit, not a scope expansion).
- Followed the DOCS-07/DATA-02/QA-06 free-text-note style for the README-03 traceability row rather than inventing a new status vocabulary.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected `cd aquapose` to `cd AquaPose` in docs/contributing.md**
- **Found during:** Task 1
- **Issue:** The plan's action text specified only the `git clone` URL change. Leaving `cd aquapose` (lowercase) after changing the clone target to `McGrathLab/AquaPose.git` would break the documented setup command on case-sensitive filesystems, since `git clone` creates a directory matching the URL's repo-name casing.
- **Fix:** Changed `cd aquapose` to `cd AquaPose` in the same edit.
- **Files modified:** `docs/contributing.md`
- **Verification:** `hatch run docs:build` still exits 0; the sweep for remaining `tlancaster6` outside `CHANGELOG.md`/`.planning/` returns nothing.
- **Committed in:** `bca5e2c` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix, Rule 1)
**Impact on plan:** Necessary for correctness of the edited setup instructions on non-Windows systems. No scope creep — the fix is strictly within the file the task already touches.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both visitor-facing repo-hygiene fixes (D-13) are closed; `docs/contributing.md` is safe for Plan 04 (Wave 2) to edit next without carrying a stale clone URL forward.
- README-03's deferral is fully recorded; Plan 04's README rewrite does not need to address hero media and can cite this todo if the topic comes up.
- `hatch run docs:build` exits 0 and `hatch run test` passes (1410 passed, 2 skipped, 17 deselected) — no regression introduced, consistent with this plan touching no source code.
- No blockers for Wave 1's remaining plans (114-02, 114-03).

---
*Phase: 114-publication-readme-badges-live-docs*
*Completed: 2026-09-10*
