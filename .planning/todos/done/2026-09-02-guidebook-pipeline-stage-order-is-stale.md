---
created: 2026-09-02T00:00:00.000Z
title: GUIDEBOOK.md section 6 documents a stale pipeline stage order and feeds it into discuss-phase
area: docs
files:
  - .planning/GUIDEBOOK.md
  - CLAUDE.md
  - src/aquapose/engine/pipeline.py
---

## Problem

`.planning/GUIDEBOOK.md` §6 "Pipeline Stages" documents:

```
Detection -> 2D Tracking -> Cross-Camera Association -> Midline -> Reconstruction
```

The actual pipeline is different. `build_stages` in
`src/aquapose/engine/pipeline.py` states its own order explicitly in its
docstring:

```
DetectionStage -> PoseStage -> TrackingStage -> AssociationStage -> ReconstructionStage
```

and calls the difference out directly: *"PoseStage (Stage 2) runs before
tracking, enriching..."*. Midline/keypoint extraction now happens **before**
tracking and association, not after. Phase 110's published API pages
(`docs/api/core/{detection,pose,tracking,association,reconstruction}.rst`)
corroborate the real order.

The guidebook text predates the v3.7 pipeline reorder and was never updated.

## Why it matters

This is not an inert stale doc. `CLAUDE.md` contains an explicit
agent instruction:

> ### discuss-phase
> When running `gsd:discuss-phase`, before doing anything else:
> 1. Inform the user: "I noticed project instructions to read the guidebook..."
> 2. Read this document and incorporate its content as context for the
>    discussion: .planning/GUIDEBOOK.md

So every `discuss-phase` run ingests the wrong stage order as authoritative
project context, and any phase whose scope touches pipeline structure inherits
the error. Phase 113's own plan acceptance criteria were written against the
stale order and had to be deviated from at execution time (see
`.planning/phases/113-concepts-tutorial/113-04-SUMMARY.md`), which is exactly
the failure mode this todo exists to stop recurring.

## Solution

1. Correct §6's stage-flow line and per-stage subsections to the real order,
   verified against `build_stages` and each stage module's docstring rather
   than against any other prose doc.
2. Note the synthetic-mode variant while there: `build_stages` returns a
   **4-stage** list when `config.mode == "synthetic"`
   (`SyntheticDataStage -> TrackingStage -> AssociationStage -> ReconstructionStage`),
   which §6 does not mention at all.
3. Audit the rest of GUIDEBOOK.md against source for the same class of drift —
   if §6 went stale through a reorder, neighboring sections likely did too.
4. Consider adding a cheap guard so this cannot silently rot again: a test that
   asserts the stage-name sequence in `build_stages` matches the sequence named
   in GUIDEBOOK.md §6.

Terminal gate: GUIDEBOOK.md §6 stage order matches `build_stages` exactly,
including the synthetic-mode variant.

## Notes

Found during Phase 113 while authoring the concepts page (DOCS-04), which
required grounding every pipeline claim in source. The concepts page at
`docs/getting-started/concepts.md` already documents the **correct** order --
so the published user-facing docs are right and only the internal planning
guidebook is wrong. Fixing this is about stopping bad context from reaching
future planning agents, not about correcting anything a user reads.

Related: the same phase corrected `CLAUDE.md`'s stale `{p, psi, kappa, s}`
"Domain Conventions" line (D-01), which was a sibling instance of internal
agent-facing docs drifting from the codebase.

## Fixed

**Date:** 2026-09-02
**Fixed by:** Phase 113.1, Plan 03 (`113.1-03-PLAN.md`, D-14, D-15).
**Evidence:** GUIDEBOOK.md section 6's stage-flow line and per-stage
subsections were corrected against `build_stages` in
`src/aquapose/engine/pipeline.py` (real order: Detection -> Pose -> Tracking
-> Association -> Reconstruction), and the previously-undocumented 4-stage
synthetic-mode variant was added. Commits `04496a7`, `ce1b54a`. A guard test
now asserts the GUIDEBOOK-documented stage-name sequence matches
`build_stages` so this cannot silently drift again.
