---
phase: 108-branch-reconciliation-repo-hygiene
plan: 04
subsystem: docs
tags: [milestones, project-record, git-archaeology, backfill]

requires:
  - phase: 108-01
    provides: "main's 665-file .planning/ historical archive tracked on dev, including .planning/milestones/v2.2-phases/ (the v2.2 source material)"
  - phase: 108-03
    provides: "clean working tree, .planning/ un-ignored"
provides:
  - "MILESTONES.md contains a v3.11 Appearance-Based ReID entry (REC-01), reconstructed from ROADMAP.md and .planning/phases/102-107/"
  - "MILESTONES.md contains a v2.2 Backends entry, reconstructed from .planning/milestones/v2.2-phases/29-* through 33.1-*"
  - "MILESTONES.md reads strictly newest-first by ship date across all 16 entries (v1.0/v2.0/v2.1 tail re-sorted)"
affects: [108-05]

tech-stack:
  added: []
  patterns:
    - "Reachable-ancestor verification (git merge-base --is-ancestor) before trusting any git-log-derived milestone metric, after discovering dev's history contains orphaned/duplicate commits from a prior history rewrite"

key-files:
  created: []
  modified:
    - .planning/MILESTONES.md

key-decisions:
  - "v3.11 plan/task counts measured only over the 4 *-PLAN.md files that survive on disk (102-01, 102-02, 105-01, 105-02; 12 tasks) — phases 103, 104, 106, 107 have SUMMARYs but no surviving PLAN files, so the entry documents this as an undercount rather than estimating a true total (T-108-18)."
  - "v3.11 Timeline/Codebase/Git range derived via git log/diff exactly as the plan specified: git log on .planning/phases/10[2-7]-* (all commits land on 2026-03-25 local time; ROADMAP's 2026-03-26 'shipped' date is a UTC/local timezone artifact, not a discrepancy in the work itself) and git diff --shortstat a33f25e^..19f612b (55 commits, 42 files, +9,136/-0 — the milestone was purely additive, no existing files touched)."
  - "v2.2 Timeline/Codebase/Git range required deviating from a naive path-scoped git log: git log -- .planning/phases/29-guidebook-audit (the original pre-archival path) returned a first commit (ae2cecb) that git merge-base --is-ancestor proved is NOT reachable from HEAD or from the phase's own last commit — an orphaned duplicate from an earlier history rewrite. Re-derived using the first commit that IS a verified ancestor (6f94652) through the last real content commit before the archival move (c3046bd, verified reachable): 69 commits, 109 files changed (+14,513/-883), 23,903 LOC source. Documented in the commit message rather than silently trusting the first git log hit."
  - "v2.2 Known gaps sourced directly from the two VERIFICATION.md files with status: gaps_found (Phase 31's stale yolo-bbox/--resume ROADMAP-REQUIREMENTS mismatches; Phase 33.1's undeclared AUG-01..04 requirement IDs) rather than re-auditing the milestone."

patterns-established:
  - "Verify git-log-derived milestone dates/ranges against merge-base ancestry before use — a naive 'first/last commit touching this path' can silently pick up an unreachable duplicate commit in a repo with rewritten history."

requirements-completed: [REC-01]

duration: 40min
completed: 2026-08-17
---

# Phase 108 Plan 04: Milestone Record Backfill Summary

**Backfilled the missing v3.11 Appearance-Based ReID (REC-01) and v2.2 Backends milestone entries into MILESTONES.md from ROADMAP.md and the phase/SUMMARY record, then re-sorted the file's broken tail into strict newest-first chronological order — every numeric field either measured from git or explicitly omitted, never estimated.**

## Performance

- **Duration:** ~40 min
- **Tasks:** 3/3 completed
- **Files modified:** 1 (`.planning/MILESTONES.md`, 3 commits — one per task)

## Accomplishments

- `.planning/MILESTONES.md` now opens with `## v3.11 Appearance-Based ReID (Shipped: 2026-03-26)`, positioned above v3.10, with 7 accomplishments each traceable to a named Phase 102-107 SUMMARY/VERIFICATION file. Plan/task counts are honestly scoped to the 4 `*-PLAN.md` files that survive on disk (12 tasks) with an explicit note that phases 103/104/106/107 lack surviving PLAN files. Timeline (1 day, 2026-03-25), Codebase (37,308 LOC at `19f612b`), and Git range (55 commits, 42 files, +9,136/-0) are all measured via `git log`/`git diff --shortstat`, not estimated.
- `.planning/MILESTONES.md` now contains `## v2.2 Backends (Shipped: 2026-03-01)` directly below v3.0, with 6 accomplishments traceable to the 12 SUMMARY files under `.planning/milestones/v2.2-phases/` (the archive the 108-01 merge brought onto `dev`). The source-archive gate (`git ls-files .planning/milestones/v2.2-phases | wc -l` = 41, well above the 0/35 thresholds) was checked before writing. Timeline (1 day, 2026-02-28), Codebase (23,903 LOC at `c3046bd`), and Git range (69 commits, 109 files, +14,513/-883) required discovering and routing around an orphaned duplicate commit in `dev`'s history (see Deviations).
- All 16 milestone entries now read strictly newest-first by `(Shipped: ...)` date: v3.11, v3.10, ..., v3.0, v2.2, v2.1, v2.0, v1.0. The `v1.0`/`v2.0`/`v2.1` blocks were moved as whole units with zero content edits — verified by comparing the blank-stripped, sorted line multiset of the file before and after the move (byte-identical). Double-blank-line separators between the moved entries were normalized to single blank lines during the move, as instructed.
- `(none recorded)` (v2.1's un-backfilled accomplishment list, D-21's explicit exclusion) still occurs exactly once in the file after all three tasks — no archaeology beyond v3.11/v2.2 was performed.
- The diff across all three commits touches exactly `.planning/MILESTONES.md` and nothing else; nothing was pushed to any remote (`git log --oneline origin/dev..dev` shows 29 unpushed commits after this plan, consistent with the phase's single push being deferred to 108-05).

## Task Commits

1. **Task 1: Backfill the v3.11 Appearance-Based ReID entry** — `1d35637` (docs)
2. **Task 2: Backfill the v2.2 Backends entry from the merged archive** — `2a0f440` (docs)
3. **Task 3: Re-sort the tail into chronological order** — `a87ec03` (docs)

## Files Created/Modified

- `.planning/MILESTONES.md` — two new milestone entries inserted (v3.11 at top, v2.2 below v3.0), then the v1.0/v2.0/v2.1 tail block-moved into `v2.1, v2.0, v1.0` order with separator normalization only.

## Measured Plan/Task Counts (per plan's `<output>` instruction)

| Milestone | Phases | PLAN.md files on disk | Tasks (from `<task` count) | Note |
|---|---|---|---|---|
| v3.11 Appearance-Based ReID | 6 (102-107) | 4 (102-01, 102-02, 105-01, 105-02) | 12 | 103, 104, 106, 107 have SUMMARYs but no surviving PLAN.md — true plan/task volume is undercounted; documented in the entry's Known gaps |
| v2.2 Backends | 6 (29-33.1) | 11 (complete set) | 35 | Complete record — every phase has both PLAN and SUMMARY files on disk |

## Omitted Schema Fields and Why

- **v3.11:** No field was omitted — Timeline, Codebase, and Git range were all cheaply derivable (git log on the phase-doc paths; `git diff --shortstat` over a clean reachable range) and are included.
- **v2.2:** No field was omitted in the final entry, but the derivation method for Timeline/Codebase/Git range was **not** the plan's literally-specified path-scoped `git log` (that path's first commit, `ae2cecb`, proved unreachable from `HEAD` — see Deviations below). Instead these fields were derived from a verified-reachable commit pair (`6f94652`..`c3046bd`), which is the closest honest analog to the specified method.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in derivation method, not in prior work] `git log -- .planning/phases/29-guidebook-audit` returned an unreachable orphaned commit as the "first" v2.2 commit**
- **Found during:** Task 2, deriving v2.2's Timeline/Codebase/Git range fields
- **Issue:** `git log --all --reverse -- .planning/phases/29-guidebook-audit` (following the pre-archival path) returned `ae2cecb` (`docs(29): capture phase context`, dated 2026-02-28) as the earliest commit touching that path. `git merge-base --is-ancestor ae2cecb HEAD` and `... ae2cecb c3046bd` both failed — `ae2cecb` is not reachable from `dev`'s current history at all (`git branch --all --contains ae2cecb` returns nothing), meaning it is an orphaned duplicate left over from a prior history rewrite (consistent with duplicate-hash commit pairs observed elsewhere in this date range, e.g. two distinct hashes for "feat(32-02): extend Overlay2DObserver..."). Using it as the range start would have produced a `git diff --shortstat` computed across a non-ancestor pair — numbers that `git diff` would still print but that would not correspond to any real, reachable set of changes.
- **Fix:** Re-ran the search restricted to reachable history (`git log` without `--all`), found `6f94652` (same commit message, same date, verified `git merge-base --is-ancestor 6f94652 HEAD` and `...6f94652 c3046bd` both succeed) as the true earliest reachable commit for phase 29. Used `6f94652`..`c3046bd` (the last real content commit before the archival move, also verified reachable) for all three derived fields: 69 commits, 109 files changed (+14,513/-883) full-repo, 23,903 LOC source at `c3046bd`.
- **Files modified:** none beyond the intended `.planning/MILESTONES.md` edit — this was a derivation-method correction, not a code change.
- **Commit:** `2a0f440` (the correct, reachable-history-derived numbers are what landed in the entry; the discovery itself is documented in the commit message and here, not in a separate commit)

### Notes

- The plan's `<context>` block states ship dates as "verified facts — do not re-derive." Those dates (v3.11: 2026-03-26; v2.2: 2026-03-01) were used verbatim for the `(Shipped: ...)` headings. Separately, when deriving each entry's `Timeline` field via `git log`, every commit touching the relevant `.planning/phases/` paths showed a local commit date one calendar day earlier (2026-03-25 for v3.11, 2026-02-28 for v2.2) than the corresponding ROADMAP-stated ship date. This is consistent with a `-0400` local-timezone vs. UTC boundary effect (commits made late at night local time land on the next UTC day) and was treated as expected, not as a contradiction requiring reconciliation — the two fields (`Shipped:` heading vs. `Timeline:` body) serve different purposes and both instructions were followed independently.

## Self-Check: PASSED

- `.planning/MILESTONES.md` exists and contains `## v3.11 Appearance-Based ReID (Shipped: 2026-03-26)`: confirmed via `grep -cx`, returns `1`
- `.planning/MILESTONES.md` contains `## v2.2 Backends (Shipped: 2026-03-01)`: confirmed via `grep -cx`, returns `1`
- Ship dates strictly descending across all 16 `## v` headings: confirmed via `sort -r` round-trip diff (no output)
- `grep -c '(none recorded)' .planning/MILESTONES.md` → `1` (unchanged across all three tasks)
- `grep -c '^## v' .planning/MILESTONES.md` → `16`
- Blank-stripped sorted-line multiset identical before/after Task 3's re-sort: confirmed via `diff` (no output) against `HEAD~1:.planning/MILESTONES.md`
- `git diff --name-only HEAD~3 HEAD | tr '\n' ' '` → `.planning/MILESTONES.md ` (only file touched across all three commits)
- `git status --porcelain` → empty
- Commits `1d35637`, `2a0f440`, `a87ec03` all exist: confirmed via `git log --oneline -3`
- `git log --oneline origin/dev..dev | wc -l` → `29` (nothing pushed)
