---
created: 2026-09-02T00:00:00.000Z
title: GUIDEBOOK.md sections 3, 4, 7, 8 and 14 drift the same way section 6 did
area: docs
files:
  - .planning/GUIDEBOOK.md
---

## Problem

While correcting `.planning/GUIDEBOOK.md` section 6's pipeline stage order
(113.1-03, D-14/D-15), the plan's bounded drift scan checked sections 3, 4, 7,
8, and 14 against the source tree for the same class of staleness. It found
drift in four of the five — more than the "at most two" threshold at which
the phase's own scope fence says to file rather than fix (bug phase, not a
docs phase).

Each item below states the stale claim and the source that contradicts it.

### Section 3 — Architectural Layers

> Pure computation modules: calibration, detection, **segmentation**, 2D
> tracking, cross-camera association, **midline extraction**, triangulation,
> optimization.

`grep -ri segmentation src/aquapose -r` (excluding `__pycache__`) returns
nothing — no `segmentation` module exists anywhere in the source tree. The
segmentation midline backend was removed in v3.7 (per Phase 113's
`deferred-items.md`). "Midline extraction" as a named computation is also
gone as a standalone concept; it is now split between Stage 2 (Pose, raw
keypoint extraction) and Stage 5 (Reconstruction, keypoint-to-midline
interpolation) — see the corrected section 6.

### Section 4 — Source Layout

The `core/` subtree in the file tree lists only `types/`, `association/`,
`detection/`, `midline/`, `reconstruction/`, `tracking/`. Actual layout
(`ls src/aquapose/core/`): `association/`, `context.py`, `detection/`,
`inference.py`, `midline/` (now nearly empty — `backends/` has no files, only
`__pycache__`), `pose/` (the real Stage 2 module: `stage.py`, `types.py`,
`crop.py`, `backends/pose_estimation.py` — **not listed at all**), `reid/`
(re-identification embedder/miner/eval — **not listed at all**),
`reconstruction/`, `stitching.py`, `synthetic.py`, `tracking/`, `types/`.
The `midline/` entry's comment ("Midline stage, types, backends/
(segmentation, pose_estimation)") is doubly wrong: there is no `types.py` or
stage module under `core/midline/`, and its `backends/` directory is empty
(verified via `ls src/aquapose/core/midline/backends/` — only
`__pycache__`).

### Section 7 — Stage Interface Design

> Each stage accepts `PipelineContext`, reads what it needs, appends typed
> results, and returns the updated context.

This omits the one stage that doesn't fit: `TrackingStage.run()` has the
signature `(context, carry) -> (context, carry)`, not `(context) ->
context`. `src/aquapose/engine/pipeline.py`'s own module docstring calls
this out explicitly: *"Stage 2 (TrackingStage) uses a different `run()`
signature ... because it maintains per-camera tracker state across
batches. The pipeline runner detects this stage via `isinstance(stage,
TrackingStage)` and dispatches accordingly."* (Note: that docstring itself
still says "Stage 2" for TrackingStage, pre-dating the v3.7 reorder that made
Pose Stage 2 and Tracking Stage 3 — a second, smaller instance of the same
drift, inside a source file's own docstring rather than the guidebook.)

### Section 8 — Swappable Backends vs Configurable Models

> Examples: ... segment-then-extract vs direct pose estimation for midline
> extraction ... YOLO26n-seg vs a future segmentation model within the
> segment-then-extract midline backend.
>
> **Adding a genuinely new backend** (e.g., a transformer-based midline
> estimator) ... requires a new `backends/<name>.py` under the relevant stage
> directory ...

Both examples anchor to `core/midline/__init__.py` and a
`segment_then_extract` backend. `ls src/aquapose/core/midline/backends/`
shows no such backend file exists (only `__pycache__`); `ls
src/aquapose/core/pose/backends/` shows the only backend is
`pose_estimation.py`. There is currently exactly one backend for keypoint
extraction, not a swappable pair — the entire "swappable backends" worked
example for this stage describes a choice that no longer exists.

### Section 14 — CLI

> Major command groups: **run**, **init**, **eval**, **tune**, **viz**,
> **train**

`grep -n "@cli.command\|add_command" src/aquapose/cli.py` shows the real
top-level surface: `run`, `init`, `eval`, `eval-compare`, `tune`, `viz`,
`stitch`, `smooth-z` (all `@cli.command()`, not groups), plus `data`,
`train`, `prep`, `pseudo-label`, `reid` (registered via `add_command`, the
only true command *groups*). The list is missing `prep` (used constantly
elsewhere in this same phase for `generate-luts` and `calibrate-keypoints`),
`data`, `pseudo-label`, `reid`, `stitch`, `smooth-z`, and `eval-compare`, and
mischaracterizes single commands as "groups."

## Solution

Same discipline as section 6: read each corrected section's current claims,
verify each replacement claim against the source tree (not against another
prose document), rewrite, and re-run `hatch run lint`. Section 4's tree is
probably worth doing first since it is the most load-bearing for a new
contributor's mental model and the most concretely falsifiable (`ls` catches
all of it).

## Notes

Filed by 113.1-03 (D-14/D-15's bounded drift scan) rather than fixed, per
that plan's Claude's Discretion clause: "if the audit turns up more than a
couple of drifted sections, file a follow-up todo rather than fixing them
here — this is a bug phase, not a docs phase." Section 6 itself was
corrected in the same plan; these five are the next candidates.
