---
phase: 111-example-dataset-reference-outputs
plan: 01
subsystem: infra
tags: [zenodo, ffmpeg, packaging, dataset, licensing, checksums]

requires:
  - phase: 109-correctness-green-test-suite-config-consolidation
    provides: platform-neutral relative-path config pattern
provides:
  - "scripts/package_tutorial_dataset.py — standalone reproducible packaging orchestrator (ffmpeg trim/re-encode, tree assembly, model/calibration copy, config/README/zenodo-metadata authoring, SHA-256 checksum helper)"
  - "Assembled deposit tree (194 MB) at aquapose-tutorial-data/ (gitignored): 12 trimmed 1600x1200 H.264 clips, geometry/calibration.json, models/{yolo_obb.pt,yolo_pose.pt}, relative-path config.yaml, license-correct README.md, zenodo-metadata.json, checksums.sha256"
affects: [111-02 reference-outputs regeneration, 111-03 checksum manifest + Zenodo upload]

tech-stack:
  added: []
  patterns: ["standalone scripts/ tool mirroring tools/smoke_test.py (_build_parser + main(argv)->int + lazy imports)", "ffmpeg subprocess trim/re-encode with hard no-spatial-downscale constraint"]

key-files:
  created:
    - scripts/package_tutorial_dataset.py
    - tests/scripts/test_package_tutorial_dataset.py
    - tests/scripts/__init__.py
  modified:
    - .gitignore

key-decisions:
  - "Default trim window is 0:30–1:00 (start-offset 30.0s, duration 30.0s) — Claude's-discretion offset per D-04; user-approved at the Task-3 checkpoint"
  - "CRF 23 yielded a 194 MB deposit — inside the 150–200 MB D-04 target band; no CRF adjustment needed"
  - "Un-ignored scripts/ in .gitignore (blanket rule was hiding tracked Python scripts); deposit output dir aquapose-tutorial-data/ added to .gitignore so the 194 MB tree is never committed"

patterns-established:
  - "Publication tooling lives in scripts/ as a standalone script, NOT a shipped aquapose CLI subcommand (D-09)"
  - "Deposit config authored fresh with relative paths (project_dir: .) — never ship the live YH config's absolute /home paths (D-07/T-111-01)"

requirements-completed: [DATA-01]

duration: ~20min
completed: 2026-09-01
---

# Phase 111 · Plan 01: Tutorial-Dataset Packaging Script Summary

**A single standalone `scripts/package_tutorial_dataset.py` trims + re-encodes the 12 YH cameras (no spatial downscale), assembles the CC-BY-4.0 Zenodo deposit tree with the canonical `run_20260318_*` models, and authors a platform-neutral config, a license-correct README, and Zenodo metadata — verified against the real staging dir.**

## Performance

- **Duration:** ~20 min (code) + 207 s (real-data packager run)
- **Completed:** 2026-09-01
- **Tasks:** 3/3 (Tasks 1+2 automated; Task 3 human-verify checkpoint — approved)
- **Files modified:** 4 committed (script, test, test __init__, .gitignore)

## Accomplishments

- **DATA-01 delivered.** `scripts/package_tutorial_dataset.py` (683 lines) implements: `_build_parser()`, `main(argv)->int`, `_build_ffmpeg_cmd()` (libx264 CRF 23, `-an`, yuv420p, `-ss`/`-t`, **no `-vf`/`scale`**), `trim_and_encode_videos()`, `copy_models_and_calibration()` (canonical `run_20260318_082016`/`run_20260318_013005`, friendly-renamed, no LUTs), `write_deposit_config()` (relative paths, no absolute leaks), `write_deposit_readme()` (CC-BY-4.0 + AGPL-derived label + no-downscale note), `write_zenodo_metadata()`, and `_sha256()`/`write_checksums()`.
- **`--regenerate-outputs`** is a documented stub delegating to `regenerate_reference_outputs()` — filled by Plan 02.
- **437-line test module** covers parser, ffmpeg-cmd construction (asserts no `scale` token), missing-ffmpeg guard, `_sha256`, config authoring (no `/home/`/`D:\`), README/metadata wording, and model-run naming. Full suite: **1342 passed, 3 skipped**; lint clean; basedpyright 0 errors on the script.

## Human-verify checkpoint (Task 3) — approved

Ran the packager against `D:\AquaPose_Zenodo_staging\YH` (207.5 s). Verified: 12 clips, **194 MB** total; sampled clip h264 **1600×1200** yuv420p **29.9997 s**, 0 audio; `config.yaml` all-relative (`project_dir: .`, no absolute leaks); README licensing wording present; models byte-exact vs source; `checksums.sha256` 18/18 files. A 12-camera contact sheet was reviewed and user approved.

## Deviations

- Tasks 1 and 2 were committed as one atomic commit (`beab1d9`) — they modify the same two files, so splitting would have produced a non-buildable intermediate.
- `.gitignore` was corrected to un-ignore `scripts/` (pre-existing blanket rule) so the new script is tracked.

## Notes for downstream plans

- **Plan 02 (Wave 2, GPU):** implement `regenerate_reference_outputs()` — run `aquapose run --config config.yaml` (diagnostic) then `aquapose viz` on the **deposited** tree to produce `reference_outputs/{outputs.h5, animation_3d.html, overlay_mosaic.mp4, timing.txt}`.
- **Plan 03 (Wave 3):** re-run `write_checksums()` over the **complete** tree (including `reference_outputs/`) — the current 18-file manifest is interim; then manual Zenodo upload + DOI, recorded back into README.

## Self-Check: PASSED

- [x] DATA-01 covered
- [x] Tasks committed atomically (beab1d9)
- [x] Tests green (1342 passed), lint + typecheck clean on new files
- [x] Human-verify checkpoint approved
- [x] SUMMARY.md created
