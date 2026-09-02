# Phase 113: Concepts & Tutorial - Pattern Map

**Mapped:** 2026-09-02
**Files analyzed:** 9 (3 new docs pages, 1 new section index, 2 doc-graph edits, 1 config change, 1 generator-script patch, 2 test/prod bugfix sites)
**Analogs found:** 8 / 9

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `docs/getting-started/index.md` (new) | doc-section-index | request-response (static nav) | `docs/reference/index.md` | exact |
| `docs/getting-started/installation.md` (new) | doc-page (narrative) | request-response (static content) | `docs/contributing.md` (dev-setup section) | role-match |
| `docs/getting-started/concepts.md` (new) | doc-page (narrative + Mermaid) | transform (explains data flow) | `docs/reference/config.md` (prose + table structure) | role-match |
| `docs/getting-started/tutorial.md` (new) | doc-page (narrative walkthrough) | batch (CLI walkthrough with expected outputs) | `aquapose-tutorial-data/README.md` (deposit's own short-form recipe) | exact (content), partial (not in-repo location) |
| `docs/index.md` (modified — add card + toctree) | doc-section-index | request-response (static nav) | itself, using the existing card/toctree entries as the pattern | exact |
| `pyproject.toml` (modified — drop `UV_EXTRA_INDEX_URL`) | config | config | itself (`[tool.hatch.envs.default.env-vars]` block) | exact |
| `scripts/package_tutorial_dataset.py` (modified — `write_deposit_config`, `write_deposit_readme`) | utility (template generator) | file-I/O | itself (functions already exist; this is a template-string edit, not a new file) | exact |
| `tests/unit/calibration/test_luts.py` (modified — 2 angular-error assertion sites) | test | transform (numeric validation) | itself (existing assertion blocks at the two flagged sites) | exact |
| `src/aquapose/calibration/luts.py` (modified — `validate_forward_lut`) | utility (validation function) | transform | itself (existing `dot`/`acos` block, lines ~438-440) | exact |

## Pattern Assignments

### `docs/getting-started/index.md` (doc-section-index)

**Analog:** `docs/reference/index.md` (Phase 112's parallel section, per D-07)

Full file for reference — copy this shape exactly, just retarget the grid cards and toctree entries:
```markdown
# Reference

Look up any command or configuration field.

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} CLI Reference
:link: cli
:link-type: doc

All ``aquapose`` subcommands, options, and worked examples.
:::

:::{grid-item-card} Config Reference
:link: config
:link-type: doc

Every configuration field — Essential fields for quick setup and Advanced
fields for fine-tuning each pipeline stage.
:::

::::

\`\`\`{toctree}
:maxdepth: 2
:hidden:

cli
config
\`\`\`
```
For `docs/getting-started/index.md`, retarget to three cards linking `installation`, `concepts`, `tutorial` (in that reading order, matching D-07's "Installation, Concepts, Tutorial" ordering).

### `docs/index.md` (modified)

**Analog:** itself — `docs/index.md` lines 1-46 (already read in full above)

Add a new `grid-item-card` for "Getting Started" **before** the existing "Reference" card (Claude's Discretion: ordering — beginner-first flow suggests Getting Started leads), and add `getting-started/index` to the hidden toctree, mirroring the exact syntax of the existing `Reference` card:
```markdown
:::{grid-item-card} Getting Started
:link: getting-started/index
:link-type: doc

Install AquaPose, understand the pipeline, and run the tutorial dataset
end-to-end.
:::
```
and in the toctree block, add `getting-started/index` as the first entry (before `reference/index`).

### `docs/getting-started/installation.md` (new)

**Analog:** `docs/contributing.md` lines 1-19 (Development Setup section) — same "clone → install → env create" shape, but this page targets **end users**, not contributors, so `pip install aquapose` replaces `git clone` + `hatch env create` as the primary path.

**Pattern to copy (fenced bash blocks, imperative step order):**
```markdown
## Development Setup

\`\`\`bash
# Clone the repository
git clone https://github.com/tlancaster6/aquapose.git
cd aquapose

# Install Hatch (build/environment manager)
pip install hatch

# Create the default development environment
hatch env create

# Install pre-commit hooks
hatch run pre-commit install
hatch run pre-commit install --hook-type pre-push
\`\`\`
```
Adapt into: `pip install aquapose` (D-09, accepted-risk not-yet-true command) → install torch per pytorch.org for your platform (D-08) → verify with `python -c "import torch; print(torch.cuda.is_available())"`. Then a "Prerequisites" section (D-10: ffmpeg on PATH, ~600 MB LUT disk headroom + 215 MB dataset, GPU footprint floor GTX 1660 SUPER 6.4 GB). Cross-reference `docs/contributing.md`'s existing dev-setup instead of duplicating it — that page stays the contributor path per the canonical refs.

### `docs/getting-started/concepts.md` (new)

**Analog:** `docs/reference/config.md` lines 1-17 and its "Essential fields" table (lines 20-36) — the prose-then-table pattern for explaining a layered/staged system concisely, plus its pattern of linking out to `[engine module reference](../api/engine.rst)` for auto-generated detail rather than restating it.

**Core content shape to build (per D-01/D-02/D-03a/D-03b), using GUIDEBOOK.md §6 (`.planning/GUIDEBOOK.md` lines 105-199) as the source-of-truth for the 5-stage table** (Detection → 2D Tracking → Cross-Camera Association → Midline → Reconstruction) and the `PipelineContext` read/write table (GUIDEBOOK lines 179-199):

```markdown
## Pipeline Stages

\`\`\`{mermaid}
flowchart LR
    A[Detection] --> B[2D Tracking]
    B --> C[Cross-Camera Association]
    C --> D[Midline]
    D --> E[Reconstruction]
\`\`\`
```
(Mermaid fence syntax confirmed available: `docs/conf.py:55` lists `sphinxcontrib.mermaid` in `extensions` — no new dependency, D-03a is satisfied as-is.)

Do **not** describe a `{p, ψ, κ, s}` state vector (D-01) — instead document arc-length-sampled midline points → B-spline, citing the verified `outputs.h5` schema from `<code_context>`:
```
midlines/ (group, attrs: SPLINE_K=3, SPLINE_KNOTS=[0,0,0,0,.25,.5,.75,1,1,1,1])
  points          (900, 9, 6, 3)
  control_points  (900, 9, 7, 3)
  half_widths     (900, 9, 6)
  arc_length      (900, 9)
  n_cameras, mean_residual, max_residual, is_low_confidence  (900, 9)
```
Refraction section: intuition-depth only (D-02) — flat air-water interface bends light, naive triangulation is wrong underwater, AquaPose casts refracted rays via Snell's law and precomputes forward/inverse LUTs for speed (GUIDEBOOK §5, referenced but not re-read in full here — planner should pull the exact refraction paragraph from GUIDEBOOK.md §5 when drafting).

### `docs/getting-started/tutorial.md` (new)

**Analog:** `aquapose-tutorial-data/README.md`'s "How to Reproduce" section (reconstructed verbatim below from `scripts/package_tutorial_dataset.py:write_deposit_readme`, since the deposit itself is gitignored) — the short-form recipe D-11 says to *expand*, not replace:

```markdown
## How to Reproduce

\`\`\`bash
# Install AquaPose
pip install aquapose

# Change into the deposit directory (config.yaml uses relative paths)
cd aquapose-tutorial-data

# One-time setup: generate the refractive lookup tables (~600 MB, ~2-5 min)
# The LUTs are deterministic from calibration.json and are NOT shipped with the deposit.
# The pipeline will fail-fast with an error if you skip this step.
aquapose prep generate-luts

# Run the pipeline (generates outputs.h5 + per-chunk diagnostic cache)
aquapose run

# Produce the 3D animation and overlay mosaic
aquapose viz runs/<run_dir>
\`\`\`
```
**IMPORTANT — this exact recipe already has the D-05 bug baked into the surrounding config.yaml header comment** (`aquapose run --config config.yaml`, no such flag exists). When expanding this into `tutorial.md`, do not reproduce that comment; state plainly that `aquapose run` (no `--config` flag) resolves the project by walking CWD upward for `config.yaml` — copy the resolution logic explanation from `src/aquapose/cli_utils.py` (`resolve_project()` docstring/lines 14-47, not fully re-read here, planner should pull directly).

Interpretation section: quote `<specifics>` verbatim as tolerance ranges (D-12) — 95.2% fish-frames reconstructed, median 2.84 px / mean 3.92 px / p95 9.73 px reprojection residual (present as "~3 px median"), median 4 cameras per fish (range 0-6 of 12), 4.0% flagged `is_low_confidence`, 6-9 fish visible per frame (9 median). Timing: quote both hardware points per D-15 (786.45 s pipeline / 150.85 s viz on GTX 1660 SUPER, plus the RTX 4070 Ti number obtained during the D-14 verification run — to be filled in when that run completes).

### `pyproject.toml` (modified)

**Analog:** itself, exact block to edit (already fully captured above, `pyproject.toml:69-71`):
```toml
[tool.hatch.envs.default.env-vars]
UV_EXTRA_INDEX_URL = "https://download.pytorch.org/whl/cu121"
```
D-08: delete this block entirely (or the single line + now-empty table header). No other `[tool.hatch.envs.default]` keys reference it. `dependencies` list (`pytest`, `pytest-cov`, `ruff`, `pre-commit`, `basedpyright`) is unaffected — torch is not in that list at all, confirming the pin only affected index resolution for optional/dev installs, not a hard dependency declaration.

### `scripts/package_tutorial_dataset.py` (modified)

**Analog:** itself — two functions to patch, both fully captured above (`scripts/package_tutorial_dataset.py` lines ~496-643):

1. `write_deposit_config()` — the `header` string (lines ~533-538) contains the D-05 bug:
   ```python
   header = (
       "# AquaPose tutorial dataset config (CC-BY-4.0 data, AGPL-3.0 models)\n"
       "# Run from the aquapose-tutorial-data/ directory:\n"
       "#   cd aquapose-tutorial-data\n"
       "#   aquapose run --config config.yaml\n\n"
   )
   ```
   Fix: replace the last line with `"#   aquapose run\n\n"` (bare form, matching what `resolve_project()` actually does per D-05).

2. `write_deposit_readme()` — the `content` triple-quoted string (lines ~565-566) contains the wrong repo URL:
   ```python
   content = """\
   # AquaPose YH Tutorial Dataset

   A 30-second, 12-camera tutorial clip for [AquaPose](https://github.com/tucklancaster/AquaPose) —
   ```
   Fix: `tucklancaster/AquaPose` → `McGrathLab/AquaPose` (D-05, verified correct org).
   Note the "How to Reproduce" bash block inside this same string (already shown above under the tutorial.md analog) is **correct as-is** — do not touch it.

**Corresponding test file to extend:** `tests/scripts/test_package_tutorial_dataset.py` (existing, per `<integration_points>`) — add/update assertions that `write_deposit_config()`'s header no longer contains `--config` and that `write_deposit_readme()`'s content contains `McGrathLab/AquaPose` and not `tucklancaster`.

### `tests/unit/calibration/test_luts.py` (modified — 2 sites)

**Analog:** itself — both sites already fully captured above.

Site 1 (`test_forward_lut_cast_ray_matches_model`, ~line 149-152):
```python
dot = (lut_dirs * model_dirs).sum(dim=-1).clamp(-1.0, 1.0)
angular_errors = torch.acos(dot).abs() * (180.0 / torch.pi)
assert float(angular_errors.max()) < 0.01, (
    f"Max angular error {float(angular_errors.max()):.4f}° exceeds 0.01° threshold"
)
```
Site 2 (`test_forward_lut_interpolation_accuracy`, ~line 186-189): identical shape with `< 0.1` threshold.

**Fix pattern (D-17)** — replace the `dot`/`acos` computation with a stable float64 `atan2`-based angle in both sites, keeping thresholds (`0.01`, `0.1`) unchanged:
```python
cross_norm = torch.linalg.cross(lut_dirs.double(), model_dirs.double(), dim=-1).norm(dim=-1)
dot = (lut_dirs.double() * model_dirs.double()).sum(dim=-1)
angular_errors = torch.atan2(cross_norm, dot).abs() * (180.0 / torch.pi)
```
(Exact variable names/dims must match each site's existing tensor shapes — both sites already have `lut_dirs`/`model_dirs` in scope from the code above, shown in full above.)

### `src/aquapose/calibration/luts.py` (modified — `validate_forward_lut`)

**Analog:** itself — full function body already captured above (`src/aquapose/calibration/luts.py` lines 394-455).

Site to patch (~lines 438-440):
```python
dot = (lut_dirs * model_dirs).sum(dim=-1).clamp(-1.0, 1.0)
angular_errors_deg = torch.acos(dot).abs() * (180.0 / torch.pi)
```
Apply the identical D-17 stable-angle fix (D-18), keeping the `> 0.1` `ValueError` threshold in the guard below (`if max_angular_error_deg > 0.1: raise ValueError(...)`) unchanged. The docstring's `Raises: ValueError: If max angular error exceeds 0.1 degrees` remains accurate — no docstring edit needed.

---

## Shared Patterns

### Docs section index (grid-item-card + hidden toctree)
**Source:** `docs/reference/index.md` (full file, 30 lines, captured above)
**Apply to:** `docs/getting-started/index.md`, and the edit to `docs/index.md`'s own grid/toctree.
```markdown
::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} <Title>
:link: <doc-name>
:link-type: doc

<one-line description>
:::

::::

\`\`\`{toctree}
:maxdepth: 2
:hidden:

<doc-name-1>
<doc-name-2>
\`\`\`
```

### Cross-linking to Phase 112 reference instead of duplicating
**Source:** `docs/reference/config.md` line 15-16: `For the full auto-generated API documentation ... see the [engine module reference](../api/engine.rst).`
**Apply to:** `installation.md` (link CLI flags to `../reference/cli.rst`), `tutorial.md` (link config fields to `../reference/config.md`), `concepts.md` (link stage internals to `../api/index.rst` tier-one modules). Do not restate CLI options or config fields — narrate and link.

### Bash fenced code blocks with inline `#` comments as step narration
**Source:** `docs/contributing.md` (Development Setup / Running Tests / Code Quality sections, full file captured above) and the deposit's "How to Reproduce" block (reconstructed from `scripts/package_tutorial_dataset.py`).
**Apply to:** `installation.md`, `tutorial.md` — every runnable step gets its own commented bash fence; narration text goes in prose between fences, not as a big comment block.

### Stable-angle numeric fix (float32 acos ill-conditioning)
**Source:** the shared `dot`/`acos` pattern present at 3 sites: `tests/unit/calibration/test_luts.py` (2 sites) and `src/aquapose/calibration/luts.py:438-440`.
**Apply to:** all three sites identically (D-17, D-18) — same `atan2(cross_norm, dot)` in float64, same unchanged thresholds.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `docs/getting-started/tutorial.md`'s Mermaid data-flow diagram (optional, per Claude's Discretion) | doc-page (diagram) | transform | No existing Mermaid diagram exists anywhere in the docs tree to copy shape from — `grep -rl mermaid docs/` outside `conf.py`/`pyproject` returns nothing. Planner should originate the diagram directly from the GUIDEBOOK §6 PipelineContext read/write table (`.planning/GUIDEBOOK.md` lines 179-199) using plain Mermaid `flowchart` syntax (same syntax family used for the stage-flow diagram above, for which there's also no in-repo precedent, but the syntax itself is standard and low-risk).

## Metadata

**Analog search scope:** `docs/`, `pyproject.toml`, `scripts/package_tutorial_dataset.py`, `tests/scripts/test_package_tutorial_dataset.py`, `tests/unit/calibration/test_luts.py`, `src/aquapose/calibration/luts.py`, `src/aquapose/cli.py`, `.planning/GUIDEBOOK.md`, `.github/workflows/test.yml` (referenced, not modified — no CI workflow file changes are required by D-16/D-17/D-18, only source/test files).
**Files scanned:** ~15 (docs pages, pyproject.toml, package_tutorial_dataset.py, test_luts.py, luts.py, cli.py, cli_utils.py referenced, GUIDEBOOK.md, docs/conf.py)
**Pattern extraction date:** 2026-09-02
