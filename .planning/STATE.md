---
gsd_state_version: 1.0
milestone: v4.0
milestone_name: Publication
status: planning
last_updated: "2026-08-12T16:13:02.502Z"
last_activity: 2026-08-12
progress:
  total_phases: 7
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-12)

**Core value:** Accurate 3D fish midline reconstruction from multi-view silhouettes via refractive multi-view triangulation
**Current focus:** v4.0 Publication — roadmap created, ready to plan Phase 108

## Current Position

Phase: 108 (Branch Reconciliation & Repo Hygiene) — not started
Plan: —
Status: Roadmap approved, awaiting phase planning
Last activity: 2026-08-12 — ROADMAP.md created for v4.0 (Phases 108-114)

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

### Pending Todos

12 pending todos — see .planning/todos/pending/ (review for relevance)

### Blockers/Concerns

- Docs build is RED on `dev` — 4 dead `automodule` targets (`aquapose.mesh`, `aquapose.optimization`, `aquapose.segmentation`, `aquapose.utils`) fail under `sphinx-build -W`. Read the Docs is connected but cannot build until the `a66287a` repair is forward-ported. Addressed by Phase 108.
- 8 failing tests on `dev` — `test_luts.py::test_forward_lut_cast_ray_matches_model` is a tier-one blocker; the other 7 are stale CLI-help assertions and fixtures in `training/` and `evaluation/`. Addressed by Phase 109.
- `.planning/` is gitignored on `dev` (commit `78d9b7a`) — planning commits require `git add -f`.
- v3.11 has no MILESTONES.md entry — it was in progress when `.planning/` was untracked. ROADMAP.md and `phases/102-107/` retain the record; backfill scheduled in Phase 108.

### Environment Notes

- Working branch is `dev` (fast-forwarded to `origin/dev`, 1494 commits ahead of `main`).
- PROJECT.md, MILESTONES.md, config.json, GUIDEBOOK.md, and todos/ restored from `78d9b7a^` — the last commit before `.planning/` was untracked on `dev`.
- Phase numbering continues from **108** through **114** for v4.0.

## Session Continuity

Last activity: 2026-08-12 — v4.0 ROADMAP.md created (7 phases, 108-114), REQUIREMENTS.md traceability filled in
Stopped at: Roadmap approved and written; next step is `/gsd:plan-phase 108`
Resume file: None
