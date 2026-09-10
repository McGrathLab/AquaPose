---
created: 2026-09-10T00:00:00.000Z
title: Document the model training workflow end to end
area: docs
files:
  - docs/reference/cli.rst
  - docs/getting-started/concepts.md
  - docs/index.md
---

## Problem

AquaPose ships a full model-training toolchain — 23 modules under
`src/aquapose/training/` and four CLI command groups (`train`, `data`,
`pseudo-label`, `reid`) — and there is **no narrative documentation for any of it**.

What exists today is reference-only, and only incidentally:

- `docs/reference/cli.rst:18` uses `sphinx-click` with `:nested: full`, so every
  training subcommand's *flags* are auto-documented. That tells a reader which options
  exist, not which command to run first.
- The hand-written **Worked Examples** section of the same file covers eight commands
  — `run`, `viz`, `eval`, `eval-compare`, `init`, `smooth-z`, `stitch`, `tune`. All
  pipeline-side. **None of `train`, `data`, `pseudo-label`, or `reid`.**
- `docs/getting-started/concepts.md:226-228` explicitly disclaims the area, directing
  readers to the API reference for "the research-tier utilities (training, evaluation,
  re-identification, pseudo-labeling) that this page intentionally does not cover."

So a user who wants to retrain on their own rig has to reconstruct the order of
operations by reading `--help` output across four command groups and inferring how
they chain.

## Why this matters

The published tutorial runs against pretrained weights on the reference dataset. Any
lab applying AquaPose to *their* aquarium, species, or camera geometry has to retrain
— that is the first thing a real adopter hits after the tutorial, and it is the step
with no map. The v4.0 milestone's goal is that an outside researcher can "install,
run, and cite"; retraining is what stands between running the tutorial and using the
tool.

There is also a preservation argument. Several non-obvious behaviours in this
toolchain were expensive to discover, are now correct in code, and are recorded
nowhere a user would look. If they are not written down they will be rediscovered the
hard way by whoever inherits this.

## Solution

Add a task-oriented training guide. Suggested home: a new
`docs/getting-started/training.md` (it is a how-to, not reference) added to
`docs/index.md`'s toctree, with `concepts.md:226-228` updated to point at it instead
of disclaiming the topic. Alternatively a `docs/training/` section if it grows past
one page.

**Cover the actual chain**, verified against `--help`:

1. **Annotate** — Label Studio is the source of truth; see `labelstudio_export.py` /
   `labelstudio_import.py` for the round trip.
2. **Convert** — `aquapose data convert --coco-file <json> --images-dir <dir>
   --output-dir <dir> --type {obb|pose|both} --n-keypoints 6`
3. **Import into the store** — `aquapose data import --store {obb|pose} --source
   {manual|corrected|pseudo} --input-dir <yolo-dir> [--augment]`
4. **Curate** — `aquapose data list` / `status` to inspect, `exclude` / `include` to
   soft-delete reversibly, `remove` for hard deletes (permanent, cascades to children).
5. **Assemble** — `aquapose data assemble --store {obb|pose} --name <dataset>
   [--source ...] [--tags-include/--tags-exclude ...] [--min-confidence ...]
   [--val-fraction 0.2]`, which builds a symlinked dataset.
6. **Train** — `aquapose train {obb|pose|seg} --data-dir <dir> --tag <run-tag>
   [--epochs] [--batch-size] [--device]`
7. **Compare and select** — `aquapose train compare`
8. **Deploy** — where the chosen weights go so the pipeline picks them up
   (`<project>/models/{yolo_obb,yolo_pose,yolo_seg}.pt`); confirm the exact contract
   against the config loader rather than trusting this note.

Also document the **pseudo-labelling loop** (`aquapose pseudo-label`, backed by
`pseudo_labels.py` / `hard_mining.py` / `select_diverse_subset.py`) as the iterative
path — generate from pipeline diagnostic caches, mine hard cases, select a diverse
subset, re-import as `--source pseudo`. And `aquapose reid` for re-identification
training, which has its own flow via `reid_training.py`.

**Capture the non-obvious behaviours**, verified before writing:

- **`flip_idx` in `dataset.yaml`.** Ultralytics silently disables `fliplr`
  augmentation when `flip_idx` is absent from a pose dataset — and `args.yaml` records
  the *requested* `fliplr`, not the effective one, so the failure is invisible. Omitting
  it once produced a model that had learned a pure positional prior for keypoint order.
  The code now writes it automatically (`coco_convert.py:493`, `store.py:816`,
  `pseudo_label_cli.py:740`), so document it as *handled for you*, and why the
  identity mapping `[0..K-1]` is correct here (midline keypoints have no handedness).
- **Stretch-fill crops, not letterbox.** Both seg and pose models train on
  stretch-filled crops via a 3-point affine mapping OBB corners to canvas corners.
  Inference must match; letterboxing was removed from the codebase entirely.
- **Ultralytics OBB corner order.** `obb.xyxyxyxy` returns
  `[right-bottom, right-top, left-top, left-bottom]` — the true top-left is `pts[2]`,
  not `pts[0]` — and Ultralytics does not guarantee `w >= h`, so side lengths must be
  measured before building an affine crop. Training data uses `pca_obb`, which does
  return `[TL, TR, BR, BL]`. The mismatch between these two conventions has caused
  real bugs.

Verify each of these against current source before publishing — some were fixed after
they were first recorded, and documenting a solved problem as a live gotcha is its own
kind of wrong.

## Verification

- A new training page exists, is listed in `docs/index.md`'s toctree, and is reachable
  from the built docs.
- `concepts.md`'s "intentionally does not cover" passage is updated to link to it
  rather than dead-ending the reader.
- Every command and flag in the guide is checked against `aquapose <group> <cmd> --help`
  — no invented options. (A prior review of this project found two nonexistent commands
  shipped in the README; the same check applies here.)
- The documented order of operations is confirmed by running it end to end on a small
  sample, or explicitly marked as untested if not.
- Each recorded gotcha is re-verified against current source, and anything now handled
  automatically is described as such rather than as a manual step.
- `hatch run docs:build` exits 0 with no new warnings (the docs env builds under
  `sphinx-build -W --keep-going`, so a warning is a failure).
