---
phase: 109-correctness-green-test-suite-config-consolidation
plan: "04"
subsystem: test-suite / re-identification
tags: [correctness, slow-tests, swin-backbone, fixture-fix, ci-delegated]
dependency_graph:
  requires: []
  provides: [backbone-compatible-reid-fixtures]
  affects: [tests/unit/training/test_reid_training.py]
tech_stack:
  added: []
  patterns: [end-to-end fixture crop_size must match backbone fixed-input contract]
key_files:
  modified:
    - tests/unit/training/test_reid_training.py
decisions:
  - "D-10 root cause: the 2 @slow TestTrainReidEndToEnd fixtures passed crop_size=32 into the 224-input MegaDescriptor-T Swin backbone, tripping timm _assert(H==img_size). Classified per D-02 as a stale TEST fixture error, not a production regression — the production default (crop_size=224) and the sibling ImageCropDataset unit tests already use 224."
  - "Fix corrects the fixture input (crop_size 32->224) in both end-to-end tests; no @pytest.mark.skip/xfail, no backbone weakening, no img_size/dynamic_img_size override added to timm.create_model — the fixed-224 contract is intended and end-to-end training exercises the real input size."
  - "Follow-up (device-adaptive): the two end-to-end fixtures also hardcoded device='cpu', so 224px Swin fine-tuning ran on CPU (~2h, the runtime a prior local attempt hit) even on a CUDA box. Changed to device='cuda' if torch.cuda.is_available() else 'cpu' so GPU is used locally and CPU-only CI runners still fall back. Committed separately from the crop_size fix."
  - "Slow-suite verified LOCALLY on GPU (not deferred to CI): both @slow end-to-end tests pass (2 passed in 47m on CUDA). The other 13 runnable slow tests pass (78s); the 2 e2e real-data smoke tests skip (no local real data, expected)."
metrics:
  duration: "recovered after agent internal-error mid-run; slow tests re-run on GPU (~47m)"
  completed: "2026-09-01"
  tasks_completed: 1
  tasks_total: 1
  files_changed: 1
---

# Phase 109 Plan 04: Re-ID Swin Input-Size Mismatch Summary

The two `@slow` re-ID end-to-end training tests fed `crop_size=32` into the fixed-224
MegaDescriptor-T Swin backbone; corrected the fixtures to `crop_size=224` so the
resized crops match the backbone contract. No skip/xfail, no production regression.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Classify and fix the re-ID Swin input-size mismatch (D-10) | `58e3091` | test_reid_training.py |
| 1b | Make end-to-end fixtures device-adaptive (CUDA when available) | `4be6a35` | test_reid_training.py |

## What Was Built

Changed `crop_size=32` → `crop_size=224` in both `ReidTrainingConfig(...)` constructions
in `TestTrainReidEndToEnd::test_smoke_end_to_end_training` and
`::test_checkpoint_has_backbone_state`, with inline D-10 root-cause notes. The 32×32
source jpgs in `_make_crops_dir` are unchanged (they are upscaled by the dataset resize;
only the post-resize `crop_size` must match the backbone's expected 224 input).

## Root-Cause Note (D-02 / D-10)

`train_reid_end_to_end` builds the backbone via
`timm.create_model("hf-hub:BVRA/MegaDescriptor-T-224", ...)` with no `img_size` override —
a fixed-224-input Swin that asserts `H == 224`. The two end-to-end fixtures passed
`crop_size=32`, so 32px inputs reached the backbone and tripped timm's
`_assert(H == img_size)`. The production default is `crop_size=224` and the sibling
`ImageCropDataset` unit tests already use 224, so the fixtures — not the production code —
were wrong. This is a **stale test fixture error**, fixed by correcting the fixture input;
the backbone's fixed-224 contract is intentional and is exercised at its real input size.

## Deviations from Plan

- **Execution recovery:** The first executor agent applied this exact fixture edit but hit
  an internal error and terminated before committing or running the slow suite (it had been
  running the slow end-to-end tests for ~2 hours). The orchestrator recovered by committing
  the already-correct, uncommitted edit and authoring this SUMMARY. No duplicate/conflicting
  edits — `git diff` confirmed the edit was solely the two `crop_size` changes plus comments,
  with no skip/xfail.
- **Device-adaptive follow-up (enabled real local verification):** the fixtures hardcoded
  `device="cpu"`, so the 224px Swin fine-tuning ran on CPU (~2 h) even though the machine
  has a CUDA GPU — this was the true cause of the ~2 h runtime the first agent hit. Changed
  to `device="cuda" if torch.cuda.is_available() else "cpu"` (commit `4be6a35`). With GPU in
  use, both slow tests complete in ~47 min and were confirmed green locally — no CI deferral
  needed. CPU-only CI runners still fall back gracefully.

## Verification Results

- **Both `@slow` end-to-end tests PASS on GPU** — `2 passed in 2847.03s (0:47:27)` for
  `test_smoke_end_to_end_training` + `test_checkpoint_has_backbone_state`.
- Remaining slow suite — `13 passed, 2 skipped in 78.29s`; the 2 skips are the e2e real-data
  smoke tests (`tests/e2e/test_smoke.py`), correctly skipped without local real data.
- `hatch run test` (fast/not-slow) — **1295 passed, 3 skipped, 0 failures**.
- `git diff` audit — only the two `crop_size` values changed + the device-adaptive line
  (+ root-cause comments); no `@pytest.mark.skip`/`xfail` added.

## Known Stubs

None.

## Threat Flags

None — internal test-correctness work; no new network endpoints, auth paths, or
trust-boundary changes.

## Self-Check: PASSED

- Fixture edit committed (`crop_size=224` in both end-to-end tests) — `58e3091`
- Device-adaptive fixture edit committed — `4be6a35`
- `tests/unit/training/test_reid_training.py` modified; no skip/xfail added
- Both `@slow` end-to-end tests confirmed green locally on GPU (47m)
- Fast suite green (1295 passed, 0 failures); remaining slow tests green (13 passed, 2 e2e skipped)
