# Phase 110: API Reference & Docs Tiering - Pattern Map

**Mapped:** 2026-09-01
**Files analyzed:** ~22 new/modified rst files + 1 conf.py
**Analogs found:** 8 / 8 existing rst files + conf.py

---

## File Classification

| New / Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `docs/api/index.rst` | curated toctree index (two-section) | n/a | `docs/api/index.rst` (current) | exact — replace in place |
| `docs/api/core/types.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/core/detection.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/core/tracking.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/core/association.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/core/pose.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/core/reconstruction.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/core/runtime.rst` | per-package automodule page (loose modules) | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/calibration.rst` | per-package automodule page (expanded) | n/a | `docs/api/calibration.rst` | exact — extend in place |
| `docs/api/engine.rst` | per-package automodule page (expanded) | n/a | `docs/api/engine.rst` | exact — extend in place |
| `docs/api/io.rst` | per-package automodule page (expanded) | n/a | `docs/api/io.rst` | exact — extend in place |
| `docs/api/cli.rst` | per-package automodule page (single module) | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/evaluation.rst` | tier-two section index with status note | n/a | `docs/api/evaluation.rst` + `docs/api/index.rst` | role-match |
| `docs/api/evaluation/core.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/evaluation/stages.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/evaluation/viz.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/training.rst` | tier-two section index with status note | n/a | `docs/api/training.rst` + `docs/api/index.rst` | role-match |
| `docs/api/training/core.rst` | per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/api/synthetic.rst` | tier-two per-package automodule page with status note | n/a | `docs/api/synthetic.rst` | exact — extend in place |
| `docs/api/core/reid.rst` | tier-two per-package automodule page | n/a | `docs/api/calibration.rst` | exact role |
| `docs/conf.py` | Sphinx config (autodoc_mock_imports extension) | n/a | `docs/conf.py` | exact — extend in place |

---

## Pattern Assignments

### `docs/api/index.rst` — curated two-section toctree index

**Analog:** `docs/api/index.rst` (current, lines 1–13) — replace entirely.

**Current pattern** (`docs/api/index.rst`, lines 1–13):
```rst
API Reference
=============

.. toctree::
   :maxdepth: 2

   calibration
   core
   engine
   evaluation
   io
   synthetic
   training
```

**New pattern — two toctrees under labelled rubrics:**
```rst
API Reference
=============

Core Pipeline
-------------

.. toctree::
   :maxdepth: 2

   calibration
   core/types
   core/detection
   core/tracking
   core/association
   core/pose
   core/reconstruction
   core/runtime
   engine
   io
   cli

Research Utilities
------------------

.. toctree::
   :maxdepth: 2

   evaluation
   training
   synthetic
   core/reid
```

Key rules:
- Two `.. toctree::` blocks, each preceded by a section heading (implemented as `rubric` or underlined heading — underlined headings create sidebar entries, `rubric` does not; choose based on sidebar visibility requirement from D-04).
- Stage narrative order within Core Pipeline toctree matches D-06: types → detection → tracking → association → pose → reconstruction → runtime (context/inference/stitching) → engine → io → cli.
- No `:glob:` or `:recursive:` — paths are hand-authored.

---

### `docs/api/calibration.rst` — per-package automodule page (expanded)

**Analog:** `docs/api/calibration.rst` (lines 1–7) — extend by adding submodule entries below the top-level `automodule`.

**Existing pattern** (`docs/api/calibration.rst`, lines 1–7):
```rst
Calibration
===========

.. automodule:: aquapose.calibration
   :members:
   :undoc-members:
   :show-inheritance:
```

**Expanded pattern — add one `automodule` per submodule:**
```rst
Calibration
===========

.. automodule:: aquapose.calibration
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.calibration.loader
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.calibration.luts
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.calibration.projection
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.calibration.uncertainty
   :members:
   :undoc-members:
   :show-inheritance:
```

**Rule:** Top-level `__init__` `automodule` first, then one `automodule` per submodule in source order (`autodoc_member_order = "bysource"` in conf.py). All three options (`:members:`, `:undoc-members:`, `:show-inheritance:`) are applied uniformly — no exceptions unless a submodule has specific exclusion needs (see engine pattern below).

---

### `docs/api/core/types.rst` — per-package automodule page (new file, new subdirectory)

**Analog:** `docs/api/calibration.rst` — copy structure exactly.

```rst
Types
=====

.. automodule:: aquapose.core.types
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.types.crop
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.types.detection
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.types.frame_source
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.types.midline
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.types.reconstruction
   :members:
   :undoc-members:
   :show-inheritance:
```

**Note:** `docs/api/core/` is a new subdirectory. An `index.rst` in that directory is NOT needed — toctree entries in `docs/api/index.rst` use paths like `core/types` directly (Sphinx resolves relative to the toctree file's directory).

---

### `docs/api/core/detection.rst` — per-package automodule page

**Analog:** `docs/api/calibration.rst`.

```rst
Detection
=========

.. automodule:: aquapose.core.detection
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.detection.stage
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.detection.backends.yolo
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.detection.backends.yolo_obb
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/api/core/tracking.rst` — per-package automodule page

**Analog:** `docs/api/calibration.rst`.

```rst
Tracking
========

.. automodule:: aquapose.core.tracking
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.tracking.keypoint_sigmas
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.tracking.keypoint_tracker
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.tracking.stage
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.tracking.types
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/api/core/association.rst` — per-package automodule page

**Analog:** `docs/api/calibration.rst`.

```rst
Cross-Camera Association
========================

.. automodule:: aquapose.core.association
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.association.clustering
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.association.recovery
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.association.scoring
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.association.stage
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.association.types
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.association.validation
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/api/core/pose.rst` — per-package automodule page

**Analog:** `docs/api/calibration.rst`.

```rst
Pose & Midline
==============

.. automodule:: aquapose.core.pose
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.pose.crop
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.pose.stage
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.pose.types
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.pose.backends.pose_estimation
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/api/core/reconstruction.rst` — per-package automodule page

**Analog:** `docs/api/calibration.rst`.

```rst
Reconstruction
==============

.. automodule:: aquapose.core.reconstruction
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reconstruction.stage
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reconstruction.temporal_smoothing
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reconstruction.utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reconstruction.backends.dlt
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/api/core/runtime.rst` — loose core runtime modules

**Analog:** `docs/api/calibration.rst`. Groups `context.py`, `inference.py`, `stitching.py` — the three loose `core/` modules that are on the tier-one runtime path but do not belong to a subpackage.

```rst
Runtime Core
============

.. automodule:: aquapose.core.context
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.inference
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.stitching
   :members:
   :undoc-members:
   :show-inheritance:
```

**Note:** No `aquapose.core` top-level `automodule` here — that would duplicate what the old `core.rst` was doing. Only the three explicit loose modules.

---

### `docs/api/engine.rst` — per-package automodule page (expanded)

**Analog:** `docs/api/engine.rst` (lines 1–8) — extend in place.

**Existing pattern** (`docs/api/engine.rst`, lines 1–8):
```rst
Engine
======

.. automodule:: aquapose.engine
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: PipelineContext, Stage, ChunkHandoff, load_chunk_cache
```

**Expanded pattern:**
```rst
Engine
======

.. automodule:: aquapose.engine
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: PipelineContext, Stage, ChunkHandoff, load_chunk_cache

.. automodule:: aquapose.engine.config
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.engine.events
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.engine.observers
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.engine.observer_factory
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.engine.console_observer
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.engine.diagnostic_observer
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.engine.orchestrator
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.engine.pipeline
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.engine.timing
   :members:
   :undoc-members:
   :show-inheritance:
```

**Rule on `:exclude-members:`:** The existing exclusion list on the top-level `aquapose.engine` automodule is kept as-is on that entry. Submodule entries do NOT carry `:exclude-members:` unless a specific conflict appears during the build. The planner may choose to review the exclusion list once submodules are separately documented (Claude's Discretion per CONTEXT.md).

---

### `docs/api/io.rst` — per-package automodule page (expanded)

**Analog:** `docs/api/io.rst` (lines 1–7) — extend in place.

**Existing pattern** (`docs/api/io.rst`, lines 1–7):
```rst
IO
==

.. automodule:: aquapose.io
   :members:
   :undoc-members:
   :show-inheritance:
```

**Expanded:**
```rst
IO
==

.. automodule:: aquapose.io
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.io.discovery
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.io.midline_writer
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/api/cli.rst` — single-module automodule page (new)

**Analog:** `docs/api/calibration.rst` — minimal single-entry form.

```rst
CLI
===

.. automodule:: aquapose.cli
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.cli_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.logging
   :members:
   :undoc-members:
   :show-inheritance:
```

**Note:** `aquapose.cli` is the CLI entry point (D-03). `cli_utils.py` and `logging.py` are top-level support modules also absent from the current docs; grouping them here is a discretionary choice consistent with D-07 (one page per logical grouping).

---

### `docs/api/evaluation.rst` — tier-two section index with status note

**Analog:** `docs/api/index.rst` (toctree pattern) + `docs/api/evaluation.rst` (automodule). This becomes a sub-index, not a flat automodule page.

**New pattern:**
```rst
Evaluation
==========

.. note::

   Research utility — not part of the supported pipeline API.

.. toctree::
   :maxdepth: 2

   evaluation/core
   evaluation/stages
   evaluation/viz
```

**Rules:**
- The `.. note::` admonition carries the verbatim tier-two status label from D-05 / CONTEXT.md specifics.
- The `.. toctree::` replaces the flat `automodule` — sub-pages document the subpackages.
- Paths are relative to `docs/api/` (where `evaluation.rst` lives).

---

### `docs/api/evaluation/core.rst` — per-package automodule page (new)

**Analog:** `docs/api/calibration.rst`.

```rst
Evaluation Core
===============

.. automodule:: aquapose.evaluation
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.compare
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.metrics
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.output
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.runner
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.tuning
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/api/evaluation/stages.rst` — per-package automodule page (new)

**Analog:** `docs/api/calibration.rst`.

```rst
Evaluation Stages
=================

.. automodule:: aquapose.evaluation.stages
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.stages.detection
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.stages.tracking
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.stages.association
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.stages.fragmentation
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.stages.midline
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.stages.reconstruction
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.stages.smoothing
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.stages.stitching
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/api/evaluation/viz.rst` — per-package automodule page (new)

**Analog:** `docs/api/calibration.rst`.

```rst
Evaluation Visualisation
========================

.. automodule:: aquapose.evaluation.viz
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.viz.animation
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.viz.detections
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.viz.overlay
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.evaluation.viz.trails
   :members:
   :undoc-members:
   :show-inheritance:
```

**Note:** `evaluation/viz/_frames.py` and `evaluation/viz/_loader.py` are private (underscore-prefixed). They will not appear unless explicitly automoduled. Do not include them — the `:undoc-members:` option covers any symbols re-exported from `__init__`, but private modules are intentionally excluded.

---

### `docs/api/training.rst` — tier-two section index with status note

**Analog:** Same pattern as `docs/api/evaluation.rst` (new form above).

```rst
Training
========

.. note::

   Research utility — not part of the supported pipeline API.

.. toctree::
   :maxdepth: 2

   training/core
```

**Note:** Training is a large flat package (~22 modules, no subpackages). All modules go on one page (`training/core.rst`) per D-07, unless the planner decides to split (Claude's Discretion).

---

### `docs/api/training/core.rst` — per-package automodule page (new)

**Analog:** `docs/api/calibration.rst`.

```rst
Training
========

.. automodule:: aquapose.training
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.store
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.store_schema
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.datasets
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.coco_convert
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.coco_interchange
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.yolo_training
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.reid_training
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.pseudo_labels
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.pseudo_label_cli
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.prep
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.run_manager
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.elastic_deform
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.hard_mining
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.compare
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.common
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.geometry
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.select_diverse_subset
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.labelstudio_export
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.labelstudio_import
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.cli
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.training.data_cli
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/api/synthetic.rst` — tier-two per-package automodule page with status note (expanded in place)

**Analog:** `docs/api/synthetic.rst` (lines 1–7) — extend with status note + submodules.

**Existing pattern** (`docs/api/synthetic.rst`, lines 1–7):
```rst
Synthetic
=========

.. automodule:: aquapose.synthetic
   :members:
   :undoc-members:
   :show-inheritance:
```

**Expanded:**
```rst
Synthetic
=========

.. note::

   Research utility — not part of the supported pipeline API.

.. automodule:: aquapose.synthetic
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.synthetic.fish
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.synthetic.rig
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.synthetic.scenarios
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.synthetic.trajectory
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.synthetic.detection
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.synthetic.stubs
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.synthetic
   :members:
   :undoc-members:
   :show-inheritance:
```

**Note:** `core/synthetic.py` is tier-two per D-02 and logically belongs with the synthetic package. Including it on this page (rather than on a core page) keeps tier-two material together.

---

### `docs/api/core/reid.rst` — tier-two per-package automodule page (new)

**Analog:** `docs/api/calibration.rst` form, but carries the tier-two note (D-02: `core/reid/` is research tooling).

```rst
Re-identification
=================

.. note::

   Research utility — not part of the supported pipeline API.

.. automodule:: aquapose.core.reid
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reid.embedder
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reid.eval
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reid.miner
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reid.runner
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reid.swap_detector
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aquapose.core.reid.cli
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### `docs/conf.py` — autodoc_mock_imports extension only

**Analog:** `docs/conf.py` (lines 102–125) — read-only reference; only extend if the build fails with an import error on a newly surfaced module.

**Existing list** (`docs/conf.py`, lines 102–125):
```python
autodoc_mock_imports = [
    "aquacal",
    "boxmot",
    "click",
    "cv2",
    "h5py",
    "igraph",
    "leidenalg",
    "loguru",
    "matplotlib",
    "plotly",
    "PIL",
    "pycocotools",
    "pytorch_metric_learning",
    "scipy",
    "shapely",
    "skimage",
    "sklearn",
    "timm",
    "torch",
    "torchvision",
    "ultralytics",
    "yaml",
]
```

**Rule:** Do not touch `conf.py` unless `sphinx-build -W` reports an import error for a module newly surfaced by the expanded automodule directives. If it does, add the offending top-level package name to `autodoc_mock_imports` following the existing alphabetical order convention.

---

## Shared Patterns

### automodule directive options
**Source:** Every existing `docs/api/*.rst` file.
**Apply to:** All new per-package rst pages.

The three options appear on every `automodule` directive without exception:
```rst
.. automodule:: aquapose.<dotted.module.path>
   :members:
   :undoc-members:
   :show-inheritance:
```

`:exclude-members:` is the only variation — it appears only on `docs/api/engine.rst` line 8 and only on the top-level `aquapose.engine` entry (not on submodule entries).

### tier-two status note admonition
**Source:** D-05 in CONTEXT.md (verbatim wording fixed in `<specifics>`).
**Apply to:** `evaluation.rst`, `training.rst`, `synthetic.rst`, `core/reid.rst`.

```rst
.. note::

   Research utility — not part of the supported pipeline API.
```

Place the note immediately after the page heading and before any `automodule` or `toctree` directives.

### toctree options
**Source:** `docs/api/index.rst` (lines 3–7) and `docs/index.md` (lines 31–38).
**Apply to:** `docs/api/index.rst` (new two-section form), `evaluation.rst`, `training.rst`.

```rst
.. toctree::
   :maxdepth: 2

   child-page-name
```

No `:hidden:` on API sub-indexes (the existing `docs/api/index.rst` does not use `:hidden:`). `:hidden:` is used only in `docs/index.md` where it suppresses the toctree from the visible body.

---

## New Subdirectories Required

| Directory | Purpose |
|---|---|
| `docs/api/core/` | Houses `types.rst`, `detection.rst`, `tracking.rst`, `association.rst`, `pose.rst`, `reconstruction.rst`, `runtime.rst`, `reid.rst` |
| `docs/api/evaluation/` | Houses `core.rst`, `stages.rst`, `viz.rst` |
| `docs/api/training/` | Houses `core.rst` |

No `index.rst` files are needed inside these subdirectories — all entries are reached via toctree paths from `docs/api/index.rst` or tier-two section indexes.

---

## No Analog Found

All new files have close rst analogs. No files require falling back to RESEARCH.md patterns.

---

## Metadata

**Analog search scope:** `docs/api/`, `docs/conf.py`, `docs/index.md`
**Files scanned:** 11 (8 rst + conf.py + index.md + CONTEXT.md)
**Source module inventory:** 95+ modules across `src/aquapose/` (Glob enumerated)
**Pattern extraction date:** 2026-09-01
