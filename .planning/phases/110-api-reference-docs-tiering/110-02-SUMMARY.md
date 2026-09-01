---
phase: 110-api-reference-docs-tiering
plan: "02"
subsystem: docs
tags: [rst, sphinx, automodule, tier-two, research-utilities]
dependency_graph:
  requires: [110-01]
  provides: [tier-two-rst-pages]
  affects: [docs/api/evaluation.rst, docs/api/training.rst, docs/api/synthetic.rst, docs/api/core/reid.rst, docs/api/evaluation/core.rst, docs/api/evaluation/stages.rst, docs/api/evaluation/viz.rst, docs/api/training/core.rst]
tech_stack:
  added: []
  patterns: [sphinx-automodule, rst-note-admonition, rst-toctree]
key_files:
  created:
    - docs/api/evaluation/core.rst
    - docs/api/evaluation/stages.rst
    - docs/api/evaluation/viz.rst
    - docs/api/training/core.rst
    - docs/api/core/reid.rst
  modified:
    - docs/api/evaluation.rst
    - docs/api/training.rst
    - docs/api/synthetic.rst
decisions:
  - "D-05 note placed verbatim on all 4 tier-two section pages (evaluation, training, synthetic, core/reid), exactly once per page, immediately after the heading"
  - "Private viz modules _frames.py and _loader.py intentionally excluded from evaluation/viz.rst"
  - "core/synthetic.py grouped with synthetic package per D-02 (both are tier-two)"
  - "Training 21 submodules ordered alphabetically in training/core.rst (source order within flat package)"
metrics:
  duration: "~10 minutes"
  completed: "2026-09-01"
  tasks_completed: 2
  files_changed: 8
---

# Phase 110 Plan 02: Research Utilities Tier-Two API Pages Summary

Authored all tier-two "Research Utilities" API reference pages: section indexes with
verbatim D-05 status notes plus per-package automodule content pages covering evaluation,
training, synthetic, and core/reid.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Evaluation section index + core/stages/viz content pages | 824b4c2 | evaluation.rst (rewrite), evaluation/core.rst, evaluation/stages.rst, evaluation/viz.rst |
| 2 | Training section, synthetic, and core/reid tier-two pages | 4c276f2 | training.rst (rewrite), training/core.rst, synthetic.rst (extend), core/reid.rst |

## Tier-Two RST Files Authored

### Section Index Pages (with D-05 note + toctree)

| File | Note placed | Toctree children |
|------|-------------|------------------|
| `docs/api/evaluation.rst` | After "Evaluation" heading | evaluation/core, evaluation/stages, evaluation/viz |
| `docs/api/training.rst` | After "Training" heading | training/core |

### Expanded/Extended Pages (with D-05 note + automodules)

| File | Note placed | Automodule targets |
|------|-------------|-------------------|
| `docs/api/synthetic.rst` | After "Synthetic" heading | aquapose.synthetic, .fish, .rig, .scenarios, .trajectory, .detection, .stubs, aquapose.core.synthetic |
| `docs/api/core/reid.rst` | After "Re-identification" heading | aquapose.core.reid, .embedder, .eval, .miner, .runner, .swap_detector, .cli |

### Content Pages (automodule only, note lives on section index)

| File | Automodule targets |
|------|-------------------|
| `docs/api/evaluation/core.rst` | aquapose.evaluation, .compare, .metrics, .output, .runner, .tuning |
| `docs/api/evaluation/stages.rst` | aquapose.evaluation.stages, .detection, .tracking, .association, .fragmentation, .midline, .reconstruction, .smoothing, .stitching (all 8) |
| `docs/api/evaluation/viz.rst` | aquapose.evaluation.viz, .animation, .detections, .overlay, .trails (private _frames, _loader excluded) |
| `docs/api/training/core.rst` | aquapose.training + 21 submodules: cli, coco_convert, coco_interchange, common, compare, data_cli, datasets, elastic_deform, geometry, hard_mining, labelstudio_export, labelstudio_import, prep, pseudo_label_cli, pseudo_labels, reid_training, run_manager, select_diverse_subset, store, store_schema, yolo_training |

## Verbatim Note Placement

All four section-level pages carry exactly the D-05 note:

```rst
.. note::

   Research utility — not part of the supported pipeline API.
```

Placement: immediately after the page heading, before any `automodule` or `toctree` directives.
Files written as UTF-8 to preserve the em-dash in the note text.

## Deviations from Plan

None — plan executed exactly as written.

## Notes for Plan 110-03

- `docs/api/evaluation/`, `docs/api/training/` subdirectories are now populated; plan 03 must wire `evaluation`, `training`, `synthetic`, and `core/reid` into the Research Utilities toctree in `docs/api/index.rst`.
- `docs/api/core/reid.rst` is live in the already-existing `docs/api/core/` directory (created by plan 110-01); plan 03's index wiring must include `core/reid` in the Research Utilities section.
- No `sphinx-build -W` run in this plan — the full build gate is plan 03's responsibility.

## Self-Check: PASSED

All files exist and verified by task verification commands:
- `docs/api/evaluation.rst` — contains note, toctree to evaluation/core|stages|viz
- `docs/api/evaluation/core.rst` — contains aquapose.evaluation.runner
- `docs/api/evaluation/stages.rst` — contains .reconstruction and .stitching
- `docs/api/evaluation/viz.rst` — contains .animation; does NOT contain _frames or _loader
- `docs/api/training.rst` — contains note, toctree to training/core
- `docs/api/training/core.rst` — contains all 21 submodules including store, store_schema, yolo_training, run_manager, pseudo_labels, select_diverse_subset, labelstudio_import
- `docs/api/synthetic.rst` — contains note, aquapose.synthetic.trajectory, aquapose.core.synthetic
- `docs/api/core/reid.rst` — contains note, aquapose.core.reid.swap_detector
