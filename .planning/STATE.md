---
gsd_state_version: 1.0
milestone: v4.0
milestone_name: Publication
status: executing
stopped_at: Phase 109 Plan 01 complete
last_updated: "2026-09-01T15:15:00.000Z"
last_activity: 2026-09-01 -- Phase 109 Plan 01 executed (config alias removal + run_manager forward-slash fix)
progress:
  total_phases: 7
  completed_phases: 1
  total_plans: 10
  completed_plans: 6
  percent: 16
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-12)

**Core value:** Accurate 3D fish midline reconstruction from multi-view silhouettes via refractive multi-view triangulation
**Current focus:** Phase 109 — correctness-green-test-suite-config-consolidation

## Current Position

Phase: 109 (correctness-green-test-suite-config-consolidation) — EXECUTING
Plan: 2 of 5
Status: Executing Phase 109 (Plan 01 complete)
Last activity: 2026-09-01 -- Phase 109 Plan 01 executed (config alias removal + run_manager forward-slash fix)

## Performance Metrics

**v3.10 Velocity:**

- Phases: 5 (97-101)
- Plans: 5
- Timeline: 29 days (2026-02-14 → 2026-03-15)

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

### Pending Todos

12 pending todos — see .planning/todos/pending/ (review for relevance)

### Blockers/Concerns

- Docs build is RED on `dev` — 4 dead `automodule` targets (`aquapose.mesh`, `aquapose.optimization`, `aquapose.segmentation`, `aquapose.utils`) fail under `sphinx-build -W`. Read the Docs is connected but cannot build until the `a66287a` repair is forward-ported. Addressed by Phase 108 (108-01 merge delivered the repaired docs tree; verification is 108-05's remaining scope item).
- 8 failing tests on `dev` — `test_luts.py::test_forward_lut_cast_ray_matches_model` is a tier-one blocker; the other 7 are stale CLI-help assertions and fixtures in `training/` and `evaluation/`. Addressed by Phase 109.
- ~~`.planning/` is gitignored on `dev`~~ — **resolved by 108-03**: the `.gitignore:100` rule was removed; `.planning/` is tracked normally.
- ~~v3.11 has no MILESTONES.md entry~~ — **resolved by 108-04**: `v3.11 Appearance-Based ReID` and `v2.2 Backends` entries backfilled, tail re-sorted into chronological order (REC-01 satisfied).
- Repo transferred mid-108-05 from tlancaster6/AquaPose to McGrathLab/AquaPose (verified: same object history). Stale tlancaster6 URLs remain in pyproject.toml (3: Homepage/Repository/Issues, ships in PyPI metadata), CODE_OF_CONDUCT.md (1), docs/contributing.md (1), and ~829 historical links in CHANGELOG.md. pyproject.toml is closed per 108-02; out of Phase 108 scope. Follow-up for Phase 109 or 114.

### Environment Notes

- Working branch is `dev` (fast-forwarded to `origin/dev`, 1494 commits ahead of `main`).
- PROJECT.md, MILESTONES.md, config.json, GUIDEBOOK.md, and todos/ restored from `78d9b7a^` — the last commit before `.planning/` was untracked on `dev`.
- Phase numbering continues from **108** through **114** for v4.0.

## Session Continuity

Last activity: 2026-09-01 — Phase 109 Plan 01 complete (config alias removal, run_manager forward-slash fix)
Stopped at: Phase 109 Plan 01 complete — continuing to Plan 02
Resume file: .planning/phases/109-correctness-green-test-suite-config-consolidation/109-02-PLAN.md
