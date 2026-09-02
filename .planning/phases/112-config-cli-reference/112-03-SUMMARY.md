---
phase: 112-config-cli-reference
plan: "03"
subsystem: docs
tags: [docs, config, reference, myst]
dependency_graph:
  requires: [112-01]
  provides: [docs/reference/config.md]
  affects: [DOCS-06]
tech_stack:
  added: []
  patterns: [MyST authored tables, tiered reference page]
key_files:
  created:
    - docs/reference/config.md
  modified: []
decisions:
  - "All 86 leaf fields documented in a single pass (Essential + Advanced written together)"
  - "TrackingConfig has 14 fields (PATTERNS.md said 13; source is authoritative)"
  - "Container fields on PipelineConfig (detection, pose, association, tracking, reconstruction, synthetic, lut) included in PipelineConfig Advanced table as cross-reference entries"
metrics:
  duration: "~20 minutes"
  completed: "2026-09-01"
  tasks_completed: 2
  files_created: 1
---

# Phase 112 Plan 03: Config Reference Page Summary

Hand-authored tiered MyST config reference page covering all 86 leaf fields across 10 AquaPose config dataclasses, satisfying DOCS-06.

## What Was Built

`docs/reference/config.md` — a 216-line MyST Markdown page with:

- **Intro** stating the four-layer loading precedence (defaults → YAML → CLI `--set` → freeze) and the `--set key=val` override syntax
- **Essential table** (Tier 1): single flat table with columns Field / Type / Default / What to set it to, covering the 9 fields that `aquapose init` scaffolds (`project_dir`, `video_dir`, `calibration_path`, `output_dir`, `n_animals`, `detection.detector_kind`, `detection.weights_path`, `pose.weights_path`, `mode`)
- **Advanced section** (Tier 2): per-stage subsections ordered Detection → Pose → Tracking → Association → Reconstruction (with nested ZDenoising sub-table) → LUT → Synthetic → ReID → PipelineConfig top-level fields
- **Cross-reference** to `../api/engine.rst` for the full auto-generated module API
- **Note** that `z_denoising` is nested under `ReconstructionConfig`

## Coverage Verification

```
LEAF_FIELDS 86
MISSING []
```

The Task 2 verification script confirmed all 86 leaf field names appear in the page. The assert passed with no missing fields.

## Deviations from Plan

### Auto-fixed Issues

None.

### Observations

**1. TrackingConfig field count: 14 not 13**
- PATTERNS.md listed 13 fields for TrackingConfig; the actual source has 14: `tracker_kind`, `max_coast_frames`, `n_init`, `det_thresh`, `track_thresh`, `birth_thresh`, `base_r`, `lambda_ocm`, `max_gap_frames`, `match_cost_threshold`, `ocr_threshold`, `max_match_distance`, `merger_distance_px`, `merger_max_coast_frames`.
- Source code is authoritative; all 14 are documented.

**2. Tasks executed atomically in one write**
- Tasks 1 and 2 were completed in a single file write (Essential and Advanced sections authored together). The single commit captures the complete artifact. Both verification checks pass.

## Known Stubs

None. The page documents real field values from the source docstrings.

## Threat Flags

None. Documentation-only page; no new runtime surface introduced.

## Self-Check: PASSED

- docs/reference/config.md: FOUND
- Commit ceba729: FOUND
