---
created: 2026-09-10T00:00:00.000Z
title: CHANGELOG has no v4.0.0 entry and the generation path was retired
area: release
files:
  - CHANGELOG.md
  - .github/workflows/release.yml
  - pyproject.toml
---

## Problem

`aquapose` 4.0.0 is published on PyPI, GitHub, and Zenodo, but `CHANGELOG.md`'s
generated region (everything below the `<!-- version list -->` marker at line 57) has
no `v4.0.0` entry. Its newest entry is:

```
## v1.2.0-dev.6 (2026-09-03)
```

A user who opens the changelog to find out what is in the release they just installed
finds a prerelease from before it.

This is a direct consequence of a Phase 114 decision, not an oversight in isolation.
`release.yml` previously ran `semantic-release version` on every push to `main` and
`dev`, which is what wrote those entries. Phase 114 retired that trigger to
`workflow_dispatch` only, because the same command recomputes the version from commit
history and would have clobbered the deliberate `4.0.0` reset — and on `main` would
have cut a trigger-matching tag and published an unintended, immutable version to
PyPI. See `.planning/phases/114-publication-readme-badges-live-docs/114-02-SUMMARY.md`
("Blocker Found and Fixed: release.yml").

Retiring the automation was correct. What was not carried forward is the changelog
half of what that automation did.

## Why this matters

The changelog gap is not cosmetic for a publication milestone. The v4.0 milestone's
core value is "install, run, cite" for an outside researcher, and a changelog that
stops three commits before the released version undercuts the same trust signal the
badge row and DOI are meant to build. It also compounds: every future release cut by
the new manual `git tag -a` path will have the same gap unless the process is fixed
once.

Note the trap: running `semantic-release version` manually to regenerate the entry
would reintroduce exactly the hazard Phase 114 removed — it bumps the version and cuts
a tag as a side effect. This is not a matter of "just run it once."

## Solution

Two parts, and the second matters more than the first.

**1. Backfill the `v4.0.0` entry.** Write it by hand above the existing
`## v1.2.0-dev.6` block, covering what actually landed in 4.0.0 relative to the last
real release (`1.0.0`, 2026-02-19 — not `1.2.0-dev.6`, which was never published).
That is a large span; the milestone summaries under `.planning/phases/` are the
practical source. Keep the existing hand-maintained `## Migration Notes` section
above the marker untouched.

**2. Decide and document the ongoing changelog process.** Options, roughly in
increasing order of effort:

- Generate the changelog only, without versioning or tagging, e.g. via
  `semantic-release changelog` (verify the subcommand exists in the pinned
  python-semantic-release version) invoked from the retired `release.yml` under
  `workflow_dispatch`, or as a pre-tag step in the release checklist.
- Maintain `CHANGELOG.md` by hand as part of the release procedure, and delete or
  clearly fence the now-unmaintained generated region so it does not look current.
- Re-enable automated versioning on a release-only path (e.g. a dedicated workflow
  gated on a manually-dispatched input) with the 4.0.0 baseline anchored so it cannot
  recompute a wrong version.

Whichever is chosen, record it where the next releaser will see it — the
`[tool.semantic_release]` comment block in `pyproject.toml` and `release.yml`'s
header already carry the hazard note and are the natural place.

## Verification

- `CHANGELOG.md` contains a `## v4.0.0` entry describing the release, placed in the
  correct position relative to the existing generated entries.
- The `## Migration Notes` hand-maintained section above `<!-- version list -->` is
  unchanged.
- The chosen ongoing process is documented in `pyproject.toml`'s
  `[tool.semantic_release]` comment block and/or `.github/workflows/release.yml`.
- If a generation command is adopted: running it produces changelog output and does
  **not** modify `pyproject.toml`'s `version` field and does **not** create a git tag.
  Verify with `git status --porcelain` and `git tag --list` immediately after.
- `hatch version` still reports the intended version afterwards.
