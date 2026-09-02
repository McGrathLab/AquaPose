---
phase: 112-config-cli-reference
verified: 2026-09-01T00:00:00Z
status: passed
score: 9/9 must-haves verified
overrides_applied: 0
---

# Phase 112: Config & CLI Reference — Verification Report

**Phase Goal:** A user can look up any CLI command or config field and understand its purpose, arguments, and effect without reading source
**Verified:** 2026-09-01
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The docs env can import and register the sphinx-click extension | VERIFIED | `sphinx_click.ext` present in `docs/conf.py` extensions list; `pyproject.toml` docs dependencies contain `sphinx-click`; build log shows `[extensions changed ('sphinx_click.ext')] 23 added` |
| 2 | sphinx-build imports aquapose.cli:cli cleanly under mocked imports (no unmocked-import warning under -W) | VERIFIED | `hatch run docs:build` exits 0 with zero warnings; no `WARNING.*import` or `No module named` messages in build log |
| 3 | A user can look up every CLI command group (run/init/eval/eval-compare/tune/viz/stitch/smooth-z plus data/train/prep/pseudo-label/reid) with its purpose and arguments without reading source | VERIFIED | `docs/reference/cli.rst` contains `.. click:: aquapose.cli:cli` with `:nested: full` — all 13 command entry points are auto-rendered from Click definitions; confirmed by successful docs build |
| 4 | Each documented command group carries a hand-authored worked example using generic placeholder paths | VERIFIED | 13 `.. code-block:: bash` blocks present, all using `aquapose -p myproject ...` style; all 5 critical review issues (CR-01 through CR-05) fixed in commit c45877c: `data import` now uses `--source manual --input-dir`, `data exclude` uses `--ids`, `data status` has no `--store`, `tune` includes `--stage`, `train compare` includes `--model-type` |
| 5 | The top-level --project/-p option is rendered as a global option before the subcommand | VERIFIED | Intro paragraph in `cli.rst` explicitly states `--project / -p` is a top-level argument placed before the subcommand; `sphinx-click` renders it as a global option at the `cli` group level via `:nested: full` |
| 6 | A user can look up any config field — its type, default, and effect — without reading source | VERIFIED | `docs/reference/config.md` contains all 86 leaf fields across all 10 dataclasses; the Task 2 coverage script confirmed `LEAF_FIELDS 86 / MISSING []`; field defaults cross-checked against source and found accurate (e.g., `max_match_distance=75.0`, `eviction_reproj_threshold=0.02`, `keypoint_confidence_floor=0.2` all match field values in `config.py`) |
| 7 | The reference is tiered: an Essential flat table (the fields aquapose init scaffolds) and an Advanced per-stage section | VERIFIED | `config.md` contains an Essential section (9-row flat table: `project_dir`, `video_dir`, `calibration_path`, `output_dir`, `n_animals`, `detection.detector_kind`, `detection.weights_path`, `pose.weights_path`, `mode`) and an Advanced section with per-stage subsections (Detection, Pose, Tracking, Association, Reconstruction+ZDenoising, LUT, Synthetic, ReID, PipelineConfig) |
| 8 | Every leaf config field across all 10 dataclasses (PipelineConfig + 9 stage/reid configs) is covered | VERIFIED | Source confirms 86 leaf fields (TrackingConfig has 14, not the 13 from PATTERNS.md — all 14 documented); coverage script asserted no missing field names |
| 9 | A new top-level Reference section appears in the docs sidebar, wired into docs/index.md toctree above API Reference, with Phase 110 api/cli.rst and api/engine.rst cross-linked | VERIFIED | `docs/reference/index.md` exists with two grid-item-cards and hidden toctree; `docs/index.md` has Reference card and `reference/index` entry above `api/index`; `docs/api/cli.rst` has `:doc:` cross-ref to `../reference/cli`; `docs/api/engine.rst` has `:doc:` cross-ref to `../reference/config`; automodule blocks on both API pages unchanged |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | sphinx-click in docs env dependencies | VERIFIED | Line 95: `"sphinx-click"` present in `[tool.hatch.envs.docs].dependencies` |
| `docs/conf.py` | `sphinx_click.ext` in extensions list | VERIFIED | Line 56: `"sphinx_click.ext"` present in `extensions` list after `"sphinxcontrib.mermaid"` |
| `docs/reference/cli.rst` | Auto-rendered CLI reference with worked examples | VERIFIED | File exists, 185 lines, contains `.. click:: aquapose.cli:cli`, `:prog: aquapose`, `:nested: full`, 13 code-block examples; all 5 critical review fixes applied (c45877c) |
| `docs/reference/config.md` | Tiered config reference — Essential table + Advanced subsections | VERIFIED | File exists, 217 lines, contains Essential section with 9-field flat table, Advanced section with 9 per-stage subsections, loading-precedence intro, cross-reference to `../api/engine.rst` |
| `docs/reference/index.md` | Reference landing page with grid cards and hidden toctree | VERIFIED | File exists, contains `# Reference` title, two grid-item-cards (CLI Reference, Config Reference), hidden toctree listing `cli` and `config` |
| `docs/index.md` | Reference grid-card and toctree entry above api/index | VERIFIED | Contains Reference grid-item-card with `:link: reference/index` and `reference/index` toctree entry placed above `api/index` |
| `docs/api/cli.rst` | Reciprocal cross-link to reference/cli; automodule blocks intact | VERIFIED | Line 4: `For the command-line usage reference, see :doc:`../reference/cli`.`; all three automodule blocks unchanged |
| `docs/api/engine.rst` | Reciprocal cross-link to reference/config; automodule blocks intact | VERIFIED | Line 4: `For the tiered configuration-field reference, see :doc:`../reference/config`.`; all automodule blocks unchanged |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `docs/conf.py` | `aquapose.cli:cli` | `autodoc_mock_imports` covers CLI import graph | VERIFIED | Cross-read confirmed: all third-party imports reachable from `aquapose.cli:cli` (click, yaml, cv2, numpy, torch, timm, etc.) are in `autodoc_mock_imports`; build exits 0 with no import warnings |
| `docs/reference/cli.rst` | `aquapose.cli:cli` | `.. click:: aquapose.cli:cli` with `:nested: full` | VERIFIED | Directive present; sphinx-click renders all command groups at build time; build succeeded |
| `docs/reference/cli.rst` | `docs/api/cli` | `:doc:` cross-reference | VERIFIED | `See also: :doc:`API module reference <../api/cli>`` present |
| `docs/index.md` | `docs/reference/index.md` | grid-item-card + hidden toctree entry | VERIFIED | Card with `:link: reference/index` and toctree entry `reference/index` both present |
| `docs/reference/index.md` | `docs/reference/cli.rst` and `docs/reference/config.md` | hidden toctree listing `cli` and `config` | VERIFIED | Toctree contains `cli` and `config` entries |
| `docs/api/cli.rst` | `docs/reference/cli.rst` | `:doc:` cross-reference | VERIFIED | Commit 259c446 added cross-ref; build resolves it cleanly |
| `docs/reference/config.md` | `docs/api/engine.rst` | cross-reference link | VERIFIED | `[engine module reference](../api/engine.rst)` present in config.md intro |

### Data-Flow Trace (Level 4)

Not applicable — documentation-only phase. No dynamic data rendering.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `sphinx-build -W --keep-going` exits 0 with zero warnings | `hatch run docs:build` | `build succeeded.` with no warnings emitted | PASS |
| sphinx-click renders CLI groups from the Click definitions | Inspected build output | 23 pages added per build log; CLI Reference page generated | PASS |

### Probe Execution

No phase-declared probes. The build gate (`hatch run docs:build`) serves as the primary integration probe and was run live during verification: exit 0, zero warnings.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DOCS-05 | 112-01, 112-02, 112-04 | Every CLI command group documented with purpose, arguments, and a worked example | SATISFIED | `docs/reference/cli.rst` auto-renders all groups via `sphinx-click`; 13 worked examples present and correct post-CR-01..05 fixes |
| DOCS-06 | 112-03, 112-04 | Every config field documented with type, default, and effect, tiered | SATISFIED | `docs/reference/config.md` covers all 86 leaf fields in Essential + Advanced tiers; coverage script confirmed zero missing fields |

No orphaned requirements: REQUIREMENTS.md maps DOCS-05 and DOCS-06 to Phase 112 (both marked Complete). No additional phase-112 requirements appear in REQUIREMENTS.md that were unclaimed by a plan.

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `docs/reference/cli.rst` (pre-c45877c) | 5 worked examples with wrong/missing flags | Resolved | Fixed in commit c45877c — CR-01 through CR-05 all addressed |
| `docs/reference/cli.rst` | WR-01: `viz` example shows only bare form, no flag examples | Info | Non-blocking; command works; decided not fixed post-review |
| `docs/reference/cli.rst` | WR-03: `init` example omits note about `n_animals: SET_ME` sentinel | Info | Non-blocking; config.md documents the `0` sentinel; the scaffold writes `SET_ME` which leads to a `TypeError` rather than the documented `ValueError` — minor doc gap |
| `docs/reference/config.md` | IN-01: `iou_threshold` not noted as invalid under `tracking:` YAML | Info | Non-blocking; field is correctly documented under `detection:` |

No TBD/FIXME/XXX markers found in any phase-modified file. No stubs, no placeholder content, no empty implementations.

**Decision D-03 honored:** No automated drift-guard test was added. This was explicitly declined by the user and is not flagged as a gap.

**Decision D-13 honored:** `docs/api/cli.rst` and `docs/api/engine.rst` were kept with automodule blocks intact; only one-line cross-references were added.

### Human Verification Required

No items require human verification. All observable truths are verifiable from the codebase. The build gate provides end-to-end integration confirmation. Visual/rendering quality of the Sphinx-rendered HTML is informational.

### Gaps Summary

No gaps. All 9 must-haves verified. Both DOCS-05 and DOCS-06 are satisfied. The build gate passes. The 5 critical CLI example errors from the code review (CR-01 through CR-05) were all resolved in commit c45877c before this verification. The 3 remaining warnings (WR-01, WR-03, IN-01) are non-blocking and do not prevent the phase goal from being achieved — a user can look up any CLI command or config field and understand its purpose, arguments, and effect without reading source.

---

_Verified: 2026-09-01_
_Verifier: Claude (gsd-verifier)_
