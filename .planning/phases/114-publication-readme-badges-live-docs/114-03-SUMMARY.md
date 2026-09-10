---
phase: 114-publication-readme-badges-live-docs
plan: 03
subsystem: release-metadata
tags: [packaging, semantic-release, citation, changelog]
dependency-graph:
  requires: []
  provides:
    - "version = 4.0.0 in pyproject.toml"
    - "CITATION.cff (Pass A, no DOI)"
    - "CHANGELOG.md migration note for the version reset"
  affects:
    - "114-04 (README, reads the 4.0.0 version and links to CITATION.cff)"
    - "114-06 (tags v4.0.0, relying on tag_format producing a trigger-matching tag)"
    - "114-07 (Pass B, backfills the Zenodo concept DOI into CITATION.cff)"
tech-stack:
  added: []
  patterns:
    - "CFF 1.2.0 citation metadata sourced from pyproject.toml + LICENSE, no doi key (two-pass DOI sequencing, D-11)"
key-files:
  created:
    - CITATION.cff
  modified:
    - pyproject.toml
    - CHANGELOG.md
decisions:
  - "date-released in CITATION.cff was written as 2026-09-10 (today's date at execution time); Plan 07 must re-verify this against the actual v4.0.0 tag date and correct it in Pass B if they differ."
metrics:
  duration: "~15m"
  completed: "2026-09-10"
---

# Phase 114 Plan 03: Pre-tag release metadata (version reset, CHANGELOG note, CITATION.cff) Summary

Reset `pyproject.toml`'s version to `4.0.0`, added a hand-maintained CHANGELOG
entry explaining the `1.2.0-dev.6` → `4.0.0` discontinuity, and created a
DOI-less `CITATION.cff` (D-11 Pass A) — putting the repo in a state where
tagging `v4.0.0` will actually fire `publish.yml`.

## What Was Built

### Task 1 — Version reset (`pyproject.toml`)

Changed `[project] version` from `1.2.0-dev.6` to `4.0.0`. `git diff pyproject.toml`
confirms exactly one changed line; `[tool.semantic_release]` is byte-identical to
HEAD. `hatch version` reports `4.0.0`.

**Evidence gathered per the plan's `read_first`/`done` requirements:**

- `git tag --list` (full output observed):
  `pre-108-merge, v1.0, v1.0.0, v1.1.0, v1.1.0-dev.1..8, v1.1.1, v1.2.0-dev.1..6, v2.0, v2.1, v3.1, v3.10, v3.2, v3.3, v3.4, v3.5, v3.6, v3.8, v3.9`.
  None of the `v3.x` / `v2.x` / `v1.x` tags are three-component
  (`v[0-9]+.[0-9]+.[0-9]+`) — `v3.4`..`v3.9` and `v2.0`/`v2.1` are two-component,
  and the `-dev.N` tags carry a prerelease suffix that also does not match the
  trigger regex. `v1.0.0` and `v1.1.0`/`v1.1.1` are the only historically
  three-component tags, but they predate `publish.yml`'s creation. **None of the
  existing tags currently on the repo match the trigger going forward under the
  reset scheme.**
- `tag_format = "v{version}"` combined with `version = "4.0.0"` yields the
  literal tag `v4.0.0`, which `python -c "re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', 'v4.0.0')"`
  confirms matches `publish.yml`'s trigger.
- **Explicit trap recorded:** `[tool.semantic_release.branches.dev]` sets
  `prerelease = true` with `prerelease_token = "dev"`. If `semantic-release
  version` is ever run on the `dev` branch, it will compute a `-dev.N` suffix
  (e.g. `v4.0.1-dev.1`), producing a tag that does **not** match
  `v[0-9]+.[0-9]+.[0-9]+` — reproducing the exact failure mode that has
  blocked every prior release. **Plan 06 must create the `v4.0.0` release tag
  as a plain annotated `git tag v4.0.0`, not via `semantic-release version` on
  `dev`.**

### Task 2 — CHANGELOG migration note

Added a new `###` sub-heading under `## Migration Notes`, above the existing
`### Unreleased — aquapose.io.discovery submodule removed` entry and above the
`<!-- version list -->` marker. The note states: the jump is a one-time
milestone alignment (D-01), not a semver-earned bump; no 2.x/3.x releases
exist on PyPI because AquaPose was never published before `4.0.0`; the
two-component `v3.x` git tags never matched `publish.yml`'s trigger, which is
why nothing has ever published. `git diff CHANGELOG.md` shows only added
lines, all above the marker — zero changes to the generated region.

### Task 3 — `CITATION.cff` (Pass A, no DOI)

Created `CITATION.cff` at the repo root, CFF 1.2.0, sourced from
`pyproject.toml`'s `[project]` metadata and the `LICENSE` copyright line
(`Copyright (C) 2026 Tucker Lancaster and the McGrath Lab at the Georgia
Institute of Technology`):

- `cff-version: 1.2.0`, `title: AquaPose`, `version: 4.0.0`
- `license: AGPL-3.0-or-later` — byte-identical to `pyproject.toml:11`
- `authors[0]`: `family-names: Lancaster`, `given-names: Tucker`,
  `affiliation: McGrath Lab, Georgia Institute of Technology` (no ORCID —
  none found in-repo, not invented)
- `url` / `repository-code`: `https://github.com/McGrathLab/AquaPose`
  (exact casing)
- `keywords`: copied verbatim from `pyproject.toml`'s `keywords` list
- **`date-released: "2026-09-10"`** — the date this task was executed. **Plan
  07 must re-verify this against the actual `v4.0.0` tag date and correct it
  if the tag lands on a different day.**
- **No `doi` key at all** — verified by `'doi' not in yaml.safe_load(...)` and
  `grep -c '^\s*#*\s*doi'` returning 0 (no commented-out line either).
- No dataset DOI (`10.5281/zenodo.22264079` or `...78`) present anywhere in
  the file — confirmed via grep.
- `docs/getting-started/tutorial.md` untouched (`git diff --stat` empty).

## Verification

- `hatch version` → `4.0.0`
- `python -c "import yaml; yaml.safe_load(open('CITATION.cff'))"` succeeds;
  no `doi` key present.
- `CITATION.cff`'s `license` field byte-identical to `pyproject.toml`'s.
- `git diff CHANGELOG.md` — changes only above `<!-- version list -->`.
- `hatch run lint` — all checks passed.
- `hatch run docs:build` — exit 0 (Sphinx `-W --keep-going`, `index.html`
  produced).
- `hatch run test` — 1410 passed, 2 skipped, 17 deselected, 0 failures (no
  new failures beyond the documented Windows env baseline).

## Deviations from Plan

None — plan executed exactly as written. All three tasks matched their
`read_first`/`action`/`verify`/`acceptance_criteria` blocks with no
auto-fixes, no blocking issues, and no scope changes.

## Commits

- `dde7a4d` — `chore(114-03): reset package version to 4.0.0 for v4.0 Publication milestone`
- `605560f` — `docs(114-03): explain 1.2.0-dev.6 to 4.0.0 version reset in CHANGELOG`
- `a6b54c8` — `feat(114-03): add CITATION.cff (Pass A, no DOI)`

## Self-Check: PASSED

- FOUND: `pyproject.toml` contains `version = "4.0.0"`
- FOUND: `CHANGELOG.md` contains the new migration note above `<!-- version list -->`
- FOUND: `CITATION.cff` at repo root, valid YAML, no `doi` key
- FOUND: commit `dde7a4d` in `git log`
- FOUND: commit `605560f` in `git log`
- FOUND: commit `a6b54c8` in `git log`
