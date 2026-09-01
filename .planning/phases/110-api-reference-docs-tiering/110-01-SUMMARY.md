---
phase: 110-api-reference-docs-tiering
plan: "01"
subsystem: docs
tags: [rst, sphinx, automodule, api-reference, tier-one]
dependency_graph:
  requires: []
  provides: [docs/api/core/types.rst, docs/api/core/detection.rst, docs/api/core/tracking.rst, docs/api/core/association.rst, docs/api/core/pose.rst, docs/api/core/reconstruction.rst, docs/api/core/runtime.rst, docs/api/calibration.rst, docs/api/engine.rst, docs/api/io.rst, docs/api/cli.rst]
  affects: [docs/api/index.rst (plan 03 wires these)]
tech_stack:
  added: []
  patterns: [per-package automodule rst, calibration.rst analog]
key_files:
  created:
    - docs/api/core/types.rst
    - docs/api/core/detection.rst
    - docs/api/core/tracking.rst
    - docs/api/core/association.rst
    - docs/api/core/pose.rst
    - docs/api/core/reconstruction.rst
    - docs/api/core/runtime.rst
    - docs/api/cli.rst
  modified:
    - docs/api/calibration.rst
    - docs/api/engine.rst
    - docs/api/io.rst
decisions:
  - "Followed calibration.rst pattern exactly: heading underlined with =, one automodule block per module with :members: :undoc-members: :show-inheritance:"
  - "No index.rst created under docs/api/core/ — plan 03 reaches pages via toctree paths like core/types"
  - "engine.rst top-level :exclude-members: preserved unchanged; submodule entries carry no :exclude-members:"
  - "runtime.rst lists only context/inference/stitching — no bare aquapose.core top-level automodule to avoid duplication with old core.rst"
metrics:
  duration: "~10 minutes"
  completed: "2026-09-01"
  tasks_completed: 2
  files_created: 8
  files_modified: 3
---

# Phase 110 Plan 01: Tier-One API Reference Pages Summary

**One-liner:** Authored 11 tier-one rst files (7 new core/ pages + 4 expanded top-level pages) automoduling all pipeline submodules via the calibration.rst pattern.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create docs/api/core/ per-package pages | 52201da | docs/api/core/{types,detection,tracking,association,pose,reconstruction,runtime}.rst |
| 2 | Expand calibration/engine/io and add cli pages | 215762e | docs/api/{calibration,engine,io,cli}.rst |

## Files Created / Modified with Automodule Targets

### Task 1: New files under docs/api/core/

**docs/api/core/types.rst** (heading: "Types")
- `aquapose.core.types`
- `aquapose.core.types.crop`
- `aquapose.core.types.detection`
- `aquapose.core.types.frame_source`
- `aquapose.core.types.midline`
- `aquapose.core.types.reconstruction`

**docs/api/core/detection.rst** (heading: "Detection")
- `aquapose.core.detection`
- `aquapose.core.detection.stage`
- `aquapose.core.detection.backends.yolo`
- `aquapose.core.detection.backends.yolo_obb`

**docs/api/core/tracking.rst** (heading: "Tracking")
- `aquapose.core.tracking`
- `aquapose.core.tracking.keypoint_sigmas`
- `aquapose.core.tracking.keypoint_tracker`
- `aquapose.core.tracking.stage`
- `aquapose.core.tracking.types`

**docs/api/core/association.rst** (heading: "Cross-Camera Association")
- `aquapose.core.association`
- `aquapose.core.association.clustering`
- `aquapose.core.association.recovery`
- `aquapose.core.association.scoring`
- `aquapose.core.association.stage`
- `aquapose.core.association.types`
- `aquapose.core.association.validation`

**docs/api/core/pose.rst** (heading: "Pose & Midline")
- `aquapose.core.pose`
- `aquapose.core.pose.crop`
- `aquapose.core.pose.stage`
- `aquapose.core.pose.types`
- `aquapose.core.pose.backends.pose_estimation`

**docs/api/core/reconstruction.rst** (heading: "Reconstruction")
- `aquapose.core.reconstruction`
- `aquapose.core.reconstruction.stage`
- `aquapose.core.reconstruction.temporal_smoothing`
- `aquapose.core.reconstruction.utils`
- `aquapose.core.reconstruction.backends.dlt`

**docs/api/core/runtime.rst** (heading: "Runtime Core")
- `aquapose.core.context`
- `aquapose.core.inference`
- `aquapose.core.stitching`

### Task 2: Expanded top-level pages and new cli page

**docs/api/calibration.rst** (expanded in place)
- `aquapose.calibration` (existing)
- `aquapose.calibration.loader` (new)
- `aquapose.calibration.luts` (new)
- `aquapose.calibration.projection` (new)
- `aquapose.calibration.uncertainty` (new)

**docs/api/engine.rst** (expanded in place, top-level exclude-members preserved)
- `aquapose.engine` + `:exclude-members: PipelineContext, Stage, ChunkHandoff, load_chunk_cache` (existing, unchanged)
- `aquapose.engine.config` (new)
- `aquapose.engine.events` (new)
- `aquapose.engine.observers` (new)
- `aquapose.engine.observer_factory` (new)
- `aquapose.engine.console_observer` (new)
- `aquapose.engine.diagnostic_observer` (new)
- `aquapose.engine.orchestrator` (new)
- `aquapose.engine.pipeline` (new)
- `aquapose.engine.timing` (new)

**docs/api/io.rst** (expanded in place)
- `aquapose.io` (existing)
- `aquapose.io.discovery` (new)
- `aquapose.io.midline_writer` (new)

**docs/api/cli.rst** (new file, heading: "CLI")
- `aquapose.cli`
- `aquapose.cli_utils`
- `aquapose.logging`

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None. These are rst documentation files with automodule directives — no stub data or placeholder text is present.

## Threat Flags

None. Documentation-only rst files introduce no new security surface.

## Self-Check: PASSED

Files exist:
- docs/api/core/types.rst: FOUND
- docs/api/core/detection.rst: FOUND
- docs/api/core/tracking.rst: FOUND
- docs/api/core/association.rst: FOUND
- docs/api/core/pose.rst: FOUND
- docs/api/core/reconstruction.rst: FOUND
- docs/api/core/runtime.rst: FOUND
- docs/api/calibration.rst: FOUND (expanded)
- docs/api/engine.rst: FOUND (expanded)
- docs/api/io.rst: FOUND (expanded)
- docs/api/cli.rst: FOUND

Commits verified: 52201da, 215762e
