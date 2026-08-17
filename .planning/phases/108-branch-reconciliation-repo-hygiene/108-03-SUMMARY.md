---
phase: 108-branch-reconciliation-repo-hygiene
plan: 03
subsystem: infra
tags: [gitignore, repo-hygiene, dead-code, working-tree-cleanup]

requires:
  - phase: 108-02
    provides: "AGPL-relicensed repo with pyproject.toml closed for the rest of the phase"
provides:
  - "git check-ignore .planning/<any-untracked-path> exits non-zero — .planning/ is tracked normally, no more git add -f for GSD commits"
  - "the complete project record is in git history: 108-01's 665-file historical archive plus the 6 previously invisible .planning/todos/ files"
  - "tests/integration/segmentation dead package removed; live src/aquapose/core/{reconstruction,tracking} untouched and importable"
  - "clean working tree: no 11.0 pip log, no stray ./~ directory, no top-level src/aquapose/{reconstruction,segmentation,tracking,visualization} residue"
affects: [108-04, 108-05]

tech-stack:
  added: []
  patterns:
    - "Un-ignore-then-audit: remove a stale .gitignore rule, let git status surface exactly what becomes visible, and gate the resulting commit on detect-secrets plus manual credential greps before staging"

key-files:
  created: []
  modified:
    - .gitignore
  deleted:
    - tests/integration/segmentation/__init__.py
    - src/aquapose/reconstruction (untracked residue, not a git deletion)
    - src/aquapose/segmentation (untracked residue, not a git deletion)
    - src/aquapose/tracking (untracked residue, not a git deletion)
    - src/aquapose/visualization (untracked residue, not a git deletion)
    - 11.0 (untracked, not a git deletion)
    - ./~ (untracked, not a git deletion; quarantined then permanently deleted per user decision)

key-decisions:
  - "pyproject.toml ownership: this plan never touched pyproject.toml. Its key-link contract cites [tool.hatch.build.targets.sdist] exclude = ['.planning/', ...] as 'what makes un-ignoring .planning/ safe' — that exclude was already present (added by 108-01's merge, confirmed unmodified by 108-02) and needed no edit here. `git diff --exit-code HEAD -- pyproject.toml` is clean across every commit in this plan. 108-02's 'closed for the rest of the phase' claim on the file held; no conflict materialized. Flagging explicitly per dispatch instruction so 108-05/phase verification can confirm the same."
  - "OI-02 resolved as 'delete', not 'keep' or 'relocate': plan text anticipated the tilde directory held downloaded SAM2 model weights justifying a quarantine-first approach. On measurement, checkpoints/ contained only download_ckpts.sh (2.7 KB) — no weights were ever downloaded. This corrected premise was surfaced to the user at the checkpoint before any deletion; the user then explicitly chose 'delete' knowing the 192 MB was almost entirely the .git clone (129 MB of .git/objects) plus demo/notebook assets, re-obtainable from GitHub. Quarantine step (../aquapose-quarantine-108/) still ran first per the plan's OI-02 mitigation, and was only rm -rf'd after the explicit user reply."
  - "Absolute-Windows-path grep count (T-108-15, accept disposition): 116 files under .planning/ contain 'C:\\Users' paths naming the already-public author's local machine. Recorded per plan's <output> instruction; not scrubbed, matching D-19/T-108-15's accept disposition."

patterns-established: []

requirements-completed: [FOUND-04]

duration: ~35min
completed: 2026-08-17
---

# Phase 108 Plan 03: Repo Hygiene (.gitignore, Dead Code, Working Tree) Summary

**Un-ignored `.planning/` to end the `git add -f` friction (D-18), deleted the dead `tests/integration/segmentation` package (D-20), and cleared the working tree of `11.0`, four stale top-level `src/aquapose/` residue directories, and a 192 MB stray `~/` directory holding an unused SAM2 source clone — the last removed only after a checkpoint correcting the plan's "downloaded model weights" assumption and an explicit user "delete" decision.**

## Performance

- **Duration:** ~35 min (including one blocking-human checkpoint)
- **Tasks:** 3/3 completed
- **Files modified:** 1 modified (`.gitignore`), 6 newly tracked (`.planning/todos/`), 1 deleted (`tests/integration/segmentation/__init__.py`); 6 untracked filesystem paths removed (4 residue dirs, `11.0`, `./~`)

## Accomplishments

- `.gitignore`'s `.planning/` rule (line 102) is gone — a single-line deletion, no rule added, matching D-19's ban on defensive ignore entries. `git check-ignore` now exits non-zero for `.planning/` paths (verified against an untracked todo file, since already-tracked files like `STATE.md` were never reported as ignored by `check-ignore` regardless of the rule — the untracked-file test is the one that actually exercises the pattern).
- The 6 previously invisible `.planning/todos/{completed,pending}/*.md` files are now tracked — exactly the set the plan predicted, verified via `git status --porcelain .planning/` before staging. `detect-secrets --all-files` passed, targeted credential/PEM/token greps found zero hits, no file exceeded 1 MB, and `.secrets.baseline` was not touched.
- `git ls-files .planning` is now 712 (was 706 pre-plan); `.planning/todos` is 25; `.planning/milestones/v2.2-phases` is 41 (the archive 108-04 needs, still intact).
- The empty `tests/integration/segmentation/__init__.py` package (a v3.7 segmentation-removal leftover, docstring-only, zero references anywhere outside `.planning/`) was `git rm`'d. Integration test collection still succeeds (12 tests collected, 0 errors) and `docs/api` retains its correct 8-file set.
- The four top-level `src/aquapose/{reconstruction,segmentation,tracking,visualization}` directories — confirmed to hold zero non-`.pyc` files and zero tracked paths each — were deleted from disk. This is what ROADMAP criterion 4 actually meant; the same-named `src/aquapose/core/{reconstruction,tracking}` production modules were left untouched and still import cleanly.
- `11.0` (an 11 KB `pip install boxmot` log, never tracked) was deleted unconditionally per D-19.
- The stray literal-tilde directory was **not** blindly deleted. It was measured first (192 MB total, 129 MB of which is `.git/objects` — the clone's own history), moved to `../aquapose-quarantine-108/tilde/` outside the repo, and the move verified byte-for-byte (same 192 MB, `PycharmProjects/sam2` intact) before pausing at the mandated blocking-human checkpoint (T-108-12).
- **Checkpoint correction:** the plan's premise — that `checkpoints/` held "downloaded model weights" — was factually wrong. The directory contained only `download_ckpts.sh` (2.7 KB); no weights were ever downloaded. This was surfaced explicitly to the user before any destructive action, per T-108-12's mitigation design.
- **User decision: delete.** After the corrected picture, the user explicitly chose "delete." `../aquapose-quarantine-108/` (including `tilde/PycharmProjects/sam2`) was permanently removed with `rm -rf` only after that reply.
- Post-deletion, `git status --porcelain` is empty (FOUND-04 satisfied) and `hatch run python -c "import aquapose.core.reconstruction, aquapose.core.tracking"` still exits 0.
- `pyproject.toml` was never edited by this plan (see Files Created/Modified below and the pyproject.toml ownership note).
- Nothing was pushed to any remote.

## Task Commits

1. **Task 1: Un-ignore `.planning/` and commit the previously invisible files** — `852fcd8` (chore)
2. **Task 2: Delete the dead `tests/integration/segmentation` package** — `6adf69f` (chore)
3. **Task 3: Clear the working tree — checkpoint gate on SAM2 model weights** — no commit required (all changes were to previously-untracked paths); the quarantine-then-delete sequence ran entirely outside git.

## Files Created/Modified

- `.gitignore` — removed the single `.planning/` line (line 102). No other line touched.
- `.planning/todos/completed/2026-03-09-taper-confidence-for-extrapolated-midline-points.md`, `.planning/todos/pending/2026-03-06-*.md`, `2026-03-10-*.md`, `2026-03-11-*.md`, `2026-03-12-iterate-*.md`, `2026-03-12-triangulate-*.md` — newly tracked (6 files).
- `tests/integration/segmentation/__init__.py` — deleted (`git rm`).
- `src/aquapose/reconstruction/`, `src/aquapose/segmentation/`, `src/aquapose/tracking/`, `src/aquapose/visualization/` — deleted from disk (never tracked; pure `__pycache__` residue).
- `11.0`, `./~` (and everything under it, including `PycharmProjects/sam2`) — deleted from disk (never tracked).
- `pyproject.toml` — **not modified.** See key-decisions above.

## Decisions Made

- pyproject.toml ownership question (raised at dispatch): this plan needed no edit to `pyproject.toml`. Its `[tool.hatch.build.targets.sdist] exclude = [".planning/", ".claude/", ".hooks/"]` block — the fact the key-link contract cites as making D-18 safe — was already present from 108-01's merge and untouched by 108-02. `git diff --exit-code HEAD -- pyproject.toml` is clean at every point in this plan's execution. No conflict with 108-02's "closed for the rest of the phase" claim materialized; 108-05 or phase verification can treat `pyproject.toml` as still fully owned by 108-02's final state.
- OI-02 resolution: "delete" (user's explicit, informed choice after the checkpoint's premise correction — see Deviations).
- Absolute-path grep count: 116 files under `.planning/` contain `C:\Users` style paths naming the repo's already-public author. Recorded per the plan's `<output>` spec; not scrubbed (T-108-15 accept disposition, D-19).

## Deviations from Plan

### Auto-fixed Issues

None — no bugs, missing functionality, or blocking issues required Rule 1/2/3 fixes in this plan.

### Checkpoint / Premise Correction

**1. [Checkpoint gate — corrected a factual premise in the plan and threat model before acting] "Downloaded model weights" assumption was wrong**
- **Found during:** Task 3, step 3 (measuring the tilde directory before any move/delete)
- **Issue:** The plan's `<action>`, `<what-built>`, and the threat register's T-108-12 all describe the tilde directory as containing "192 MB of SAM2 model weights" / "checkpoints ... not trivially re-obtainable offline." Measurement showed `checkpoints/` held only `download_ckpts.sh` (2.7 KB) — the download script itself, never run. The actual 192 MB is 129 MB of `.git/objects` (the SAM2 GitHub clone's history) plus demo/notebook assets.
- **Resolution:** Did not proceed on the plan's stated premise. Surfaced the corrected picture explicitly at the mandated checkpoint before offering the keep/relocate/delete choice, so the user's decision was informed by facts rather than the plan's inaccurate description. The user then chose "delete" specifically because no weights were at stake — a decision that would not have been well-founded under the plan's original (incorrect) framing.
- **Files/paths affected:** `../aquapose-quarantine-108/` (created, then permanently removed after user confirmation)
- **Commit:** N/A — quarantine and deletion both occurred outside git version control (the path was never tracked)

### Notes

- `git check-ignore .planning/STATE.md` alone (as literally written in the plan's `<verify>` block) is **not** a valid test of the un-ignore — `STATE.md` is tracked, and `git check-ignore` reports tracked paths as "not ignored" independent of matching `.gitignore` patterns. The acceptance criterion was validated instead against an untracked `.planning/todos/` path both before and after the edit, which correctly showed rule-match → no-match.

## Self-Check: PASSED

- `.gitignore` — `grep -c '^\.planning/$' .gitignore` → `0`; `git diff HEAD~1 HEAD -- .gitignore` → 1 line removed, 0 added (confirmed at commit `852fcd8`)
- `git ls-files .planning` → `712`; `git ls-files .planning/todos` → `25`; `git ls-files .planning/milestones/v2.2-phases` → `41` (confirmed)
- `git status --porcelain .planning/` → empty (confirmed)
- `hatch run pre-commit run detect-secrets --all-files` → Passed (confirmed at commit time)
- `git diff --exit-code HEAD -- .secrets.baseline` → clean (confirmed)
- `find .planning -type f -size +1M` → no output (confirmed)
- `test -e tests/integration/segmentation` → non-zero / does not exist (confirmed)
- `git ls-files tests/integration` → `2`; `git ls-files docs/api` → `8`, none of the 4 dead `.rst` files present (confirmed)
- `hatch run pytest tests/integration --collect-only -q` → 12 tests collected, 0 errors (confirmed)
- `test -e src/aquapose/{reconstruction,segmentation,tracking,visualization}` → all non-zero / do not exist (confirmed)
- `test -d src/aquapose/core/{reconstruction,tracking}` → both exist (confirmed)
- `hatch run python -c "import aquapose.core.reconstruction, aquapose.core.tracking"` → exit 0 (confirmed, re-run after quarantine deletion)
- `git status --porcelain` → empty (confirmed, re-run after quarantine deletion)
- `test -e ../aquapose-quarantine-108/` → non-zero / does not exist (confirmed, post user-decision deletion)
- `git diff --exit-code HEAD -- pyproject.toml` → clean at every commit in this plan (confirmed)
- `git ls-files src/aquapose/core/midline tests/unit/segmentation scripts/perf_validate.py` → `0` (108-01's purge still holds; confirmed)
- `git ls-files | wc -l` → `996`. Arithmetic against 108-01's recorded 988: `988` (after 108-01 task 3, commit `4152c86`) `+1` (108-01 SUMMARY, `2aa732c`) `+1` (LICENSING.md, `32f0c20`) `+1` (108-02 SUMMARY, `823424b`) `= 991` at the start of this plan; `+6` (`.planning/todos/`, `852fcd8`) `-1` (`tests/integration/segmentation/__init__.py`, `6adf69f`) `= 996`. Confirmed by direct `git ls-tree -r --name-only <commit> | wc -l` at each intermediate commit.
- Commit `852fcd8` exists: `git log --oneline --all | grep 852fcd8` — found
- Commit `6adf69f` exists: `git log --oneline --all | grep 6adf69f` — found
