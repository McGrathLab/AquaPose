---
created: 2026-09-10T00:00:00.000Z
title: Read the Docs `stable` build is broken; decide the docs version strategy for citation
area: docs
files:
  - .readthedocs.yaml
  - pyproject.toml
  - README.md
---

## Problem

Two related loose ends left by Phase 114's docs work.

**1. RTD's `stable` version has never built successfully.** Its most recent build
(2026-08-12, commit `45972d9a`) failed. `stable` normally tracks the highest semver
tag, so now that `v4.0.0` exists it is the natural target for citation-stable
documentation — and it is broken.

**2. The docs version strategy was decided under time pressure and deserves a
deliberate second look.** Phase 114's discuss stage recorded D-07: RTD's default
version should be `dev`. During execution that was **overridden** to `main` via RTD's
`latest`, because `main` was 1732 commits stale and three of the four README funnel
destinations 404'd on the published docs. `main` was fast-forwarded to `dev` and
`latest` rebuilt green. See
`.planning/phases/114-publication-readme-badges-live-docs/114-02-SUMMARY.md`
("Decision Overrides").

That override was the right call for unblocking the release. But it means the current
state is: **the README, the badge row, and `pyproject.toml`'s declared Documentation
URL all point at `latest`, which tracks `main`, which now moves with `dev`.** A reader
following a citation to the docs sees whatever is on the development tip, not what the
version they installed actually does.

## Why this matters

For a tool being published for citation, "the docs a reader lands on" and "the version
they can install" ideally correspond. Right now they do not, and the divergence grows
with every merge to `main`. The failure mode is subtle: a researcher reads a doc page
describing behaviour that does not exist in the 4.0.x they installed.

This is not urgent — `latest` is currently correct and green, and `main` only advances
at merges. It is the kind of thing that is cheap to fix now and expensive to discover
later from a confused user.

## Solution

**Fix `stable` first**, because the decision below depends on whether it can build.
Trigger a `stable` build from the RTD dashboard now that `v4.0.0` is tagged, read the
build log, and fix the cause. Note that `.readthedocs.yaml` uses `build.commands`
(`pip install hatch`, `hatch run docs:build`, then copying `docs/_build/html/*` into
`_readthedocs/html/`), so RTD installs nothing else — a failure is most likely
environmental or a missing file at the tagged commit rather than a config error. The
same build passes locally via `hatch run docs:build`, so resist editing
`.readthedocs.yaml` before understanding the log.

**Then choose the version strategy.** Roughly:

- **Point everything at `stable`.** Docs correspond to the latest released version.
  Requires updating `pyproject.toml`'s Documentation URL, the README's four funnel
  links and the docs badge, and setting RTD's default version to `stable`. Most
  correct for citation; means docs only update at releases.
- **Keep `latest` as default, activate `stable` alongside.** Readers get current docs
  by default with a version switcher offering the released docs. No link changes
  needed; relies on readers noticing the switcher.
- **Keep the status quo.** Defensible if releases are frequent enough that `main` and
  the latest tag rarely diverge much.

Whichever is chosen, if README URLs change, remember the file is also PyPI's long
description and the change only reaches PyPI on the next release.

## Verification

- The most recent RTD `stable` build shows status Passed, and its log shows
  `hatch run docs:build` with no torch or project install (the detached `docs` env
  premise, D-08).
- `https://aquapose.readthedocs.io/en/stable/` returns 200 and serves AquaPose's own
  content — check for a project-unique string, not just the status code.
- If links were repointed: every URL in `README.md` returns 200, and the four funnel
  destinations (Installation, Concepts, Tutorial, API reference) resolve under the
  chosen version prefix.
- `pyproject.toml`'s declared Documentation URL resolves to the intended version.
- RTD's default version matches the decision, verified by following the bare domain
  `https://aquapose.readthedocs.io` and checking the redirect target.
