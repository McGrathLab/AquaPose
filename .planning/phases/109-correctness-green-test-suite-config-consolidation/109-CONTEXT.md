# Phase 109: Correctness — Green Test Suite & Config Consolidation - Context

**Gathered:** 2026-09-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Make `hatch run test-all` fully green and unify how model-weights/config paths
resolve, so the downstream documentation and publication phases build on a
trustworthy, honest baseline.

Delivers requirements QA-01 through QA-04:
- QA-01: tier-one `test_luts.py::test_forward_lut_cast_ray_matches_model` passes (resolved, not skipped)
- QA-02: the 7 tier-two failures in `training/` and `evaluation/` pass, making the coverage badge honest
- QA-03: `keypoint_weights_path` and `detection.model_path` resolve via one convention relative to `project_dir`
- QA-04: the tutorial config uses relative, platform-neutral paths and runs unmodified on Linux, macOS, and Windows

**Not in this phase:** architectural refactors (LUT relocation), doc/narrative
authoring (Phases 110–113), and the example-dataset path convention (Phase 111).
</domain>

<decisions>
## Implementation Decisions

### Tier-one LUT test (QA-01)
- **D-01:** No prior on root cause. The planner/executor must **diagnose first**
  whether the forward-LUT code (`generate_forward_lut` / `LUT.cast_ray`) drifted
  from `model.cast_ray`, or whether the `1e-4 m` / `0.01°` tolerances are stale —
  then fix the actual cause. The failure must be **resolved, not skipped** (QA-01
  is explicit). Do not weaken the tolerance just to pass; only adjust tolerances
  if diagnosis shows the contract legitimately changed.

### Tier-two failures (QA-02)
- **D-02:** Default stance: **assume the code is correct and update the stale
  assertions/fixtures** (STATE-108 diagnosed these as stale CLI-help assertions
  and `training/` / `evaluation/` fixtures). BUT the executor must **flag any
  failure that looks like a genuine regression** rather than blindly rewriting
  the test to match current behavior. A one-line root-cause note per fixed test
  is expected.

### Config path convention (QA-03)
- **D-03:** Canonical convention: **model-weights paths resolve relative to
  `project_dir`** when given as relative paths; absolute paths are honored as-is.
  Applies to both `keypoint_weights_path` and `detection.model_path`. This matches
  the existing project-aware CLI model and is the least-surprising choice.
- **D-04:** **Remove** the `model_path` → `weights_path` back-compat alias in
  `config.py` (a pre-1.0 clean break — no external user base yet). Configs must
  use the canonical field name after this phase.

### Tutorial config (QA-04)
- **D-05:** Scope is **fix the existing tutorial config only** — make its paths
  relative and platform-neutral so it runs unmodified across Linux/macOS/Windows.
  Defining the path convention the Phase 111 example dataset will inherit is
  **out of scope** for 109 (keeps this phase correctness-scoped, avoids coupling
  109 to 111).

### Repo hygiene — stale URLs (opportunistic, beyond QA scope)
- **D-06:** Fix the **3 `tlancaster6/AquaPose` URLs in `pyproject.toml`** in this
  phase (Homepage/Repository/Issues — they ship in PyPI metadata for the dev
  releases this baseline supports). Leave the remaining stale URLs
  (`CODE_OF_CONDUCT.md`, `docs/contributing.md`, ~829 historical `CHANGELOG.md`
  links) for the **Phase 114** publication polish. See STATE-108 for provenance.

### Folded Todos
- **Regenerate golden regression test data for v2.1** (`testing`): folded
  **conditionally** — regenerate golden/reference data **only when fixing a
  specific failing test actually depends on it**, and record why. Do NOT
  wholesale-regenerate (that would risk masking real regressions the tier-two
  work is meant to catch).
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — QA-01…QA-04 acceptance criteria (lines 26–29) and traceability table
- `.planning/ROADMAP.md` — Phase 109 section: goal, dependencies (Phase 108), success criteria
- `.planning/STATE.md` — Phase 108 blockers/concerns: diagnosis of the 8 failing tests and the stale-URL inventory

### Architecture / conventions
- `.planning/GUIDEBOOK.md` §11 (Configuration System) — frozen-dataclass config hierarchy, `defaults → YAML → CLI → freeze` precedence; the convention QA-03 must honor
- `.planning/GUIDEBOOK.md` §12 (Error Handling) — fail-fast default (context for why the suite must be honest-green)

### Code touchpoints
- `tests/unit/calibration/test_luts.py` — `test_forward_lut_cast_ray_matches_model` (line 121); asserts LUT `cast_ray()` vs `model.cast_ray()` within `1e-4 m` / `0.01°`
- `src/aquapose/engine/config.py` — path-field resolution + the `model_path` → `weights_path` alias (line ~597) to be removed
- `pyproject.toml` — 3 stale `tlancaster6` URLs (Homepage/Repository/Issues)
- `tests/unit/training/` and `tests/unit/engine/` — homes of the tier-two CLI-help / fixture failures

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/aquapose/engine/config.py`: already centralizes config-field resolution and
  carries the legacy alias map — the natural single place to enforce the QA-03
  convention and delete the alias.
- `make_test_model()` in `tests/unit/calibration/test_luts.py`: seeded, deterministic
  fixture used by the tier-one test — reuse for any diagnosis harness.

### Established Patterns
- Project-aware CLI (`--project` / `project_dir`) per GUIDEBOOK §14 — the QA-03
  "relative to `project_dir`" convention aligns with this existing pattern.
- Frozen-config precedence (GUIDEBOOK §11): path resolution belongs at the
  CLI/entrypoint parse layer, not inside stages.

### Integration Points
- Config path resolution feeds detection and midline (keypoint) backends — verify
  both consume the unified convention after the alias removal.

</code_context>

<specifics>
## Specific Ideas

- "Resolved, not skipped" is a hard constraint on QA-01 — no `@pytest.mark.skip`
  or `xfail` as a shortcut.
- "Honest coverage badge" is the intent behind QA-02 — the badge must reflect a
  genuinely green suite, not a suite with quarantined failures.

</specifics>

<deferred>
## Deferred Ideas

- **LUT generation → pre-pipeline setup** (from folded todo, then deferred): this
  is an architectural refactor, not correctness work. Keep 109 correctness-only;
  revisit as its own task/phase. Only touch LUT placement if the tier-one fix
  makes it strictly unavoidable (it should not).
- **Example-dataset path convention** → Phase 111.
- **Remaining stale `tlancaster6` URLs** (`CODE_OF_CONDUCT.md`, `docs/contributing.md`,
  ~829 `CHANGELOG.md` links) → Phase 114 publication polish.

### Reviewed Todos (not folded)
- **Move LUT generation to pre-pipeline setup** (`calibration`) — architectural
  refactor; deferred to keep 109 correctness-scoped (see D above).
- Training/reconstruction feature todos surfaced by keyword match (frame-selection
  wiring, on-the-fly augmentation, hard-case mining, direct keypoint triangulation,
  active-frame reconstruction loop) — all belong to other milestones/phases; not
  in 109 scope.

</deferred>

---

*Phase: 109-correctness-green-test-suite-config-consolidation*
*Context gathered: 2026-09-01*
