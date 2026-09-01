---
phase: 109-correctness-green-test-suite-config-consolidation
plan: 04
type: execute
wave: 2
depends_on: ["03"]
files_modified:
  - src/aquapose/cli.py
  - tests/unit/engine/test_cli.py
  - pyproject.toml
autonomous: true
requirements: [QA-04]

must_haves:
  truths:
    - "The starter/tutorial config produced by `aquapose init` uses only relative, platform-neutral paths (no absolute or home-expanded path baked into path fields)"
    - "The generated config would run unmodified on Linux, macOS, and Windows (no OS-specific separators or drive letters serialized into it)"
    - "pyproject.toml [project.urls] contains no tlancaster6 references — Homepage, Repository, and Issues point at the current McGrathLab/AquaPose repo"
  artifacts:
    - path: "src/aquapose/cli.py"
      provides: "init_cmd scaffold that writes a platform-neutral relative-path config.yaml"
      contains: "init_cmd"
    - path: "pyproject.toml"
      provides: "Corrected project URLs shipped in PyPI metadata"
      contains: "[project.urls]"
  key_links:
    - from: "init_cmd config scaffold"
      to: "load_config project_dir resolution"
      via: "relative path fields resolved at load time, project_dir supplied by CLI"
      pattern: "weights_path"
---

<objective>
Make the existing tutorial/starter config platform-neutral (QA-04) and fix the
3 stale tlancaster6 URLs in pyproject.toml (D-06, opportunistic hygiene).

The "existing tutorial config" is the `config.yaml` scaffold emitted by
`aquapose init` (`init_cmd` in `src/aquapose/cli.py`, ~lines 155-210). Its
weights-path and directory fields are already relative (`videos`,
`geometry/calibration.json`, `runs`, `models/yolo_obb.pt`, `models/yolo_pose.pt`),
but `project_dir` is serialized as an absolute, home-expanded, OS-specific path
(`str(Path("~/aquapose/projects").expanduser() / name)`), which is neither
relative nor platform-neutral and would not run unmodified across OSes.

Per D-05, scope is FIX THE EXISTING TUTORIAL CONFIG ONLY — do NOT define the
Phase 111 example-dataset path convention. Per D-06, fix ONLY the 3 pyproject.toml
URLs (Homepage/Repository/Issues); leave CODE_OF_CONDUCT.md, docs/contributing.md,
and CHANGELOG.md links for Phase 114.

This plan depends on Plan 03 (which also edits cli.py's config resolution surface
and removes the model_path alias) so the scaffold is made platform-neutral against
the finalized single path convention.

Purpose: A tutorial config a new user can run unmodified on any OS, plus correct
PyPI metadata for dev releases.
Output: Platform-neutral init scaffold, corrected URLs, a test asserting neutrality.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/109-correctness-green-test-suite-config-consolidation/109-CONTEXT.md
@src/aquapose/cli.py
@pyproject.toml
</context>

<tasks>

<task type="auto">
  <name>Task 1: Make the init_cmd tutorial config platform-neutral and relative</name>
  <read_first>
    - src/aquapose/cli.py (init_cmd, lines ~155-214 — the data dict it builds: project_dir set to str(project_dir) absolute; video_dir="videos"; calibration_path="geometry/calibration.json"; output_dir="runs"; detection.weights_path="models/yolo_obb.pt"; pose.weights_path="models/yolo_pose.pt"; and the yaml.dump write to project_dir/config.yaml)
    - src/aquapose/engine/config.py (load_config layer-3.5: relative video_dir/calibration_path/output_dir/weights_path are resolved against project_dir at load time — confirm relative values in the scaffold resolve correctly given the CLI already knows project_dir)
    - src/aquapose/cli_utils.py (get_project_dir / project-aware CLI — how project_dir is discovered at run time so it need not be baked into the config)
    - .planning/GUIDEBOOK.md §11 (path resolution at the entrypoint layer) and §14 (project-aware CLI --project/project_dir)
  </read_first>
  <action>
    Remove the absolute/home-expanded project_dir value from the serialized config.yaml so no OS-specific path (drive letter, backslashes, or an expanded home path) is written into any path field. Either omit project_dir from the emitted YAML entirely (letting the project-aware CLI supply project_dir at run time via --project / upward config.yaml discovery in cli_utils), or serialize it as a relative/neutral marker consistent with how load_config and get_project_dir supply project_dir — whichever keeps the generated config runnable unmodified on Linux, macOS, and Windows. Keep all other path fields as the existing forward-slash relative values (videos, geometry/calibration.json, runs, models/yolo_obb.pt, models/yolo_pose.pt) — forward slashes are platform-neutral and load_config resolves them against project_dir. Do NOT introduce the Phase 111 example-dataset path convention (D-05 out of scope). Preserve the n_animals="SET_ME" sentinel, the header comment, and the keypoint_t_values reminder comment. Preserve type hints and Google-style docstring on init_cmd.
  </action>
  <acceptance_criteria>
    - After running `aquapose init` (or invoking init_cmd via CliRunner), the generated config.yaml contains no absolute path, no drive letter, no backslash separators, and no home-expanded path in any field.
    - All remaining path fields (video_dir, calibration_path, output_dir, detection.weights_path, pose.weights_path) are relative with forward-slash separators.
    - The scaffold still emits n_animals sentinel, header, and the keypoint reminder comment; no Phase 111 dataset-path convention was added.
  </acceptance_criteria>
  <done>The init scaffold writes a fully relative, platform-neutral config.yaml that runs unmodified across OSes.</done>
</task>

<task type="auto">
  <name>Task 2: Add a platform-neutrality test and fix the 3 pyproject.toml URLs</name>
  <read_first>
    - tests/unit/engine/test_cli.py (existing CliRunner-based tests for init_cmd / project scaffolding — reuse the invocation and tmp-dir patterns)
    - src/aquapose/cli.py (the init_cmd changes from Task 1)
    - pyproject.toml (lines 46-50, [project.urls]: Homepage/Repository/Issues currently https://github.com/tlancaster6/aquapose ...; Documentation line is already correct and stays)
    - .planning/STATE.md (repo transferred to McGrathLab/AquaPose; the 3 pyproject URLs ship in PyPI dev-release metadata)
  </read_first>
  <action>
    Add a test (reusing the CliRunner + tmp-path pattern already in test_cli.py) that runs the init scaffold, reads the generated config.yaml text, and asserts it contains no backslash, no drive-letter pattern (a letter followed by a colon), no leading-slash absolute POSIX path in path fields, and no home-expanded segment — proving platform neutrality. In pyproject.toml [project.urls], replace the tlancaster6 owner in Homepage, Repository, and Issues with the current owner McGrathLab (Homepage/Repository -> https://github.com/McGrathLab/AquaPose, Issues -> https://github.com/McGrathLab/AquaPose/issues), matching the transferred repo in STATE. Leave the Documentation URL unchanged. Do NOT touch CODE_OF_CONDUCT.md, docs/contributing.md, or CHANGELOG.md (Phase 114 scope).
  </action>
  <acceptance_criteria>
    - `hatch run test tests/unit/engine/test_cli.py` passes, including the new platform-neutrality assertion on the generated config.yaml.
    - `grep -c 'tlancaster6' pyproject.toml` returns 0.
    - pyproject.toml [project.urls] Homepage, Repository, and Issues reference McGrathLab/AquaPose; the Documentation URL is unchanged.
    - CODE_OF_CONDUCT.md, docs/contributing.md, and CHANGELOG.md were not modified.
  </acceptance_criteria>
  <done>A test locks in tutorial-config platform neutrality and the PyPI-metadata URLs point at the current repository.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

None new. init_cmd writes a local scaffold file; pyproject.toml metadata is static.
No network endpoint, no untrusted input parsing added.

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-109-04 | Information Disclosure | Serialized project_dir in config.yaml | mitigate | Removing the absolute/home-expanded project_dir also avoids leaking a local user path into a shared/committed tutorial config; keeps paths relative. |
| T-109-04b | Tampering | Corrected project URLs | accept | Static metadata pointing at the canonical repo; no runtime trust boundary. |
</threat_model>

<verification>
- Generated config.yaml has no absolute/OS-specific path in any field.
- `grep -c 'tlancaster6' pyproject.toml` returns 0.
- `hatch run test tests/unit/engine/test_cli.py` passes with the neutrality test.
</verification>

<success_criteria>
QA-04 satisfied: the tutorial config uses only relative, platform-neutral paths
and runs unmodified on Linux/macOS/Windows. D-06 satisfied: the 3 stale
tlancaster6 URLs in pyproject.toml are corrected.
</success_criteria>

<output>
Create `.planning/phases/109-correctness-green-test-suite-config-consolidation/109-04-SUMMARY.md` when done. Note the project_dir handling change and the URL fixes.
</output>
