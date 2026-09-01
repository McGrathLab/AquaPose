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
  - "Local slow-suite verification deferred to CI: on this CPU-torch machine an end-to-end re-ID run at 224px takes ~2 hours (a prior local attempt ran ~2h before aborting). The @slow marker exists precisely so these run on slow-tests.yml CI, not per-push/locally. Confirmed authorized by user to defer slow verification to CI."
metrics:
  duration: "recovered after agent internal-error mid-run"
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
- **Slow-suite verification delegated to CI (user-authorized):** `hatch run test-all
  tests/unit/training/test_reid_training.py` is impractical locally (~2 h on CPU torch). Per
  user decision, the slow re-ID end-to-end confirmation is delegated to `slow-tests.yml` CI.
  The fix is correct by analysis (matches the production default and the passing sibling
  224px dataset tests) and adds no skip/xfail.

## Verification Results

- `hatch run test tests/unit/training/test_reid_training.py -q` (fast subset) — **1295 passed,
  3 skipped, 17 deselected (@slow), 0 failures**. Confirms the file collects/imports cleanly
  and the edit introduced no syntax/regression in the non-slow tests.
- `git diff` audit — only the two `crop_size` values changed (+ root-cause comments); no
  `@pytest.mark.skip`/`xfail` added.
- **Deferred to CI:** the 2 `@slow` end-to-end tests
  (`test_smoke_end_to_end_training`, `test_checkpoint_has_backbone_state`) — to be confirmed
  green by `slow-tests.yml`.

## Known Stubs

None.

## Threat Flags

None — internal test-correctness work; no new network endpoints, auth paths, or
trust-boundary changes.

## Self-Check: PASSED (local scope) — slow-suite CONFIRMATION PENDING (CI)

- Fixture edit committed (`crop_size=224` in both end-to-end tests)
- `tests/unit/training/test_reid_training.py` modified; no skip/xfail added
- Fast subset green (1295 passed, 0 failures)
- Slow end-to-end verification delegated to `slow-tests.yml` CI per user decision
