---
phase: 109-correctness-green-test-suite-config-consolidation
plan: 02
type: execute
wave: 3
depends_on: ["01", "03", "04"]
files_modified:
  - tests/unit/training/
  - tests/unit/engine/
autonomous: true
requirements: [QA-02]

must_haves:
  truths:
    - "The 7 tier-two failures in tests/unit/training/ and tests/unit/engine/ pass"
    - "Each fixed test passes BECAUSE a stale assertion/fixture was corrected (or a real bug fixed) — with a one-line root-cause note per test, not because a skip/xfail was added"
    - "hatch run test-all exits with zero failures across the whole suite (tier-one LUT + tier-two + all others)"
    - "No @pytest.mark.skip/@pytest.mark.xfail was added anywhere to reach green"
  artifacts:
    - path: "tests/unit/training/"
      provides: "Green training tests (stale CLI-help/fixtures corrected)"
    - path: "tests/unit/engine/"
      provides: "Green engine tests"
  key_links:
    - from: "hatch run test-all"
      to: "full suite exit code"
      via: "zero failures including test_forward_lut_cast_ray_matches_model and the 7 tier-two tests"
      pattern: "test-all"
---

<objective>
Resolve the 7 tier-two failures in `tests/unit/training/` and `tests/unit/engine/`
(QA-02), then run the terminal full-suite green gate.

STATE-108 diagnosed these as stale CLI-help assertions and training/evaluation
fixtures. Per D-02, the default stance is: assume the code is correct and update
the stale assertions/fixtures — BUT flag any failure that looks like a genuine
regression rather than blindly rewriting the test, and record a one-line
root-cause note per fixed test. Per the folded-todo decision, regenerate
golden/reference data ONLY when a specific failing test genuinely depends on it,
and record why — do NOT wholesale-regenerate (that risks masking real regressions).

This plan runs LAST (wave 3, depends on Plan 01 fixing the tier-one LUT test,
Plan 03 removing the model_path alias / unifying config resolution, and Plan 04
making the init scaffold platform-neutral) so the final `hatch run test-all`
green gate validates the whole corrected baseline.

Note on file ownership: this plan does NOT modify tests/unit/engine/test_cli.py
(owned by Plan 04) — the 7 tier-two failures are stale CLI-help/fixture tests in
training/ and other engine test modules, not the init-scaffold CLI test.

Purpose: An honestly green suite and coverage badge for downstream doc/publication phases.
Output: 7 tier-two tests green with recorded root causes, and a zero-failure full suite.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/109-correctness-green-test-suite-config-consolidation/109-CONTEXT.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Enumerate and diagnose the 7 tier-two failures</name>
  <read_first>
    - .planning/STATE.md (Phase 108 blockers: "the other 7 are stale CLI-help assertions and fixtures in training/ and evaluation/")
    - .planning/phases/109-correctness-green-test-suite-config-consolidation/109-CONTEXT.md (D-02 stance: update stale assertions/fixtures but flag genuine regressions; folded-todo: regenerate golden data only when a specific failing test depends on it)
    - CLAUDE.md (run tests via `hatch run test` / `hatch run test-all`; never bare `pytest -k`; CUDA tensors use .cpu().numpy())
  </read_first>
  <action>
    Run the suite (`hatch run test`, or `python -m hatch run test` if the hatch shim is unavailable) and capture the exact set of currently-failing tests in tests/unit/training/ and tests/unit/engine/. There should be about 7 (excluding the tier-one LUT test, which Plan 01 fixes, and excluding tests/unit/engine/test_cli.py which Plan 04 owns). For EACH failing test, read the assertion/fixture and the code it exercises, and classify: (A) STALE — the production code changed legitimately and the test's expected CLI-help string / fixture / golden value is out of date; or (B) GENUINE REGRESSION — the test encodes correct behavior and the code is actually wrong. Record a one-line root-cause note per test naming the bucket and the specific drift (e.g. "help text renamed --foo to --bar", "fixture references removed field X", "golden output shape changed because Y"). Do NOT edit anything in this task — this is diagnosis only. If any test is bucket (B), STOP and flag it prominently in the note rather than silently rewriting it.
  </action>
  <acceptance_criteria>
    - The exact list of tier-two failing tests (file::test names) is recorded.
    - Each failing test has a one-line root-cause note with bucket (A) STALE or (B) GENUINE REGRESSION and the specific drift.
    - No test file was modified in this task.
  </acceptance_criteria>
  <done>Every tier-two failure has a recorded root cause and bucket, gating the Task 2 fixes.</done>
</task>

<task type="auto">
  <name>Task 2: Fix each stale tier-two test and record the root cause</name>
  <read_first>
    - The Task 1 per-test diagnosis (bucket A vs B and the specific drift)
    - Each failing test file identified in Task 1 (in tests/unit/training/ or tests/unit/engine/, excluding test_cli.py)
    - The specific production module each stale test exercises (to update the expected CLI-help string / fixture to current, correct behavior)
  </read_first>
  <action>
    For each bucket (A) STALE test: update the stale assertion or fixture to match the current, correct production behavior — e.g. correct the expected CLI-help substring, refresh the fixture to the current field names/shapes, or regenerate a specific golden/reference file ONLY if that exact test genuinely depends on it (record the regeneration reason inline). Do NOT wholesale-regenerate golden data and do NOT loosen or delete assertions merely to pass. Under NO circumstance add @pytest.mark.skip or @pytest.mark.xfail. For any bucket (B) GENUINE REGRESSION surfaced in Task 1: do NOT rewrite the test to match wrong behavior — instead fix the underlying production bug so the test passes as written, or if the fix is out of this phase's correctness scope, record it as a blocker in the SUMMARY and surface it rather than masking it. Do not modify tests/unit/engine/test_cli.py (Plan 04's file). Preserve CUDA-safety and code-style rules on any touched code.
  </action>
  <acceptance_criteria>
    - Each of the previously-failing tier-two tests now passes under `hatch run test`.
    - Each fixed test has a recorded one-line root cause; passing is due to a corrected stale assertion/fixture (or a fixed real bug), not an added skip/xfail.
    - `grep -rnE "@pytest.mark.(skip|xfail)" tests/unit/training tests/unit/engine` shows no marker newly added by this plan.
    - Any golden/reference regeneration is limited to files a specific failing test depends on, with the reason recorded.
  </acceptance_criteria>
  <done>All 7 tier-two failures pass because their stale assertions/fixtures were corrected (or a real bug was fixed), each with a recorded root cause.</done>
</task>

<task type="auto">
  <name>Task 3: Run the terminal full-suite green gate</name>
  <read_first>
    - CLAUDE.md (`hatch run test-all` runs the full suite including slow tests; never bare pytest -k)
    - The Plan 01, Plan 03, and Plan 04 SUMMARYs (confirm the tier-one LUT fix, the config-alias removal, and the platform-neutral scaffold landed, since this gate validates the whole corrected baseline)
  </read_first>
  <action>
    Run `hatch run test-all` (or `python -m hatch run test-all` if the shim is unavailable) across the entire suite and confirm zero failures — including test_forward_lut_cast_ray_matches_model (Plan 01), the 7 tier-two tests (Task 2), the config tests reflecting the removed model_path alias (Plan 03), and the init-scaffold neutrality test (Plan 04). If any failure remains, diagnose it under the same D-02 discipline (stale vs genuine regression) and fix the stale case or surface the genuine regression; do not add skip/xfail to force green. Record the final pass/fail counts in the SUMMARY.
  </action>
  <acceptance_criteria>
    - `hatch run test-all` exits 0 with zero failures.
    - The run explicitly includes test_forward_lut_cast_ray_matches_model as passed and the 7 previously-failing tier-two tests as passed.
    - No `@pytest.mark.skip`/`xfail` was added anywhere in the repo to reach green (grep across tests/ shows none introduced by this phase).
    - Final pass/fail/skip counts are recorded in the SUMMARY.
  </acceptance_criteria>
  <done>The full suite is honestly green — zero failures, no quarantined tests — making the coverage badge trustworthy.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

None new. This plan edits internal test assertions/fixtures and runs the suite.
No network, no user-input parsing, no new attack surface.

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-109-02 | Tampering | Tier-two test assertions/fixtures | mitigate | D-02 discipline: correct stale assertions but flag genuine regressions rather than rewriting tests to match wrong behavior; forbid skip/xfail so green is honest. |
</threat_model>

<verification>
- `hatch run test-all` exits 0 with zero failures.
- Each of the 7 tier-two fixes has a recorded one-line root cause (bucket A stale / B regression).
- No skip/xfail introduced; golden data regenerated only where a specific test depends on it.
</verification>

<success_criteria>
QA-02 satisfied: the 7 tier-two failures pass with recorded root causes, and the
full `hatch run test-all` suite is honestly green (including the Plan 01 tier-one
fix, Plan 03 config change, and Plan 04 scaffold change), making the coverage
badge honest.
</success_criteria>

<output>
Create `.planning/phases/109-correctness-green-test-suite-config-consolidation/109-02-SUMMARY.md` when done. Include the per-test root-cause notes and the final full-suite pass counts.
</output>
