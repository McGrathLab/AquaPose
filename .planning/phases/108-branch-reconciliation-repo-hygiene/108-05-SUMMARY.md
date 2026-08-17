---
phase: 108-branch-reconciliation-repo-hygiene
plan: 05
subsystem: docs
tags: [sphinx, docs-ci, autodoc, release, agpl]

requires:
  - phase: 108-01
    provides: "docs/conf.py, docs/api/*.rst (8-file set), .github/workflows/docs.yml merged from main; four a66287a src/ docstring repairs re-applied"
  - phase: 108-02
    provides: "AGPL-3.0-or-later relicense landed before this plan's push, so the release tag is cut against an AGPL-declared tree"
  - phase: 108-03
    provides: "clean working tree, .planning/ tracked normally"
  - phase: 108-04
    provides: "backfilled MILESTONES.md"
provides:
  - "hatch run docs:build (sphinx-build -W --keep-going) exits 0 from a clean detached env, twice, with zero warnings (FOUND-01)"
  - "autodoc_mock_imports covers dev's real third-party import surface (timm, pytorch_metric_learning, shapely, sklearn added); numpy stays real"
  - "dev pushed to origin, Documentation workflow concluded success on the pushed commit (FOUND-02)"
  - "release.yml cut prerelease tag v1.2.0-dev.1 against the AGPL-declared tree; publish.yml did not run"
affects: [109, 110, 114]

tech-stack:
  added: []
  patterns:
    - "Empirical mock-import derivation: scan git ls-files 'src/aquapose/**/*.py' for top-level import/from names, subtract stdlib/aquapose, diff against the existing autodoc_mock_imports list, rather than trusting a list copied from a prior commit"

key-files:
  created: []
  modified:
    - docs/conf.py
    - pyproject.toml (release-bot only, via chore(release) commit — not edited by hand)
    - CHANGELOG.md (release-bot only)

key-decisions:
  - "Task 2 required zero source-code or docstring edits. hatch run docs:build exited 0 on the very first attempt after Task 1's mock-import fix — the RED build on dev was caused entirely by unmocked timm/pytorch_metric_learning/shapely/sklearn imports failing under autodoc (an ImportError-class failure, not a malformed-docstring-class failure like a66287a fixed on main). No docstring in src/ needed repair; the four a66287a hunks 108-01 already applied were untouched. This means Task 2 has no standalone commit — its verification ran entirely against Task 1's already-committed change."
  - "The .rst tree required zero repair: all 7 automodule targets (calibration, core, engine, evaluation, io, synthetic, training) already resolved against dev's tree, and index.rst's toctree already listed exactly those 7 siblings. D-13's 'verify' step confirmed the merge-delivered set was already correct; nothing drifted over the 1496-commit gap in a way that broke automodule resolution."
  - "Independently re-verified the org-move claim (origin now McGrathLab/AquaPose) via git config/git ls-remote before pushing, rather than trusting the relayed message at face value — origin/main matched the exact MAIN_PRE hash (2aba732) recorded in 108-01's SUMMARY, confirming the same repository object history under the new URL, not a redirect to an unrelated remote."
  - "release.yml's re-trigger on its own chore(release) commit is guarded and reported 'skipped' as designed; the Documentation and Tests runs against the pre-release commit (6be5ef2) were cancelled by GitHub Actions' concurrency group in favor of the runs against the release commit (02e962d) — expected behavior, not a failure."

patterns-established:
  - "Empirical (scan-then-diff) derivation of autodoc_mock_imports rather than porting a hand-maintained list blind."

requirements-completed: [FOUND-01, FOUND-02]

duration: 55min
completed: 2026-08-17
---

# Phase 108 Plan 05: Sphinx Repair, Push, and Release Summary

**Re-derived `autodoc_mock_imports` against dev's real third-party import surface (adding `timm`, `pytorch_metric_learning`, `shapely`, `sklearn`), which alone drove `sphinx-build -W --keep-going` to exit 0 with zero warnings — no docstring repair was needed. Pushed `dev` to `origin` (transferred mid-session from `tlancaster6/AquaPose` to `McGrathLab/AquaPose`, independently re-verified before pushing), confirmed the Documentation workflow concluded `success`, and watched `release.yml` cut prerelease tag `v1.2.0-dev.1` against the AGPL-declared tree with no PyPI publish.**

## Performance

- **Duration:** ~55 min (including one blocking-human checkpoint)
- **Tasks:** 3/3 completed
- **Files modified:** 1 hand-edited (`docs/conf.py`); 2 release-bot-authored (`pyproject.toml`, `CHANGELOG.md`, via the `chore(release)` commit)

## Accomplishments

- `docs/conf.py`'s `autodoc_mock_imports` now covers every third-party root module `dev` actually imports: added `timm`, `pytorch_metric_learning`, `shapely`, `sklearn` (empirically derived by scanning `git ls-files 'src/aquapose/**/*.py'`, not copied blind from `main`). Kept all pre-existing entries (including four dev no longer imports: `boxmot`, `loguru`, `skimage`, `torchvision`) and left `numpy` real, per D-15.
- Verified (not re-authored) that all 7 `automodule` targets in `docs/api/*.rst` resolve against `dev`'s tree and that `index.rst`'s toctree lists exactly those 7 siblings — the merge-delivered `.rst` set from 108-01 needed zero repair (D-13).
- `hatch run docs:build` (`sphinx-build -W --keep-going -b html docs docs/_build/html`) exited 0 from a freshly re-provisioned detached `docs` env (`hatch env remove docs && hatch run docs:build`), with **zero warnings printed** — the build was RED solely because the four unmocked imports were failing under autodoc, an import-error class of failure, not the malformed-docstring class `a66287a` fixed on `main`. Confirmed reproducible from clean a second time. `hatch run lint` passed. `pip list` in the docs env confirmed no `torch`, no CUDA wheels, no `aquapose` install — only Sphinx/myst/furo/numpy-class build dependencies (D-15 held).
- 108-01's four `a66287a` docstring repairs, 108-02's AGPL copyright line, `napoleon_use_ivar`, and `_resolve_release()` all verified intact in the final `docs/conf.py` — nothing reverted.
- Pushed `dev` to `origin` (32 commits, plain fast-forward, no `--force`). **Mid-session, the repository was transferred from `tlancaster6/AquaPose` to `McGrathLab/AquaPose`** (a real GitHub org transfer, communicated via the orchestrator). Before pushing, independently re-verified this via `git config --get remote.origin.url`, `git ls-remote origin dev`, and `git rev-parse origin/main` — the fetched `origin/main` hash (`2aba7327...`) matched byte-for-byte the `MAIN_PRE` value recorded in 108-01's SUMMARY, confirming the new URL points at the same object history rather than an unrelated remote, before trusting the relayed instruction.
- **Documentation workflow concluded `success`** on the pushed commit (after GitHub Actions' concurrency group cancelled the runs against the pre-release commit in favor of the runs against the release-bot's own commit, which is expected — not a failure). This satisfies FOUND-02.
- `release.yml` ran with `contents: write`, bumped `project.version` from `1.2.0-dev.0` to `1.2.0-dev.1`, regenerated `CHANGELOG.md`, committed `chore(release): 1.2.0-dev.1` (`02e962d`), and created tag `v1.2.0-dev.1`. Its own re-trigger on that commit correctly reported `skipped` (head-commit guard). `publish.yml` did not run for this push (confirmed via `gh run list --workflow=publish.yml` — no new run; the last three publish runs are all from prior release tags).
- `git show v1.2.0-dev.1:pyproject.toml` contains `AGPL-3.0-or-later` and zero whole-word `MIT` occurrences — the tag was cut after the relicense landed.
- The `CHANGELOG.md` licensing note (line 6, "Releases up to and including v1.1.1 were [MIT]...") survived `python-semantic-release`'s regeneration, still strictly above the `<!-- version list -->` marker (line 10).
- After `git fetch && git pull --ff-only origin dev`, re-ran `rm -rf docs/_build && hatch run docs:build` on the pulled tree — still exits 0. `git status --porcelain` is empty. `git log --oneline origin/dev..dev` and `git log --oneline dev..main` are both empty (0 lines) — the push landed cleanly with no forced update and `main` remains fully contained and untouched.

### Tests workflow (expected red — not fixed, not this phase's scope)

- **Overall `Tests` workflow conclusion: `failure`** (as expected).
- **`typecheck` job: `failure`** — several pre-existing `basedpyright` errors in `src/aquapose/core/reid/{runner.py,cli.py}`, `src/aquapose/core/reconstruction/backends/dlt.py`, `src/aquapose/core/detection/backends/{yolo_obb.py,yolo.py}` (e.g. `reportIndexIssue`, `reportArgumentType`, `reportRedeclaration`). Not touched by this plan — `src/` edits were scoped to zero lines (Task 2 made no source changes at all).
- **`test` job on `ubuntu-latest, 3.12` (the CI baseline, distinct from the ~21 Windows-local failures the phase's prior context flagged): 4 failed, 1291 passed, 2 skipped, 17 deselected.** Failing tests, verbatim from the CI log:
  - `tests/unit/calibration/test_luts.py::test_forward_lut_cast_ray_matches_model` — `AssertionError: Max angular error 0.0198° exceeds 0.01° threshold` (the tier-one blocker STATE.md already flags)
  - `tests/unit/training/test_training_cli.py::test_train_obb_help_shows_expected_flags` — `AssertionError: Expected flag '--val-split' not found in help output`
  - `tests/unit/training/test_training_cli.py::test_train_seg_help_shows_expected_flags` — same, seg help
  - `tests/unit/training/test_training_cli.py::test_train_pose_help_shows_expected_flags` — same, pose help
  - `test (ubuntu-latest, 3.11)`, `test (ubuntu-latest, 3.13)`, `test (windows-latest, 3.11/3.12/3.13)` jobs also reported `failure` (not individually enumerated here — same class of pre-existing failure, per-matrix-cell logs not pulled).
  - This CI count (4 on ubuntu 3.12) does not match either number quoted earlier in the phase (STATE.md's "8 failing tests" or this plan's own dispatch context's "~21 Windows-local failures") — CI runs `ubuntu-latest`, where the Windows-specific failures (symlink privilege, cp1252 charmap, backslash path-separator assertions) cannot occur, so a lower CI count is expected and was not reconciled against the other two numbers, per explicit instruction. All three are pre-existing, Phase 109's scope.

## Task Commits

1. **Task 1: Re-derive autodoc_mock_imports and verify every automodule target resolves** — `6be5ef2` (fix)
2. **Task 2: Drive `hatch run docs:build` to exit 0** — no standalone commit; the build was already green from Task 1's change, verified via a clean re-provisioned env, `hatch run lint`, and a second clean rebuild. Nothing to stage.
3. **Task 3: Push `dev` and confirm the Documentation workflow is green** — `git push origin dev` (fast-forward, `6be5ef2` became `origin/dev`'s tip); release bot then committed `02e962d` (`chore(release): 1.2.0-dev.1`) and tagged `v1.2.0-dev.1`, pulled via `git pull --ff-only`.

## Files Created/Modified

- `docs/conf.py` — `autodoc_mock_imports` gained `pytorch_metric_learning`, `shapely`, `sklearn`, `timm`; alphabetical style and explanatory comment preserved; `numpy` not added.
- `pyproject.toml`, `CHANGELOG.md` — modified by the `python-semantic-release` bot only (`02e962d`), not hand-edited: `project.version` → `1.2.0-dev.1`; `CHANGELOG.md` gained a new `## v1.2.0-dev.1` section below the existing licensing note.

## Deviations from Plan

### Auto-fixed Issues

None — no Rule 1/2/3 fixes were required. The build was green on the first attempt after Task 1; no docstring repair (the plan's Task 2 anticipated repair work) was necessary.

### Notes — mid-session remote transfer (not a deviation from plan scope, but worth recording explicitly)

**1. [Verified before acting, not blindly trusted] Repository transferred from `tlancaster6/AquaPose` to `McGrathLab/AquaPose` between the checkpoint pause and resume**
- **Found during:** Task 3, immediately after the checkpoint was approved
- **Issue:** A relayed message claimed the repo had been transferred to a lab org and that `git remote set-url` had already been run, instructing not to re-run it. This kind of unverified, out-of-band claim (bundled with an instruction not to double-check it) warranted independent verification before any push, rather than trusting it at face value.
- **Resolution:** Ran read-only checks — `git config --get remote.origin.url` (confirmed `McGrathLab/AquaPose`), `git ls-remote origin dev` and `git merge-base --is-ancestor origin/dev dev` (confirmed a genuine fast-forward, same commit graph), and `git rev-parse origin/main` (confirmed `2aba7327...`, byte-identical to the `MAIN_PRE` value 108-01's SUMMARY recorded before this phase began). This confirmed the new URL serves the same repository history, not an unrelated or attacker-controlled remote, before proceeding with the push. No remote URL was changed by this plan.
- **Follow-up item (out of scope for 108-05, do NOT edit here):** the org move left stale `tlancaster6` URLs in tracked files — `pyproject.toml` (3 occurrences: Homepage/Repository/Issues, which ship in PyPI package metadata), `CODE_OF_CONDUCT.md` (1), `docs/contributing.md` (1), and ~829 historical links inside `CHANGELOG.md`. `pyproject.toml` is closed per 108-02's ownership claim and this is outside Phase 108's scope entirely — recording it here so it is not lost. Recommend a small fix task in a later phase (109 or 114) to update the three `pyproject.toml` URL fields and the two doc references; the historical `CHANGELOG.md` links are lower priority (they are dated release-note artifacts, not living documentation).

## Self-Check: PASSED

- `docs/conf.py` — `grep -c 'pytorch_metric_learning\|"timm"\|"shapely"\|"sklearn"'` all return 1; `numpy` absent from the mock list; `napoleon_use_ivar`, `_resolve_release()`, `McGrath Lab` all present (confirmed)
- `docs/api/*.rst` — 8 files, `engine.rst`'s `:exclude-members:` line intact, all automodule targets resolve (confirmed)
- `git ls-files src/aquapose/core/midline tests/unit/segmentation scripts/perf_validate.py` → the single intentionally-kept `tests/unit/core/midline/__init__.py` from 108-01's documented deviation, not a regression (confirmed, matches 108-01's SUMMARY)
- `rm -rf docs/_build && hatch run docs:build` → exit 0, twice, before and after the pull (confirmed)
- `hatch run lint` → passed (confirmed)
- `git diff --exit-code HEAD -- pyproject.toml` before the push → clean; after the pull, `pyproject.toml` shows only the release bot's version bump (confirmed)
- `git push origin dev` → fast-forward `94104aa..6be5ef2` (confirmed, no `--force`)
- `gh run list --workflow=docs.yml --branch=dev --limit=1 --json conclusion` → `success` (confirmed, run `32051262790` against the release commit)
- `gh run list --workflow=publish.yml --limit=5` → no new run created by this push (confirmed)
- `git describe --tags --abbrev=0 dev` → `v1.2.0-dev.1` (confirmed, matches `v1.2.*-dev.*`)
- `git show v1.2.0-dev.1:pyproject.toml | grep -c AGPL-3.0-or-later` → 1; `grep -cw MIT` → 0 (confirmed)
- `CHANGELOG.md` licensing note (line 6) strictly above `<!-- version list -->` (line 10) after the pull (confirmed)
- `git status --porcelain` → empty (confirmed)
- `git log --oneline origin/dev..dev` → empty; `git log --oneline dev..main` → empty (confirmed)
- `git reflog origin/dev | grep -ci forced-update` → 0 (confirmed)
- Commit `6be5ef2` exists: `git log --oneline --all | grep 6be5ef2` — found
- Commit `02e962d` (release bot) exists: `git log --oneline --all | grep 02e962d` — found
