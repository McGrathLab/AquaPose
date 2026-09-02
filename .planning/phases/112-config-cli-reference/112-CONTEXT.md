# Phase 112: Config & CLI Reference - Context

**Gathered:** 2026-09-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the **user-facing CLI command reference** (DOCS-05) and **config-field
reference** (DOCS-06) so a user can look up any CLI command or config field —
its purpose, arguments, and effect — without reading source.

Like Phase 110, this is **IA/structuring work, not prose-writing**: docstring
coverage is already excellent (config dataclasses carry full Google-style
`Attributes:` blocks; most CLI commands have good `help=` text). The job is to
surface that content in a discoverable, tiered, user-oriented form.

**In scope:**
- A new user-facing **"Reference"** docs section containing a **CLI Reference**
  page (all command groups) and a **Config Reference** page (all config fields,
  tiered).
- Wiring `sphinx-click` into the Sphinx build for CLI auto-rendering.
- Keeping the docs build green (`sphinx-build -W --keep-going`).

**Explicitly NOT this phase (scope fence):**
- Concepts page, install guide, end-to-end tutorial → **Phase 113** (DOCS-03/04/07).
- README, badge row, hero media, docs landing redesign, Read the Docs publish →
  **Phase 114** (DOCS-08).
- Rewriting/adding docstrings — coverage is already sufficient; adapt existing text.
- The API-reference module pages from Phase 110 stay as-is (see D-13).

</domain>

<decisions>
## Implementation Decisions

### Generation mechanism
- **D-01:** **CLI reference → `sphinx-click` (auto-generated).** Add the
  `sphinx-click` extension and let it render every command group/subcommand with
  argument tables pulled directly from the Click definitions. Rationale: CLI help
  text lives *on* the command and cannot drift from it — so auto-generation here
  does **not** hit the drift concern that led Phase 110 (D-08) to reject
  autosummary/apidoc for the module API. Worked examples are still hand-authored
  (see D-07).
- **D-02:** **Config reference → curated, hand-authored tiered pages** (NOT
  autodoc). Flat `autodoc` (already present via `api/engine.rst`) cannot deliver
  the DOCS-06 tiering requirement ("not all 71 at once"), so the config reference
  is hand-authored, adapting text from the existing field docstrings. This matches
  Phase 110's D-08 curation philosophy.
- **D-03:** **No automated drift-guard.** Ship the curated config pages without a
  pytest that asserts documented fields match the dataclasses. Config is treated
  as stable enough now; reviewers catch config changes needing doc updates. (User
  chose "keep it simple" over adding an introspection test.)

### Config tiering (DOCS-06)
- **D-04:** **Two tiers: Essential vs Advanced.** Chosen over a three-tier
  (Essential/Tunable/Expert) scheme and over a by-stage-with-badges scheme. Maps
  directly onto "what `init` scaffolds" vs "what you tune later."
- **D-05:** **Page layout — Essential = one flat table; Advanced = per-stage
  subsections.** Tier 1 is a single "Essential fields" table (field, type,
  default, what to set it to) covering the ~7–10 must-set fields (`n_animals`,
  video/calibration/output paths, the two `weights_path` fields, `mode`, etc. —
  the set the `init` command scaffolds). Tier 2 is "Advanced," organized into
  per-stage subsections (Detection, Pose, Association, Tracking, Reconstruction,
  LUT, Synthetic, Reid).
- **D-06:** **Coverage = every field that exists (~86), not the roadmap's "71".**
  Document all 9 stage-config dataclasses **and** the top-level `PipelineConfig`
  (18 fields incl. `n_animals`, paths, `mode`, `device`, `chunk_size`, `stop_after`)
  **and** `ReidConfig`. The roadmap's "71 fields across 9 dataclasses" is an
  undercount — several essential fields (e.g. `n_animals`) live on `PipelineConfig`
  and MUST be covered. The researcher should reconcile the exact inventory against
  `src/aquapose/engine/config.py` and document the complete set. **Note this
  discrepancy in planning — do not treat "71" as the coverage target.**

### CLI reference (DOCS-05)
- **D-07:** Every command group documented with **purpose, arguments, and a worked
  example**. `sphinx-click` supplies purpose+arguments; examples are hand-authored.
- **D-08:** **Flat organization, grouped by Click group** — NOT mirroring Phase
  110's "Core Pipeline vs Research Utilities" tier split. Let `sphinx-click`'s
  natural structure drive it (root commands, then `train`/`data`/`prep`/`reid`/
  `pseudo-label` subgroups).
- **D-09:** **Generic illustrative examples**, using placeholder project/paths
  (e.g. `aquapose -p myproject run --max-chunks 6`) that show correct syntax and
  common flags. Deliberately **decoupled from the Phase 111 tutorial dataset** — no
  dependency on Phase 111 paths being finalized. (Runnable dataset-anchored
  examples belong to the Phase 113 tutorial.)

### IA & page placement
- **D-10:** **New top-level "Reference" section** in the docs toctree, alongside
  the existing "API Reference" section, holding the CLI Reference and Config
  Reference pages. Signals these are user-facing lookups, distinct from the
  auto-generated module API.
- **D-11:** Two pages: **CLI Reference** and **Config Reference** (both under the
  new Reference section).
- **D-12:** **Docs format** — follow the existing hybrid: MyST `.md` for authored
  narrative/landing content, `.rst` where `sphinx-click`/autodoc directives are
  needed. Furo theme (unchanged).
- **D-13:** **Keep Phase 110's `api/cli.rst` and `api/engine.rst` as-is and
  cross-link.** Do NOT trim them. They satisfy Phase 110's DOCS-02 "every module
  rendered" guarantee; the new Reference pages serve a different audience
  (user lookup vs API completeness). Add cross-links between the two surfaces.

### Claude's Discretion
- Exact `sphinx-click` directive form and where worked examples are attached
  (per-command docstring epilog vs authored around the auto-rendered tables).
- Precise wording/headings of the Reference landing page and the "Essential
  fields" table columns.
- Whether the two Reference pages share an index/landing page and how the
  cross-links (D-13) are phrased.
- Exact per-stage subsection ordering within the Advanced config tier (pipeline
  narrative order per GUIDEBOOK §6 is a sensible default).
- Any additions to `autodoc_mock_imports` in `docs/conf.py` needed to keep
  `-W` green after wiring `sphinx-click`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase requirements & scope
- `.planning/ROADMAP.md` — Phase 112 section (goal + 3 success criteria).
  **⚠ Correction:** SC#2's "71 fields across 9 dataclasses" is an undercount —
  see D-06. Document the complete inventory (~86 fields incl. `PipelineConfig`
  and `ReidConfig`), reconciled against `src/aquapose/engine/config.py`.
- `.planning/REQUIREMENTS.md` — DOCS-05 (every CLI command group: purpose,
  arguments, worked example) and DOCS-06 (every config field: type, default,
  effect, tiered so a tutorial user isn't hit with all fields at once).

### Prior-phase precedent (build ON this, don't undo it)
- `.planning/phases/110-api-reference-docs-tiering/110-CONTEXT.md` — Phase 110's
  decisions. Especially **D-08** (curated toctree + `automodule`, autosummary/
  apidoc rejected — the curation philosophy D-02 extends), and the "Core Pipeline
  vs Research Utilities" tier split (D-04/D-05) that D-08-here deliberately does
  NOT mirror for the CLI. The `api/` pages it produced are the ones D-13 keeps.
- `.planning/GUIDEBOOK.md` §14 (CLI — command groups: run/init/eval/tune/viz/
  train/prep), §11 (Configuration System — frozen dataclasses, loading precedence
  defaults→YAML→CLI→freeze), §8 (backends vs configurable models — relevant to
  documenting `detector_kind`/`backend` fields).

### Existing docs to extend
- `docs/conf.py` — Sphinx config (furo, autodoc, napoleon, myst_parser). Add
  `sphinx-click` to extensions; may need `autodoc_mock_imports` additions.
- `docs/index.md` — top-level toctree; add the new "Reference" section card here.
- `docs/api/index.rst`, `docs/api/cli.rst`, `docs/api/engine.rst` — the Phase 110
  API pages to keep and cross-link (D-13).

### Build gate
- SC#3 / Phase 110 gate: `sphinx-build -W --keep-going` must stay clean. Build via
  `hatch run docs:build`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/aquapose/cli.py` — root command group + 8 root commands (`run`, `init`,
  `eval`, `eval-compare`, `tune`, `viz`, `stitch`, `smooth-z`); good docstrings +
  `help=` text on most options. Source for the CLI reference.
- Subcommand groups registered in `cli.py`: `data` (`training/data_cli.py`),
  `train` (`training/cli.py`: obb/seg/pose/compare), `prep` (`training/prep.py`:
  calibrate-keypoints/generate-luts), `pseudo-label` (`training/pseudo_label_cli.py`),
  `reid` (`core/reid/cli.py`). ~13 command entry points total.
- `src/aquapose/engine/config.py` — the 9 frozen stage dataclasses
  (`DetectionConfig` 7, `PoseConfig` 9, `AssociationConfig` 21, `TrackingConfig` 13,
  `LutConfig` 5, `SyntheticConfig` 4, `ZDenoisingConfig` 1, `ReconstructionConfig` 8,
  `ReidConfig` 5) plus top-level `PipelineConfig` (18). Fields carry Google-style
  `Attributes:` docs with type/default/effect — adapt these for the config reference.
- `src/aquapose/cli.py` `init` command (~lines 176–208) scaffolds the minimal
  starter YAML — its fields ARE the Essential tier (D-05).
- `aquapose-tutorial-data/config.yaml` — a real minimal working config (paths,
  `n_animals`, weights only); confirms the essential field set.

### Established Patterns
- Docs are MyST `.md` (index, contributing) + `.rst` (api/ autodoc), Furo theme.
- Config loading precedence (GUIDEBOOK §11): defaults → YAML → CLI `--set` overrides
  → freeze. Worth surfacing in the config reference intro.
- No `sphinx-click`, jsonschema, or custom config-doc generator is installed yet —
  `sphinx-click` is a new dependency this phase adds (D-01).

### Integration Points
- New "Reference" toctree section wired into `docs/index.md` and a new
  `docs/reference/` (or similar) directory holding the CLI + Config pages.
- Cross-links between `docs/reference/*` and `docs/api/cli.rst` / `api/engine.rst`.

</code_context>

<specifics>
## Specific Ideas

- **Essential field set (Tier 1)** is defined by what `aquapose init` scaffolds:
  `n_animals`, `video_dir`, `calibration_path`, `output_dir`, `detection.weights_path`,
  `pose.weights_path`, `detection.detector_kind`, `mode` (+ any other must-set to run).
- **CLI example style** is generic/placeholder: `aquapose -p myproject <command> ...`
  (project ID `-p` is a top-level arg before the subcommand — see CLAUDE.md).
- Coverage target is "every field that actually exists," reconciled against source —
  NOT the roadmap's literal "71."

</specifics>

<deferred>
## Deferred Ideas

- Runnable, dataset-anchored CLI/config examples against the published example data
  → **Phase 113** tutorial (DOCS-07). This phase stays generic (D-09).
- Automated config-doc drift-guard test → considered and declined (D-03); could be
  revisited if config churn increases.
- Read the Docs publish / docs landing redesign → **Phase 114** (DOCS-08).

None of the discussion strayed beyond the CLI/config-reference scope.

</deferred>

---

*Phase: 112-config-cli-reference*
*Context gathered: 2026-09-01*
