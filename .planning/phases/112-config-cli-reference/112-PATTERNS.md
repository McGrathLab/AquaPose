# Phase 112: Config & CLI Reference - Pattern Map

**Mapped:** 2026-09-01
**Files analyzed:** 5 new + 3 modified = 8
**Analogs found:** 8 / 8 (all have strong in-repo precedent from Phase 110)

> This is a **Sphinx documentation** phase, not application code. "Role" = the
> kind of docs artifact (MyST page, RST autodoc/directive page, conf.py edit,
> toctree wiring, dependency edit). "Data flow" = how content reaches the page
> (hand-authored narrative, autodoc-style directive introspecting source,
> pyproject dependency). Analogs are the Phase 110 artifacts (`docs/conf.py`,
> `docs/index.md`, `docs/api/index.rst`, `docs/api/cli.rst`, `docs/api/engine.rst`).

---

## File Classification

| New/Modified File | Role | Content Flow | Closest Analog | Match Quality |
|-------------------|------|--------------|----------------|---------------|
| `docs/reference/index.md` *(new)* | MyST landing page (section index + toctree) | hand-authored narrative | `docs/index.md` (grid-cards + hidden toctree) | exact |
| `docs/reference/cli.rst` *(new)* | RST directive page (`sphinx-click` auto-render) | source-introspecting directive + hand-authored examples | `docs/api/cli.rst` (`.. automodule::` on `aquapose.cli`) | role-match (autodoc→sphinx-click) |
| `docs/reference/config.rst` *or* `.md` *(new)* | authored tiered reference page (tables + per-stage subsections) | hand-authored, adapted from `config.py` `Attributes:` docstrings | `docs/api/engine.rst` (structure/ordering) + `docs/reports/z_uncertainty_report.md` (authored MyST prose) | role-match |
| `docs/conf.py` *(modified)* | Sphinx config | register `sphinx_click.ext`; maybe extend `autodoc_mock_imports` | `docs/conf.py` `extensions=[...]` list (lines 45-56) | exact |
| `docs/index.md` *(modified)* | top-level toctree wiring | add "Reference" grid-card + `reference/index` toctree entry | `docs/index.md` "API Reference" card (lines 8-13) + hidden toctree (lines 31-38) | exact |
| `pyproject.toml` *(modified)* | docs env dependency | add `sphinx-click` to `[tool.hatch.envs.docs].dependencies` | `pyproject.toml` lines 87-96 (existing sphinx-* deps) | exact |
| `docs/api/cli.rst` *(modified, optional)* | cross-link back to Reference | one-line MyST/RST cross-ref (D-13) | itself + `docs/api/index.rst` toctree | exact |
| `docs/api/engine.rst` *(modified, optional)* | cross-link back to Config Reference | one-line cross-ref (D-13) | itself | exact |

---

## Pattern Assignments

### `docs/reference/index.md` (MyST landing page, hand-authored)

**Analog:** `docs/index.md` — the only authored MyST landing page with a
grid-card + hidden-toctree pattern. Copy its exact structure for the new
Reference section landing page.

**Grid-card + hidden toctree pattern** (`docs/index.md` lines 5-38):
```markdown
::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} API Reference
:link: api/index
:link-type: doc

Auto-generated documentation for all public modules.
:::

::::

```{toctree}
:maxdepth: 2
:hidden:

api/index
contributing
reports/z_uncertainty_report
```
```

**Apply as:** two cards ("CLI Reference" → `cli`, "Config Reference" → `config`)
plus a hidden toctree listing `cli` and `config`. `:link-type: doc` is the
established cross-page link convention (used verbatim in `docs/index.md`).
`colon_fence` + `sphinx_design` are already enabled (conf.py lines 53, 84-87),
so `:::{grid-item-card}` works without new config.

---

### `docs/reference/cli.rst` (sphinx-click directive page)

**Analog:** `docs/api/cli.rst` (Phase 110). Same *shape* — an RST page whose
body is a single source-introspecting directive block over the CLI — but swap
`.. automodule::` for `.. click::`. RST (not MyST) is the established format for
directive pages (D-12); every `docs/api/*.rst` uses this.

**Existing autodoc-directive pattern to mirror** (`docs/api/cli.rst` lines 1-7):
```rst
CLI
===

.. automodule:: aquapose.cli
   :members:
   :undoc-members:
   :show-inheritance:
```

**New `sphinx-click` form** (the directive targets the Click **group object**,
`cli`, NOT the `main` wrapper — see `pyproject.toml` line 53
`aquapose = "aquapose.cli:main"`, but `main()` just calls `cli()`; sphinx-click
needs the group):
```rst
CLI Reference
=============

.. click:: aquapose.cli:cli
   :prog: aquapose
   :nested: full
```
- `:prog: aquapose` sets the rendered command name (matches the console script).
- `:nested: full` recurses into every registered subgroup (`data`, `train`,
  `prep`, `pseudo-label`, `reid`) so all ~24 subcommands render (D-08 flat,
  group-driven organization).
- **Worked examples (D-07/D-09)** are hand-authored RST prose interleaved around
  the directive, using the CLAUDE.md generic style
  `aquapose -p myproject run --max-chunks 6` (note `-p` is a **top-level** arg
  before the subcommand). Use RST literal blocks (` .. code-block:: bash `) or,
  if authored in MyST elsewhere, fenced ```` ```bash ````.

**CLI source-of-truth inventory** (from `src/aquapose/cli.py` — what
sphinx-click will render):

| Surface | Object | Commands |
|---------|--------|----------|
| Root group | `cli` (`cli.py:26`) | global `--project/-p` option (`cli.py:27-33`) |
| Root commands | on `cli` | `run` (85), `init` (155), `eval` (237), `eval-compare` (279), `tune` (342), `viz` (492), `stitch` (614), `smooth-z` (721) |
| `data` group | `data_group` (`training/data_cli.py:21`) | import, convert, assemble, status, list, exclude, include, remove |
| `train` group | `train_group` (`training/cli.py:13`) | obb, seg, pose, compare |
| `prep` group | `prep_group` (`training/prep.py:26`) | calibrate-keypoints, generate-luts |
| `pseudo-label` group | `pseudo_label_group` (`training/pseudo_label_cli.py:40`) | generate, mine-hard, select, from-labelstudio, inspect |
| `reid` group | `reid_group` (`core/reid/cli.py:19`) | embed, mine-crops, fine-tune, repair |

Groups are registered at `cli.py:880-884` via `cli.add_command(...)`.
`help=` text already exists on nearly every option; command docstrings supply
the purpose (D-07). No docstring edits needed (scope fence).

---

### `docs/reference/config.rst` / `.md` (authored tiered config reference)

**Analog (structure/ordering):** `docs/api/engine.rst` — establishes the
per-section stacking that the Advanced tier's per-stage subsections mirror.
**Analog (authored MyST prose + tables):** `docs/reports/z_uncertainty_report.md`
is the repo's precedent for a long hand-authored MyST page with narrative +
tables. D-12 permits either format; choose `.md` if the page is mostly authored
tables/prose (recommended — no directives are strictly required), or `.rst` for
consistency with `cli.rst`.

**Content is adapted from the `Attributes:` docstrings in
`src/aquapose/engine/config.py`** — do NOT autodoc (D-02: flat autodoc can't
deliver tiering). Each field's type/default/effect is already written; the job
is to re-table it into two tiers.

**Config source-of-truth inventory** (reconciled against
`src/aquapose/engine/config.py` per D-06 — the roadmap's "71" is an undercount;
**86 fields** across **11 dataclasses**):

| Dataclass | Source lines | Field count | Key fields |
|-----------|-------------|-------------|------------|
| `PipelineConfig` (top-level) | 428-488 | 18 | `run_id`, `output_dir`, `video_dir`, `calibration_path`, `mode`, `n_animals`, `device`, `n_sample_points`, `project_dir`, `stop_after`, `chunk_size` + 7 nested stage configs |
| `DetectionConfig` | 28-79 | 7 | `detector_kind`, `conf_threshold`, `iou_threshold`, `weights_path`, `crop_size`, `detection_batch_frames`, `extra` |
| `PoseConfig` | 82-118 | 9 | `backend`, `confidence_threshold`, `weights_path`, `detection_tolerance`, `n_keypoints`, `keypoint_t_values`, `keypoint_confidence_floor`, `min_observed_keypoints`, `pose_batch_crops` |
| `AssociationConfig` | 121-202 | 21 | `ray_distance_threshold`, `score_min`, `t_min`, `leiden_resolution`, `expected_fish_count`, recovery/validation/centroid fields |
| `TrackingConfig` | 205-267 | 13 | `tracker_kind`, `max_coast_frames`, `n_init`, `track_thresh`, `birth_thresh`, `ocr_threshold`, merger fields |
| `LutConfig` | 279-297 | 5 | `tank_diameter`, `tank_height`, `voxel_resolution_m`, `margin_fraction`, `forward_grid_step` |
| `SyntheticConfig` | 300-316 | 4 | `fish_count`, `frame_count`, `noise_std`, `seed` |
| `ZDenoisingConfig` | 319-333 | 1 | `enabled` (nested under `ReconstructionConfig.z_denoising`) |
| `ReconstructionConfig` | 336-375 | 8 | `backend`, `outlier_threshold`, `min_cameras`, `max_interp_gap`, `n_control_points`, `n_sample_points`, `spline_enabled`, `z_denoising` |
| `ReidConfig` | 378-401 | 5 | `model_name`, `batch_size`, `crop_size`, `device`, `embedding_dim` |

**Total: 18 + 7 + 9 + 21 + 13 + 5 + 4 + 1 + 8 + 5 = 91 field declarations**
(86 leaf/scalar fields once the 5 nested stage-config references on
`PipelineConfig` and the 1 nested `z_denoising` reference are counted as
containers, not leaves — reconcile exact count during authoring per D-06).

**Tier 1 (Essential) — one flat table** (D-05). The essential set is defined by
what `aquapose init` scaffolds (`cli.py:178-208`):
```python
data["project_dir"] = str(project_dir)
data["video_dir"] = "videos"
data["calibration_path"] = "geometry/calibration.json"
data["output_dir"] = "runs"
data["n_animals"] = "SET_ME"          # required, must be int
data["detection"] = {"detector_kind": "yolo_obb",
                     "weights_path": "models/yolo_obb.pt"}
data["pose"] = {"weights_path": "models/yolo_pose.pt"}
```
→ Essential table rows: `n_animals`, `video_dir`, `calibration_path`,
`output_dir`, `project_dir`, `detection.detector_kind`,
`detection.weights_path`, `pose.weights_path`, `mode` (+ `device` if
must-know). Columns (D-05): field | type | default | what to set it to.
Cross-check against `aquapose-tutorial-data/config.yaml` (real minimal config).

**Tier 2 (Advanced) — per-stage subsections** ordered by GUIDEBOOK §6 pipeline
narrative: Detection → Pose → Tracking → Association → Reconstruction (incl.
`z_denoising`) → LUT → Synthetic → Reid. Each subsection is a table adapted from
the corresponding dataclass `Attributes:` block.

**Config-loading precedence intro** (surface in the page intro per
`config.py:1-8` and GUIDEBOOK §11):
> defaults → YAML file → CLI `--set` overrides → freeze.
CLI override syntax lives on the `run` command (`cli.py:51-56`):
```python
@click.option("--set", "overrides", multiple=True,
    help="Config override as key=val (e.g. --set detection.detector_kind=mog2).")
```

---

### `docs/conf.py` (modified — register sphinx-click)

**Analog:** the existing `extensions` list. Append the extension; the module
name is `sphinx_click.ext` (import path), registered as the string
`"sphinx_click.ext"`.

**Extensions list to extend** (`docs/conf.py` lines 45-56):
```python
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "nbsphinx",
    "sphinxcontrib.mermaid",
]
```
→ add `"sphinx_click.ext",`.

**`autodoc_mock_imports` (lines 108-131)** already mocks `click` — critical,
because the docs env is detached and does not install the project. sphinx-click
imports `aquapose.cli:cli`, which imports `click` and the whole CLI import
chain. **Verify the mock list still covers every transitive import pulled in by
importing `aquapose.cli`** (D-discretion / conf.py note). The `run` build gate
`sphinx-build -W --keep-going` (pyproject line 99) will fail on any unmocked
import — this is the primary risk to clear. `click` is already present
(line 111); confirm `yaml` (line 130), `torch` (line 127), `boxmot` (112),
`ultralytics` (129) etc. cover the CLI's import graph.

---

### `docs/index.md` (modified — top-level toctree wiring, D-10)

**Analog:** itself — add a third grid-card and a toctree entry using the exact
existing pattern.

**Card to add** (mirror lines 8-13):
```markdown
:::{grid-item-card} Reference
:link: reference/index
:link-type: doc

CLI commands and configuration fields for looking up any command or setting.
:::
```

**Toctree entry to add** (into the hidden toctree, lines 31-38):
```markdown
```{toctree}
:maxdepth: 2
:hidden:

reference/index
api/index
contributing
reports/z_uncertainty_report
```
```
Place `reference/index` **above** `api/index` so the user-facing lookup section
precedes the auto-generated module API in the sidebar (D-10 signal).

---

### `pyproject.toml` (modified — add sphinx-click dep)

**Analog:** the existing docs dependency list.

**Dependency block to extend** (`pyproject.toml` lines 87-96):
```toml
dependencies = [
    "sphinx>=6.2",
    "furo",
    "myst-parser",
    "sphinx-copybutton",
    "sphinx-design",
    "nbsphinx>=0.9.8",
    "sphinxcontrib-mermaid",
    "numpy",
]
```
→ add `"sphinx-click",` (PyPI package name uses a hyphen; import/extension name
uses underscore `sphinx_click.ext`). The env is `detached = true` (line 86) —
sphinx-click is pure-Python and light, so it fits the "no heavy deps" constraint
that keeps the build under Read the Docs limits.

---

## Shared Patterns

### Cross-linking between Reference and API surfaces (D-13)
**Source convention:** `docs/index.md` `:link-type: doc` cards and RST
`:doc:` roles. **Apply to:** `docs/reference/cli.rst` ↔ `docs/api/cli.rst`, and
`docs/reference/config.rst` ↔ `docs/api/engine.rst`.
- In RST: `` :doc:`API module reference <../api/cli>` ``
- In MyST: `[API module reference](../api/engine.rst)` or `{doc}` role.
Phase 110's `api/cli.rst` and `api/engine.rst` are kept **as-is** (D-13) — only
a one-line cross-ref may be added; do NOT trim their `automodule` blocks.

### Build gate (SC#3, inherited from Phase 110)
**Source:** `pyproject.toml:99` `sphinx-build -W --keep-going -b html`.
**Apply to:** every file in this phase. `-W` promotes warnings to errors, so:
- No broken cross-refs, no orphaned pages (every new page must be in a toctree).
- sphinx-click must import `aquapose.cli:cli` cleanly under mocked imports.
Run via `hatch run docs:build`.

### Ordering by pipeline narrative (GUIDEBOOK §6)
**Source:** `docs/api/index.rst` lines 7-20 order tier-one pages by the 5-stage
story (Detection → Tracking → Association → Pose → Reconstruction). **Apply to:**
the Advanced config tier's per-stage subsection order (D-discretion default).

### RST directive-page shape
**Source:** every `docs/api/*.rst` — title underline + directive block with
option lines. **Apply to:** `docs/reference/cli.rst` (`.. click::` block).

---

## No Analog Found

None. Every file has a concrete Phase 110 or existing-docs analog. The only
*new mechanism* is the `sphinx-click` extension (D-01), but its host page
(`cli.rst`) directly mirrors the existing `docs/api/cli.rst` automodule page —
same page shape, different directive.

| Concern | Note for planner |
|---------|------------------|
| `sphinx-click` directive exact form | New to repo; use `.. click:: aquapose.cli:cli` with `:prog:` + `:nested: full`. No existing example — this is the one pattern to introduce carefully. |
| Config page format (.md vs .rst) | D-12 permits either; `.md` recommended (page is authored tables/prose, no directives required). `z_uncertainty_report.md` is the MyST-authored-page precedent. |

---

## Metadata

**Analog search scope:** `docs/` (all `.rst`/`.md`), `docs/conf.py`,
`pyproject.toml` docs env, `src/aquapose/cli.py`, `src/aquapose/engine/config.py`,
`src/aquapose/training/{cli,data_cli,prep,pseudo_label_cli}.py`,
`src/aquapose/core/reid/cli.py`.
**Files scanned:** 12
**Pattern extraction date:** 2026-09-01
