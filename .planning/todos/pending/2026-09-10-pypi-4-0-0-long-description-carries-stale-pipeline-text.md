---
created: 2026-09-10T00:00:00.000Z
title: PyPI's 4.0.0 page describes a pipeline architecture removed in v3.7
area: publication
files:
  - README.md
  - pyproject.toml
---

## Problem

`README.md` is also PyPI's long description (`pyproject.toml:9`). The version
published with `aquapose` 4.0.0 contained a `## Pipeline` section describing an
architecture that was removed in v3.7:

- **OC-SORT tracking** — removed; `src/aquapose/engine/config.py:600` records
  `"removed (OC-SORT only; keypoint_oks does not use IoU matching)"`. The tracker is
  `KeypointTracker`, matching on OKS keypoint similarity.
- **A YOLO-seg midline backend** — no seg backend exists in the pipeline; only
  `src/aquapose/training/yolo_training.py` references seg models, for training.
- **Stage order** `Detection → Tracking → Association → Midline → Reconstruction` —
  contradicted by `src/aquapose/engine/pipeline.py:280-289`, which documents
  `Detection → Pose → Tracking → Association → Reconstruction`. `PoseStage` runs
  second, enriching `Detection` objects in place before tracking.

This was caught by the Phase 114 code review and **fixed in the repository** (commit
`18190e5`). GitHub and Read the Docs are correct.

**PyPI is not, and cannot be.** Long descriptions are frozen per release; PyPI has no
metadata-edit path. The 4.0.0 project page will describe the wrong architecture until
a later version supersedes it.

## Why this matters

PyPI is a primary discovery surface for a published research tool, and this is the
one surface the Phase 114 verification could not correct after the fact. A researcher
evaluating AquaPose from its PyPI page reads that it tracks with OC-SORT and extracts
midlines with a segmentation backend — neither of which is true — and may form a
judgement about fit, or cite the approach incorrectly.

The scale of the error is worth being honest about: it is a wrong description of the
method, not a typo. Against that, 4.0.0 is functional and correctly installable; the
defect is purely descriptive.

## Solution

This is a judgement call for the maintainer, not a mechanical fix. Two paths:

**Cut a 4.0.1 patch release.** The corrected README propagates to PyPI as the current
project page (PyPI shows the latest release's long description). Mechanically cheap
now that the release path is proven: the tag-driven `publish.yml` works end to end
(`test → build → publish-testpypi → publish`), trusted publishers are registered on
both indexes, and the release procedure is a plain annotated tag. It also mints a new
Zenodo version DOI under the same concept DOI, which is harmless — the concept DOI
`10.5281/zenodo.22692575` in `CITATION.cff` continues to resolve to the latest version.

Doing this well means pairing it with the `v4.0.0` changelog backfill — see
`2026-09-10-changelog-has-no-v4-0-0-entry-generation-path-retired.md` — so 4.0.1 does
not inherit the same gap.

**Leave it and let the next feature release carry the fix.** No wrong code is
published; only wrong prose, on one surface, for as long as 4.0.0 remains latest.
Acceptable if another release is expected soon.

## Verification

If 4.0.1 is cut:

- `https://pypi.org/pypi/aquapose/json` reports `info.version` of `4.0.1`.
- The published long description contains `**Pose**` and does **not** contain
  `OC-SORT` or `YOLO-seg`. Fetch and compare against the local `README.md`:
  read the JSON with `urllib` and decode explicitly as UTF-8 — piping through stdin
  on Windows mangles em-dashes via cp1252 and produces a false mismatch.
- Do **not** assert on `https://pypi.org/project/aquapose/...` HTML. That endpoint is
  bot-challenge-protected and returns HTTP 200 with a "Client Challenge" page for any
  URL, including versions that do not exist. Use the simple index
  (`https://pypi.org/simple/aquapose/`) and the JSON API instead.
- `CITATION.cff`'s concept DOI still resolves; the new version DOI is distinct.
