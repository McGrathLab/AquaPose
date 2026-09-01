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

<baseline_diagnosis>
## ⚠ Baseline Diagnosis (2026-09-01) — SUPERSEDES the "8 failures / failing LUT" premise

The suite was run for real on a fresh Python-3.12 hatch env (torch 2.5.1+cu121,
numpy 2.5.2, pytest 9.1.1, ultralytics 8.4.137, GPU: GTX 1660 SUPER). Actual
`hatch run test-all`: **23 failed, 1287 passed, 5 skipped** (the 5 skips are
`tests/e2e/test_smoke.py`, correctly marker-skipped). This differs sharply from
STATE-108's estimate of 8 — that was the **Linux/CI** baseline; the extra failures
are **Windows-specific**.

**QA-01 is already GREEN.** `test_luts.py::test_forward_lut_cast_ray_matches_model`
PASSES on this env (not failed, not skipped) — no LUT/tolerance drift reproduces.
QA-01 becomes **confirm reliably green + record why STATE-108 believed it failed**
(env/precision, or already fixed in Phase 108), NOT diagnose-and-fix. Still honors
"resolved, not skipped" because it genuinely passes.

**The 23 failures cluster into 6 root causes (not "7 stale fixtures"):**

| Cluster | # | Root cause | CI impact |
|---|---|---|---|
| Symlink privilege (WinError 1314 / OSError 22) | 14 | `store.assemble()` `symlink_to()` (store.py:755-756); Windows lacks SeCreateSymbolicLinkPrivilege | Real Windows **hot-path** break — `data assemble` CLI dies. GitHub runner may hold the privilege (CI may pass) but real Windows-no-DevMode users break. |
| Path separator `\` vs `/` | 2 | `run_manager` writes `weights_path` as `\new\best.pt`; expected `/new/best.pt` | Fails Windows CI cell. On QA-03 surface. |
| cp1252 encoding | 1 | `test_viz` `out_path.read_text()` uses Windows default cp1252 on UTF-8/binary content | Fails Windows CI cell. QA-04-aligned. |
| Ordering | 1 | `test_store.py::test_list_models_returns_all` expects `run_b`, got `run_a` | Possibly both cells — classify stale vs real. |
| timm Swin input size | 2 | re-ID backbone: 32px fed to a 224 model → timm `_assert(H==img_size)` | `@pytest.mark.slow` → only slow-tests (any OS). |
| CLI `--val-split` help | 3 | `train obb/seg/pose --help` no longer contains `--val-split` | Fails **both** CI cells (platform-independent). STATE-108's "stale CLI-help". |

**CI reality:** `test.yml` matrix = {ubuntu, windows} × {3.11, 3.12, 3.13}, runs
`hatch run test` (NOT slow). `slow-tests.yml` runs `test-all` (manual, default ubuntu).
The 3 CLI-flag failures are platform-independent + not-slow → they fail every per-push
cell now (dev CI is red). Path-sep/encoding fail the Windows cells. The timm failures
only appear in slow-tests. **"Honest green" target = all CI cells green.**

**Local:** Windows Developer Mode is OFF on the dev machine → enable it so the suite is
runnable locally regardless of the code fix (independent of D-09).
</baseline_diagnosis>

<decisions>
## Implementation Decisions

> **NOTE (2026-09-01):** D-01 and D-02 below are **superseded by the Baseline
> Diagnosis above**. QA-01 is already green (confirm, don't diagnose-fix). QA-02 is
> 23 failures across 6 clusters — see the new decisions **D-07…D-11**, not "7 stale
> fixtures." Original D-01/D-02 text retained for provenance.

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

### Platform correctness (added 2026-09-01 from Baseline Diagnosis)
- **D-07 (QA-03 + portability):** In `run_manager` weights-path writing, normalize the
  written `weights_path` to **forward slashes** so `detection.weights_path` /
  `midline.weights_path` are platform-neutral (fixes the `\new\best.pt` failure). Fold
  into the QA-03 config-unification work — same surface as D-03/D-04.
- **D-08 (QA-04 portability):** The `read_text()` behind
  `test_viz.py::test_prefers_stitched_h5` must pass **`encoding="utf-8"`** (never rely on
  the OS default / cp1252). Audit sibling `read_text`/`write_text` on user-facing paths
  for the same latent bug while in the file.
- **D-09 (QA-04 hot-path robustness — Option A, user-confirmed 2026-09-01):** Make
  `store.assemble()` resilient to missing symlink privilege: try `symlink_to` → on
  privilege `OSError` fall back to **hardlink** (`os.link`, same-volume, no data
  duplication) → fall back to **copy** (`shutil.copy2`) only if cross-volume. Fixes the
  14 failures AND unblocks real Windows `data assemble` usage (store.py:755-756 is the
  only symlink site in `src/`). Update `test_symlinks_are_relative` semantics to "symlink
  when privileged, else a valid hardlink/copy" rather than asserting a hard symlink.
- **D-10 (QA-02 timm, slow):** Resolve the re-ID Swin input-size mismatch (32px vs 224).
  Per D-02, first classify: is the fixture's 32px input wrong (should be 224), does the
  backbone need `dynamic_img_size`, or is it a timm-version behavior change? Fix the real
  cause. Gates slow-tests green.
- **D-11 (QA-02 CLI flag):** For the 3 `--val-split` help-assertion failures, determine
  whether the flag was renamed/removed (→ update the stale assertions to the real CLI) or
  genuinely dropped (→ restore it). One-line root-cause note per test (D-02 discipline).

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
