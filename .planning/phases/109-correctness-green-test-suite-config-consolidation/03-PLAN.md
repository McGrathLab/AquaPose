---
phase: 109-correctness-green-test-suite-config-consolidation
plan: 03
type: execute
wave: 1
depends_on: []
files_modified:
  - src/aquapose/engine/config.py
  - tests/unit/engine/test_config.py
autonomous: true
requirements: [QA-03]

must_haves:
  truths:
    - "Relative weights-path fields (detection weights_path and pose/keypoint weights_path) resolve relative to project_dir; absolute paths are honored as-is"
    - "The model_path -> weights_path back-compat alias is removed from config.py; a config using model_path now raises the strict unknown-field ValueError"
    - "Both the detection backend and the midline/keypoint (pose) backend consume the same project_dir-relative resolution convention"
  artifacts:
    - path: "src/aquapose/engine/config.py"
      provides: "Single project_dir-relative resolution for weights-path fields, alias removed"
      contains: "project_dir"
    - path: "tests/unit/engine/test_config.py"
      provides: "Tests asserting unified resolution and alias removal"
  key_links:
    - from: "load_config layer 3.5 (project_dir-relative resolution)"
      to: "DetectionConfig.weights_path and PoseConfig.weights_path"
      via: "resolve relative to project_dir when not absolute"
      pattern: "weights_path"
---

<objective>
Consolidate model-weights path resolution to ONE convention (QA-03) and perform
the pre-1.0 clean break on the legacy alias (D-04).

Per D-03: relative weights-path values resolve relative to `project_dir`;
absolute paths are honored as-is; this applies to BOTH the detection weights
field (`detection.weights_path`) and the pose/keypoint weights field
(`pose.weights_path`). Per D-04: REMOVE the `model_path` -> `weights_path` entry
from the `_RENAME_HINTS` alias map in `src/aquapose/engine/config.py` (~line 597)
— there is no external user base, so `model_path` becomes a plain strict-reject
unknown field.

Per GUIDEBOOK §11, path resolution belongs at the CLI/entrypoint parse layer
(the `load_config` layer-3.5 block at ~line 733), not inside stages. The existing
block already resolves `det_kwargs["weights_path"]` and `pose_kwargs["weights_path"]`
relative to `project_dir` — verify this is the single convention and that BOTH the
detection and midline/keypoint (pose) backends consume it after the alias removal.

Purpose: A trustworthy single path convention so downstream doc/tutorial phases
and the final green suite validate against unified behavior.
Output: Alias removed, resolution verified unified for both backends, tests updated.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/109-correctness-green-test-suite-config-consolidation/109-CONTEXT.md
@src/aquapose/engine/config.py
@tests/unit/engine/test_config.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Remove the model_path alias and confirm the single project_dir-relative convention</name>
  <read_first>
    - src/aquapose/engine/config.py (the _RENAME_HINTS map at line ~591-600 containing "model_path": "weights_path"; the layer-3.5 project_dir resolution block at lines ~733-753 that resolves det_kwargs/pose_kwargs weights_path; the DetectionConfig.weights_path field at line 63 and PoseConfig.weights_path field at line 111)
    - .planning/GUIDEBOOK.md §11 (Configuration System — defaults -> YAML -> CLI -> freeze precedence; path resolution belongs at the CLI/entrypoint parse layer, NOT inside stages)
    - .planning/phases/109-correctness-green-test-suite-config-consolidation/109-CONTEXT.md (D-03 relative-to-project_dir convention, D-04 remove the alias)
  </read_first>
  <action>
    Delete the `"model_path": "weights_path"` entry from the _RENAME_HINTS dict in src/aquapose/engine/config.py (~line 597) so model_path is no longer a recognized rename hint — a config passing model_path now raises the standard strict-reject "unknown field 'model_path'" ValueError from _filter_fields. Confirm the layer-3.5 resolution block (~lines 737-753) is the single place resolving relative weights_path against project_dir for BOTH det_kwargs and pose_kwargs, and that absolute paths (Path(val).is_absolute()) are left untouched. Do NOT add per-stage resolution inside DetectionConfig/PoseConfig or the backends (GUIDEBOOK §11 keeps resolution at the entrypoint layer). Do not rename the weights_path fields; QA-03's field names in CONTEXT refer to the config sections (detection weights vs keypoint/pose weights), which are already unified on weights_path. Preserve type hints and Google-style docstrings on any touched function.
  </action>
  <acceptance_criteria>
    - `grep -c '"model_path": "weights_path"' src/aquapose/engine/config.py` returns 0 (alias removed).
    - The layer-3.5 block still resolves both det_kwargs["weights_path"] and pose_kwargs["weights_path"] relative to project_dir only when `not Path(val).is_absolute()`.
    - No weights-path resolution logic was added inside DetectionConfig, PoseConfig, the detection backend, or the pose backend.
  </acceptance_criteria>
  <done>The alias is gone and the single project_dir-relative resolution convention at the entrypoint layer is confirmed to serve both weights fields.</done>
</task>

<task type="auto">
  <name>Task 2: Update/extend config tests for unified resolution and alias removal</name>
  <read_first>
    - tests/unit/engine/test_config.py (existing tests covering load_config, project_dir resolution, and any test asserting the model_path -> weights_path rename hint)
    - src/aquapose/engine/config.py (the modified _filter_fields error message and the layer-3.5 resolution block)
  </read_first>
  <action>
    Find any existing test that asserts the model_path rename hint text ("did you mean 'weights_path'?") and update it to assert model_path is now rejected as a plain unknown field (the ValueError message no longer contains the "did you mean" hint for model_path). Add or strengthen a test proving: (a) a relative detection.weights_path resolves to project_dir / value; (b) a relative pose.weights_path resolves to project_dir / value; (c) an absolute weights_path is returned unchanged. Reuse the existing test project_dir setup pattern in the file. Do NOT weaken any assertion merely to make it pass — if an existing test encodes the removed alias behavior, replace it with the new strict-reject expectation, not a skip.
  </action>
  <acceptance_criteria>
    - `hatch run test tests/unit/engine/test_config.py` passes (via `python -m hatch run test` if needed), including the new/updated relative-resolution and alias-removal assertions.
    - A test asserts a relative detection.weights_path and a relative pose.weights_path each resolve to `project_dir / value`, and an absolute weights_path is unchanged.
    - No `@pytest.mark.skip`/`xfail` was added to reach green.
  </acceptance_criteria>
  <done>Config tests encode the unified project_dir-relative convention and the strict rejection of the removed model_path alias.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| YAML/CLI config -> load_config | Config path strings enter here; existing strict-field validation applies. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-109-03 | Tampering | project_dir-relative path resolution | accept | Resolution only joins a relative value to project_dir or honors an absolute path — same behavior class the removed alias had; no new traversal capability introduced beyond existing behavior. Internal config only, no untrusted network input. |
</threat_model>

<verification>
- `grep -c '"model_path": "weights_path"' src/aquapose/engine/config.py` returns 0.
- `hatch run test tests/unit/engine/test_config.py` passes with the new unified-resolution assertions.
- Both detection and pose weights fields resolve via the single layer-3.5 convention.
</verification>

<success_criteria>
QA-03 satisfied: detection and keypoint/pose weights-path fields resolve via one
convention relative to project_dir (absolute honored as-is), the legacy
model_path alias is removed, and config tests lock in the behavior.
</success_criteria>

<output>
Create `.planning/phases/109-correctness-green-test-suite-config-consolidation/109-03-SUMMARY.md` when done. Note the alias removal and the confirmed single resolution point.
</output>
