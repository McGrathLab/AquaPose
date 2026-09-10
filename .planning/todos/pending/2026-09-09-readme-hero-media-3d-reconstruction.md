---
created: 2026-09-09T00:00:00.000Z
title: Add README hero media showing a 3D reconstruction rendering inline on GitHub
area: publication
files:
  - README.md
  - reference_outputs/animation_3d.html
  - reference_outputs/overlay_mosaic.mp4
---

## Problem

README-03 ("Hero media shows a 3D reconstruction rendering inline on GitHub") was
**deferred out of Phase 114 by explicit user decision on 2026-09-09**, not attempted
and abandoned. See `.planning/phases/114-publication-readme-badges-live-docs/114-CONTEXT.md`
`<deferred>` for the discussion record. Phase 114's ROADMAP success criterion 3 and
REQUIREMENTS.md's README-03 bullet and traceability row are annotated as deferred
(not deleted) pointing at this todo, so the milestone's coverage accounting stays
honest and a future maintainer can find where to resume.

## Why this matters

A hero media section is a meaningful trust/engagement signal on the README landing
page (the "who is this for, does it actually work" first impression), but it is not
required for the v4.0 Publication milestone's core value: install, run, cite. The
user chose to drop it outright rather than negotiate a cheaper version of it, and
explicitly did not want it reintroduced as a "small" scope addition to Phase 114.

## Solution

The source assets already exist — no re-rendering or re-capture is required. They
were produced and shipped as part of the Phase 111 Zenodo tutorial deposit
(`10.5281/zenodo.22264079`):

- `reference_outputs/animation_3d.html` — interactive Plotly 3D midline animation.
- `reference_outputs/overlay_mosaic.mp4` — 2D reprojection overlay mosaic across
  the 12-camera rig (re-encoded at CRF 28, ~12 MB).

Two format constraints recorded in `.planning/REQUIREMENTS.md`'s Open Decisions
table ("Hero media format") apply to whichever asset is chosen:

- GitHub strips `<iframe>` from rendered Markdown, so `animation_3d.html` cannot be
  embedded directly and inline-interactive playback is not an option as-is (it would
  need re-rendering to a GIF/MP4 loop, or linking out rather than embedding).
- An uploaded `.mp4` (such as `overlay_mosaic.mp4`) renders inline on GitHub if the
  file is small enough — the existing 12 MB re-encode is a reasonable starting point
  to test against GitHub's inline video size/format limits.

Whichever asset lands must preserve the README's absolute-URL discipline: per
`pyproject.toml:9`, `README.md` is also PyPI's long description, and PyPI does not
resolve relative asset paths the way GitHub does. Any embedded media reference must
use an absolute URL (e.g. a `raw.githubusercontent.com` link, a GitHub user-content
CDN link from an uploaded asset, or a link to the Zenodo deposit) rather than a
repo-relative path.

## Verification

- `README.md` contains a hero media element (image, GIF, or video embed) that
  renders inline on both github.com and pypi.org.
- The embedded/linked asset resolves via an absolute URL, not a relative repo path.
- `hatch run docs:build` still exits 0 (no new warning introduced by the change).
- `git diff --stat` shows the new media reference in `README.md`; if a new binary
  asset is added to the repo (rather than linked from the Zenodo deposit or GitHub's
  user-content CDN), confirm it does not bloat the repo clone size unreasonably.
