---
phase: 109-correctness-green-test-suite-config-consolidation
plan: "05"
subsystem: test-suite / verification
tags: [correctness, honest-green, qa-01, qa-02, sign-off]
dependency_graph:
  requires: [109-01, 109-02, 109-03, 109-04]
  provides: [honest-green-suite, qa-01-confirmed, qa-02-confirmed]
  affects: [tests/unit/calibration/test_luts.py]
tech_stack:
  added: []
  patterns: [honest-green attestation — no skip/xfail, no weakened tolerances]
key_files:
  modified: []
decisions:
  - "QA-01 (D-01): test_forward_lut_cast_ray_matches_model is collected (not skipped/xfail) and passes with original 1e-4 m / 0.01° tolerances. test_luts.py is UNCHANGED across the entire phase (git diff empty) — tolerances literally untouched."
  - "STATE-108 discrepancy: STATE-108 listed QA-01 among '8 failing tests on dev' — that was the Linux/CI baseline estimate. On the fresh local Python 3.12 env (torch 2.5.1+cu121, pytest 9.1.1) it passes cleanly. Confirm-and-document per baseline diagnosis; no code fix."
  - "QA-02: full suite verified green LOCALLY (not deferred to CI). hatch run test = 1295 passed / 3 skipped / 0 failures. Slow suite (17 collected): 15 passed (2 re-ID end-to-end on GPU ~47m + 13 others in 78s), 2 e2e real-data smoke SKIPPED (no local real data, expected)."
  - "Honest-green attestation: repo-wide audit of all phase commits (0fea7fd..HEAD) shows NO @pytest.mark.skip or xfail added anywhere, and no LUT tolerance weakened."
metrics:
  duration: "~50 min (dominated by GPU slow-test run)"
  completed: "2026-09-01"
  tasks_completed: 3
  tasks_total: 3
  files_changed: 0
---

# Phase 109 Plan 05: Terminal Green Gate Summary

The AquaPose test suite is honestly green after Wave-1 fixes (109-01…04): both
`hatch run test` and the full slow suite pass locally, QA-01 (LUT parity) is confirmed
resolved with original tolerances, and no test was skipped/xfailed or had its tolerance
weakened anywhere in the phase.

## Tasks Completed

| # | Task | Result |
|---|------|--------|
| 1 | Confirm QA-01 LUT test green + document STATE-108 discrepancy (D-01) | LUT test green, no skip/xfail, tolerances intact; discrepancy documented |
| 2 | Full-suite green gate — `hatch run test` + slow suite | Fast: 1295 passed/0 fail. Slow: 15 passed, 2 e2e skipped |
| 3 | Human-verify checkpoint (blocking) | Approved by user |

## QA-01 — LUT Parity (D-01)

`test_forward_lut_cast_ray_matches_model` (tests/unit/calibration/test_luts.py:121) is
collected (no skip/xfail decorator) and passes as part of the green fast suite, asserting
LUT `cast_ray()` vs `model.cast_ray()` within **1e-4 m** (line 147) and **0.01°** (line 153).
`git diff 0fea7fd..HEAD -- tests/unit/calibration/test_luts.py` is **empty** — the tolerances
are literally unchanged.

**STATE-108 discrepancy (confirm-and-document, no code fix):** STATE-108 listed QA-01 among
"8 failing tests on dev." That figure was the Linux/CI baseline estimate; on the fresh local
Python 3.12 env (torch 2.5.1+cu121, numpy 2.x, pytest 9.1.1) the test passes cleanly with
original tolerances. Per the phase baseline diagnosis, QA-01 was already green — no code
change was required beyond confirmation.

## QA-02 — Honest Full-Suite Green

| Suite | Command | Result |
|-------|---------|--------|
| Fast (per-push) | `hatch run test` | **1295 passed, 3 skipped, 0 failures** |
| Slow re-ID end-to-end (GPU) | pytest 2 nodeids | **2 passed in 2847.03s (47m)** |
| Rest of slow suite | pytest `-m slow` (minus the 2 above) | **13 passed, 2 skipped in 78.29s** |

The 2 slow skips are the e2e real-data smoke tests (`tests/e2e/test_smoke.py::TestRealData`),
which correctly skip without local real data. Combined with the 3 fast-suite skips, this is
the expected set of marker/data skips — none are quarantined failures.

## Honest-Green Attestation

- Repo-wide audit `git diff 0fea7fd..HEAD -- tests/ src/ | grep '+.*(pytest.mark.skip|xfail)'`
  → **none added** anywhere in the phase.
- LUT tolerances (`1e-4` / `0.01`) unchanged; `test_luts.py` untouched.
- No production code weakened to reach green; every fix in 109-01…04 is a real root-cause fix.

## Deviations from Plan

- **Executed inline by the orchestrator** (not a spawned executor) because Task 2's
  `hatch run test-all` would otherwise trigger the multi-hour slow re-ID run under an agent
  that had already died once mid-run; the orchestrator controlled the slow-test execution
  directly (see 109-04 SUMMARY).
- **Slow suite run locally on GPU rather than deferred to CI.** An earlier plan considered
  CI-deferral (the slow re-ID tests hardcoded `device="cpu"` → ~2 h). After making those
  fixtures device-adaptive (109-04, commit `4be6a35`), the slow suite ran on the local GPU
  (~47 m) and is confirmed green here — a stronger result than CI deferral.

## Known Stubs

None.

## Threat Flags

None — verification/sign-off work only.

## Self-Check: PASSED

- QA-01 LUT test green, collected, tolerances unchanged (test_luts.py untouched)
- QA-02 both suites green locally (fast 1295 passed; slow 15 passed / 2 e2e skipped)
- No skip/xfail added anywhere in Phase 109
- Human-verify checkpoint approved
