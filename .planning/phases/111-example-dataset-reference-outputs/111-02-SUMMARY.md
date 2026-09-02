---
phase: 111-example-dataset-reference-outputs
plan: 02
subsystem: infra
tags: [zenodo, reference-outputs, pipeline, gpu, viz, luts]

requires:
  - phase: 111-example-dataset-reference-outputs
    provides: "packaging script skeleton + assembled deposit tree (Plan 01)"
provides:
  - "regenerate_reference_outputs() — runs aquapose run (diagnostic) + aquapose viz against the deposited tree, times it, normalizes artifacts, writes timing.txt"
  - "Freshly regenerated reference_outputs/{outputs.h5, animation_3d.html, overlay_mosaic.mp4, timing.txt} on dev with the canonical run_20260318_* models"
affects: [111-03 final tree composition + checksums + Zenodo]

tech-stack:
  added: []
  patterns: ["console-script discovery to invoke aquapose as subprocess (cwd=deposit so project_dir:. resolves)"]

key-files:
  created: []
  modified:
    - scripts/package_tutorial_dataset.py
    - tests/scripts/test_package_tutorial_dataset.py

key-decisions:
  - "aquapose run has NO --config flag (deviation from plan text) — config is resolved by walking CWD upward; the regen runs from cwd=deposit_dir so it finds deposit/config.yaml"
  - "viz run dir resolved as the latest run_* under reference_outputs/ (output_dir override puts runs there, not the default runs/ subdir)"
  - "3D animation shipped as interactive HTML (D-08 Claude's-discretion default)"

patterns-established:
  - "Reference outputs generated from the DEPOSITED clip + config (not the full source) so the tutorial is reproducible"

requirements-completed: [DATA-02]

duration: ~5min (code) + ~19min (GPU regen: pipeline 786s + viz 151s)
completed: 2026-09-01
---

# Phase 111 · Plan 02: Reference-Output Regeneration Summary

**`--regenerate-outputs` runs the real 5-stage pipeline (diagnostic) + viz against the deposited 30 s clip with the canonical `run_20260318_*` models on `dev`, producing outputs.h5 (900 frames × 9 fish × 6 keypoints × 3D, median reprojection 2.75 px), a 3D animation, an overlay mosaic, and timing.**

## Performance

- **Duration:** ~5 min (code, commit `7eae426`) + GPU regen 937 s (pipeline 786 s, viz 151 s) on a GTX 1660 SUPER (6.4 GB)
- **Completed:** 2026-09-01
- **Tasks:** 2/2 (Task 1 automated; Task 2 human-verify checkpoint — approved after eyeballing overlay frames + reconstruction stats)

## Accomplishments

- **DATA-02 delivered.** `regenerate_reference_outputs()` implemented: Step A runs `aquapose run --set output_dir=<ref> --mode diagnostic` (cwd=deposit), Step B runs `aquapose viz <run_dir> --animation --overlay --output-dir <ref>`, Step C normalizes to canonical names + writes `timing.txt`. Mocked-subprocess unit test added (asserts run/viz argv + timing write). Full suite **1348 passed, 3 skipped**; lint clean; typecheck 0 errors on modified files.
- **Reference outputs verified:** `outputs.h5` shape `(900, 9, 6, 3)`, median mean-reprojection-residual **2.75 px** (production full-run was 3.41 px), median 4 cameras/fish, frames 0–899. Overlay frames + stats reviewed and user-approved.

## Deviations & findings

- **`aquapose run` has no `--config` flag** — config resolved by CWD walk; regen runs from `cwd=deposit_dir`. (Executor read cli.py and adapted.)
- **⚠ LUTs are NOT auto-generated (blocking finding).** The pipeline fail-fasts (`LUTs not found. Run: aquapose prep generate-luts`) — the v3.5 prep/fail-fast behavior superseded the v2.1 auto-generation that CONTEXT D-03 assumed. Worked around for this run by copying the prebuilt YH LUTs (597 MB, hash-validated against the identical calibration.json) into `geometry/luts/`. **CONTEXT D-03 amended** with the correction; the fix (script runs `prep generate-luts` before regen; deposit excludes LUTs + documents the prep step) is folded into Plan 03.
- **overlay_mosaic.mp4 was 110 MB** (seed estimated ~19 MB). User decision: re-encode at CRF 28 (~12 MB). Applied in Plan 03's final assembly.
- **`reference_outputs/run_*/` cache dir (19 MB)** left in place by the run — excluded from the shipped tree in Plan 03.

## Notes for Plan 03 (final assembly + Zenodo)

- Final shippable tree MUST exclude `geometry/luts/` (597 MB) and `reference_outputs/run_*/` (cache).
- Re-encode `overlay_mosaic.mp4` at CRF 28.
- Deposit `README.md` MUST document the one-time `aquapose prep generate-luts` step.
- Packaging script's regen path should run `aquapose prep generate-luts` before the pipeline (self-contained maintainer regeneration).
- Regenerate `checksums.sha256` over the final cleaned tree; then the manual Zenodo upload + DOI.

## Self-Check: PASSED

- [x] DATA-02 covered (reference outputs regenerated on dev with canonical models)
- [x] Code committed (7eae426); tests green (1348 passed); lint/typecheck clean
- [x] Human-verify checkpoint approved (reconstruction quality eyeballed)
- [x] Blocking LUT finding recorded + D-03 corrected; composition fixes routed to Plan 03
