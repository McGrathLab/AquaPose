---
phase: 113-concepts-tutorial
plan: 02
subsystem: testing
tags: [pytorch, numerical-conditioning, ci-green-up, calibration]

requires:
  - phase: 109-05-qa-gates
    provides: "The QA-01 record this plan corrects — Phase 109-05 reported the test 'confirmed green (resolved, not skipped, tolerances intact)', which D-17 establishes was a vacuous local pass, not genuine verification"
provides:
  - "Numerically stable float64 atan2(||cross||, dot) angular-error metric, applied identically at all three sites that previously used torch.acos(clamp(dot, -1, 1))"
  - "Both test_luts.py angular-error assertions with their original 0.01/0.1 degree thresholds unchanged, now measuring real signal instead of float32 rounding noise"
  - "validate_forward_lut reporting a trustworthy max_angular_error_deg with its existing 0.1 degree ValueError guard intact"
affects: [114-publication]

actuals:
  tokens: 658
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Stable angle-between-vectors metric: atan2(cross(a,b).norm(-1), (a*b).sum(-1)) in float64, replacing acos(dot) which is ill-conditioned as dot approaches 1"

key-files:
  created: []
  modified:
    - tests/unit/calibration/test_luts.py
    - src/aquapose/calibration/luts.py

key-decisions:
  - "Kept both thresholds (0.01, 0.1 degrees) exactly unchanged per D-17/D-18 and the plan's explicit prohibition — this was a metric correction, not a tolerance relaxation"
  - "Demonstrated the assertion is not vacuous by temporarily perturbing model_dirs[0,0] by 0.01 (rotating one direction vector) directly in test_forward_lut_cast_ray_matches_model, confirming red, then reverting to confirm green — the exact check D-17/T-113-06 requires"
  - "Did not run hatch run typecheck as a gate (D-19 boundary); no # type: ignore suppressions added anywhere"

requirements-completed: [QA-01]

coverage:
  - id: D1
    description: "Both angular-error assertion sites in test_luts.py use the stable float64 atan2 formula with unchanged thresholds, and are demonstrated to go red on genuine disagreement"
    requirement: "QA-01"
    verification:
      - kind: unit
        ref: "hatch run test tests/unit/calibration/test_luts.py::test_forward_lut_cast_ray_matches_model"
        status: pass
      - kind: unit
        ref: "hatch run test tests/unit/calibration/test_luts.py::test_forward_lut_interpolation_accuracy"
        status: pass
    human_judgment: false
  - id: D2
    description: "validate_forward_lut reports the same stable, trustworthy angular-error metric, with its 0.1 degree ValueError guard and returned dictionary keys unchanged"
    requirement: "QA-01"
    verification:
      - kind: unit
        ref: "tests/unit/calibration/test_luts.py::test_validate_forward_lut_passes"
        status: pass
    human_judgment: false
  - id: D3
    description: "hatch run test, hatch run lint, and hatch run ruff format --check src/ tests/ scripts/ all exit 0 (D-16 regression guard held; the one remaining test failure is the pre-existing, unrelated test_pseudo_label_cli.py case)"
    requirement: "QA-01"
    verification:
      - kind: other
        ref: "hatch run test (1374 passed, 1 pre-existing unrelated failure, 3 skipped); hatch run lint (All checks passed); hatch run ruff format --check src/ tests/ scripts/ (238 files already formatted)"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-09-02
status: complete
---

# Phase 113 Plan 02: CI Green-Up — Stable Angular-Error Metric (D-17, D-18) Summary

**Replaced the ill-conditioned `torch.acos(dot)` angular-error metric with a numerically stable float64 `atan2(||cross||, dot)` formula at all three sites (two test assertions + `validate_forward_lut`), keeping every threshold unchanged, and proved the fix by driving a deliberate perturbation to a measured red.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-02T12:34:26Z
- **Completed:** 2026-09-02T12:40:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Replaced `torch.acos(clamp(dot, -1, 1))` with `torch.atan2(cross_norm, dot)` computed in float64 at both angular-error assertion sites in `tests/unit/calibration/test_luts.py` (`test_forward_lut_cast_ray_matches_model`, threshold 0.01°; `test_forward_lut_interpolation_accuracy`, threshold 0.1°). Both thresholds were left exactly as they were.
- Measured the true max angular error under the new formula in `test_forward_lut_cast_ray_matches_model`: **2.0716e-05°** — matching the CONTEXT.md D-17 prediction (2.07e-5°) and confirming a ~500x real margin under the 0.01° threshold, versus the old metric's vacuous 0.000000° (float32 dot rounding to exactly 1.0 on this machine).
- Proved the assertion is not structurally vacuous: temporarily perturbed `model_dirs[0, 0]` by `+0.01` (a rotation of one direction vector) directly in the test, re-ran, and observed the assertion fail with **`Max angular error 0.5558° exceeds 0.01° threshold`** — a clean red. Reverted the perturbation and re-ran to confirm green again (2.07e-05°, matching the unperturbed baseline). This is the exact red/green demonstration D-17 and threat T-113-06 require.
- Applied the identical stable formula to `validate_forward_lut` in `src/aquapose/calibration/luts.py` (D-18), leaving the `max_angular_error_deg > 0.1` `ValueError` guard, its message, the four returned dictionary keys, and the docstring's `Raises:` clause unchanged.
- Confirmed all three CI failure causes this plan owns are cleared: `hatch run test` exits 0 (aside from the pre-existing, unrelated `test_pseudo_label_cli.py` failure already logged in `deferred-items.md` by Plan 01), `hatch run lint` exits 0, and `hatch run ruff format --check src/ tests/ scripts/` exits 0 (D-16 regression guard held — no formatting drift was reintroduced).
- Confirmed the D-19 boundary was respected: `hatch run typecheck` was not run as a gate, and `git diff | grep -c 'type: ignore'` is 0 across both commits.

## Task Commits

1. **Task 1: Replace the ill-conditioned angular-error metric at both test sites (D-17)** - `01c60ae` (fix)
2. **Task 2: Apply the same stable-angle formula to `validate_forward_lut` (D-18) and confirm the CI-red causes are cleared** - `ff8b0df` (fix)

**Plan metadata:** (this commit, docs-only)

## Files Created/Modified

- `tests/unit/calibration/test_luts.py` - Both angular-error assertion sites now compute the angle as `torch.atan2(torch.linalg.cross(lut_dirs.double(), model_dirs.double(), dim=-1).norm(dim=-1), (lut_dirs.double() * model_dirs.double()).sum(dim=-1))`, replacing `torch.acos((lut_dirs * model_dirs).sum(dim=-1).clamp(-1.0, 1.0))`. Thresholds (0.01, 0.1), origin-distance assertions (1e-4, 1e-3), seeds, sample counts, and `.cpu()` calls untouched.
- `src/aquapose/calibration/luts.py` - `validate_forward_lut`'s angular-error computation replaced with the identical stable float64 formula. The `> 0.1` `ValueError` guard, its message, the four returned dictionary keys (`max_angular_error_deg`, `mean_angular_error_deg`, `max_origin_error_m`, `mean_origin_error_m`), and the docstring are unchanged.

## Decisions Made

- **Metric correction, not tolerance relaxation:** both thresholds (0.01°, 0.1°) were kept byte-identical to the plan's must-haves prohibitions. The real margin under the stable formula is roughly 500x, but that margin comes from measuring correctly, not from loosening the bar.
- **Vacuous-pass proof performed in-situ:** rather than relying only on the CONTEXT.md's documented CI evidence, the plan's required red/green demonstration was performed directly against the current codebase (perturb → red → revert → green) to generate first-hand evidence rather than trusting the prior analysis alone.
- **D-19 boundary strictly held:** `hatch run typecheck` was deliberately not invoked as part of this plan's verification, consistent with the CONTEXT.md build gate; the 98-error basedpyright backlog remains untouched and tracked separately in `.planning/todos/pending/2026-09-02-fix-basedpyright-typecheck-backlog.md`.

## Deviations from Plan

None - plan executed exactly as written. No Rule 1-4 auto-fixes were required in either task.

## Issues Encountered

- `hatch run ruff format` reformatted both edited files' new multi-line expressions (line-wrapping the `torch.linalg.cross(...)` calls) after the initial edit — expected formatter behavior, not a deviation; verified tests still passed after reformatting before committing.
- The pre-existing, unrelated `tests/unit/training/test_pseudo_label_cli.py::TestGenerateCommand::test_generates_merged_obb_and_separate_pose` failure (already logged in `.planning/phases/113-concepts-tutorial/deferred-items.md` by Plan 01) is still present and untouched — confirmed out of scope for this plan, not a regression introduced here.

## Known Stubs

None.

## Threat Flags

None. Both threats this plan owned — T-113-05 (tampering: `validate_forward_lut` guard reporting rounding noise instead of signal) and T-113-06 (repudiation: a vacuously-passing test producing an unreliable green CI record) — were mitigated exactly as the plan's threat model specified. No new unmitigated surface was introduced.

## User Setup Required

None - no external service configuration required.

## Correction to the Phase 109-05 Record (QA-01)

Phase 109-05 reported `test_luts.py::test_forward_lut_cast_ray_matches_model` as "confirmed green (resolved, not skipped, tolerances intact)" and attributed the CI failure that motivated this plan to a stale "Linux/CI estimate." That conclusion was luck, not verification: on this machine the float32 dot product of two nearly-parallel unit vectors rounds to exactly `1.0` (max observed `1.0000001192`, clamped), so `torch.acos(1.0)` returns `0.000000°` and the assertion passed while measuring nothing. On CI, a 1-ulp difference put the dot at approximately `1 − 6e-8`, which `acos`'s infinite derivative at `x → 1` amplified to `0.0198°`, tripping the 0.01° threshold. QA-01 is genuinely satisfied only as of this plan: the metric now measures the real angular disagreement (2.0716e-05° on this machine), the thresholds are unchanged, and the assertion has been demonstrated (via deliberate perturbation) to actually detect disagreement rather than passing vacuously.

## Next Phase Readiness

- All three CI-red causes folded into this phase (D-16 already done, D-17 and D-18 fixed here) are cleared. The `pre-commit` and `test` CI jobs should have no remaining cause of failure from this repository state.
- The `typecheck` CI job remains red by design (D-19) — tracked in `.planning/todos/pending/2026-09-02-fix-basedpyright-typecheck-backlog.md`, out of scope for Phase 113/114.
- No changes here touch the tutorial dataset, `aquapose prep generate-luts`, or any doc page — Plan 05 (tutorial verification run) and Plan 07 (tutorial page) are unaffected.

## Self-Check: PASSED

- FOUND: tests/unit/calibration/test_luts.py (modified — 2 atan2 sites, 0 acos)
- FOUND: src/aquapose/calibration/luts.py (modified — 1 atan2 site, 0 acos)
- FOUND commit: 01c60ae
- FOUND commit: ff8b0df

---
*Phase: 113-concepts-tutorial*
*Completed: 2026-09-02*
