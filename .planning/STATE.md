---
gsd_state_version: 1.0
milestone: v4.0
milestone_name: Publication
status: planning
last_updated: "2026-08-12T16:13:02.502Z"
last_activity: 2026-08-12
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-12)

**Core value:** Accurate 3D fish midline reconstruction from multi-view silhouettes via refractive multi-view triangulation
**Current focus:** v4.0 Publication — defining requirements

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-08-12 — Milestone v4.0 started

## Performance Metrics

**v3.10 Velocity:**

- Phases: 5 (97-101)
- Plans: 5
- Timeline: 29 days (2026-02-14 → 2026-03-15)

## Accumulated Context

### Decisions

Full decision log in PROJECT.md Key Decisions table.

Recent decisions affecting current work:

- [v3.11 roadmap]: Post-hoc ReID only — no changes to the chunk pipeline; all work in `core/reid/` and `training/`
- [v3.11 roadmap]: MegaDescriptor-T (timm) as backbone; pytorch-metric-learning for losses; zero-shot baseline evaluated in Phase 102 before committing to fine-tuning
- [v3.11 roadmap]: Female-female AUC >= 0.75 gate in Phase 104; milestone downscopes to male-female only if gate fails
- [Phase 102 testing]: Zero-shot MegaDescriptor-T achieves 97.4% Rank-1, 73.6% mAP on clean segment (frames 0-599). Fish 2↔8 pair most confusable (0.869 cosine similarity).
- [Phase 106-01]: Use SimpleNamespace for embed config to avoid forbidden engine/ import in core/ module (import boundary rule)
- [Phase 106-01]: Remove top-level mine-reid-crops command; delete scripts/train_reid_head.py — both superseded by reid group subcommands

### Pending Todos

12 pending todos — see .planning/todos/pending/ (review for relevance)

### Blockers/Concerns

- Docs build is RED on `dev` — 4 dead `automodule` targets (`aquapose.mesh`, `aquapose.optimization`, `aquapose.segmentation`, `aquapose.utils`) fail under `sphinx-build -W`. Read the Docs is connected but cannot build until the `a66287a` repair is forward-ported.
- 8 failing tests on `dev` — `test_luts.py::test_forward_lut_cast_ray_matches_model` is a tier-one blocker; the other 7 are stale CLI-help assertions and fixtures in `training/` and `evaluation/`.
- `.planning/` is gitignored on `dev` (commit `78d9b7a`) — planning commits require `git add -f`.
- v3.11 has no MILESTONES.md entry — it was in progress when `.planning/` was untracked. ROADMAP.md and `phases/102-107/` retain the record.

### Environment Notes

- Working branch is now `dev` (fast-forwarded to `origin/dev`, 1494 commits ahead of `main`).
- PROJECT.md, MILESTONES.md, config.json, GUIDEBOOK.md, and todos/ restored from `78d9b7a^` — the last commit before `.planning/` was untracked on `dev`.
- Phase numbering continues from **108** (phase 107 shipped with a VERIFICATION.md).

## Session Continuity

Last activity: 2026-08-12 — Milestone v4.0 Publication started
Stopped at: Defining requirements
Resume file: None
