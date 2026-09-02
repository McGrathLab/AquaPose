---
gsd_state_version: 1.0
milestone: v4.0
milestone_name: Publication
current_phase: 113.1
current_phase_name: Pre-Release Bug Fixes
status: planned
stopped_at: Completed 113.1-01-PLAN.md
last_updated: "2026-09-02T20:35:22.030Z"
last_activity: 2026-09-02
last_activity_desc: Phase 113.1 planned — 6 plans, 3 waves, checker passed
progress:
  total_phases: 9
  completed_phases: 5
  total_plans: 33
  completed_plans: 27
  percent: 56
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-12)

**Core value:** Accurate 3D fish midline reconstruction from multi-view silhouettes via refractive multi-view triangulation
**Current focus:** Phase 113.1 — Pre-Release Bug Fixes (Phase 113 blocked at 6/7 on its two `calibrate-keypoints` bugs)

## Current Position

Phase: 113.1 (Pre-Release Bug Fixes) — PLANNED
Plan: 1 of 6
Status: Ready to execute — 6 plans in 3 waves
Last activity: 2026-09-02 — Phase 113.1 planned (6 plans, 3 waves)

## Performance Metrics

**v3.10 Velocity:**

- Phases: 5 (97-101)
- Plans: 5
- Timeline: 29 days (2026-02-14 → 2026-03-15)

**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 113 P01 | 4min | 2 tasks | 5 files |
| Phase 113 P02 | 6min | 2 tasks | 2 files |
| Phase 113 P03 | 6min | 2 tasks | 5 files |
| Phase 113 P04 | ~20min | 2 tasks | 4 files |
| Phase 113 P05 | ~46min | 2 tasks | 4 files |
| Phase 113 P07 | ~14min | 2 tasks | 3 files |
| Phase 113.1 P01 | 25min | 3 tasks | 2 files |

## Accumulated Context

### Decisions

Full decision log in PROJECT.md Key Decisions table.

Recent decisions affecting current work:

- [v4.0 roadmap]: Develop on `dev`, `main` release-only; phase numbering continues from 108 (last shipped phase 107)
- [v4.0 roadmap]: Relicense MIT → AGPL-3.0 (FOUND-05), gating README-02 badge row and README-04 citation block
- [v4.0 roadmap]: Docs split into two phases — reference material (Phase 112: CLI + config) vs narrative/tutorial (Phase 113: concepts + install + tutorial) — to avoid one oversized docs phase
- [v4.0 roadmap]: FOUND-01 (Sphinx repair forward-port) gates all DOCS-* phases; QA-01/02 gate README-02; DATA-02/DATA-03/QA-04 gate DOCS-07 and README-04
- [v4.0 roadmap]: REC-01 (v3.11 MILESTONES.md backfill) attached to Phase 108 rather than given its own phase — too small to stand alone
- [v3.11 roadmap]: Post-hoc ReID only — no changes to the chunk pipeline; all work in `core/reid/` and `training/`
- [v3.11 roadmap]: MegaDescriptor-T (timm) as backbone; pytorch-metric-learning for losses; zero-shot baseline evaluated in Phase 102 before committing to fine-tuning
- [v3.11 roadmap]: Female-female AUC >= 0.75 gate in Phase 104; milestone downscopes to male-female only if gate fails
- [Phase 102 testing]: Zero-shot MegaDescriptor-T achieves 97.4% Rank-1, 73.6% mAP on clean segment (frames 0-599). Fish 2↔8 pair most confusable (0.869 cosine similarity).
- [Phase 106-01]: Use SimpleNamespace for embed config to avoid forbidden engine/ import in core/ module (import boundary rule)
- [Phase 106-01]: Remove top-level mine-reid-crops command; delete scripts/train_reid_head.py — both superseded by reid group subcommands
- [Phase 108]: Merged main into dev via real --no-ff merge (113 conflicts resolved by stated path-scoped policy, 29 silently-resurrected hazard-2 paths purged) — Establishes true ancestry (D-01) so every future main-to-dev sync is conflict-free (FOUND-03)
- [Phase 108-02]: Relicensed AquaPose MIT to AGPL-3.0-or-later (PEP 639 SPDX string form accepted by hatchling on first attempt) — LICENSING.md names Ultralytics (AGPL-3.0) and python-igraph/leidenalg (GPL-2.0+) as the forcing dependencies; v1.1.1 MIT grant stands, AGPL applies from 1.2.0
- [Phase 108]: [Phase 108-03]: un-ignored .planning/ (D-18), removed dead tests/integration/segmentation and 4 stale top-level src/aquapose/ residue dirs (D-20), quarantined then permanently deleted the untracked SAM2 source clone after correcting the plan's model-weights premise and getting explicit user confirmation (OI-02) — Satisfies FOUND-04; pyproject.toml was not touched, confirming 108-02's ownership claim held with no conflict
- [Phase 108]: [Phase 108-04]: Backfilled v3.11 Appearance-Based ReID and v2.2 Backends milestone entries into MILESTONES.md and re-sorted the tail into chronological order (REC-01) - all numeric fields measured from git, never estimated; two orphaned/unreachable commits discovered in dev's history and routed around during derivation
- [Phase 108]: [Phase 108-05]: Re-derived autodoc_mock_imports empirically (timm, pytorch_metric_learning, shapely, sklearn) which alone drove sphinx-build -W to exit 0 with zero warnings; pushed dev to origin (transferred mid-session to McGrathLab/AquaPose, independently re-verified before push) - Documentation workflow succeeded (FOUND-02), release.yml cut v1.2.0-dev.1 against the AGPL-declared tree
- [Phase 109-01]: Removed model_path alias from _RENAME_HINTS (D-04 clean break); verified layer 3.5 already handles both det_kwargs/pose_kwargs weights_path resolution (D-03); fixed run_manager.update_config_weights to use as_posix() for platform-neutral YAML writes (D-07), fixing 2 Windows path-separator test failures
- [Phase 109-02]: Added _link_or_copy() helper in store.py with symlink→hardlink→copy three-tier fallback (D-09) fixing 14 WinError 1314 / symlink-privilege failures; updated test_symlinks_are_relative to accept hardlink/copy while preserving relative-symlink assertion on privileged branch; added rowid DESC tiebreaker to list_models() ORDER BY fixing non-deterministic ordering when created_at timestamps tie (D-02)
- [Phase 109-03]: Removed --val-split from train obb/seg/pose expected_flags (D-11 stale assertion; splitting is data assemble's responsibility); fixed test_viz cp1252 read with encoding="utf-8" (D-08); added encoding="utf-8" to init_cmd config.yaml write_text (D-08/QA-04); replaced tlancaster6/aquapose with McGrathLab/AquaPose in pyproject.toml Homepage/Repository/Issues (D-06)
- [Phase 109-04]: Corrected the 2 @slow re-ID end-to-end fixtures crop_size 32→224 to match the fixed-224 MegaDescriptor-T Swin contract (D-10, stale fixture not a regression); made the fixtures device-adaptive (cuda if available else cpu) — the hardcoded device="cpu" was the true cause of the ~2h runtime. Both slow tests verified green on GPU (~47m); slow suite green locally rather than deferred to CI
- [Phase 109-05]: Terminal green gate — QA-01 LUT parity confirmed green (resolved not skipped, 1e-4/0.01 tolerances untouched; STATE-108's "8 failing" was the Linux/CI estimate); QA-02 both suites green locally (fast 1295 passed; slow 15 passed / 2 e2e data-skips); no skip/xfail added anywhere in the phase. Code review WR-01 (store-registration weights_path not as_posix()) fixed post-review for D-07 consistency; phase verified 8/8 must-haves
- [Phase ?]: suppress_warnings=['ref.python'] in conf.py resolves cross-reference ambiguity from re-exported submodule symbols without relaxing -W
- [Phase ?]: Reference section landing page wired into docs IA; reference/index placed above api/index (D-10); reciprocal :doc: cross-links added to api/cli.rst and api/engine.rst without modifying automodule blocks (D-13); build-green gate confirmed
- [Phase ?]: docs/index.md card ordering: Getting Started placed first, before Reference/API Reference/Contributing/Reports (beginner-first flow)
- [Phase ?]: README nvrtc troubleshooting note carried into installation.md Troubleshooting, reframed for the pytorch.org selector rather than a hardcoded cu124 reinstall
- [Phase ?]: Torch baseline for D-08: 2.5.1+cu121, CUDA available=True before and after removing the cu121 wheel-index pin (existing env not recreated)
- [Phase ?]: [Phase 113-02]: Replaced ill-conditioned torch.acos(dot) angular-error metric with stable float64 atan2(||cross||, dot) at all 3 sites (test_luts.py x2, validate_forward_lut); thresholds (0.01/0.1 deg) unchanged; deliberate perturbation proved assertion is not vacuous (0.5558 deg red vs 2.07e-5 deg green); corrects Phase 109-05's QA-01 record which was a lucky local pass, not genuine verification (D-17, D-18)
- [Phase ?]: [Phase 113-03]: Fixed D-05 deposit template errors (bare aquapose run, McGrathLab/AquaPose URL) plus two empirically-confirmed additional defects — aquapose viz runs/<run_dir> double-nests under resolve_run (proven via direct invocation), and the README's 'generates outputs.h5' claim was false (real pipeline writes midlines.h5; outputs.h5 is only the packaging script's own rename for reference_outputs/). Template and tree corrected identically (D-06); checksums.sha256 re-emitted, 22/22 OK, verify_deposit() returns [].
- [Phase ?]: [Phase 113-04]: Grounded the concepts page's five-stage pipeline description in current source (engine/pipeline.py::build_stages docstring, stage module docstrings, Phase 110 API titles) rather than GUIDEBOOK.md sec 6's stale pre-v3.7 order (Detection/2D Tracking/Cross-Camera Association/Midline/Reconstruction with a post-association Midline stage); real order is Detection/Pose/Tracking/Association/Reconstruction with midline extraction (Pose) running before tracking. Logged GUIDEBOOK.md and two other stale CLAUDE.md bullets to deferred-items.md
- [Phase ?]: [Phase 113-05]: End-to-end GPU verification run (RTX 4070 Ti) executed prep generate-luts -> run -> viz against the deposit, exit 0 on all three; measured D-15's second timing point (224s pipeline / 85s viz vs reference's 786.45s / 150.85s) and D-12's statistics independently from midlines.h5 (95.9% reconstructed / 2.82px median residual vs reference's 95.2% / 2.84px, both within tolerance). Corrected a disproven '~2-5 min' LUT-generation timing claim to 'varies by GPU' in both the template and tree (D-06); source-confirmed two alarming per-chunk log lines (clustering count mismatch, more-dropped-than-kept reconstruction) as designed diagnostic behavior, not defects. Deposit restored to a verified 22-file state (verify_deposit() -> [], sha256sum -c -> 22 OK). Flagged the pre-existing 'Mean of empty slice' RuntimeWarning in recovery.py as out-of-scope, queued as a todo.
- [Phase ?]: [Phase 113-07]: Authored docs/getting-started/tutorial.md end-to-end against the locally verified deposit with an explicit ZENODO-DOI-PENDING placeholder at every archive-reference site (D-21) -- no doi.org link or invented DOI anywhere on the page. Kept the upload todo open rather than closing it (overriding stale plan-file prose to move it to done/), updated to note the tutorial is written and blocked only on the DOI fill-in pass. Completed the three-card Getting Started section.
- [Phase ?]: calibrate-keypoints writer now targets pose.keypoint_t_values (was midline.keypoint_t_values); stale legacy key removed with a notice (D-06)
- [Phase ?]: YOLO arc-length now measured in pixel space via new _resolve_sibling_image sibling-image resolution, matching the COCO path (D-08)
- [Phase ?]: Terminal-gate fixture uses a zigzag (both-axes) path rather than a straight diagonal, since a straight evenly-pixel-spaced line is invariant to the arc-length bug under any linear per-axis scaling

### Pending Todos

17 pending todos — triaged 2026-09-02. 5 bugs scheduled into Phase 113.1, the basedpyright backlog into Phase 113.2; 2 stale ones to be filed to done/ by 113.1. The rest are features or non-critical refactors — see .planning/todos/pending/

### Blockers/Concerns

- Docs build is RED on `dev` — 4 dead `automodule` targets (`aquapose.mesh`, `aquapose.optimization`, `aquapose.segmentation`, `aquapose.utils`) fail under `sphinx-build -W`. Read the Docs is connected but cannot build until the `a66287a` repair is forward-ported. Addressed by Phase 108 (108-01 merge delivered the repaired docs tree; verification is 108-05's remaining scope item).
- ~~8 failing tests on `dev`~~ — **resolved by Phase 109**: the real baseline was 23 local-Windows failures (config paths, symlink privilege, CLI-help, encoding, re-ID Swin size); QA-01 `test_luts.py::test_forward_lut_cast_ray_matches_model` was already green on the local 3.12 env (STATE-108's count was the Linux/CI estimate). Full suite green locally (fast 1295 passed; slow 15 passed / 2 e2e data-skips), no skip/xfail introduced.
- ~~`.planning/` is gitignored on `dev`~~ — **resolved by 108-03**: the `.gitignore:100` rule was removed; `.planning/` is tracked normally.
- ~~v3.11 has no MILESTONES.md entry~~ — **resolved by 108-04**: `v3.11 Appearance-Based ReID` and `v2.2 Backends` entries backfilled, tail re-sorted into chronological order (REC-01 satisfied).
- Repo transferred mid-108-05 from tlancaster6/AquaPose to McGrathLab/AquaPose (verified: same object history). **pyproject.toml URLs resolved by 109-03** (Homepage/Repository/Issues → McGrathLab/AquaPose). Stale tlancaster6 references still remain in CODE_OF_CONDUCT.md (1), docs/contributing.md (1), and ~829 historical links in CHANGELOG.md — deferred to Phase 114 (Publication).

### Environment Notes

- Working branch is `dev` (fast-forwarded to `origin/dev`, 1494 commits ahead of `main`).
- PROJECT.md, MILESTONES.md, config.json, GUIDEBOOK.md, and todos/ restored from `78d9b7a^` — the last commit before `.planning/` was untracked on `dev`.
- Phase numbering continues from **108** through **114** for v4.0.

### Roadmap Evolution

- Phase 113.1 inserted after Phase 113: Pre-Release Bug Fixes: clear the verified bug backlog; blocks 113-06 DOI mint (URGENT)
- Phase 113.2 inserted after Phase 113: Typecheck Backlog: 98 basedpyright errors to 0; blocks Phase 114 badge row (URGENT)

## Session Continuity

**Last session:** 2026-09-02T20:35:22.019Z

Last activity: 2026-09-01 — Phase 112 Plan 03 complete: config reference page authored with all 86 leaf fields covered (Essential + Advanced tiers), MISSING=[]
Stopped at: Completed 113.1-01-PLAN.md
Resume file: None

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| Phase 110 P01 | 10 | 2 tasks | 11 files |
| Phase 110 P03 | 30m | 2 tasks | 9 files |
| Phase 112 P03 | ~20m | 2 tasks | 1 file |
| Phase 112 P04 | 5m | - tasks | - files |
