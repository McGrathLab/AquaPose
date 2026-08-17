---
phase: 108-branch-reconciliation-repo-hygiene
plan: 02
subsystem: infra
tags: [licensing, agpl, pyproject, sphinx, changelog]

requires:
  - phase: 108-01
    provides: "dev merged with main (pyproject.toml at 1.2.0-dev.0, docs/conf.py and CHANGELOG.md byte-identical to main's verified-green versions)"
provides:
  - "LICENSE is the verbatim GNU AGPL v3 text under the D-08 institutional copyright line, no MIT text remaining"
  - "pyproject.toml declares license = \"AGPL-3.0-or-later\" (PEP 639 SPDX string form) plus the AGPLv3+ OSI classifier, validated by hatch project metadata"
  - "LICENSING.md at repo root explaining the AGPL is imposed by Ultralytics (AGPL-3.0) and python-igraph/leidenalg (GPL-2.0+), not chosen"
  - "README License section declares AGPL-3.0-or-later and links LICENSING.md"
  - "CHANGELOG.md carries a Licensing note above the <!-- version list --> marker recording the v1.1.1-MIT / v1.2.0-AGPL boundary"
  - "docs/conf.py copyright names the McGrath Lab institution; unused datetime import removed"
affects: [108-03, 108-04, 108-05, 114]

tech-stack:
  added: []
  patterns:
    - "License-boundary notes placed above python-semantic-release's <!-- version list --> marker survive changelog regeneration (verified empirically against commit 2aba732 before writing)"

key-files:
  created:
    - LICENSING.md
  modified:
    - LICENSE
    - pyproject.toml
    - docs/conf.py
    - README.md
    - CHANGELOG.md

key-decisions:
  - "hatchling accepted the PEP 639 SPDX string form (license = \"AGPL-3.0-or-later\") alongside the OSI classifier — hatch project metadata exited 0 on the first attempt, so the table-form fallback was not needed."
  - "Removed the now-dead `from datetime import datetime` import in docs/conf.py after replacing the f-string copyright with a literal string, to keep ruff clean (plan's action explicitly permitted this)."
  - "pre-commit's ruff-format hook reformatted the docs/conf.py copyright assignment onto a wrapped multi-line string during the task 1 commit attempt; re-staged and re-committed rather than fighting the formatter."

patterns-established: []

requirements-completed: [FOUND-05]

duration: 25min
completed: 2026-08-17
---

# Phase 108 Plan 02: AGPL Relicense Summary

**Relicensed AquaPose from MIT to AGPL-3.0-or-later across LICENSE, pyproject.toml, docs/conf.py, README.md, and CHANGELOG.md, and added LICENSING.md explaining Ultralytics (AGPL-3.0) and python-igraph/leidenalg (GPL-2.0+) as the forcing dependencies.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3/3 completed
- **Files modified:** 5 modified (LICENSE, pyproject.toml, docs/conf.py, README.md, CHANGELOG.md), 1 created (LICENSING.md)

## Accomplishments

- `LICENSE` is now 663 lines: the D-08 copyright line (`Copyright (C) 2026 Tucker Lancaster and the McGrath Lab at the Georgia Institute of Technology`) followed by the verbatim canonical GNU AGPL v3 text fetched from `gnu.org/licenses/agpl-3.0.txt`. Zero occurrences of `tlancaster6` or whole-word `MIT`.
- `pyproject.toml`'s `[project]` table now declares `license = "AGPL-3.0-or-later"` (PEP 639 SPDX string form — hatchling accepted it on the first `hatch project metadata` run, no fallback to the table form needed) plus the AGPLv3+ OSI classifier. `version = "1.2.0-dev.0"` and `detached = true` from 108-01 both survived unchanged.
- `docs/conf.py`'s `copyright` field is now the literal institutional string; the now-unused `datetime` import was removed to keep `ruff` clean. `napoleon_use_ivar`, `autodoc_mock_imports`, and `_resolve_release()` from 108-01's merge are all untouched.
- New `LICENSING.md` (59 lines) names Ultralytics and python-igraph/leidenalg as the forcing dependencies, explains the network-copyleft implication of AGPL vs. GPL, records that an Ultralytics Enterprise License and replacing Ultralytics were both considered and rejected, and states the v1.1.1-MIT / v1.2.0-AGPL boundary without adjudicating prior compliance.
- `README.md`'s three-line License section now declares AGPL-3.0-or-later and links `LICENSING.md`; no other README content touched.
- `CHANGELOG.md` carries a `## Licensing` note between line 1 and the `<!-- version list -->` marker — verified empirically against `python-semantic-release`'s actual insertion behavior (commit `2aba732`) before writing, confirming content above the marker survives regeneration. The merged `v1.1.1` and `v1.1.0` sections are untouched; the diff is insertion-only.
- Nothing was pushed to any remote (`git log --oneline origin/dev..dev` shows 20 unpushed commits after this plan).

## Task Commits

1. **Task 1: Replace the MIT license text and metadata with AGPL-3.0-or-later** — `ee68b44` (feat)
2. **Task 2: Write LICENSING.md and point the README at it** — `32f0c20` (docs)
3. **Task 3: Record the license boundary in CHANGELOG.md** — `e5d50c2` (docs)

## Files Created/Modified

- `LICENSE` — full rewrite: D-08 copyright line + verbatim AGPL v3 text (663 lines total).
- `pyproject.toml` — `license` field and OSI classifier changed to AGPL-3.0-or-later; nothing else touched.
- `docs/conf.py` — `copyright` literal string with institution name; `datetime` import removed.
- `LICENSING.md` — new; explains the AGPL rationale.
- `README.md` — License section rewritten to declare AGPL-3.0-or-later and link `LICENSING.md`.
- `CHANGELOG.md` — `## Licensing` note inserted above `<!-- version list -->`.

## Decisions Made

- Used the PEP 639 SPDX string form for `pyproject.toml`'s `license` field rather than the table form — `hatch project metadata` validated it on the first attempt, so the plan's documented fallback was not exercised.
- Removed the dead `datetime` import from `docs/conf.py` (plan explicitly permitted this) rather than leaving an unused import for ruff to flag.

## Deviations from Plan

None — plan executed exactly as written. The only wrinkle was pre-commit's `ruff-format` hook reformatting `docs/conf.py`'s copyright assignment onto a wrapped line during the first `git commit` attempt for task 1; this is standard hook behavior (the commit fails, the file is reformatted, you re-stage and re-commit), not a deviation from the plan's instructions.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- FOUND-05 satisfied: every license declaration in the repo (`LICENSE`, `pyproject.toml`, README, CHANGELOG) now reads AGPL-3.0-or-later consistently, and `LICENSING.md` gives a reader the "why."
- 108-01's merged artifacts (version, detached docs env, napoleon_use_ivar, `_resolve_release()`, the v1.1.0/v1.1.1 CHANGELOG history) all verified intact after this plan's edits.
- `pyproject.toml` is now closed for the remainder of the phase per this plan's ownership claim — no later 108-0x plan should edit it.
- Ready for 108-03 (Sphinx forward-port verification) and 108-04 (repo hygiene / MILESTONES.md backfill).
- The single phase-wide push remains deferred to 108-05, as required.

---
*Phase: 108-branch-reconciliation-repo-hygiene*
*Completed: 2026-08-17*
