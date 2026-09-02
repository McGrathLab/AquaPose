---
phase: 111-example-dataset-reference-outputs
plan: 03
subsystem: infra
tags: [zenodo, checksums, verify-deposit, licensing, publish]

requires:
  - phase: 111-example-dataset-reference-outputs
    provides: "packaging script + reference outputs (Plans 01, 02)"
provides:
  - "verify_deposit() completeness+licensing gate and finalize_deposit() cleanup (drops LUTs + pipeline cache)"
  - "Final checksums.sha256 (LF, sha256sum -c clean) over the complete 215 MB deposit tree"
  - "Publish-ready aquapose-tutorial-data/ deposit + zenodo-metadata.json — Zenodo upload DEFERRED (DOI pending)"
affects: [113 tutorial citation, 114 README + DOI badge]

tech-stack:
  added: []
  patterns: ["transient build-artifact model: LUTs generated for regen then excluded from the shipped tree", "LF-forced manifest for cross-platform sha256sum -c"]

key-files:
  created: []
  modified:
    - scripts/package_tutorial_dataset.py
    - tests/scripts/test_package_tutorial_dataset.py

key-decisions:
  - "LUTs are a transient build dependency: prep generate-luts runs before the pipeline, then finalize_deposit removes geometry/luts/ (597 MB) from the shipped tree; users regenerate via a documented one-time prep step (corrected D-03)"
  - "overlay_mosaic.mp4 re-encoded at CRF 28 (110 MB -> 12 MB); deposit lands at 215 MB"
  - "Zenodo upload deferred at user request — deposit is publish-ready; DOI recorded as a pending todo + README placeholder (D-11 human-only publish)"

patterns-established:
  - "verify_deposit gate blocks checksumming an incomplete/mislicensed/LUT-or-cache-polluted tree"

requirements-completed: [DATA-03]

duration: ~9min (code) + finalization
completed: 2026-09-01
---

# Phase 111 · Plan 03: Deposit Finalization & Publish-Prep Summary

**The 215 MB AquaPose YH tutorial deposit is assembled, integrity-verified (`sha256sum -c` 22/22 OK), and correctly licensed (CC-BY-4.0 data + AGPL-derived weights) — ready for Zenodo; the manual upload + DOI mint is deferred to a tracked follow-up.**

## Performance

- **Duration:** ~9 min (code, commits `9dfa6bf` + `e531009`) + finalization
- **Completed:** 2026-09-01
- **Tasks:** 3/3 — Task 1 (checksums + verify_deposit + Wave-2 corrections) automated; Task 2 (manifest verify) done — clean; Task 3 (manual Zenodo upload) **deferred** by user.

## Accomplishments

- **DATA-03 automatable portion delivered.** `verify_deposit()` gates tree completeness + licensing (12 videos, all reference outputs, no absolute paths, CC-BY-4.0 + AGPL-derived-weights wording, `geometry/luts/` absent, no `reference_outputs/run_*` cache). `finalize_deposit()` removes transient LUTs + cache. `write_checksums()` emits the final LF manifest over the clean tree.
- **Four Wave-2 corrections folded in** (see 111-02-SUMMARY): prep-generate-luts before the pipeline run; overlay re-encode CRF 28; exclude LUTs + cache from the shipped tree; README documents the one-time `aquapose prep generate-luts` step.
- **Portability bug fixed:** the manifest was CRLF on Windows (trailing `\r` broke `sha256sum -c` everywhere) — now LF-forced with a regression test.
- Full suite **1375 passed, 3 skipped**; lint clean.

## Final deposit (`aquapose-tutorial-data/`, 215 MB)

`videos/` 12 × 1600×1200 H.264 30 s (181 MB) · `models/` yolo_obb.pt + yolo_pose.pt (run_20260318_*) · `geometry/calibration.json` (LUTs excluded) · `config.yaml` (relative) · `README.md` (licensing + prep step) · `zenodo-metadata.json` (cc-by-4.0) · `reference_outputs/` outputs.h5 + animation_3d.html + overlay_mosaic.mp4 (12 MB) + timing.txt · `checksums.sha256` (22/22 verify OK).

## Deferred (tracked)

- **Manual Zenodo upload + DOI mint** — deferred by user. Recorded as pending todo `2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md`. README citation carries `<DOI filled after upload>`. Blocks Phase 114 DOI badge/citation and Phase 113 tutorial citation until minted.

## Self-Check: PASSED (with tracked deferral)

- [x] DATA-03 automatable portion covered (verify + checksums + licensing)
- [x] Deposit publish-ready (215 MB, sha256sum -c clean)
- [x] Code committed (9dfa6bf, e531009); tests green (1375 passed); lint clean
- [~] Manual Zenodo upload + DOI — deferred, tracked as todo (D-11 human step)
