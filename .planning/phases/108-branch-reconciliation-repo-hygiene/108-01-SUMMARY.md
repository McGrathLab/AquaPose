---
phase: 108-branch-reconciliation-repo-hygiene
plan: 01
subsystem: infra
tags: [git, merge, branch-reconciliation, pyproject, sphinx, docs-ci, secrets-scan]

requires: []
provides:
  - "dev fully contains main via a real --no-ff merge commit with true ancestry (git log --oneline dev..main is empty)"
  - "pyproject.toml at 1.2.0-dev.0 with a detached docs env (main's block verbatim) and dev's dependency list intact"
  - "docs/conf.py, docs/index.md, docs/api/*.rst (8-file set), .github/workflows/docs.yml byte-identical to main's verified-green versions"
  - "main's 665-file .planning/ historical archive tracked, including .planning/milestones/v2.2-phases/ needed by 108-04"
  - "a66287a's four src/ docstring RST-escaping repairs re-applied with no code change"
affects: [108-02, 108-03, 108-04, 108-05]

tech-stack:
  added: []
  patterns:
    - "Path-scoped merge conflict resolution (git checkout --ours/--theirs applied to enumerated path sets, never a blanket -X strategy)"
    - "Mechanically-derived silent-addition purge: git diff --cached --diff-filter=A --name-only $PRE -- <trees> to find files git resurrects with no conflict signal, verified against a hand-audited list before deletion"

key-files:
  created: []
  modified:
    - pyproject.toml
    - .gitignore
    - CHANGELOG.md
    - CLAUDE.md
    - docs/conf.py (verified, merge-delivered)
    - docs/index.md (verified, merge-delivered)
    - docs/api/*.rst (verified, merge-delivered)
    - .github/workflows/docs.yml (verified, merge-delivered)
    - src/aquapose/core/context.py
    - src/aquapose/engine/observers.py
    - src/aquapose/synthetic/fish.py
    - src/aquapose/synthetic/scenarios.py
    - .planning/ (665 main-only files newly tracked; 5 .planning/research/*.md kept deleted)

key-decisions:
  - "PRE=ed98296e9024fdc46eb67bfaddb199547296f633, MAIN_PRE=2aba7327eb182d50b8e14d9a19cf2cb7e6f281f1 recorded before merge; MAIN_PRE re-verified unchanged after both commits."
  - "113 conflicts resolved by stated path-scoped policy: 98 src/tests dev-side, CLAUDE.md+.gitignore dev-side (then re-applied main's _readthedocs/ hunk by hand), CHANGELOG.md main-side (verified superset), 5 .planning/ docs dev-side, REQUIREMENTS.md kept dev's version, 5 .planning/research/*.md kept deleted, pyproject.toml hand-resolved (version + docs env from main, dependencies verbatim from dev)."
  - "29 silently-resurrected src/tests/scripts paths (git diff --cached --diff-filter=A against PRE) matched the plan's HAZARD 2 list exactly and were git rm -f'd before committing the merge."
  - "tests/unit/core/midline/__init__.py was NOT deleted despite the plan's directory-sweep instruction naming that directory: it predates the merge (committed a3b74b8, not part of the derived 29-path hazard set) and D-20 explicitly caps dead-code removal at two named items, excluding a broader sweep. Kept to preserve the plan's own git ls-files == 988 acceptance criterion, which only holds if this file survives."
  - "Local environment workaround: the .hooks/check-import-boundary.sh pre-commit hook calls `python3`, which resolves to a broken Windows Store alias on this machine (no real python3.exe installed). Used a temporary PATH-prepended shim script (python3 -> exec python) scoped to the two git commit invocations in this session only; no repo files or global PATH were changed."

patterns-established:
  - "Mechanically-derived diff-filter=A verification before any bulk deletion during a squash-merge reconciliation, rather than trusting a hand-transcribed file list."

requirements-completed: [FOUND-01, FOUND-02, FOUND-03]

duration: 45min
completed: 2026-08-17
---

# Phase 108 Plan 01: Branch Reconciliation Summary

**Merged main's 4 frozen-release commits into dev via a real `--no-ff` merge (113 conflicts resolved by stated path-scoped policy, 29 silently-resurrected dead modules purged), giving dev true ancestry to main while keeping production code byte-identical and main untouched.**

## Performance

- **Duration:** ~45 min
- **Tasks:** 3/3 completed
- **Files modified:** merge commit touched 1011 paths (988 tracked post-purge incl. 665 newly-tracked `.planning/` files); follow-up commit touched 4 `src/` files

## Accomplishments

- `dev` (HEAD `4152c86`) fully contains `main` (`2aba732`) via merge commit `abbe987`, a real 3-parent-listed (2-parent) `--no-ff` merge; `git log --oneline dev..main` is empty.
- All 113 conflicts resolved by the plan's stated path-scoped policy — 98 `src/`+`tests/` paths dev-side, `CLAUDE.md`/`.gitignore` dev-side plus a hand-applied `_readthedocs/` hunk, `CHANGELOG.md` main-side (verified superset), 5 `.planning/` docs dev-side, `.planning/REQUIREMENTS.md` kept as dev's version, 5 `.planning/research/*.md` kept deleted, `pyproject.toml` hand-resolved.
- All 29 silently-resurrected superseded modules (`core/midline/**`, `training/yolo_{obb,pose,seg}.py`, `tracking/ocsort_wrapper.py`, `association/refinement.py`, `scripts/perf_validate.py`, 14 matching test files) purged from both the index and the working tree before the merge commit landed.
- `pyproject.toml` is `1.2.0-dev.0` with main's detached docs env (`detached = true`, `numpy` mock dep) and dev's full dependency list (`timm`, `shapely`, `pytorch-metric-learning`, `igraph`, `leidenalg`, `ultralytics`) intact; MIT license fields untouched for 108-02.
- `docs/conf.py`, `docs/index.md`, `docs/api/*.rst` (8-file set), and `.github/workflows/docs.yml` verified byte-identical to `main`'s known-green versions.
- `a66287a`'s four dropped `src/` docstring RST-escaping repairs (context.py, fish.py, observers.py, scenarios.py) re-applied in a separate follow-up commit with zero code change.
- `main`'s 665-file `.planning/` historical archive (including the `v2.2-phases/` set 108-04 needs) is now tracked; `detect-secrets --all-files` and manual credential/PEM/large-file greps found nothing.
- Nothing was pushed to any remote (`git log --oneline origin/dev..dev` has 15 unpushed commits, consistent with the phase's single push being deferred to 108-05).

## Task Commits

1. **Task 1: Run the merge and resolve all 113 conflicts** — staged as part of the merge in progress (no standalone commit; plan explicitly defers the commit to task 2 so the hazard-2 purge lands in the same merge commit).
2. **Task 2: Purge the 29 silently-resurrected paths, scan for secrets, and commit the merge** — `abbe987` (merge)
3. **Task 3: Verify merged docs/CI artifacts and re-apply a66287a's four dropped docstring hunks** — `4152c86` (fix)

_No plan-metadata commit yet — STATE.md/ROADMAP.md/REQUIREMENTS.md updates and the final `docs(108-01): ...` commit follow this SUMMARY._

## Files Created/Modified

- `pyproject.toml` — version `1.2.0-dev.0`; `[tool.hatch.envs.docs]` replaced with main's detached block; dependencies kept verbatim from dev.
- `.gitignore` — dev's content plus main's `_readthedocs/` two-line hunk under the Sphinx heading.
- `CHANGELOG.md` — main's content (adds `v1.1.0`/`v1.1.1` shipped sections above dev's existing entries).
- `CLAUDE.md`, `.planning/{GUIDEBOOK,MILESTONES,PROJECT,ROADMAP,STATE,REQUIREMENTS}.md` — dev's content preserved.
- `.planning/research/{ARCHITECTURE,FEATURES,PITFALLS,STACK,SUMMARY}.md` — kept deleted (`git rm -f`).
- `.planning/` — 665 main-only historical files (milestones archive, debug/, inbox/, todos/, quick/, PIPELINE.md, RETROSPECTIVE.md, SOURCES.md, etc.) newly tracked.
- 29 hazard-2 paths under `src/`, `tests/`, `scripts/` — removed (see key-decisions for the full derivation method).
- `docs/conf.py`, `docs/index.md`, `docs/api/*.rst`, `.github/workflows/docs.yml` — arrived via merge from main, verified not re-authored.
- `src/aquapose/core/context.py`, `src/aquapose/engine/observers.py`, `src/aquapose/synthetic/fish.py`, `src/aquapose/synthetic/scenarios.py` — four one-line docstring RST-escaping fixes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] `python3` unavailable, blocking the `import-boundary` pre-commit hook**
- **Found during:** Task 2 commit (`git commit --no-edit`)
- **Issue:** `.hooks/check-import-boundary.sh` invokes `python3`, which on this Windows machine resolves only to a broken Microsoft Store execution alias (`Python was not found...`). No `python3.exe` exists anywhere on `PATH`; only `python.exe` (hatch venv, first on `PATH`) works.
- **Fix:** Created a throwaway shell shim (`python3 -> exec python "$@"`) in the session scratchpad directory and prepended its directory to `PATH` for the two `git commit` invocations in this plan only. No repo file, hook config, or global environment/PATH was modified. `--no-verify` was never used.
- **Files modified:** none (session-scoped `PATH` only)
- **Commit:** N/A (environment workaround, not a code change)

**2. [Deviation from plan's literal directory-sweep instruction, resolved via D-20] `tests/unit/core/midline/__init__.py` kept, not deleted**
- **Found during:** Task 2, purge step
- **Issue:** The plan's action text says to "remove the directories left empty: `src/aquapose/core/midline/`, `tests/unit/core/midline/`, and `tests/unit/segmentation/`" after purging the 29 hazard paths. `tests/unit/core/midline/__init__.py` is not one of the 29 (it predates the merge, committed `a3b74b8`), so the directory was not actually empty post-purge. Deleting it would satisfy the literal directory-sweep wording but contradicts the plan's own `git ls-files | wc -l == 988` acceptance criterion (988 = 1022 dry-run merge total − 29 hazard purge − 5 research-kept-deleted; this pre-existing file is already counted in the 1022, so removing it would yield 987) and 108-CONTEXT.md's D-20, which caps dead-code removal at exactly two named items and explicitly rules out a broader sweep.
- **Resolution:** Restored the file (`git checkout --`) after an initial deletion attempt; left it tracked. Verified `git ls-files | wc -l` returns exactly `988` as the plan specifies. The truly-empty leftover directories (`src/aquapose/core/midline/`, `tests/unit/segmentation/`, including stray `__pycache__` contents) were removed from disk as instructed.
- **Files modified:** none in the final commit (file restored to its pre-merge state)
- **Commit:** N/A

### Notes

- `git ls-files src/aquapose/core/midline tests/unit/core/midline tests/unit/segmentation scripts/perf_validate.py | wc -l` returns `1` (the retained `__init__.py`), not the `0` literally stated in one acceptance-criterion line — see deviation 2 above for why this is the correct outcome given the plan's other, numerically-precise criteria.

## Self-Check: PASSED

- `git log --oneline dev..main` — empty (confirmed)
- `git rev-parse main` — `2aba7327eb182d50b8e14d9a19cf2cb7e6f281f1` (unchanged, confirmed before and after both commits)
- `git rev-list --parents -n1 abbe987` — 2 parents (`ed98296`, `2aba732`) confirmed
- `git reflog dev | grep -ciE 'rebase|cherry-pick'` — `0` (confirmed)
- `git ls-files | wc -l` — `988` (confirmed)
- `pyproject.toml` — `version = "1.2.0-dev.0"`, `detached = true` present (confirmed)
- `CHANGELOG.md` — `## v1.1.0` and `## v1.1.1` present (confirmed)
- `.github/workflows/docs.yml` — `branches: [main, dev]` present (confirmed)
- `docs/api/*.rst` — exactly 8 files, none of the 4 dead ones (confirmed)
- `hatch run lint` — all checks passed (confirmed)
- `hatch run python -c "import aquapose"` — exit 0 (confirmed)
- `hatch run pre-commit run detect-secrets --all-files` — passed (confirmed)
- `find .planning -type f -size +1M` — no output (confirmed)
- Commit `abbe987` exists: `git log --oneline --all | grep abbe987` — found
- Commit `4152c86` exists: `git log --oneline --all | grep 4152c86` — found
