# Phase 110: API Reference & Docs Tiering - Context

**Gathered:** 2026-09-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Restructure the Sphinx **API reference** so it (1) visibly separates the tier-one
production pipeline from tier-two research utilities with honest status labels, and
(2) renders **every** public module. Delivers DOCS-01 and DOCS-02.

Today `docs/api/` holds 8 package-level `.rst` files that each `automodule` only the
top-level package `__init__.py` (`aquapose.core`, `aquapose.engine`, etc.). Every
submodule — `core/association/*`, `core/tracking/*`, `core/types/*`, all `backends/`
packages, `cli.py`, `io/*`, `evaluation/viz/*` — is invisible in the rendered docs.
There are 120 `.py` modules in `src/aquapose/`; roughly half never appear.

Docstring coverage is already **99.7% Google-style** — this phase is **IA/structure
work, not prose-writing**.

**In scope:** the API reference section of the docs (`docs/api/`), its tier structure,
its module coverage, and keeping the build green.

**Explicitly NOT this phase (scope fence):**
- CLI *command* reference and config-field reference → **Phase 112**
- Concepts page, install guide, tutorial → **Phase 113**
- README, badge row, hero media, docs landing redesign → **Phase 114**
- Rewriting/adding docstrings → out of scope (coverage already 99.7%)
- Enforcing an import boundary between core and research code → out of scope
  (tiering is a docs-only decision; REQUIREMENTS.md "Out of Scope")

</domain>

<decisions>
## Implementation Decisions

### Tier taxonomy & boundaries
The tier line is **"needed to run or consume the production pipeline."**

- **D-01:** Tier-one (Core Pipeline): `core/detection/*`, `core/tracking/*`,
  `core/association/*`, `core/pose/*`, `core/reconstruction/*` (all incl. their
  `backends/`), `calibration/*`, `engine/*` (including the observer implementations),
  `core/types/*` (the public data contract), `io/*` (video discovery + HDF5 writer),
  and `cli.py`. Also the loose `core/` modules that are part of the runtime path:
  `core/context.py`, `core/inference.py`, `core/stitching.py`.
- **D-02:** Tier-two (Research Utilities): `training/*`, `evaluation/*` (including
  `evaluation/viz/*` and `evaluation/stages/*`), `core/reid/*`, pseudo-labeling
  (the pseudo-label modules under `training/`), and `synthetic/*` (+ `core/synthetic.py`).
  Rationale: these are test-data generation, model training, evaluation, and post-hoc
  research tooling — not part of running/consuming the pipeline.
- **D-03:** `cli.py` appears as a tier-one **module page** to satisfy DOCS-02, but the
  human-facing CLI *command* reference is a separate deliverable in Phase 112 — do not
  build a command reference here.

### Tier presentation & status labels
- **D-04:** The API reference index splits into **two top-level sections/toctrees**:
  "Core Pipeline" (tier-one) and "Research Utilities" (tier-two). The split must be
  visible in the sidebar before the reader clicks into any page. (Chosen over
  per-page banners and over the both-sections-and-banners option.)
- **D-05:** Tier-two carries the honest status label
  **"Research utility — not part of the supported pipeline API."** Because the split
  is section-based (not per-page banners), place this as a **section-level note/admonition
  on the Research Utilities index**, not on every individual page.

### API reference structure (IA)
- **D-06:** Tier-one is ordered by the **5-stage pipeline narrative** —
  Detection → 2D Tracking → Cross-Camera Association → Pose/Midline → Reconstruction —
  with Calibration, Engine, `core/types/`, and `io/` framing it. Order follows the
  GUIDEBOOK pipeline story, not alphabetical/filesystem order. (See GUIDEBOOK §6.)
- **D-07:** **One page per package/subpackage** (e.g. a single "Association" page
  documenting all of `core/association/*` together), not one page per module.
  Split a package into multiple pages only if it is large enough to warrant it.

### Generation mechanism
- **D-08:** **Curated toctree + per-package `automodule` rst.** Hand-author a small
  curated index establishing the two tier sections and the narrative order, plus one
  `.rst` per package that `automodule`s its submodules (`:members: :undoc-members:
  :show-inheritance:`). Roughly 15–20 small rst files. **No `autosummary --recursive`
  and no `sphinx-apidoc` generation** — both were considered and rejected:
  autosummary produces per-module pages in package order (fights D-06/D-07);
  sphinx-apidoc regeneration overwrites curation and drifts (maintenance footgun for a
  published project). This extends the pattern already in `docs/api/`.

### Claude's Discretion
- Exact per-package page splits within a large package (D-07 allows sub-splitting).
- Precise rst wording/headings and how the framing modules (`calibration`, `engine`,
  `core/types`, `io`) are threaded around the stage narrative.
- Whether to keep or drop the existing `:exclude-members:` list on the engine page
  (see `docs/api/engine.rst`) once submodules are documented.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase requirements & scope
- `.planning/ROADMAP.md` — Phase 110 section (goal, 3 success criteria).
  **⚠ Discrepancy to correct:** SC#2 lists `io/video.py` and `visualization/*` as
  modules to cover — **neither exists**. Video/frame-source loading is
  `src/aquapose/core/types/frame_source.py`; visualization lives in
  `src/aquapose/evaluation/viz/`. Plan against the real tree (see module list below),
  not the SC#2 names.
- `.planning/REQUIREMENTS.md` — DOCS-01 (tiering + honest labels) and DOCS-02
  (every public module rendered); "Out of Scope" table (no import-boundary
  enforcement, no docstring rewriting).
- `.planning/seed-publication-polish.md` — milestone vision; "No narrative
  documentation" gap and the "four authored pages + seven automodule stubs" finding.

### Authoritative tier-one / pipeline definition
- `.planning/GUIDEBOOK.md` §4 (Source Layout), §6 (Pipeline Stages — the canonical
  5-stage narrative and PipelineContext data-flow table), §8 (backends vs configurable
  models), §10 (observers). This is the source of truth for D-06 ordering and the
  tier-one/tier-two conceptual split.

### Existing docs to extend (not replace)
- `docs/conf.py` — Sphinx config established/repaired by Phase 108: furo theme,
  `autodoc_typehints="description"`, `autodoc_member_order="bysource"`,
  `napoleon_use_ivar=True`, `autodoc_mock_imports` list. Any new modules that import
  new heavy deps may need additions to `autodoc_mock_imports` to keep `-W` green.
- `docs/api/index.rst` and `docs/api/*.rst` — the 8 current package-level stubs
  (`calibration, core, engine, evaluation, io, synthetic, training`) to be replaced by
  the tiered, per-package structure.
- `docs/index.md` — top-level toctree with the "API Reference" card (links to
  `api/index`). The API index becomes the two-section tiered page; the broader landing
  redesign is Phase 114, not here.

### Build gate
- Success criterion #3: `sphinx-build -W --keep-going` must still exit clean with the
  expanded tree. Build via `hatch run docs:build`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/conf.py`: working, `-W`-clean Sphinx config from Phase 108 — reuse as-is,
  extend `autodoc_mock_imports` only if newly-surfaced modules import uncovered deps.
- `docs/api/*.rst`: the existing package-level `automodule` pattern is the seed for
  D-08 — expand it to per-package pages that `automodule` each submodule.

### Established Patterns
- Import discipline (GUIDEBOOK §3): `core/ → nothing`, `engine/ → core/`,
  `cli/ → engine/`. The doc tier split mirrors this conceptually but must NOT be
  enforced as a code boundary (out of scope).
- The `.planning/` archive was un-ignored in Phase 108; docs CI runs on `dev` pushes
  (FOUND-02) — so any build breakage is caught at push.

### Integration Points / full module inventory (120 modules)
Tier-one packages: `calibration/` (loader, luts, projection, uncertainty);
`core/types/` (crop, detection, frame_source, midline, reconstruction);
`core/detection/` (+ backends: yolo, yolo_obb); `core/tracking/`
(keypoint_sigmas, keypoint_tracker, stage, types); `core/association/`
(clustering, recovery, scoring, stage, types, validation); `core/pose/`
(+ backends: pose_estimation; crop, stage, types); `core/reconstruction/`
(+ backends: dlt; stage, temporal_smoothing, utils); loose core
(context, inference, stitching); `engine/` (config, console_observer,
diagnostic_observer, events, observer_factory, observers, orchestrator,
pipeline, timing); `io/` (discovery, midline_writer); `cli.py`, `cli_utils.py`,
`logging.py`.

Tier-two packages: `training/` (~24 modules incl. coco_convert, datasets,
elastic_deform, prep, pseudo_labels, pseudo_label_cli, reid_training, run_manager,
store, yolo_training, etc.); `evaluation/` (compare, metrics, output, runner,
tuning) + `evaluation/stages/*` + `evaluation/viz/*`; `core/reid/`
(cli, embedder, eval, miner, runner, swap_detector); `synthetic/`
(detection, fish, rig, scenarios, stubs, trajectory) + `core/synthetic.py`.

</code_context>

<specifics>
## Specific Ideas

- Tier-two status label wording is fixed verbatim:
  **"Research utility — not part of the supported pipeline API."**
- Section names are "Core Pipeline" (tier-one) and "Research Utilities" (tier-two).

</specifics>

<deferred>
## Deferred Ideas

- CLI command reference and config-field reference — **Phase 112** (DOCS-05/06).
- Concepts page, install guide, end-to-end tutorial — **Phase 113** (DOCS-03/04/07).
- README, badge row, hero media, docs landing-page redesign — **Phase 114**.
- Moving tier-two utilities behind a `pip install aquapose[research]` extra — future
  requirement **PKG-01**, not this milestone.

None of the discussion strayed beyond the API-reference scope.

</deferred>

---

*Phase: 110-api-reference-docs-tiering*
*Context gathered: 2026-09-01*
