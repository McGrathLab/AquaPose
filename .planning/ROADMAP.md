# Roadmap: AquaPose

## Milestones

- ✅ **v1.0 MVP** - Phases 1-9 (shipped 2026-02-25)
- ✅ **v2.0 Alpha** - Phases 13-21 (shipped 2026-02-27)
- ✅ **v2.1 Identity** - Phases 22-28 (shipped 2026-02-28)
- ✅ **v2.2 Backends** - Phases 29-33.1 (shipped 2026-03-01)
- ✅ **v3.0 Ultralytics Unification** - Phases 35-39 (shipped 2026-03-02)
- ✅ **v3.1 Reconstruction** - Phases 40-45 (shipped 2026-03-03)
- ✅ **v3.2 Evaluation Ecosystem** - Phases 46-50 (shipped 2026-03-03)
- ✅ **v3.3 Chunk Mode** - Phases 51-55 (shipped 2026-03-05)
- ✅ **v3.4 Performance Optimization** - Phases 56-60 (shipped 2026-03-05)
- ✅ **v3.5 Pseudo-Labeling** - Phases 61-69 (shipped 2026-03-06)
- ✅ **v3.6 Model Iteration & QA** - Phases 70-77 (shipped 2026-03-10)
- ✅ **v3.7 Improved Tracking** - Phases 78-86 (shipped 2026-03-11)
- ✅ **v3.8 Improved Association** - Phases 87-92 (shipped 2026-03-12)
- ✅ **v3.9 Reconstruction Modernization** - Phases 93-96 (shipped 2026-03-14)
- ✅ **v3.10 Publication Metrics** - Phases 97-101 (shipped 2026-03-15)
- ✅ **v3.11 Appearance-Based ReID** - Phases 102-107 (shipped 2026-03-26)
- 🚧 **v4.0 Publication** - Phases 108-114 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-9) — SHIPPED 2026-02-25</summary>

- [x] Phase 1: Calibration and Refractive Geometry (2/2 plans) — complete
- [x] Phase 2: Segmentation Pipeline (4/4 plans) — complete
- [x] Phase 02.1: Segmentation Troubleshooting (3/3 plans) — complete (INSERTED)
- [x] Phase 02.1.1: Object-detection alternative to MOG2 (3/3 plans) — complete (INSERTED)
- [x] Phase 3: Fish Mesh Model and 3D Initialization (2/2 plans) — complete
- [x] Phase 4: Per-Fish Reconstruction (3/3 plans) — shelved (ABS too slow)
- [x] Phase 04.1: Isolate phase4-specific code (1/1 plan) — complete (INSERTED)
- [x] Phase 5: Cross-View Identity and 3D Tracking (3/3 plans) — complete
- [x] Phase 6: 2D Medial Axis and Arc-Length Sampling (1/1 plan) — complete
- [x] Phase 7: Multi-View Triangulation (1/1 plan) — complete
- [x] Phase 8: End-to-End Integration Testing (3 plans, 2 summaries) — complete
- [x] Phase 9: Curve-Based Optimization (2/2 plans) — complete

**12 phases, 28 plans total**
Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

<details>
<summary>✅ v2.0 Alpha (Phases 13-21) — SHIPPED 2026-02-27</summary>

- [x] Phase 13: Engine Core (4/4 plans) — completed 2026-02-25
- [x] Phase 14: Golden Data and Verification Framework (2/2 plans) — completed 2026-02-25
- [x] Phase 14.1: Fix Critical Mismatch (2/2 plans) — completed 2026-02-25 (INSERTED)
- [x] Phase 15: Stage Migrations (5/5 plans) — completed 2026-02-26
- [x] Phase 16: Numerical Verification and Legacy Cleanup (2/2 plans) — completed 2026-02-26
- [x] Phase 17: Observers (5/5 plans) — completed 2026-02-26
- [x] Phase 18: CLI and Execution Modes (3/3 plans) — completed 2026-02-26
- [x] Phase 19: Alpha Refactor Audit (4/4 plans) — completed 2026-02-26
- [x] Phase 20: Post-Refactor Loose Ends (5/5 plans) — completed 2026-02-27
- [x] Phase 21: Retrospective, Prospective (2/2 plans) — completed 2026-02-27

**10 phases, 34 plans total**
Full details: `.planning/milestones/v2.0-ROADMAP.md`

</details>

<details>
<summary>✅ v2.1 Identity (Phases 22-28) — SHIPPED 2026-02-28</summary>

- [x] Phase 22: Pipeline Scaffolding (2/2 plans) — completed 2026-02-27
- [x] Phase 23: Refractive Lookup Tables (2/2 plans) — completed 2026-02-27
- [x] Phase 24: Per-Camera 2D Tracking (1/1 plan) — completed 2026-02-27
- [x] Phase 25: Association Scoring and Clustering (2/2 plans) — completed 2026-02-27
- [x] Phase 26: Association Refinement and Pipeline Wiring (3/3 plans) — completed 2026-02-27
- [x] Phase 27: Diagnostic Visualization (1/1 plan) — completed 2026-02-27
- [x] Phase 28: E2E Testing (1/1 plan) — completed 2026-02-27

**7 phases, 12 plans total**
Full details: `.planning/milestones/v2.1-ROADMAP.md`

</details>

<details>
<summary>✅ v2.2 Backends (Phases 29-33.1) — SHIPPED 2026-03-01</summary>

- [x] **Phase 29: Guidebook Audit** — complete 2026-02-28
- [x] **Phase 30: Config and Contracts** — complete 2026-02-28
- [x] **Phase 31: Training Infrastructure** — complete 2026-02-28
- [x] **Phase 32: YOLO-OBB Detection Backend** — complete 2026-02-28
- [x] **Phase 33: Keypoint Midline Backend** — complete 2026-03-01
- [x] **Phase 33.1: Keypoint Training Data Augmentation** — complete 2026-03-01

**6 phases (including inserted 33.1), Phase 34 (Stabilization) deferred**
Full details: `.planning/phases/29-*` through `.planning/phases/33.1-*`

</details>

<details>
<summary>✅ v3.0 Ultralytics Unification (Phases 35-39) — SHIPPED 2026-03-02</summary>

- [x] Phase 35: Codebase Cleanup (2/2 plans) — completed 2026-03-01
- [x] Phase 36: Training Wrappers (2/2 plans) — completed 2026-03-01
- [x] Phase 37: Pipeline Integration (2/2 plans) — completed 2026-03-01
- [x] Phase 38: Stabilization and Tech Debt Cleanup (3/4 plans, 1 deferred) — completed 2026-03-02
- [x] Phase 39: Core Reorganization (4/4 plans) — completed 2026-03-02

**5 phases, 14 plans total**
Full details: `.planning/milestones/v3.0-ROADMAP.md`

</details>

<details>
<summary>✅ v3.1 Reconstruction (Phases 40-45) — SHIPPED 2026-03-03</summary>

- [x] Phase 40: Diagnostic Capture (2/2 plans) — completed 2026-03-02
- [x] Phase 41: Evaluation Harness (2/2 plans) — completed 2026-03-02
- [x] Phase 42: Baseline Measurement (1/1 plan) — completed 2026-03-02
- [x] Phase 43: Triangulation Rebuild (2/2 plans) — completed 2026-03-02
- [x] Phase 43.1: Association Tuning (2/2 plans) — completed 2026-03-03 (INSERTED)
- [x] Phase 44: Validation and Tuning (2/2 plans) — completed 2026-03-03
- [x] Phase 45: Dead Code Cleanup (2/2 plans) — completed 2026-03-03

**7 phases, 13 plans total**
Full details: `.planning/milestones/v3.1-ROADMAP.md`

</details>

<details>
<summary>✅ v3.2 Evaluation Ecosystem (Phases 46-50) — SHIPPED 2026-03-03</summary>

- [x] Phase 46: Engine Primitives (3/3 plans) — completed 2026-03-03
- [x] Phase 47: Evaluation Primitives (3/3 plans) — completed 2026-03-03
- [x] Phase 48: EvalRunner and eval CLI (2/2 plans) — completed 2026-03-03
- [x] Phase 49: TuningOrchestrator and tune CLI (2/2 plans) — completed 2026-03-03
- [x] Phase 50: Cleanup and Replacement (1/1 plan) — completed 2026-03-03

**5 phases, 11 plans total**
Full details: `.planning/milestones/v3.2-ROADMAP.md`

</details>

<details>
<summary>✅ v3.3 Chunk Mode (Phases 51-55) — SHIPPED 2026-03-05</summary>

- [x] Phase 51: Frame Source Refactor (2/2 plans) — completed 2026-03-03
- [x] Phase 52: Chunk Orchestrator and Handoff (3/3 plans) — completed 2026-03-03
- [x] Phase 53: Integration and Validation (1/1 plan) — completed 2026-03-04
- [x] Phase 54: Chunk-Aware Diagnostics and Eval Migration (4/4 plans) — completed 2026-03-04
- [x] Phase 55: Chunk Validation and Gap Closure (1/1 plan) — completed 2026-03-05

**5 phases, 11 plans total**
Full details: `.planning/milestones/v3.3-ROADMAP.md`

</details>

<details>
<summary>✅ v3.4 Performance Optimization (Phases 56-60) — SHIPPED 2026-03-05</summary>

- [x] Phase 56: Vectorized Association Scoring (2/2 plans) — completed 2026-03-05
- [x] Phase 57: Vectorized DLT Reconstruction (1/1 plan) — completed 2026-03-05
- [x] Phase 58: Frame I/O Optimization (1/1 plan) — completed 2026-03-05
- [x] Phase 59: Batched YOLO Inference (3/3 plans) — completed 2026-03-05
- [x] Phase 60: End-to-End Performance Validation (1/1 plan) — completed 2026-03-05

**5 phases, 8 plans total**
Full details: `.planning/milestones/v3.4-ROADMAP.md`

</details>

<details>
<summary>✅ v3.5 Pseudo-Labeling (Phases 61-69) — SHIPPED 2026-03-06</summary>

- [x] Phase 61: Z-Denoising (2/2 plans) — completed 2026-03-05
- [x] Phase 62: Prep Infrastructure (2/2 plans) — completed 2026-03-05
- [x] Phase 63: Pseudo-Label Generation (2/2 plans) — completed 2026-03-05
- [x] Phase 64: Gap Detection and Fill (2/2 plans) — completed 2026-03-05
- [x] Phase 65: Frame Selection and Dataset Assembly (3/3 plans) — completed 2026-03-05
- [x] Phase 66: Training Run Management (2/2 plans) — completed 2026-03-05
- [x] Phase 67: Elastic Deformation Augmentation (2/2 plans) — completed 2026-03-06
- [x] Phase 68: Training Data Storage (4/4 plans) — completed 2026-03-06
- [x] Phase 69: CLI Workflow Cleanup (3/3 plans) — completed 2026-03-06

**9 phases, 22 plans total**
Full details: `.planning/milestones/v3.5-ROADMAP.md`

</details>

<details>
<summary>✅ v3.6 Model Iteration & QA (Phases 70-77) — SHIPPED 2026-03-10</summary>

- [x] Phase 70: Metrics & Comparison Infrastructure (2/2 plans) — completed 2026-03-06
- [x] Phase 71: Data Store Bootstrap (2/2 plans) — completed 2026-03-07
- [x] Phase 72: Baseline Pipeline Run & Metrics (1/1 plan) — completed 2026-03-07
- [x] Phase 73: Round 1 Pseudo-Labels & Retraining (3/3 plans) — completed 2026-03-09
- [x] Phase 74: Round 1 Evaluation & Decision (2/2 plans) — completed 2026-03-09
- [ ] Phase 75: Round 2 (Conditional) — skipped per Phase 74 decision
- [x] Phase 76: Final Validation (1/1 plan) — completed 2026-03-10
- [x] Phase 77: Training Module Code Quality (2/2 plans) — completed 2026-03-09

**8 phases (1 skipped), 13 plans total**
Full details: `.planning/milestones/v3.6-ROADMAP.md`

</details>

<details>
<summary>✅ v3.7 Improved Tracking (Phases 78-86) — SHIPPED 2026-03-11</summary>

- [x] Phase 78: Occlusion Investigation (2/2 plans) — completed 2026-03-10
- [x] Phase 78.1: OBB & Pose Production Retrain (2/2 plans) — completed 2026-03-10 (INSERTED)
- [x] Phase 79: Occlusion Remediation (Conditional) — skipped (GO decision)
- [x] Phase 80: Baseline Metrics (1/1 plan) — completed 2026-03-11
- [x] Phase 81: Pipeline Reorder & Segmentation Removal (2/2 plans) — completed 2026-03-11
- [x] Phase 82: Association Upgrade — Keypoint Centroid (1/1 plan) — completed 2026-03-11
- [x] Phase 83: Custom Tracker Implementation (2/2 plans) — completed 2026-03-11
- [x] Phase 84: Integration & Evaluation (2/2 plans) — completed 2026-03-11
- [x] Phase 84.1: Tracker Tuning (2/2 plans) — completed 2026-03-11 (INSERTED)
- [x] Phase 85: Code Quality Audit & CLI Smoke Test (2/2 plans) — completed 2026-03-11
- [x] Phase 86: Cleanup (Conditional) (2/2 plans) — completed 2026-03-11

**11 phases (1 skipped, 2 inserted), 18 plans total**
Full details: `.planning/milestones/v3.7-ROADMAP.md`

</details>

<details>
<summary>✅ v3.8 Improved Association (Phases 87-92) — SHIPPED 2026-03-12</summary>

- [x] Phase 87: Tracklet2D Keypoint Propagation (1/1 plans) — completed 2026-03-11
- [x] Phase 88: Multi-Keypoint Pairwise Scoring (1/1 plans) — completed 2026-03-11
- [x] Phase 89: Fragment Merging Removal (1/1 plans) — completed 2026-03-11
- [x] Phase 90: Group Validation with Changepoint Detection (2/2 plans) — completed 2026-03-11
- [x] Phase 91: Singleton Recovery (2/2 plans) — completed 2026-03-11
- [x] Phase 91.1: Association Bottleneck Investigation & Remediation (3/3 plans) — completed 2026-03-11 (INSERTED)
- [x] Phase 92: Parameter Tuning Pass (2/2 plans) — completed 2026-03-12

**7 phases (1 inserted), 12 plans total**
Full details: `.planning/milestones/v3.8-ROADMAP.md`

</details>

<details>
<summary>✅ v3.9 Reconstruction Modernization (Phases 93-96) — SHIPPED 2026-03-14</summary>

- [x] Phase 93: Config Plumbing (1/1 plans) — completed 2026-03-13
- [x] Phase 94: Dead Code Removal (1/1 plans) — completed 2026-03-13
- [x] Phase 95: Spline Refactoring (2/2 plans) — completed 2026-03-13
- [x] Phase 96: Z-Denoising and Documentation (1/1 plans) — completed 2026-03-13

**4 phases, 5 plans total**
Full details: `.planning/milestones/v3.9-ROADMAP.md`

</details>

<details>
<summary>✅ v3.10 Publication Metrics (Phases 97-101) — SHIPPED 2026-03-15</summary>

- [x] Phase 97: Full Pipeline Run (1/1 plans) — completed 2026-03-15
- [x] Phase 98: Performance Metrics (1/1 plans) — completed 2026-03-15
- [x] Phase 99: Reconstruction Quality Metrics (1/1 plans) — completed 2026-03-15
- [x] Phase 100: Tracking and Association Metrics (1/1 plans) — completed 2026-03-15
- [x] Phase 101: Results Document (1/1 plans) — completed 2026-03-15

**5 phases, 5 plans total**
Full details: `.planning/milestones/v3.10-ROADMAP.md`

</details>

<details>
<summary>✅ v3.11 Appearance-Based ReID (Phases 102-107) — SHIPPED 2026-03-26</summary>

**Milestone Goal:** Add post-hoc appearance-based re-identification to resolve identity swaps that geometry cannot catch — specifically the known female-female cichlid swap. A new `aquapose reid` command group operates on completed pipeline output, embeds fish crops through a fine-tuned MegaDescriptor-T backbone, detects swaps at occlusion events via cosine similarity, and writes corrected trajectories to `midlines_reid.h5`.

- [x] Phase 102: Embedding Infrastructure (2/2 plans) — completed 2026-03-25
- [x] Phase 103: Training Data Mining (2/2 plans) — completed 2026-03-25
- [x] Phase 104: Backbone Fine-Tuning (2/2 plans) — completed 2026-03-25
- [x] Phase 105: Swap Detection and Repair (2/2 plans) — completed 2026-03-25
- [x] Phase 106: CLI Integration (2/2 plans) — completed 2026-03-25
- [x] Phase 107: Unfrozen Backbone Fine-Tuning (2/2 plans) — completed 2026-03-26

**6 phases, 12 plans total**

### Phase Details

#### Phase 102: Embedding Infrastructure

**Goal**: Users can extract L2-normalized embeddings for every fish detection in a completed run and inspect them
**Depends on**: Nothing (first phase of milestone)
**Requirements**: EMBED-01, EMBED-02, EMBED-03
**Success Criteria** (what must be TRUE):

  1. Given a completed run directory, `embed_runner` iterates all (frame, fish_id, camera) tuples from `midlines_stitched.h5` and writes `embeddings.h5` without error
  2. Embeddings are L2-normalized 768-dim vectors (MegaDescriptor-T output) verifiable by checking that each row has unit norm
  3. Crops are extracted using the existing stretch-fill affine warp — same convention as YOLO training — verifiable by visual inspection of saved crops
  4. Zero-shot cosine similarity between two crops of the same fish from different cameras is measurably higher than between two crops of different fish on a sample of 50 frames

**Plans**: 2 plans

- [x] 102-01-PLAN.md — Config + FishEmbedder backbone wrapper (timm, ReidConfig, embedder module)
- [x] 102-02-PLAN.md — EmbedRunner with crop extraction, NPZ output, and zero-shot eval

#### Phase 103: Training Data Mining

**Goal**: A quality-controlled training crop dataset is available, free of swap contamination and camera bias
**Depends on**: Phase 102
**Requirements**: TRAIN-01, TRAIN-02
**Success Criteria** (what must be TRUE):

  1. Training data extractor produces a `reid_crops/<fish_id>/` directory structure covering all 9 fish identities
  2. No crops appear within 150 frames of a detected changepoint or swap event (contamination filter is verifiable by checking frame indices against the swap event list)
  3. Quality filter parameters (min cameras, min duration, max residual) are configurable and documented; filtering logs show how many segments were accepted vs rejected
  4. The dataset contains at least one valid segment per fish identity, or the run exits with a clear diagnostic message

**Plans**: 2 plans

- [x] 103-01-PLAN.md — TrainingDataMiner core logic with quality gates, temporal windowing, sampling, and unit tests
- [x] 103-02-PLAN.md — mine-reid-crops CLI command wiring

#### Phase 104: Backbone Fine-Tuning

**Goal**: A fine-tuned backbone produces embeddings that discriminate female cichlids well enough to gate swap repair
**Depends on**: Phase 103
**Requirements**: TRAIN-03
**Success Criteria** (what must be TRUE):

  1. Fine-tuning loop runs to completion and saves `best_reid_model.pt` with training loss curves visible in logs
  2. Female-female pair AUC on the temporal holdout set is measured and reported; a value >= 0.75 is required to proceed to Phase 105
  3. Re-embedding all detections with the fine-tuned model produces updated `embeddings.h5` with measurably tighter within-identity cosine similarity compared to zero-shot baseline

**Plans**: 2 plans

- [x] 104-01-PLAN.md — ReID training module (ProjectionHead, feature caching, SubcenterArcFace training loop, AUC evaluation, unit tests)
- [x] 104-02-PLAN.md — Standalone driver script (end-to-end workflow with AUC gate and conditional re-embedding)

#### Phase 105: Swap Detection and Repair

**Goal**: Known identity swap events are detected and repaired, producing corrected output with no increase in reprojection error
**Depends on**: Phase 104
**Requirements**: SWAP-01, SWAP-02
**Success Criteria** (what must be TRUE):

  1. Swap detector identifies both known swap events (male-female and female-female) from the persisted `/swap_events/` in `midlines_stitched.h5`
  2. Repair is applied only at detected occlusion events with cosine margin > 0.15 — stable segments are not modified
  3. `midlines_reid.h5` is written as a corrected copy; mean reprojection error in repaired segments does not increase versus the pre-repair baseline
  4. False positive rate on confirmed-clean segments is below 5% (measurable by running repair on segments with no known swaps)

**Plans**: 2 plans

- [x] 105-01-PLAN.md — Core swap detector module (SwapDetector class, ReidEvent, cross-pattern confirmation, seeded + scan modes, repair, unit tests)
- [x] 105-02-PLAN.md — Standalone validation script (driver on YH data, validates known swaps, FP rate, produces midlines_reid.h5)

#### Phase 106: CLI Integration

**Goal**: All ReID capabilities are accessible via `aquapose reid` subcommands following existing CLI patterns
**Depends on**: Phase 105
**Requirements**: CLI-01
**Success Criteria** (what must be TRUE):

  1. `aquapose -p YH reid embed` runs the batch embed runner on a completed run and writes `embeddings.npz` with progress output
  2. `aquapose -p YH reid repair` runs swap detection and repair, writing `midlines_reid.h5` with a summary of events detected and repaired
  3. `aquapose -p YH reid mine-crops` extracts and filters training crops, reporting accept/reject counts per fish identity
  4. All subcommands follow existing CLI patterns (top-level `-p` project flag, run resolution, consistent error messaging) — smoke test passes without errors

**Plans**: 2 plans

- [x] 106-01-PLAN.md — Create reid_group Click group with embed, repair, mine-crops, fine-tune subcommands + add frame_stride to EmbedRunner
- [x] 106-02-PLAN.md — Wire reid_group into main CLI, remove old mine-reid-crops, delete standalone script, smoke test

#### Phase 107: Unfrozen Backbone Fine-Tuning

**Goal:** Support partial backbone unfreezing in ReID training so the model can learn fish-specific features beyond what frozen MegaDescriptor-T provides. Changes: (1) training runs crops through backbone end-to-end instead of using cached features, (2) re-embedding uses the fine-tuned backbone not a projection head on stale features. Configurable unfreeze depth (last N transformer blocks).
**Requirements**: UNFREEZE-01, UNFREEZE-02, UNFREEZE-03
**Depends on:** Phase 106
**Success Criteria** (what must be TRUE):

  1. `reid fine-tune --unfreeze-blocks 2` trains end-to-end through last 2 Swin blocks with differential LR (backbone 10x lower than head)
  2. Training saves combined checkpoint with `backbone_state_dict` + `head_state_dict` + config metadata
  3. Re-embedding runs crops through fine-tuned backbone+head (not stale zero-shot features), producing `embeddings_finetuned.npz`
  4. `reid fine-tune` with default (unfreeze_blocks=0) still uses cached features path unchanged
  5. SwapDetector reads `embeddings_finetuned.npz` without code changes (same NPZ schema)

**Plans**: 2 plans

- [x] 107-01-PLAN.md — Training module: unfreeze_last_n_blocks, ImageCropDataset, train_reid_end_to_end + unit tests
- [x] 107-02-PLAN.md — CLI integration: --unfreeze-blocks flag, backbone-aware re-embedding in fine_tune_cmd

### Progress

**Execution Order:** Phases execute in numeric order: 102 -> 103 -> 104 -> 105 -> 106 -> 107

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 102. Embedding Infrastructure | 2/2 | Complete | 2026-03-25 |
| 103. Training Data Mining | 2/2 | Complete | 2026-03-25 |
| 104. Backbone Fine-Tuning | 2/2 | Complete | 2026-03-25 |
| 105. Swap Detection and Repair | 2/2 | Complete | 2026-03-25 |
| 106. CLI Integration | 2/2 | Complete | 2026-03-25 |
| 107. Unfrozen Backbone Fine-Tuning | 2/2 | Complete | 2026-03-26 |

</details>

### v4.0 Publication (In Progress)

**Milestone Goal:** An outside researcher can find AquaPose, understand what it does, install it, run it end-to-end on real data, and cite it — under a correct license, with green CI and live documentation.

#### Phases

- [x] **Phase 108: Branch Reconciliation & Repo Hygiene** - Forward-port the Sphinx repair, reconcile `dev`/`main`, relicense to AGPL-3.0, remove stray artifacts, backfill the v3.11 milestone record (completed 2026-08-17)
- [x] **Phase 109: Correctness — Green Test Suite & Config Consolidation** - Fix the 8 failing tests, consolidate weights-path config, make the tutorial config platform-neutral (completed 2026-09-01)
- [x] **Phase 110: API Reference & Docs Tiering** - Two-tier documentation IA distinguishing the core pipeline from research utilities; full API coverage for the 52 missing modules (completed 2026-09-01)
- [ ] **Phase 111: Example Dataset & Reference Outputs** - Package and deposit the Zenodo tutorial dataset with regenerated reference outputs
- [ ] **Phase 112: Config & CLI Reference** - CLI command reference and the 71-field config reference
- [ ] **Phase 113: Concepts & Tutorial** - Install guide, concepts page, and end-to-end tutorial against the published dataset
- [ ] **Phase 114: Publication — README, Badges, Live Docs** - README refresh, badge row, hero media, citation block, live Read the Docs

## Phase Details

### Phase 108: Branch Reconciliation & Repo Hygiene

**Goal**: `dev` is the single source of truth — clean, correctly licensed, with a buildable docs foundation ready for doc authoring
**Depends on**: Nothing (first phase of milestone)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05, REC-01
**Success Criteria** (what must be TRUE):

  1. `sphinx-build -W --keep-going` exits clean on `dev` (the `a66287a` Sphinx repair is forward-ported: mock imports, detached docs env, `napoleon_use_ivar`, `.rst` files matching the actual module tree)
  2. The docs CI workflow runs and passes on a push to `dev`, not only `main`
  3. `main` and `dev` are reconciled — `main` is release-only and the `1.1.0-dev.7` vs `1.1.1` version conflict is resolved
  4. A fresh clone of `dev` contains no stray artifacts (vendored SAM2 clone, `11.0` pip log, top-level `yolo26n*.pt` weights, `runs/`, `tmp/`, dead `reconstruction/`/`segmentation/`/`tracking/` dirs) and `.gitignore` prevents their return
     - *Scouted correction (see `108-CONTEXT.md` `<scout_findings>`): `git ls-files` already tracks none of these and `.gitignore` already covers `tmp/`, `*.pt`, `runs/`, so the "fresh clone" half is already satisfied. The `reconstruction`/`segmentation`/`tracking` entries refer to untracked `__pycache__`-only leftovers at the **top level** of `src/aquapose/`, not the live `src/aquapose/core/` packages of the same names. Verify against the plans' `must_haves`, not this line.*
  5. `LICENSE`, `pyproject.toml` (license field + OSI classifier) declare AGPL-3.0
  6. MILESTONES.md contains the missing v3.11 Appearance-Based ReID entry

**Plans**: 5 plans (replanned 2026-08-17 — see `108-01-BLOCKER.md`; executed sequentially on the main working tree, no worktree isolation)

Plans:
**Wave 1**

- [x] 108-01-PLAN.md — Merge `main` into `dev` (D-01) resolving all 113 conflicts by a path-scoped policy, purge the 29 silently-resurrected files, keep main's `.planning/` archive, resolve `pyproject.toml` to `1.2.0-dev.0`, and re-apply `a66287a`'s four dropped docstring hunks

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 108-02-PLAN.md — Relicense to AGPL-3.0-or-later across LICENSE/pyproject/README/conf.py, add `LICENSING.md`, record the MIT boundary in CHANGELOG

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 108-03-PLAN.md — Un-ignore `.planning/`, delete the dead `tests/integration/segmentation` package, clear the working tree (SAM2 weights quarantined behind a user gate)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 108-04-PLAN.md — Backfill the v3.11 and v2.2 MILESTONES entries (v2.2 sourced from the archive the merge delivered) and re-sort the tail chronologically

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 108-05-PLAN.md — Drive `hatch run docs:build` to exit 0, then push `dev` once and confirm the Documentation workflow is green

### Phase 109: Correctness — Green Test Suite & Config Consolidation

**Goal**: The test suite is fully green and config paths follow one convention, so subsequent doc and publication work builds on a trustworthy baseline
**Depends on**: Phase 108
**Requirements**: QA-01, QA-02, QA-03, QA-04
**Success Criteria** (what must be TRUE):

  1. `hatch run test` (per-push CI: {ubuntu,windows}×{3.11,3.12,3.13}) and `hatch run test-all` pass with zero failures — including `test_luts.py::test_forward_lut_cast_ray_matches_model` passing **resolved, not skipped/xfail**, and with no skip/xfail added anywhere to reach green
  2. The real `training/` + `evaluation/` failures are resolved at root cause (stale `--val-split` CLI-help assertions, the `@slow` re-ID timm fixture, `list_models` ordering non-determinism, cp1252 encoding, and the `store.assemble` symlink hot-path) — making the coverage badge honest
  3. `detection.weights_path` and `pose.weights_path` (midline/keypoint) resolve via one convention relative to `project_dir` (absolute honored as-is), the `model_path`→`weights_path` alias is removed, and written paths are forward-slash / platform-neutral
  4. The tutorial/init config uses only relative, platform-neutral paths, and dataset assembly (`store.assemble`) runs unmodified on Linux, macOS, and Windows (symlink→hardlink→copy fallback) — no Developer Mode / admin required

**Plans**: 5 plans (replanned 2026-09-01 — prior 4 plans deleted; rebuilt against the real 23-failure baseline, not the stale "8 failures / failing LUT" premise)

**Wave 1** *(disjoint files_modified — run in parallel)*

- [x] 109-01-PLAN.md — QA-03/D-04/D-07: unify weights_path resolution relative to project_dir, remove the model_path alias, forward-slash-normalize run_manager writes
- [x] 109-02-PLAN.md — QA-04/QA-02/D-09: store.assemble symlink→hardlink→copy fallback (14 failures + WinError 1314 hot-path), update test_symlinks_are_relative semantics, fix list_models ordering flake
- [x] 109-03-PLAN.md — QA-04/QA-02/D-05/D-08/D-11/D-06: fix the 3 stale --val-split help assertions, cp1252 encoding read, platform-neutral utf-8 tutorial config, and the 3 pyproject URLs
- [x] 109-04-PLAN.md — QA-02/D-10: fix the 2 @slow re-ID Swin input-size failures (32px vs 224 backbone)

**Wave 2** *(blocked on Wave 1)*

- [x] 109-05-PLAN.md — QA-01/QA-02/D-01: confirm the LUT parity test is reliably green (resolved, tolerances intact) + document the STATE-108 discrepancy, then the terminal `hatch run test` / `test-all` honest-green gate

### Phase 110: API Reference & Docs Tiering

**Goal**: The rendered docs distinguish the tier-one production pipeline from tier-two research utilities and cover every public module
**Depends on**: Phase 109
**Requirements**: DOCS-01, DOCS-02
**Success Criteria** (what must be TRUE):

  1. The API reference visibly separates tier-one core pipeline modules (detection, tracking, association, pose/midline, reconstruction, calibration, engine) from tier-two research utilities (`training/`, `evaluation/`, `core/reid/`, pseudo-labeling), with honest status labels on tier two
  2. Every public module appears in the rendered API reference — including `core/association/*`, `core/tracking/*`, `core/types/*`, all `backends/` packages, `cli.py`, `core/types/frame_source.py` (the real video/frame source; SC#2's `io/video.py` name does not exist), and `evaluation/viz/*` (the real visualization; SC#2's `visualization/*` name does not exist)
  3. `sphinx-build -W --keep-going` still exits clean with the expanded module tree

**Plans**: 3 plans (planned 2026-09-01)

**Wave 1** *(disjoint files_modified — run in parallel)*

- [x] 110-01-PLAN.md — DOCS-01/DOCS-02: tier-one "Core Pipeline" per-package automodule pages (core/types, detection, tracking, association, pose, reconstruction, runtime; expand calibration/engine/io; new cli page) in D-06 stage order
- [x] 110-02-PLAN.md — DOCS-01/DOCS-02: tier-two "Research Utilities" pages with the verbatim D-05 status note (evaluation + stages + viz, training, synthetic, core/reid)

**Wave 2** *(blocked on Wave 1)*

- [x] 110-03-PLAN.md — DOCS-01/DOCS-02: curated two-section index (D-04/D-06), retire the old flat core.rst stub, coverage cross-check vs the 98-module inventory, and the hard `hatch run docs:build` (-W --keep-going) green gate

### Phase 111: Example Dataset & Reference Outputs

**Goal**: A researcher can download a citable, correctly licensed tutorial dataset with verifiable reference outputs
**Depends on**: Phase 109
**Requirements**: DATA-01, DATA-02, DATA-03
**Success Criteria** (what must be TRUE):

  1. A reproducible script trims and re-encodes all 12 camera videos (temporal trim + bitrate reduction only, no spatial downscale), assembles the deposit tree, and emits checksums
  2. `outputs.h5`, the 3D animation, the overlay mosaic, and timing data are regenerated on `dev` with current production models
  3. The dataset is live on Zenodo with a citable DOI; videos and calibration are CC-BY-4.0; bundled model weights are labeled separately as AGPL-derived artifacts

**Plans**: TBD

### Phase 112: Config & CLI Reference

**Goal**: A user can look up any CLI command or config field and understand its purpose, arguments, and effect without reading source
**Depends on**: Phase 110
**Requirements**: DOCS-05, DOCS-06
**Success Criteria** (what must be TRUE):

  1. Every CLI command group is documented with purpose, arguments, and a worked example
  2. All 71 config fields across the 9 dataclasses are documented with type, default, and effect
  3. The config reference is tiered so a tutorial user is not confronted with all 71 fields at once

**Plans**: TBD

### Phase 113: Concepts & Tutorial

**Goal**: A new user can install AquaPose, understand what the pipeline computes, and run it end-to-end on real data with confidence in the results
**Depends on**: Phase 111, Phase 112
**Requirements**: DOCS-03, DOCS-04, DOCS-07
**Success Criteria** (what must be TRUE):

  1. A user can install AquaPose from written instructions, including the GPU/CUDA caveat, without reading source
  2. The concepts page explains refractive projection, the `{p, ψ, κ, s}` state vector, and the five pipeline stages well enough that a reader understands what the pipeline computes before running it
  3. The tutorial walks a new user from install through a complete pipeline run on the published dataset to interpreting the 3D output, with expected results at each step matching the regenerated reference outputs

**Plans**: TBD

### Phase 114: Publication — README, Badges, Live Docs

**Goal**: An outside researcher landing on the repo understands what AquaPose is, trusts it, and can install, run, and cite it
**Depends on**: Phase 111, Phase 113
**Requirements**: README-01, README-02, README-03, README-04, DOCS-08
**Success Criteria** (what must be TRUE):

  1. The README opens with what problem AquaPose solves, what a user gets out (3D midlines and kinematics), and who it is for — legible to a researcher who has never heard of it
  2. A badge row shows tests, docs, coverage, supported Python versions, PyPI version, license, and the Zenodo DOI, all green
  3. Hero media shows a 3D reconstruction rendering inline on GitHub
  4. Install, quick start against the Zenodo dataset, docs link, and a citation block with the DOI are all present and correct
  5. Documentation builds green on Read the Docs from `dev` and is reachable at the URL declared in `pyproject.toml`

**Plans**: TBD

## Progress

**Execution Order:** Phases execute in numeric order: 108 -> 109 -> 110 -> 111 -> 112 -> 113 -> 114

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 108. Branch Reconciliation & Repo Hygiene | 5/5 | Complete   | 2026-08-17 |
| 109. Correctness — Green Test Suite & Config Consolidation | 5/5 | Complete    | 2026-09-01 |
| 110. API Reference & Docs Tiering | 3/3 | Complete   | 2026-09-01 |
| 111. Example Dataset & Reference Outputs | 0/TBD | Not started | - |
| 112. Config & CLI Reference | 0/TBD | Not started | - |
| 113. Concepts & Tutorial | 0/TBD | Not started | - |
| 114. Publication — README, Badges, Live Docs | 0/TBD | Not started | - |
