---
phase: 109-correctness-green-test-suite-config-consolidation
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/unit/calibration/test_luts.py
  - src/aquapose/calibration/luts.py
autonomous: true
requirements: [QA-01]

must_haves:
  truths:
    - "test_luts.py::test_forward_lut_cast_ray_matches_model passes when run under the real suite (hatch run test)"
    - "The failure is resolved by a recorded diagnosis of the actual root cause, not by a skip/xfail or an un-justified tolerance change"
    - "No @pytest.mark.skip or @pytest.mark.xfail marker is present on the tier-one test"
  artifacts:
    - path: "tests/unit/calibration/test_luts.py"
      provides: "Passing tier-one LUT-vs-model cast_ray parity test"
      contains: "def test_forward_lut_cast_ray_matches_model"
  key_links:
    - from: "aquapose.calibration.luts.generate_forward_lut / LUT.cast_ray"
      to: "aquapose.calibration.projection.RefractiveProjectionModel.cast_ray"
      via: "grid_step=1 parity within 1e-4 m origin / 0.01 deg angular"
      pattern: "cast_ray"
---

<objective>
Resolve the tier-one calibration failure QA-01:
`tests/unit/calibration/test_luts.py::test_forward_lut_cast_ray_matches_model`
(line 121) must PASS — resolved, not skipped.

The test asserts that a forward LUT built with `grid_step=1` reproduces
`RefractiveProjectionModel.cast_ray()` within `1e-4 m` origin distance and
`0.01°` angular error, using the seeded `make_test_model()` fixture. There is
NO prior on the root cause (D-01). The plan MUST diagnose first — determine
whether the forward-LUT code (`generate_forward_lut` / `LUT.cast_ray`) drifted
from `model.cast_ray`, or whether the `1e-4 m` / `0.01°` tolerances are stale —
THEN fix the actual cause.

Purpose: The tier-one LUT test is the gating correctness blocker for the honest
green suite; the coverage/tests badges downstream depend on it passing legitimately.
Output: A passing tier-one test plus a one-line recorded root-cause note in the SUMMARY.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/109-correctness-green-test-suite-config-consolidation/109-CONTEXT.md
@tests/unit/calibration/test_luts.py
@src/aquapose/calibration/luts.py
@src/aquapose/calibration/projection.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Diagnose the root cause of the cast_ray parity failure</name>
  <read_first>
    - tests/unit/calibration/test_luts.py (the failing test at line 121 and the seeded make_test_model() fixture at line 32; reuse make_test_model() for the diagnosis harness — do NOT invent a new model)
    - src/aquapose/calibration/luts.py (generate_forward_lut and the LUT.cast_ray implementation — how grid origins/directions are built and interpolated at grid_step=1)
    - src/aquapose/calibration/projection.py (RefractiveProjectionModel.cast_ray — the reference contract the LUT must match)
    - .planning/STATE.md (Phase 108 blockers: this is the tier-one failure with no diagnosed root cause)
  </read_first>
  <action>
    Build a temporary diagnosis harness (a throwaway script or a scratch test, NOT a committed skip) that reuses the seeded make_test_model() fixture. Generate a grid_step=1 forward LUT for image_size (640, 480) and compare LUT.cast_ray() against model.cast_ray() on the same 50 seeded pixel samples the failing test uses (rng seed 42, us in [10, 630], vs in [10, 470]). Report the actual max origin distance (metres) and max angular error (degrees). Classify the failure into exactly one of two buckets: (A) CODE DRIFT — generate_forward_lut or LUT.cast_ray diverged from model.cast_ray (e.g. a units, sign, interpolation-indexing, or origin-vs-direction bug), evidenced by errors far above 1e-4 m / 0.01 deg; or (B) STALE TOLERANCE — the LUT is faithful and the contract legitimately changed, evidenced by errors just above the threshold with no logic defect. Record which bucket and the measured numbers. Do NOT edit production code or the tolerance yet — this task only produces the diagnosis.
  </action>
  <acceptance_criteria>
    - A recorded diagnosis states measured max origin distance (m) and max angular error (deg) for grid_step=1 LUT vs model cast_ray on the seeded samples.
    - The diagnosis names bucket (A) CODE DRIFT or (B) STALE TOLERANCE with the specific evidence (which function, which quantity is off, by how much).
    - No production code and no tolerance value has been changed in this task.
  </acceptance_criteria>
  <done>The root-cause bucket and measured error magnitudes are recorded, gating the Task 2 fix.</done>
</task>

<task type="auto">
  <name>Task 2: Apply the diagnosis-gated fix so the tier-one test passes resolved</name>
  <read_first>
    - The Task 1 diagnosis (bucket A or B and the measured numbers)
    - src/aquapose/calibration/luts.py (if bucket A — the specific drifted function)
    - tests/unit/calibration/test_luts.py (the assertions at lines 147-155 with the 1e-4 m / 0.01 deg thresholds)
  </read_first>
  <action>
    If bucket A (CODE DRIFT): fix the defect in generate_forward_lut or LUT.cast_ray in src/aquapose/calibration/luts.py so grid_step=1 output matches model.cast_ray within the existing 1e-4 m / 0.01 deg thresholds. Leave the test tolerances unchanged. Preserve CUDA-safety (.cpu().numpy() never bare .numpy()), type hints on any touched public function, and Google-style docstrings per code-style rules. If bucket B (STALE TOLERANCE): adjust ONLY the specific tolerance the diagnosis proved is legitimately stale, in tests/unit/calibration/test_luts.py, to a value the faithful LUT actually meets, and record the numeric justification. Under NO circumstance add @pytest.mark.skip or @pytest.mark.xfail, and do not loosen the 1e-4 m or 0.01 deg thresholds without the Task 1 diagnosis proving the contract changed. Remove the diagnosis harness after the fix.
  </action>
  <acceptance_criteria>
    - `python -m hatch run test` (or `hatch run test`) reports `test_forward_lut_cast_ray_matches_model` as PASSED.
    - `grep -nE "@pytest.mark.(skip|xfail)" tests/unit/calibration/test_luts.py` returns no line applying to test_forward_lut_cast_ray_matches_model.
    - If any tolerance was changed, the SUMMARY records the measured error and why the contract legitimately changed; if code was changed, the 1e-4 m / 0.01 deg thresholds in the test are unchanged.
    - The sibling tests in the same file (test_forward_lut_interpolation_accuracy, test_validate_forward_lut_passes) still pass.
  </acceptance_criteria>
  <done>The tier-one test passes because the real root cause was fixed or a proven-stale tolerance corrected, with the reason recorded and no skip/xfail added.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

None new. This plan edits an internal unit test and (conditionally) an internal
calibration function. No network, no user input parsing, no new attack surface.

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-109-01 | Tampering | LUT parity test | accept | Internal test correctness only; no external input, no trust boundary crossed. N/A rationale. |
</threat_model>

<verification>
- `hatch run test` passes `tests/unit/calibration/test_luts.py::test_forward_lut_cast_ray_matches_model`.
- No skip/xfail marker on the tier-one test.
- Root-cause bucket and measured error magnitudes recorded in the SUMMARY.
</verification>

<success_criteria>
QA-01 satisfied: the tier-one calibration failure is resolved (not skipped),
with a recorded diagnosis proving the fix addresses the real root cause and no
un-justified tolerance weakening.
</success_criteria>

<output>
Create `.planning/phases/109-correctness-green-test-suite-config-consolidation/109-01-SUMMARY.md` when done. Include the root-cause bucket, measured error magnitudes, and the exact fix applied.
</output>
