---
phase: 108-branch-reconciliation-repo-hygiene
plan: 01
status: blocked
kind: replan-input
created: 2026-08-17
supersedes: "108-01-PLAN.md <context> 'Pre-verified merge facts'"
---

# 108-01 Blocker — the plan's pre-verified merge facts are wrong

Execution of 108-01 was attempted and **aborted with zero commits**. `git merge main` was run
exactly as specified, hit a 113-conflict wall, and was reverted with `git merge --abort`.

**Repo state is unchanged from pre-execution:**

- `dev` HEAD = `241e8ea` (unchanged)
- `main` = `2aba7327eb182d50b8e14d9a19cf2cb7e6f281f1` (untouched)
- Working tree: only `.planning/STATE.md`, `.planning/config.json` modified; `11.0` and `~/` untracked
- Nothing committed, nothing pushed, no history rewritten
- Pre-existing unrelated `stash@{0}` (base `3e802c0`) left untouched

## What the plan claimed

> Files changed on the **main side** since the merge base: `.github/workflows/docs.yml`,
> `docs/conf.py`, `docs/index.md`, `docs/api/*.rst`, `docs/reports/*`, `pyproject.toml`.
> Therefore **`pyproject.toml` is the only expected conflict**.

That enumeration is short by roughly 900 files.

## Corrected merge facts (re-derived, verified)

Merge base is `cdd9a74` — that part is correct. `main` has exactly 4 commits not in `dev`:

| Commit | Subject | Files |
|---|---|---|
| `19ea21e` | feat: v3.5 Pseudo-Labeling milestone | **903** |
| `9aa1fd6` | chore(release): 1.1.0 | few |
| `a66287a` | fix(docs): repair Sphinx build and gate it on push | docs/CI + 4 src files |
| `2aba732` | chore(release): 1.1.1 | few |

```
git diff --stat cdd9a74 main   ->  913 files changed, 169814 insertions(+), 1898 deletions(-)
git show --stat 19ea21e        ->  903 files changed, 169685 insertions(+), 1868 deletions(-)
```

### Root cause

`19ea21e` is **not** an incremental commit. It is a single flat **squashed snapshot** of `dev`'s
tree as of ~March 6 (its own message says "9 phases (61-69), 22 plans, 28,033 LOC"), committed to
`main` with none of `dev`'s incremental history. Consequently no file on main's side shares blob
ancestry with `dev`'s current version of the same path. Git cannot 3-way-diff them, so every path
whose content has since diverged surfaces as `CONFLICT (add/add)` — which is nearly everything,
given ~1400 further commits on `dev`.

### Hazard 1 — 113 add/add conflicts

Across `src/aquapose/core/**`, `src/aquapose/engine/**`, `src/aquapose/training/**`, ~40 test
files, `.gitignore`, `CLAUDE.md`, `CHANGELOG.md`, `pyproject.toml`, and `.planning/{GUIDEBOOK,
MILESTONES,PROJECT,ROADMAP}.md`. Plus modify/delete conflicts on `.planning/REQUIREMENTS.md` and
five files under `.planning/research/` (paths `dev` intentionally deleted — these need an explicit
"keep deleted" decision, not a mechanical resolution).

### Hazard 2 — silent resurrection of superseded modules (NOT surfaced as a conflict)

23 source/test files exist in `main` but in **neither** `dev` nor the merge base. Git adds these
with **no conflict at all**. A blind merge silently restores modules `dev` deliberately refactored
away, leaving dead code that fails only at import time:

| Resurrected on merge | Superseded on `dev` by |
|---|---|
| `src/aquapose/core/midline/{__init__,midline,orientation,stage,types}.py` | `src/aquapose/core/types/midline.py`, `src/aquapose/evaluation/stages/midline.py` |
| `src/aquapose/core/midline/backends/{__init__,pose_estimation,segmentation}.py` | reconstruction/detection backends |
| `src/aquapose/training/yolo_{obb,pose,seg}.py` | `src/aquapose/training/yolo_training.py` |
| `src/aquapose/core/tracking/ocsort_wrapper.py` | removed |
| `src/aquapose/core/association/refinement.py` | removed |
| 9 matching files under `tests/unit/**` | removed |

Full list:
```
src/aquapose/core/association/refinement.py
src/aquapose/core/midline/__init__.py
src/aquapose/core/midline/backends/__init__.py
src/aquapose/core/midline/backends/pose_estimation.py
src/aquapose/core/midline/backends/segmentation.py
src/aquapose/core/midline/midline.py
src/aquapose/core/midline/orientation.py
src/aquapose/core/midline/stage.py
src/aquapose/core/midline/types.py
src/aquapose/core/tracking/ocsort_wrapper.py
src/aquapose/training/yolo_obb.py
src/aquapose/training/yolo_pose.py
src/aquapose/training/yolo_seg.py
tests/unit/core/association/test_refinement.py
tests/unit/core/midline/test_direct_pose_backend.py
tests/unit/core/midline/test_midline_stage.py
tests/unit/core/midline/test_orientation.py
tests/unit/core/midline/test_segmentation_backend.py
tests/unit/segmentation/__init__.py
tests/unit/test_midline.py
tests/unit/tracking/test_ocsort_wrapper.py
tests/unit/training/test_yolo_pose.py
tests/unit/training/test_yolo_seg.py
```

A further 113 files under `.planning/` are also main-only (historical `debug/`, `inbox/`,
`milestones/v1.0-phases/**`, `PIPELINE.md`, `RETROSPECTIVE.md`, `SOURCES.md`). These interact
directly with plan 108-03's `.gitignore` / `.planning/` un-ignore decision (D-18) and plan
108-04's MILESTONES.md backfill — decide them together, not incidentally via the merge.

### Worth keeping from main

`a66287a` touched 4 real source files with docstring repairs that feed the Sphinx `-W` build:
`src/aquapose/core/context.py`, `src/aquapose/engine/observers.py`,
`src/aquapose/synthetic/fish.py`, `src/aquapose/synthetic/scenarios.py`.
A blanket take-dev's-side resolution drops them. Plan 108-05 owns the green Sphinx build and may
re-derive them independently — the re-plan should decide explicitly which plan owns these hunks.

## What survives from the current plan

The **goal** is unaffected: D-01 (real merge, true ancestry, no rewrite), D-03 (`1.2.0-dev.0`),
D-04/D-05 (`main` and the default-branch setting frozen), D-13/D-15/D-16/D-17 (docs + CI trigger),
FOUND-02/FOUND-03. Most `acceptance_criteria` in 108-01 remain valid as written.

What must be replaced is the `<context>` block's conflict-surface enumeration and Task 1's
resolution procedure, which currently assumes a single hand-resolved file.

## Considered and rejected

- `-X ours` / `-X theirs` blanket resolution — forbidden by D-02, and would apply a mechanical
  side-pick to ~900 unreviewed files.
- `git merge -s ours` — records no content from `main` at all; falsifies ancestry semantics and
  drops the docs/CI content the phase explicitly wants.
- `git rebase` / `git cherry-pick` / any force-push — forbidden by D-01 and T-108-01;
  `dev` has 1496 published commits.

## Recommended shape for the re-planned Task 1

A real `git merge main` whose resolution is a **stated policy**, not a per-file improvisation:

1. Conflicting paths outside `docs/**`, `.github/**`, `pyproject.toml` → take `dev`'s side.
2. Modify/delete conflicts where `dev` deleted the path → **keep deleted**.
3. The 23 main-only `src/`+`tests/` paths git auto-adds → **remove before committing the merge**.
4. `.planning/` main-only paths → defer the keep/drop call to 108-03/108-04's decisions.
5. `docs/**` and `.github/workflows/docs.yml` → take `main`'s repaired blobs.
6. `pyproject.toml` → hand-resolve exactly as the current plan already specifies (D-02, D-03, D-15).
7. Assign ownership of `a66287a`'s 4 src docstring hunks to either 108-01 or 108-05.

This yields a real merge commit with true ancestry (`git log --oneline dev..main` empty), keeps
`main` frozen, resurrects nothing, and leaves the push deferred to 108-05 so `release.yml` cannot
cut a prerelease tag against an MIT-declared tree (T-108-03).
