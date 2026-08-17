---
phase: 108-branch-reconciliation-repo-hygiene
verified: 2026-08-17T17:54:51Z
status: passed
score: 6/6 must-haves verified
overrides_applied: 0
---

# Phase 108: Branch Reconciliation & Repo Hygiene Verification Report

**Phase Goal:** `dev` is the single source of truth — clean, correctly licensed, with a buildable
docs foundation ready for doc authoring.
**Verified:** 2026-08-17T17:54:51Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP.md Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `sphinx-build -W --keep-going` exits clean on `dev` | ✓ VERIFIED | Ran `rm -rf docs/_build && hatch run docs:build` live: "build succeeded", exit 0, `docs/_build/html/index.html` produced. `docs/conf.py` carries `napoleon_use_ivar`, `autodoc_mock_imports` (22 entries incl. `timm`, `pytorch_metric_learning`, `shapely`, `sklearn`), `_resolve_release()`. |
| 2 | Docs CI workflow runs and passes on push to `dev` | ✓ VERIFIED | `gh run list --workflow=docs.yml --branch=dev` shows the Documentation run on the pushed `chore(release): 1.2.0-dev.1` commit concluded `success` (run 32051262790, live GitHub API query, not SUMMARY claim). `.github/workflows/docs.yml` triggers `on: push: branches: [main, dev]`. |
| 3 | `main` and `dev` reconciled — `main` release-only, version conflict resolved | ✓ VERIFIED | `git log --oneline dev..main` empty (live check). `git rev-parse main` == `git rev-parse origin/main` == `2aba7327eb182d50b8e14d9a19cf2cb7e6f281f1` (untouched). `pyproject.toml` version is `1.2.0-dev.1` (post-release-bot bump from 108-01's `1.2.0-dev.0`), tag `v1.2.0-dev.1` exists. GitHub default branch confirmed still `main` via `gh api repos/McGrathLab/AquaPose --jq .default_branch`. |
| 4 | Fresh clone contains no stray artifacts; `.gitignore` prevents their return | ✓ VERIFIED | `11.0`, `./~`, top-level `src/aquapose/{reconstruction,segmentation,tracking,visualization}` all confirmed absent from working tree. Live `src/aquapose/core/{reconstruction,tracking}` confirmed present and importable. `tests/integration/segmentation` confirmed absent, `docs/api/{mesh,optimization,segmentation,utils}.rst` confirmed absent (8-file `docs/api/` set only). `git status --porcelain` empty. |
| 5 | `LICENSE`, `pyproject.toml` declare AGPL-3.0 | ✓ VERIFIED | `LICENSE` is 663 lines, verbatim AGPL v3 text under the D-08 copyright line, zero `MIT` occurrences. `pyproject.toml` line 11 `license = "AGPL-3.0-or-later"`, OSI classifier present, zero `MIT`. Cross-checked consistent in `README.md`, `LICENSING.md` (names Ultralytics/leidenalg/igraph), `CHANGELOG.md` (licensing note above `<!-- version list -->` marker), `docs/conf.py` (`McGrath Lab` copyright). No partial relicense found. |
| 6 | `MILESTONES.md` contains the missing v3.11 entry | ✓ VERIFIED | `## v3.11 Appearance-Based ReID (Shipped: 2026-03-26)` present at top of file. Bonus: `## v2.2 Backends (Shipped: 2026-03-01)` also backfilled (D-21, same class of gap). All 16 `## v` headings confirmed in strict newest-first chronological order by live `grep`. |

**Score:** 6/6 roadmap success criteria verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | AGPL license + `1.2.x-dev` version + detached docs env | ✓ VERIFIED | `license = "AGPL-3.0-or-later"`, `version = "1.2.0-dev.1"`, `detached = true` all present live. |
| `LICENSE` | Verbatim AGPL v3 text, D-08 copyright | ✓ VERIFIED | 663 lines, correct header, zero MIT. |
| `LICENSING.md` | Rationale naming forcing dependencies | ✓ VERIFIED | 59 lines, names Ultralytics, python-igraph, leidenalg. |
| `.github/workflows/docs.yml` | push trigger on `[main, dev]` | ✓ VERIFIED | Confirmed live in file. |
| `docs/conf.py` | Sphinx repair + AGPL copyright + full mock list | ✓ VERIFIED | All markers present; live docs build succeeds. |
| `.gitignore` | No `.planning/` rule, `_readthedocs/` present | ✓ VERIFIED | Both confirmed live. |
| `.planning/MILESTONES.md` | v3.11 + v2.2 entries, chronological order | ✓ VERIFIED | 16 entries, correct order confirmed live. |
| `tests/unit/core/midline/__init__.py` (retained, not purged) | Coherence check requested | ✓ VERIFIED — not dead weight | File is a lone docstring (`"""Unit tests for aquapose.core.midline (Stage 2)."""`), no test modules alongside it. `hatch run test --collect-only tests/unit/core/midline` succeeds (0 errors, package contributes nothing but doesn't break collection). Its retention is explicitly documented in 108-01-SUMMARY.md as intentional (predates the merge, not part of the derived 29-path hazard set, D-20 forbids a broader sweep). Confirmed coherent, not a regression. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `dev` | `main` | merge commit | ✓ WIRED | `git log --oneline dev..main` empty; 2-parent merge commit `abbe987` in history. |
| `pyproject.toml [tool.hatch.envs.docs]` | `docs/conf.py autodoc_mock_imports` | detached env + mocks | ✓ WIRED | `detached = true` present; mock list covers all of dev's third-party imports (timm, pytorch_metric_learning, shapely, sklearn added per 108-05); live build succeeds without installing torch/CUDA. |
| `README.md` | `LICENSING.md` | markdown link | ✓ WIRED | `[LICENSING.md](LICENSING.md)` confirmed in README License section. |
| `pyproject.toml` | `LICENSE` | SPDX identifier match | ✓ WIRED | Both declare AGPL-3.0-or-later. |
| `.github/workflows/docs.yml` | `hatch run docs:build` | push to dev | ✓ WIRED | Live GitHub Actions run confirms success on push to dev. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Docs build is genuinely green (not just claimed) | `rm -rf docs/_build && hatch run docs:build` | "build succeeded", exit 0, `docs/_build/html/index.html` produced | ✓ PASS |
| Documentation CI actually passed on the real push | `gh run list --workflow=docs.yml --branch=dev --limit=3` | run 32051262790 (`chore(release): 1.2.0-dev.1`) status `completed`/`success` | ✓ PASS |
| `main` truly untouched by any write | `git rev-parse main` vs `git rev-parse origin/main` vs recorded `MAIN_PRE` | all three equal `2aba7327eb182d50b8e14d9a19cf2cb7e6f281f1` | ✓ PASS |
| GitHub default branch unchanged | `gh api repos/McGrathLab/AquaPose --jq .default_branch` | `main` | ✓ PASS |
| No debt markers left in phase-touched files | grep `TBD\|FIXME\|XXX` across 14 key files | zero hits | ✓ PASS |
| Ruff lint clean after all docstring/license edits | `hatch run lint` | "All checks passed!" | ✓ PASS |
| Hazard-2 purge still holds | `git ls-files` on 8 representative superseded paths | zero output | ✓ PASS |
| `.secrets.baseline` not widened | `git diff --exit-code HEAD -- .secrets.baseline` | exit 0 | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FOUND-01 | 108-01, 108-05 | Sphinx repair forward-ported, `-W` build clean | ✓ SATISFIED | Live docs build exits 0; mock imports, `napoleon_use_ivar`, `.rst` set all present. |
| FOUND-02 | 108-01, 108-05 | Docs CI runs and passes on push to `dev` | ✓ SATISFIED | Live GitHub Actions run confirms `success` on a `dev` push. |
| FOUND-03 | 108-01 | `dev`/`main` reconciled, version conflict resolved | ✓ SATISFIED | `dev..main` empty; version now `1.2.0-dev.1`, ahead of shipped `1.1.1`. |
| FOUND-04 | 108-03 | No stray artifacts, `.gitignore` prevents return | ✓ SATISFIED | All named artifacts confirmed absent; `git status --porcelain` empty. |
| FOUND-05 | 108-02 | AGPL-3.0 declared consistently | ✓ SATISFIED | Verified across LICENSE, pyproject.toml, README, LICENSING.md, CHANGELOG.md, docs/conf.py — no partial relicense. |
| REC-01 | 108-04 | MILESTONES.md v3.11 entry backfilled | ✓ SATISFIED | v3.11 entry present, plus bonus v2.2 entry and full re-sort. |

No orphaned requirements — REQUIREMENTS.md rows for FOUND-01..05 and REC-01 all map to Phase 108 and all are marked `Complete`, matching what plans 108-01 through 108-05 declared and what was independently verified above.

### Anti-Patterns Found

None. Scanned all phase-touched files (`pyproject.toml`, `.gitignore`, `CHANGELOG.md`, `CLAUDE.md`, the four re-applied docstring files, `LICENSE`, `LICENSING.md`, `README.md`, `docs/conf.py`, `docs/api/index.rst`, `.planning/MILESTONES.md`) for `TBD`/`FIXME`/`XXX` markers — zero hits. `hatch run lint` passes clean.

**Known, deliberately out-of-scope items (per verification context, not phase-108 defects):**
- `hatch run test` failures — pre-existing, explicitly assigned to Phase 109. Confirmed live: CI `Tests` workflow on the phase's own push shows `failure` (4 failures on ubuntu-latest 3.12, matching 108-05-SUMMARY.md's disclosure), and the merge changed zero executable code under `src/`/`tests/`/`scripts/` (only 4 docstring RST edits, all pre-existing before this phase and unrelated to test logic).
- Stale `tlancaster6` GitHub URLs in `pyproject.toml` (3 occurrences), `CODE_OF_CONDUCT.md` (1), `docs/contributing.md` (1) — confirmed present live, caused by a mid-phase org transfer, explicitly recorded as a follow-up in 108-05-SUMMARY.md and flagged by the orchestrator as out of scope for this phase.

### Human Verification Required

None. All must-haves were verifiable programmatically (live command execution, live GitHub Actions API queries), and no visual/UX/real-time behavior is in scope for this phase.

### Gaps Summary

No gaps. All 6 roadmap success criteria, all 6 requirement IDs (FOUND-01 through FOUND-05, REC-01),
and every plan-level must-have were independently re-verified against the live repository state
(not SUMMARY.md claims): live `git` state, a live `hatch run docs:build` execution, and a live
`gh run list` query against GitHub Actions. The three areas flagged for extra scrutiny in the
verification context were checked directly:

1. **`tests/unit/core/midline/__init__.py` retention** — confirmed coherent: a lone docstring file
   that does not break test collection, its retention documented and justified in 108-01-SUMMARY.md
   as required by the plan's own `git ls-files == 988` acceptance criterion and D-20's no-broader-sweep
   fence.
2. **MILESTONES.md v3.11/v2.2 entries** — confirmed evidence-backed: both entries trace to named
   SUMMARY/VERIFICATION files, all 16 entries are in strict chronological order (live-verified), and
   the plan-count undercount for v3.11 (only 4 of 6 phases have surviving PLAN.md files) is
   transparently disclosed in the entry itself rather than estimated.
3. **AGPL relicense consistency** — confirmed complete, not partial: LICENSE, pyproject.toml, README,
   LICENSING.md, CHANGELOG.md, and docs/conf.py all agree on AGPL-3.0-or-later with zero remaining
   whole-word MIT declarations anywhere in the checked files.

---

_Verified: 2026-08-17T17:54:51Z_
_Verifier: Claude (gsd-verifier)_
