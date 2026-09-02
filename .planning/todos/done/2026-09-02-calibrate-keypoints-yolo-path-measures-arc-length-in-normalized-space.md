---
created: 2026-09-02T00:00:00.000Z
title: calibrate-keypoints YOLO path measures arc length in normalized coordinates, biasing t-values on non-square crops
area: training
files:
  - src/aquapose/training/prep.py
  - src/aquapose/training/coco_interchange.py
  - tests/unit/test_calibrate_keypoints.py
---

## Problem

`aquapose prep calibrate-keypoints --annotations <dir>` computes each keypoint's
arc-length fraction directly from YOLO label coordinates, which are normalized
to `[0, 1]` independently in x (by image width) and y (by image height).

`_parse_keypoints_yolo` (`src/aquapose/training/prep.py:62-91`) appends the raw
normalized values:

```python
points.append((x, y))   # prep.py:90 -- x normalized by W, y normalized by H
```

and `_compute_t_values` (`prep.py:97-140`) then takes Euclidean chord lengths in
that space. Pose crops are **128x64** (`crop_size: tuple[int, int] = (128, 64)`,
`src/aquapose/core/pose/backends/pose_estimation.py:62`), so a 1 px vertical
displacement contributes `1/64` while a 1 px horizontal displacement contributes
`1/128` -- vertical motion is weighted **2x**. Since the fish bends across the
short axis of the crop, this systematically inflates the arc length of the
curved mid-body segments relative to the straighter head and tail.

The COCO path is unaffected: `_parse_keypoints_coco` (`prep.py:31-58`) reads
absolute pixel coordinates.

Measured on the YH manual annotation set (322 non-augmented human-labeled crops,
325 instances, from `training_data/pose.tar.gz`):

```
normalized (what the YOLO path produces):  [0.0, 0.1653, 0.3411, 0.5241, 0.7368, 1.0]
pixel-space (correct):                     [0.0, 0.1490, 0.3269, 0.5187, 0.7403, 1.0]
uniform fallback (keypoint_t_values=None): [0.0, 0.2,    0.4,    0.6,    0.8,    1.0]
```

**The shipped YH config carries the biased values.** The production project
config on the archive
(`cichlidVideo:.../__AnalysisStates/AquaPose/projects/YH/config.yaml`) contains:

```yaml
midline:
  keypoint_t_values: [0.0, 0.1653, 0.3411, 0.5241, 0.7368, 1.0]
```

-- an exact match for the normalized-space row above. Every YH run and every
pseudo-label round to date used the biased parameterization. Recalibrating YH is
part of landing this fix, not a follow-up.

Bias is ~1.6 pp on `spine1` and ~1.4 pp on `spine2`, in opposite directions from
the tail. Small relative to the gap from the uniform fallback, but it is a
systematic error in a value that is measured precisely so it can be trusted.

## Why it matters

`keypoint_t_values` is the arc-length parameterization used to reproject spline
midlines into keypoints (`reproject_spline_keypoints`,
`src/aquapose/training/pseudo_labels.py:50-95`) and in evaluation
(`src/aquapose/evaluation/runner.py:1062-1126`). A biased parameterization
propagates into every pseudo-label generated from it, and the pseudo-label loop
is self-reinforcing: pseudo-labels are produced *by* these t-values, so
recalibrating on a corpus that includes them cannot correct the bias.

The YOLO directory form is also the only form usable in practice today --
nothing in the codebase writes a COCO keypoints JSON for manually annotated
data (`write_coco_keypoints` is wired only to pseudo-label output,
`src/aquapose/training/pseudo_label_cli.py:580,586`).

## Solution

Scale normalized coordinates back to pixels in `_parse_keypoints_yolo` before
computing chord lengths. Sibling images are needed for the dimensions; the
lookup already exists in `yolo_pose_to_coco`
(`src/aquapose/training/coco_interchange.py:28-56`), which resolves
`labels/<stem>.txt` to `images/<stem>.{jpg,jpeg,png}` and reads size via
`PIL.Image.open(...).size` without decoding pixels.

Two viable shapes:

1. **Resolve the image per label file inside `_parse_keypoints_yolo`** and
   multiply by `(img_w, img_h)`. Keeps the one-directory CLI contract. Needs a
   decision for the case where no sibling image is found -- fall back to
   treating coordinates as normalized (current, biased) or skip the file. Prefer
   skipping with a warning, and fail the command if *no* file resolved, so a
   silent regression to the biased path is impossible.
2. **Reuse `yolo_pose_to_coco`** to convert the directory to a COCO dict in
   memory, then run the existing COCO parser. Less new code, but that helper
   hardcodes `images/train` + `labels/train` (`coco_interchange.py:28-29`) and
   would need generalizing to match the CLI's documented `rglob` recursion over
   `train/` and `val/`.

Option 1 is the smaller change and preserves the recursion semantics the
docstring promises (`prep.py:161-165`).

Terminal gate: a unit test with a synthetic 128x64 label set whose keypoints are
evenly spaced **in pixels** must yield t-values `[0, 0.2, 0.4, 0.6, 0.8, 1.0]`
when the path traverses the short axis. Construct it so the current code fails
-- place the points along a diagonal or purely vertical line, since a purely
horizontal layout is invariant to the bug. `tests/unit/test_calibrate_keypoints.py`
already has YOLO fixtures at `test_yolo_labels_detected_and_parsed` (line 200)
and `test_yolo_processes_all_subdirs` (line 228) to extend; note those fixtures
currently write labels without sibling images, so they will need images added
whichever option is taken.

## Notes

Found while auditing which of the YH `training_data` archives to feed
`--annotations`. Ships alongside
`2026-09-02-calibrate-keypoints-writes-t-values-to-legacy-midline-config-key.md`
-- same command, independent defects, and the second one can silently discard
whatever this one computes.

Recommended calibration corpus, for whoever picks this up: the manual,
non-augmented originals only. In the YH store those are
`training_data/pose/datasets/pose_ablation_a_manual/labels/train` (258 files,
all `source=manual`, verified against `store.db`) plus
`datasets/round1-curated/labels/val` (64, also pure manual originals). Avoid the
flat `pose/labels/` root and any `*-aug` / `production_retrain*` dataset --
those mix in pseudo-labels (circular) and elastic-deformed duplicates that
outnumber originals 4:1.

## Fixed

**Date:** 2026-09-02
**Fixed by:** Phase 113.1, Plan 01 (`113.1-01-PLAN.md`, D-08), code fix.
Recalibration on real data run separately, Phase 113.1, Plan 05
(`113.1-05-PLAN.md`, D-10/D-11).
**Evidence (code fix):** `_resolve_sibling_image` and a reworked
`_parse_keypoints_yolo` in `src/aquapose/training/prep.py` now scale
normalized YOLO keypoints to absolute pixel coordinates using the sibling
image's `(width, height)` before computing arc length, matching the
already-correct COCO path. Proven through `load_config` and proven
non-vacuous by reverting the fix to red (see `113.1-01-SUMMARY.md`). Commit
`421d327`.
**Evidence (real-data recalibration, NOT the same as archive application):**
`113.1-05` ran the fixed command over all 322 manual, non-augmented labels
(`pose_ablation_a_manual/labels/train` + `round1-curated/labels/val`) and
recomputed `[0.0, 0.149, 0.3269, 0.5187, 0.7403, 1.0]`, matching this todo's
own predicted pixel-space vector to 4 decimal places. **The production YH
archive config still carries the biased vector** — the archive was searched
and found unreachable from this machine (see
`.planning/todos/pending/2026-09-02-apply-corrected-keypoint-t-values-to-yh-archive-config.md`
for the reachability check and the corrected vector). This todo closes
because the code defect it reported is fixed and proven; applying the
corrected numbers to the production config is tracked separately and remains
open.
