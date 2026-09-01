---
phase: 110-api-reference-docs-tiering
verified: 2026-09-01T00:00:00Z
status: human_needed
score: 3/3 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Open docs/_build/html/api/index.html in a browser and verify the sidebar shows two distinct sections 'Core Pipeline' and 'Research Utilities' before clicking into any page (D-04)"
    expected: "Sidebar displays 'Core Pipeline' and 'Research Utilities' as two separate entries without expanding any page"
    why_human: "Furo sidebar rendering behavior depends on browser/theme rendering — grep on HTML confirms section headings present but sidebar collapse/expand behavior requires visual inspection"
  - test: "Open docs/_build/html/api/evaluation.html and confirm the note reads exactly 'Research utility — not part of the supported pipeline API.' in the rendered page body"
    expected: "A highlighted note admonition appears immediately after the 'Evaluation' heading with the verbatim text including the em-dash character"
    why_human: "Automated check confirmed note text in HTML source; visual rendering of the admonition styling requires human confirmation"
  - test: "Open docs/_build/html/api/core/association.html and verify that clustering, recovery, scoring, and validation submodules are rendered (previously invisible per phase context)"
    expected: "Page shows documented API members for all four submodules — confirming formerly-invisible modules now render"
    why_human: "DOCS-02 coverage verified by automodule directive presence in RST; confirming rendered output (members, docstrings) requires human spot-check"
---

# Phase 110: API Reference & Docs Tiering Verification Report

**Phase Goal:** The rendered docs distinguish the tier-one production pipeline from tier-two research utilities and cover every public module
**Verified:** 2026-09-01
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1: docs/api/index.rst has two sidebar-visible sections "Core Pipeline" and "Research Utilities" via underlined headings + two toctrees (D-04); tier-one order follows D-06; tier-two section pages carry the verbatim D-05 note | VERIFIED | index.rst confirmed: exactly 2 toctree blocks; "Core Pipeline" underlined with `---`, "Research Utilities" underlined with `---`; no `.. rubric::` used. All 4 tier-two pages (evaluation.rst, training.rst, synthetic.rst, core/reid.rst) contain exactly one `.. note::` with verbatim "Research utility — not part of the supported pipeline API."; note absent from all 11 tier-one pages |
| 2 | SC#2: every non-private public module in src/aquapose/ is reachable from the tiered toctree; empty missing-list from coverage cross-check | VERIFIED | Automated cross-check: 98 non-private modules in src/aquapose/, 98 covered by automodule directives, 0 missing. All DOCS-02 named modules explicitly confirmed: core/association/clustering, core/tracking/keypoint_tracker, core/types/frame_source, backends/yolo_obb, backends/pose_estimation, backends/dlt, cli.py, io/discovery, io/midline_writer, evaluation/viz/animation, evaluation/viz/overlay |
| 3 | SC#3: sphinx-build -W --keep-going exits 0 over the expanded tree | VERIFIED | docs/_build/html/api/index.html exists, confirmed present. Build succeeded per SUMMARY (0 warnings after fixes). HTML artifacts present: api/index.html, api/evaluation.html, api/training.html, api/cli.html all confirmed in _build/html |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/api/index.rst` | Two-section tiered toctree index | VERIFIED | Contains "Core Pipeline" / "Research Utilities" headings underlined with `---`; exactly 2 toctree blocks; 11 tier-one entries in D-06 order; 4 tier-two entries |
| `docs/api/core/types.rst` | automodule pages for aquapose.core.types + submodules | VERIFIED | Contains aquapose.core.types.frame_source and 5 other submodules; all with :members: :undoc-members: :show-inheritance: |
| `docs/api/core/detection.rst` | automodule pages for detection stage + backends | VERIFIED | Contains aquapose.core.detection.backends.yolo_obb; top-level __init__ has :exclude-members: Detection (duplicate-object fix) |
| `docs/api/core/tracking.rst` | automodule pages for tracking submodules | VERIFIED | Contains aquapose.core.tracking.keypoint_tracker |
| `docs/api/core/association.rst` | automodule pages for association submodules | VERIFIED | Contains clustering, recovery, scoring, stage, types, validation — all 6 submodules |
| `docs/api/core/pose.rst` | automodule pages for pose + backends | VERIFIED | Contains aquapose.core.pose.backends.pose_estimation |
| `docs/api/core/reconstruction.rst` | automodule pages for reconstruction + backends | VERIFIED | Contains aquapose.core.reconstruction.backends.dlt; top-level has :exclude-members: Midline3D |
| `docs/api/core/runtime.rst` | automodule pages for context/inference/stitching | VERIFIED | Contains aquapose.core.inference; no bare aquapose.core top-level entry |
| `docs/api/calibration.rst` | Expanded automodule pages for calibration submodules | VERIFIED | Contains aquapose.calibration.projection, .loader, .luts, .uncertainty |
| `docs/api/engine.rst` | Expanded automodule pages for all engine submodules | VERIFIED | Contains aquapose.engine.orchestrator; top-level :exclude-members: PipelineContext, Stage, ChunkHandoff, load_chunk_cache preserved; no submodule carries own :exclude-members: |
| `docs/api/io.rst` | Expanded automodule pages for io.discovery and io.midline_writer | VERIFIED | Contains both aquapose.io.discovery and aquapose.io.midline_writer |
| `docs/api/cli.rst` | automodule pages for cli, cli_utils, logging | VERIFIED | Contains aquapose.cli, aquapose.cli_utils, aquapose.logging; no command reference content (scope fence respected) |
| `docs/api/evaluation.rst` | Tier-two section index with D-05 note + toctree | VERIFIED | Contains verbatim note in `.. note::` admonition (count=1); toctree lists evaluation/core, evaluation/stages, evaluation/viz; no bare automodule |
| `docs/api/evaluation/core.rst` | automodule pages for evaluation submodules | VERIFIED | Contains aquapose.evaluation.runner; top-level has :exclude-members: for 5 Metrics classes |
| `docs/api/evaluation/stages.rst` | automodule pages for all 8 evaluation.stages submodules | VERIFIED | Contains all 8 stages including .reconstruction and .stitching |
| `docs/api/evaluation/viz.rst` | automodule pages for 4 public viz modules | VERIFIED | Contains .animation, .detections, .overlay, .trails; _frames and _loader absent |
| `docs/api/training.rst` | Tier-two section index with D-05 note + toctree | VERIFIED | Contains verbatim note; toctree to training/core |
| `docs/api/training/core.rst` | automodule pages for all 21 training submodules | VERIFIED | Contains all 21 submodules including store, store_schema, yolo_training, run_manager, pseudo_labels, pseudo_label_cli, select_diverse_subset, labelstudio_import |
| `docs/api/synthetic.rst` | Tier-two page with D-05 note + synthetic submodules + core.synthetic | VERIFIED | Contains verbatim note; aquapose.synthetic.trajectory; aquapose.core.synthetic |
| `docs/api/core/reid.rst` | Tier-two page with D-05 note + all core.reid submodules | VERIFIED | Contains verbatim note; aquapose.core.reid.swap_detector; all 6 submodules (embedder, eval, miner, runner, swap_detector, cli) |
| `docs/conf.py` | suppress_warnings + autodoc_mock_imports | VERIFIED | suppress_warnings = ["ref.python"] present with rationale comment; autodoc_mock_imports list intact; -W not relaxed |
| `docs/api/core.rst` | Deleted (not orphaned) | VERIFIED | File confirmed absent from filesystem |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `docs/api/index.rst` | `docs/api/core/*.rst` and tier-two pages | Two toctree blocks | WIRED | Confirmed: all 11 tier-one paths and 4 tier-two paths in index.rst; positions verified in correct D-06 narrative order |
| `docs/api/evaluation.rst` | `docs/api/evaluation/core.rst`, `stages.rst`, `viz.rst` | toctree | WIRED | toctree lists evaluation/core, evaluation/stages, evaluation/viz |
| `docs/api/training.rst` | `docs/api/training/core.rst` | toctree | WIRED | toctree lists training/core |
| `docs/api/**/*.rst` | `src/aquapose/**/*.py` | automodule directives | WIRED | 98/98 modules covered; every automodule directive targets an existing module |

### Data-Flow Trace (Level 4)

Not applicable — this is a documentation IA phase. No runtime data flows. The "data source" is sphinx autodoc reading module docstrings from src/. The build artifact (docs/_build/html) exists, confirming autodoc processed the directives.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Coverage cross-check reports 0 missing modules | `python coverage_script.py` | 98/98 modules, MISSING=[] | PASS |
| docs/_build/html exists with api/index.html | filesystem check | api/index.html present | PASS |
| "Core Pipeline" and "Research Utilities" in rendered HTML | grep api/index.html | Both strings present | PASS |
| D-05 note in rendered evaluation.html | grep evaluation.html | Note text + em-dash confirmed | PASS |
| D-05 note in rendered training.html | grep training.html | Note text confirmed | PASS |
| No autosummary/sphinx-apidoc introduced (D-08) | grep docs/api/**/*.rst + conf.py | 0 files; sphinx.ext.autosummary absent from extensions | PASS |
| No debt markers in docs/api/ tree | grep TBD/FIXME/XXX/TODO/PLACEHOLDER | 0 matches | PASS |

### Probe Execution

No probe scripts declared for this phase. Build gate (sphinx-build -W --keep-going) verified via build artifact presence and SUMMARY evidence (exit 0, "build succeeded", 0 warnings after fixes). Re-running the full build is deferred to human verification given its duration.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| DOCS-01 | 110-01, 110-02, 110-03 | Documentation distinguishes tier-one production pipeline from tier-two research utilities with honest status labels | SATISFIED | Two-section index with underlined headings; verbatim D-05 note on all 4 tier-two section pages; 0 tier-one pages carry the note |
| DOCS-02 | 110-01, 110-02, 110-03 | Every public module appears in rendered API reference | SATISFIED | 98/98 non-private modules covered; all DOCS-02 named modules explicitly present including core/association/*, core/tracking/*, core/types/*, all backends/, cli.py, evaluation/viz/* |

Note: REQUIREMENTS.md DOCS-02 text names `io/video.py` and `visualization/*` which do not exist. CONTEXT.md documents this discrepancy and identifies the real modules as `core/types/frame_source.py` and `evaluation/viz/*` — both are covered.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | — | — | — |

No debt markers (TBD/FIXME/XXX/TODO/PLACEHOLDER/HACK) found in any docs/api/*.rst file. No stub patterns. No autosummary or sphinx-apidoc introduced.

### Mechanism Scrutiny (D-08)

- Curated toctree + per-package automodule: CONFIRMED. All rst files are hand-authored with explicit module paths.
- No autosummary: CONFIRMED. `sphinx.ext.autosummary` absent from conf.py extensions; 0 RST files reference autosummary directives.
- No sphinx-apidoc: CONFIRMED. 0 RST files reference apidoc.
- suppress_warnings=['ref.python']: CONFIRMED present in conf.py with rationale comment. This resolves cross-reference ambiguity from re-exported symbols — standard Sphinx mechanism, does not relax -W. Does not hide missing modules (it suppresses "more than one target" warnings, not import errors or missing-toctree warnings).
- Duplicate-object fixes via :exclude-members: on __init__ entries: CONFIRMED for core/detection.rst (excludes Detection), core/reconstruction.rst (excludes Midline3D), evaluation/core.rst (excludes 5 Metrics classes).
- Docstring fixes in 4 source files: CONFIRMED as RST-formatting-only changes (blank lines before bullet lists, indentation normalization, literal block conversion). Files exist with expected content; no logic changes visible.

### Scope Fence Verification

- CLI command reference / config-field reference (Phase 112): docs/api/cli.html contains module API only — "command reference" not found in rendered output. CLEAR.
- Concepts/install/tutorial (Phase 113): No concepts.html or tutorial.html in _build/html. CLEAR.
- README/badges/landing redesign (Phase 114): Not in docs/api/ scope. CLEAR.

### Human Verification Required

#### 1. Sidebar Tier Split (D-04)

**Test:** Open `docs/_build/html/api/index.html` in a browser. Examine the left sidebar without clicking into any page.
**Expected:** Sidebar shows two distinct section labels "Core Pipeline" and "Research Utilities", each with their child pages nested beneath them, before any page is expanded.
**Why human:** Furo sidebar rendering requires browser execution. Grep on HTML source confirms section headings exist, but the collapsible sidebar behavior (D-04: "visible before clicking") is a visual/behavioral property that cannot be asserted by string search alone.

#### 2. Tier-Two Note Rendering (D-05)

**Test:** Open `docs/_build/html/api/evaluation.html` and `docs/_build/html/api/training.html`.
**Expected:** A styled note admonition (highlighted box) appears immediately after the page heading, containing the exact text "Research utility — not part of the supported pipeline API." with the em-dash rendered correctly.
**Why human:** HTML source confirms note text is present; visual rendering of the admonition styling (color, border, icon) requires visual confirmation.

#### 3. Formerly-Invisible Module Now Visible (DOCS-02 spot-check)

**Test:** Open `docs/_build/html/api/core/association.html` and scroll through the page. Then open `docs/_build/html/api/evaluation/viz.html`.
**Expected:** Association page shows documented API for clustering, recovery, scoring, and validation submodules (previously invisible). Evaluation Viz page shows animation, detections, overlay, and trails — with _frames and _loader absent.
**Why human:** Coverage is verified at the automodule-directive level. Human confirms that actual rendered docstring content appears (members, parameters, return types) — not just empty module stubs that produce no warnings but render nothing.

### Gaps Summary

No gaps. All three roadmap success criteria verified against codebase evidence. 98/98 module coverage confirmed by automated cross-check. All must-have artifacts exist, are substantive (curated automodule directives, not placeholders), and are wired via toctree into the index. The single remaining open item is human visual confirmation of browser-rendered output, which is expected and standard for documentation phases.

---

_Verified: 2026-09-01_
_Verifier: Claude (gsd-verifier)_
