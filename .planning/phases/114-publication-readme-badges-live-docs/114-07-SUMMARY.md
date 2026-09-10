---
phase: 114-publication-readme-badges-live-docs
plan: 07
subsystem: release
tags: [citation, doi, zenodo, readme, badges, phase-closeout]
dependency-graph:
  requires:
    - "114-06 (v4.0.0 published, both Zenodo DOIs minted and recorded)"
    - "114-02 (verified RTD/shields.io URL table)"
  provides:
    - "CITATION.cff carrying the stable Zenodo software concept DOI"
    - "Seven-badge README row (tests, docs, coverage, python, pypi, license, DOI)"
    - "Phase 114 closing evidence record: four-DOI identifier map, badge/link audits, per-requirement evidence"
  affects: []
tech-stack:
  added: []
  patterns:
    - "Zenodo concept DOI (not version DOI) as the sole software citation target — stable forever, backfilled post-release"
key-files:
  created: []
  modified:
    - CITATION.cff
    - README.md
decisions:
  - "Used the concept DOI 10.5281/zenodo.22692575 in CITATION.cff and the README DOI badge, per 114-06's explicit label — not the version DOI 10.5281/zenodo.22692576"
  - "Bundled two verified cosmetic fixes into the same README edit: tests badge &label=tests, and re-verification (no fix needed) of the pypi/v badge cache"
metrics:
  duration: "~35 min"
  completed: "2026-09-10"
---

# Phase 114 Plan 07: Backfill Software DOI, Complete Badge Row, Phase Closeout Summary

Backfilled the Zenodo software **concept** DOI (`10.5281/zenodo.22692575`) into
`CITATION.cff` and the README, completing the seven-badge row and closing Phase 114
with a full evidence record of every publication surface.

## Task 1 — CITATION.cff DOI backfill and README badge/citation completion

### The two software DOIs, quoted from 114-06-SUMMARY.md

| Label | DOI | Used where |
|---|---|---|
| **Concept DOI** (stable across versions) | `10.5281/zenodo.22692575` | **Used** — `CITATION.cff` `doi:` field, README DOI badge, README Citation section |
| Version DOI (pins v4.0.0 only) | `10.5281/zenodo.22692576` | **Not used anywhere in this plan** |

Both were re-verified independently in this plan (not merely trusted from 114-06):

```
curl -sL -o /dev/null -w "%{http_code}" https://zenodo.org/badge/DOI/10.5281/zenodo.22692575.svg
  -> 200
curl -sL https://doi.org/10.5281/zenodo.22692575
  -> 200, <title>AquaPose | Zenodo</title>, license "agpl-3.0-or-later" present in body
```

This confirms the concept DOI resolves to the **software** record (title AquaPose,
AGPL-3.0-or-later), not the dataset record — the specific failure mode D-09/T-114-07-02
exists to prevent.

### CITATION.cff changes

- Added `doi: 10.5281/zenodo.22692575` (bare form, not a URL), placed immediately after
  `date-released` and before `url`, alongside the other top-level identifier/date fields.
- `version: 4.0.0` and `date-released: "2026-09-10"` were already correct as written in
  Pass A (114-03) and confirmed to match 114-06's actual release date — no change needed
  to either field, verified against `GitHub Release / Published: 2026-09-10T14:27:35Z`.
- `license: AGPL-3.0-or-later` unchanged.

Verified via `hatch run python` + PyYAML:
```
CFF Pass B ok: 10.5281/zenodo.22692575
```
(`doi` present, starts with `10.5281/zenodo.`, is neither dataset DOI, `version == '4.0.0'`,
`license == 'AGPL-3.0-or-later'`.)

### README.md changes

1. **Seventh badge added** — `[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22692575.svg)](https://doi.org/10.5281/zenodo.22692575)`,
   appended last after `license`, preserving the existing six-badge order from Plan 04
   (tests, docs, coverage, python, pypi, license, **DOI**) — matches D-04's enumeration.
2. **Citation section** rewritten to name the software concept DOI explicitly and state
   it resolves to the latest version, then distinguish it from the dataset DOI
   (`10.5281/zenodo.22264079`) in the same paragraph — a reader can tell which one they
   want without opening either record. No BibTeX added (D-10 keeps BibTeX out of the
   README).
3. **`docs/getting-started/tutorial.md` untouched** — confirmed via
   `git diff --stat docs/getting-started/tutorial.md` (no output).

### Bundled fixes (verified, from 114-06's Findings)

| Fix | Before | After | Verification |
|---|---|---|---|
| Tests badge label | `&label=tests` missing from the `github/actions/workflow/status` badge URL; rendered `build: passing` (mismatched the `[![tests]...]` alt text) | Added `&label=tests` | Re-fetched: renders `<title>tests: passing</title>` |
| `pypi/v` badge cache | Rendered `pypi: v1.0.0` (shields.io `max-age=900` cache) at 114-06 time-of-writing | **Re-checked, not fixed** — still reads `v1.0.0` as of this plan's execution. PyPI's own JSON API (`pypi.org/pypi/aquapose/json`) already reports `"version": "4.0.0"` as latest, confirming the badge is a stale-cache artifact, not a real problem. Per the plan's instruction, the badge URL was **not** changed to work around the cache — it self-heals. |

Commit: `5746ab2` — `feat(114-07): backfill Zenodo concept DOI and complete README badge row`

## Task 2 — Phase closeout: publication-surface audit

### Four-DOI identifier map

| Identifier | DOI | Resolves to | Referenced in |
|---|---|---|---|
| Software **concept** | `10.5281/zenodo.22692575` | AquaPose software record (latest version, all versions) — verified title "AquaPose", license agpl-3.0-or-later | `CITATION.cff` (`doi:`), `README.md` (DOI badge + Citation section) |
| Software **version** | `10.5281/zenodo.22692576` | AquaPose v4.0.0 snapshot specifically | Not referenced in any repository file — recorded only in `114-06-SUMMARY.md` for provenance |
| Dataset **concept** | `10.5281/zenodo.22264078` | Tutorial video dataset, all versions | Not referenced in any repository file (only the dataset **version** DOI is used in-repo) |
| Dataset **version** | `10.5281/zenodo.22264079` | Tutorial video dataset, specific deposit used by the tutorial | `README.md` (Quick Start dataset pointer, Citation section), `docs/getting-started/tutorial.md` |

All four remain distinguishable: the software DOIs never appear alongside the dataset
DOIs in the same file except in the README's Citation section, where they are
deliberately juxtaposed and labeled.

### Badge row audit — all seven badges

| # | Badge | HTTP status | Rendered label |
|---|---|---|---|
| 1 | tests | 200 | `tests: passing` |
| 2 | docs | 200 | `docs: passing` |
| 3 | coverage | 200 | `coverage: 69%` |
| 4 | python | 200 | `python: 3.11 \| 3.12 \| 3.13` |
| 5 | pypi | 200 | `pypi: v1.0.0` — stale shields.io cache; PyPI JSON API confirms `4.0.0` is actually latest (see Task 1). No badge reads `not found` or `unknown`. |
| 6 | license | 200 | `license: AGPL-3.0-or-later` |
| 7 | DOI | 200 | `DOI \| 10.5281/zenodo.22692575` (confirmed from raw SVG `<text>` elements) |

None reads `not found` or `unknown`.

### Link audit — every absolute URL in README.md (20 unique targets)

| URL | HTTP status |
|---|---|
| `https://aquapose.readthedocs.io/en/latest/` | 200 |
| `https://aquapose.readthedocs.io/en/latest/api/index.html` | 200 |
| `https://aquapose.readthedocs.io/en/latest/getting-started/concepts.html` | 200 |
| `https://aquapose.readthedocs.io/en/latest/getting-started/installation.html` | 200 |
| `https://aquapose.readthedocs.io/en/latest/getting-started/tutorial.html` | 200 |
| `https://codecov.io/gh/McGrathLab/AquaPose` | 200 |
| `https://doi.org/10.5281/zenodo.22692575` | 200 (resolves to AquaPose software record) |
| `https://github.com/McGrathLab/AquaPose/actions/workflows/test.yml` | 200 |
| `https://github.com/McGrathLab/AquaPose/blob/main/CITATION.cff` | 200 |
| `https://github.com/McGrathLab/AquaPose/blob/main/LICENSE` | 200 |
| `https://github.com/McGrathLab/AquaPose/blob/main/LICENSING.md` | 200 |
| `https://img.shields.io/badge/license-AGPL--3.0--or--later-blue` | 200 |
| `https://img.shields.io/codecov/c/github/McGrathLab/AquaPose/main` | 200 |
| `https://img.shields.io/github/actions/workflow/status/McGrathLab/AquaPose/test.yml?branch=main&label=tests` | 200 |
| `https://img.shields.io/pypi/pyversions/aquapose` | 200 |
| `https://img.shields.io/pypi/v/aquapose` | 200 |
| `https://img.shields.io/readthedocs/aquapose/latest` | 200 |
| `https://pypi.org/project/aquapose/` | 200 — **vacuous** per 114-06's documented caveat: this endpoint is bot-challenge-protected and returns 200 for any URL including nonexistent versions. Not relied on as evidence of anything beyond "reachable." |
| `https://zenodo.org/badge/DOI/10.5281/zenodo.22692575.svg` | 200 |
| `https://zenodo.org/records/22264079` | 200 |

Every target starts with `http` — no relative links. All 20 return 200.

(Note: fetched via `curl`'s default User-Agent. `zenodo.org` and `doi.org` return 403
to Python's `urllib` default/generic `Mozilla/5.0` User-Agent strings — a WAF quirk, not
a real failure. Recorded so a future agent doesn't misread the 403 as broken.)

### Requirement evidence

| Requirement | Check | Result |
|---|---|---|
| README-01 | `README.md` opens with problem statement, what a user gets (3D midlines/kinematics), and who it's for (behavioral/neuroscience researchers with multi-camera rigs) | Present (Plan 04, unmodified by this plan) — visually confirmed in the file read at the start of this plan |
| README-02 | Seven badges present, `img.shields.io` count >= 6 plus one `zenodo.org/badge/DOI`, all seven return 200 with real (non-`unknown`) labels | Verified above — badge audit table, all 200 |
| README-04 | Install (`pip install aquapose`), quick start against Zenodo dataset (`10.5281/zenodo.22264079` linked), docs links present, Citation section with a resolvable software DOI | Verified: `pip install aquapose` line present; dataset DOI link present and 200; four docs links present and 200; Citation section names `10.5281/zenodo.22692575` and it resolves (200, AquaPose software record) |
| DOCS-08 | Docs build green and reachable at the URL declared in `pyproject.toml` (`Documentation = "https://aquapose.readthedocs.io"`) | `https://aquapose.readthedocs.io` -> 200 (redirects to `/en/latest/`, confirmed serving AquaPose's own content per 114-02). **Note:** the requirement text says "from `dev`" — D-07 was overridden in 114-02 (developer decision, recorded there): the actual RTD target is `main` via the `latest` version, not `dev`. The URL and green-build facts hold; the branch clause in the requirement's wording is stale relative to the override. Local `hatch run docs:build` also exits 0 (see Green Gates below). Requirement status update is verify-phase's job, not this plan's — recorded here as evidence only. |
| README-03 | Deferred | Recorded as deferred in `.planning/REQUIREMENTS.md` line 54, todo file `.planning/todos/pending/2026-09-09-readme-hero-media-3d-reconstruction.md` (user decision, 2026-09-09, out of Phase 114 scope) |

### License triangle consistency

| Source | Value |
|---|---|
| `LICENSE` | GNU AFFERO GENERAL PUBLIC LICENSE (AGPL text, header names AGPL) |
| `pyproject.toml` | `license = "AGPL-3.0-or-later"` |
| `LICENSING.md` | `AGPL-3.0-or-later` |
| `CITATION.cff` | `license: AGPL-3.0-or-later` |
| README license badge | `license: AGPL-3.0-or-later` (rendered label, verified above) |

All five agree.

### Org-casing and `tlancaster6` residue sweep

- `McGrathLab/AquaPose` casing checked in `README.md`, `CITATION.cff`,
  `CODE_OF_CONDUCT.md`, `docs/contributing.md`, `pyproject.toml` — no lowercase-casing
  variant found (`grep -iv` on the exact casing produced no output, i.e. every match is
  the canonical casing).
- `grep -rln "tlancaster6" --include='*.md' --include='*.toml' --include='*.yaml'
  --include='*.yml' --include='*.py' .` excluding `CHANGELOG.md`, `.planning/`,
  `docs/_build/` — **no output**, i.e. no residual occurrence outside the sanctioned
  historical-record locations.

### Green gates

| Gate | Exit code | Notes |
|---|---|---|
| `hatch run docs:build` | 0 | Sphinx build succeeded, all modules highlighted, no errors |
| `hatch run lint` | 0 | `All checks passed!` |
| `hatch run test` | 0 | **1410 passed, 2 skipped, 17 deselected** in 77.16s. Zero failures — better than the documented Windows-noise baseline (`windows-test-failures-phase-109`, ~21 expected failures); no failures to classify this run. |

### Tag integrity

```
git rev-parse v4.0.0        -> 1c2a7e507e8936530eb5452788976e404db43e64  (tag object)
git rev-list -n1 v4.0.0     -> 907425affa7d9bd2110bbf5f7f377507249e2d3f  (commit)
```
Matches `114-06-SUMMARY.md`'s recorded tagged commit exactly. No re-tag, no amend.

Per the acceptance criteria, this plan performed **no writes** to
`.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, or `.planning/STATE.md` during
Task 2 — confirmed no diff in either file prior to this SUMMARY-creation step's own
state-update phase (which happens after this document, per the executor workflow, and
is a separate, out-of-plan-scope step performed by the orchestrator's standard
post-plan protocol, not Task 2 itself).

## Deviations

None — plan executed exactly as written. Both bundled fixes from `114-06-SUMMARY.md`'s
Findings were applied/re-verified as instructed; the `pypi/v` badge cache was
re-checked and correctly left unmodified per the plan's explicit instruction not to
work around a self-healing cache.

## Self-Check: PASSED

- FOUND: `.planning/phases/114-publication-readme-badges-live-docs/114-07-SUMMARY.md`
- FOUND: commit `5746ab2` in `git log --oneline --all`
