# Phase 109: Correctness — Green Test Suite & Config Consolidation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-01
**Phase:** 109-correctness-green-test-suite-config-consolidation
**Areas discussed:** LUT test root cause, Tier-two fix policy, Config path convention (QA-03), Tutorial config scope (QA-04), Config alias, Golden regression data, LUT pre-pipeline refactor, Stale URLs

---

## LUT test: fix code or test? (QA-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Investigate first, no prior | Planner diagnoses whether LUT code drifted or tolerance is stale, then fixes accordingly | ✓ |
| Code regressed — fix LUT | Fix forward-LUT to match model.cast_ray; keep tolerances | |
| Contract changed — fix test | Update stale 1e-4m/0.01° thresholds/expected values | |

**User's choice:** Investigate first, no prior
**Notes:** QA-01 requires the failure resolved, not skipped, regardless of cause.

---

## Tier-two failures: fix policy (QA-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Update stale, flag real regressions | Assume code correct, update assertions/fixtures, surface anything that looks like a genuine regression | ✓ |
| Investigate each first | Require root-cause note before editing any test | |

**User's choice:** Update stale, flag real regressions
**Notes:** STATE-108 diagnosed these 7 as stale CLI-help assertions/fixtures.

---

## Config path convention (QA-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Relative to project_dir | Both fields resolve relative to project_dir; absolute paths honored | ✓ |
| Dedicated models/ subdir | Paths resolve under project_dir/models/ by convention | |
| You decide | Planner picks best fit for config.py resolution | |

**User's choice:** Relative to project_dir

---

## Tutorial config scope (QA-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Fix existing config only | Make current tutorial config paths relative/platform-neutral; convention for Phase 111 out of scope | ✓ |
| Define convention for Phase 111 | 109 establishes the path convention the example dataset inherits | |

**User's choice:** Fix existing config only

---

## Config alias

| Option | Description | Selected |
|--------|-------------|----------|
| Remove it (pre-1.0 clean break) | Drop model_path→weights_path alias; canonical name required | ✓ |
| Keep with deprecation warning | Retain alias, warn on old name | |
| Keep silently | Leave alias as-is | |

**User's choice:** Remove it (pre-1.0 clean break)

---

## Golden regression data (folded todo)

| Option | Description | Selected |
|--------|-------------|----------|
| Only if a fix requires it | Regenerate reference data only when a specific test fix depends on it; record why | ✓ |
| Regenerate proactively | Refresh v2.1 golden data deliberately this phase | |
| Defer to later phase | Leave in backlog | |

**User's choice:** Only if a fix requires it

---

## LUT pre-pipeline refactor (folded todo)

| Option | Description | Selected |
|--------|-------------|----------|
| Defer — keep 109 correctness-only | Don't refactor LUT placement; capture as deferred idea | ✓ |
| Only if the fix naturally touches it | Permit move only if the tier-one fix makes it natural | |
| Include as bounded refactor | Do the pre-pipeline move as its own task | |

**User's choice:** Defer — keep 109 correctness-only

---

## Stale tlancaster6 URLs

| Option | Description | Selected |
|--------|-------------|----------|
| pyproject.toml now, rest to 114 | Fix 3 pyproject URLs in 109 (ship in PyPI metadata); doc/CHANGELOG links to Phase 114 | ✓ |
| All in 109 | Correct every stale URL now | |
| All defer to 114 | Handle every URL during publication polish | |

**User's choice:** pyproject.toml now, rest to 114

---

## Claude's Discretion

- Diagnosis approach and exact fix for the tier-one LUT failure (user gave no prior).

## Deferred Ideas

- LUT generation → pre-pipeline setup (architectural refactor) — later phase/task.
- Example-dataset path convention — Phase 111.
- Remaining stale URLs (CODE_OF_CONDUCT.md, docs/contributing.md, ~829 CHANGELOG.md links) — Phase 114.
- Training/reconstruction feature todos surfaced by keyword match — other milestones/phases.
