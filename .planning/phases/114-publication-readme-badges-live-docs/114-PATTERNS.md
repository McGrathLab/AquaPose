# Phase 114: Publication — README, Badges, Live Docs - Pattern Map

**Mapped:** 2026-09-09
**Files analyzed:** 8 (created/modified)
**Analogs found:** 6 / 8 (2 have no direct in-repo analog — CITATION.cff, badge row conventions — use external standard schemas)

This phase is almost entirely repo-surface/packaging work, not application source.
There is no "role/data-flow" application code here — instead each file's closest
analog is another file of the *same document type* already in the repo. Patterns
below are extracted as literal excerpts to copy structure/tone/format from, not
as code architecture patterns.

## File Classification

| New/Modified File | Role | "Data Flow" analog | Closest Analog | Match Quality |
|---|---|---|---|---|
| `README.md` | landing doc | content funnel/rewrite | `docs/index.md` (link targets) + current `README.md` (structure to prune) | role-match |
| `pyproject.toml` (version, semantic_release reset) | config | packaging metadata | itself, `[tool.semantic_release]` block (156-166) | exact (self-edit) |
| `.github/workflows/publish.yml` | CI workflow | release/publish pipeline | read-only reference — **used unmodified per D-03** | exact (no-op) |
| `.github/workflows/test.yml` | CI workflow | test+coverage pipeline | read-only reference — Codecov upload already correct (D-05) | exact (no-op) |
| `.readthedocs.yaml` | config | docs build config | read-only reference — **no change needed per D-08** | exact (no-op) |
| `CHANGELOG.md` | changelog | hand-maintained migration note + generated version list | existing "Migration Notes" / "Unreleased" section (lines 9-27) | exact |
| `CITATION.cff` | metadata file | citation/archival metadata | **no in-repo analog** — new file; content sourced from `pyproject.toml` `[project]`/`[project.urls]`/`authors`/`license` and `LICENSE` copyright line | none (use standard CFF 1.2.0 schema) |
| `CODE_OF_CONDUCT.md` (URL fix only) | community doc | string replace | itself, line with `tlancaster6` | exact |
| `docs/contributing.md` (URL fix only) | docs page | string replace | itself, line 8 `git clone` | exact |

## Pattern Assignments

### `README.md` (landing doc, rewrite)

**Analog 1 — current `README.md`** (own prior content, 66 lines) — defines what to
**keep** vs **move out**:

Keep (per D-12): title + one-line description, Quick Start, License section.

```markdown
# AquaPose

3D fish pose estimation via refractive multi-view triangulation. AquaPose reconstructs fish 3D midlines from multi-view video using a 13-camera aquarium rig with refractive calibration, producing dense 3D trajectories and midline kinematics for behavioral research on cichlids.
```

```markdown
## Quick Start

\`\`\`bash
# Initialize a project
aquapose init-config my_project

# Run the pipeline
aquapose run --config path/to/config.yaml
\`\`\`
```

```markdown
## License

AquaPose is licensed under [AGPL-3.0-or-later](LICENSE). See
[LICENSING.md](LICENSING.md) for why.
```

**Move out** (per D-12 — these two sections leave the README entirely):

```markdown
## Development
...
hatch run test
hatch run lint
hatch run typecheck
...
See [Contributing](docs/contributing.md) for full development guidelines.
```
→ merges into `docs/contributing.md` "Development Setup" section (already has clone/install/pre-commit steps — verify no duplication before adding anything).

```markdown
### GPU Support

Hatch installs the CPU-only PyTorch by default. For GPU support, manually install
the CUDA build after creating the environment:
...
```
→ **factually wrong** post-Phase-113 (cu121 pin removed); do not move as-is — verify Phase 113's install guide (`docs/getting-started/installation.md`) already covers current torch/GPU guidance, then simply drop this section from the README rather than relocating stale content.

**Delete the commented-out doc stub** (dead TODO, currently the entire "Documentation"
section):
```markdown
## Documentation

<!-- TODO: Uncomment once docs are deployed -->
<!-- Full documentation is available at [aquapose.readthedocs.io](https://aquapose.readthedocs.io). -->
```
Replace with live badge-backed links per D-12 (Installation, Concepts, Tutorial, API
reference on RTD) — see link targets below.

**Analog 2 — `docs/index.md`** (`C:\Users\tucke\PycharmProjects\AquaPose\docs\index.md`) — the
canonical set of destination pages the README's "links out" section should mirror
(same targets, not the sphinx-design grid-card markup, since GitHub-flavored
Markdown on README/PyPI doesn't render MyST directives):

```markdown
::::{grid} 1 2 2 3
:::{grid-item-card} Getting Started
:link: getting-started/index
...
:::{grid-item-card} Reference
:link: reference/index
...
:::{grid-item-card} API Reference
:link: api/index
...
:::{grid-item-card} Contributing
:link: contributing
...
```
→ Translate to plain Markdown links using **absolute** RTD URLs (README becomes
PyPI's long_description via `readme = "README.md"` at `pyproject.toml:9`; relative
links break on PyPI). Use `https://aquapose.readthedocs.io/en/dev/...` (or whatever
canonical path resolves once RTD is live — verify against the actual built site
before finalizing), e.g.:

```markdown
- [Installation](https://aquapose.readthedocs.io/en/dev/getting-started/installation.html)
- [Concepts](https://aquapose.readthedocs.io/en/dev/getting-started/concepts.html)
- [Tutorial](https://aquapose.readthedocs.io/en/dev/getting-started/tutorial.html)
- [API Reference](https://aquapose.readthedocs.io/en/dev/api/index.html)
```

**Citation pointer** (per D-10 — no BibTeX in README, link to `CITATION.cff` only):
```markdown
## Citation

See [CITATION.cff](CITATION.cff) for citation metadata, or use GitHub's
"Cite this repository" button.
```

**License section** — keep verbatim from current README (shown above); cross-check
wording matches `LICENSING.md` framing (AGPL forced by Ultralytics/igraph/leidenalg
dependency chain, per `LICENSING.md` lines 1-20).

---

### `pyproject.toml` — version reset and urls (config, self-edit)

**Analog:** itself. **Current state** (`C:\Users\tucke\PycharmProjects\AquaPose\pyproject.toml`):

Version (line 7):
```toml
version = "1.2.0-dev.6"
```
→ D-01: one-time reset to `"4.0.0"`.

URLs already correct, no change needed (lines 51-55):
```toml
[project.urls]
Homepage = "https://github.com/McGrathLab/AquaPose"
Documentation = "https://aquapose.readthedocs.io"
Repository = "https://github.com/McGrathLab/AquaPose"
Issues = "https://github.com/McGrathLab/AquaPose/issues"
```
(These already point at `McGrathLab/AquaPose`, not `tlancaster6` — confirms the D-13
URL-fix scope is correctly narrowed to just `CODE_OF_CONDUCT.md` and
`docs/contributing.md`.)

Semantic-release config, needs the reset context documented (lines 155-167):
```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
commit_message = "chore(release): {version}"
build_command = "python -m build"
tag_format = "v{version}"

[tool.semantic_release.branches.main]
match = "^main$"
prerelease = false

[tool.semantic_release.branches.dev]
match = "^dev$"
prerelease = true
prerelease_token = "dev"

[tool.semantic_release.changelog]
changelog_file = "CHANGELOG.md"
```
No structural change to this block — only the `version` field bump plus the
CHANGELOG hand-note explaining the 1.2.0-dev → 4.0.0 jump (see CHANGELOG pattern
below). `tag_format = "v{version}"` combined with `publish.yml`'s trigger
`v[0-9]+.[0-9]+.[0-9]+` means tagging `v4.0.0` is what fires the publish workflow —
confirm semantic-release will actually produce/push that exact tag format after
the reset.

---

### `.github/workflows/publish.yml` (CI workflow, read-only reference)

**File:** `C:\Users\tucke\PycharmProjects\AquaPose\.github\workflows\publish.yml`
**Per D-03: used unmodified.** Full chain already present — trigger, test job,
build job, then publish jobs:

```yaml
on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'  # Full releases only (not v1.2.3-dev.1)
```

```yaml
  publish-testpypi:
    needs: build
    environment: testpypi
    permissions:
      id-token: write
    steps:
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

  publish:
    needs: publish-testpypi
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: pypa/gh-action-pypi-publish@release/v1
```

**Flag for the planner:** despite D-02's "no TestPyPI dry run" decision, this
workflow's `publish` job currently `needs: publish-testpypi` — i.e. the *existing*
unmodified workflow still routes every tag through a TestPyPI upload before the
real PyPI upload. D-03 says use it unmodified, so this existing intermediate
TestPyPI step happens automatically as part of tagging regardless of D-02's
framing (D-02 rejected an *additional new dry-run job*, not this pre-existing
gate). The planner should reconcile this literally when writing the pre-tag
verification checklist — confirm whether a `testpypi` GitHub Environment with
its own trusted-publishing credentials exists/needs setup, since the `publish`
job cannot succeed without the `testpypi` job succeeding first.

---

### `.github/workflows/test.yml` (CI workflow, read-only reference for D-05)

**File:** `C:\Users\tucke\PycharmProjects\AquaPose\.github\workflows\test.yml`, lines 34-44:
```yaml
      - name: Run tests
        run: hatch run test -- --cov --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v5
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: false
```
Matrix runs on `[ubuntu-latest, windows-latest] x [3.11, 3.12, 3.13]` (lines 15-19) —
relevant if the planner wants a Python-versions badge sourced from this matrix
rather than hand-typed from `pyproject.toml` classifiers. Separate `typecheck` job
(lines 46-56) exists as a distinct workflow job — Claude's discretion (D-06/D-notes)
on whether it earns its own badge.

`docs.yml` (`C:\Users\tucke\PycharmProjects\AquaPose\.github\workflows\docs.yml`) is a
second, RTD-independent docs build trigger (push to `main`/`dev`) — usable as an
alternate/supplementary docs badge target if RTD's own badge is considered
insufficient, though D-07 implies RTD's own status badge is the intended source.

---

### `CHANGELOG.md` (changelog, hand-maintained note)

**Analog:** existing "Migration Notes" pattern, `C:\Users\tucke\PycharmProjects\AquaPose\CHANGELOG.md` lines 1-27:
```markdown
# CHANGELOG

## Licensing

As of version 1.2.0, AquaPose is licensed
[AGPL-3.0-or-later](LICENSE). Releases up to and including v1.1.1 were
published under the MIT License, and that grant is unaffected. See
[LICENSING.md](LICENSING.md) for why the AGPL applies.

## Migration Notes

Hand-maintained. Entries below the version list are generated from commit
messages by python-semantic-release; this section is not.

### Unreleased — `aquapose.io.discovery` submodule removed

`discover_camera_videos` moved to `aquapose.core.types.video_discovery` so that
`aquapose/core/` no longer imports the I/O layer at module level (Phase 113.1).
...

<!-- version list -->

## v1.2.0-dev.6 (2026-09-03)
```
**Pattern to copy:** add a new dated sub-heading under "Migration Notes" (same
style as the `discover_camera_videos` note — problem statement, what changed,
old/new import paths if relevant) explaining the `1.2.0-dev.6 → 4.0.0` jump per
D-01: this is a milestone-alignment version reset, not a semver-earned bump: the
package was never actually released, so there is no real breaking change to
document — just the number discontinuity. Do not touch the generated
`<!-- version list -->` section below — that is semantic-release's territory.

---

### `CITATION.cff` (new file, no in-repo analog)

**No existing `.cff` file anywhere in this repo** to copy from. Source content
from `pyproject.toml` `[project]` metadata instead:
```toml
name = "aquapose"
version = "4.0.0"  # after D-01 reset
description = "3D fish pose estimation via refractive multi-view triangulation"
license = "AGPL-3.0-or-later"
authors = [{name = "Tucker Lancaster"}]
```
and `LICENSE` line 1 for the copyright holder attribution:
```
Copyright (C) 2026 Tucker Lancaster and the McGrath Lab at the Georgia Institute of Technology
```
and `pyproject.toml:51-55` for the `repository-code`/`url` fields (`https://github.com/McGrathLab/AquaPose`).

**Structural reference (standard CFF 1.2.0 schema, not project-specific)** — use the
canonical Citation File Format shape:
```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
title: AquaPose
authors:
  - family-names: Lancaster
    given-names: Tucker
version: 4.0.0
date-released: "<release date>"
url: "https://github.com/McGrathLab/AquaPose"
repository-code: "https://github.com/McGrathLab/AquaPose"
license: AGPL-3.0-or-later
# doi: <concept DOI>   # added in Pass B per D-11, absent in Pass A
```
**D-11 two-pass note:** Pass A ships this file with **no `doi:` key at all**
(not a placeholder — omit the field), commits, tags `v4.0.0`. Pass B adds the
`doi:` key with the Zenodo concept DOI in a follow-up commit after Zenodo mints
it. Keep the `version:`/`date-released:` fields in sync with the actual tag if
Pass B's commit lands after the tag.

**Cross-check target:** `docs/getting-started/tutorial.md` lines 40, 45, 85 use a
different, existing BibTeX-style dataset citation (already correct, do not
touch):
```bibtex
@dataset{lancaster_aquapose_yh_tutorial_2026,
  title   = {AquaPose YH Tutorial Dataset},
  author  = {Lancaster, Tucker},
  year    = {2026},
  doi     = {10.5281/zenodo.22264079},
  license = {CC-BY-4.0 (data), AGPL-3.0 (models)},
}
```
and the surrounding prose distinguishing concept vs. version DOI:
```markdown
That is the *version* DOI, which always resolves to the exact files this
tutorial was verified against — cite it when reproducing these results. The
concept DOI [10.5281/zenodo.22264078](https://doi.org/10.5281/zenodo.22264078) resolves
to the latest version instead, and is the right one to cite when you mean the
dataset in general rather than this specific snapshot.
```
This is the **dataset** DOI/concept-DOI framing pattern to mirror conceptually
(version vs. concept DOI) for the **software** DOI in `CITATION.cff` — but the
software concept DOI is a **different number** from `10.5281/zenodo.22264078`/`...79`
and must not collide with or replace these dataset references.

---

### `CODE_OF_CONDUCT.md` (URL fix, D-13)

**File:** `C:\Users\tucke\PycharmProjects\AquaPose\CODE_OF_CONDUCT.md`, the one stale line:
```markdown
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the community leaders responsible for enforcement at <https://github.com/tlancaster6/aquapose/issues>. All complaints will be reviewed and investigated promptly and fairly.
```
→ replace `tlancaster6/aquapose` with `McGrathLab/AquaPose` (matches the casing
already used consistently in `pyproject.toml:52,54,55`'s `[project.urls]` block).

### `docs/contributing.md` (URL fix, D-13)

**File:** `C:\Users\tucke\PycharmProjects\AquaPose\docs\contributing.md`, line 8:
```bash
git clone https://github.com/tlancaster6/aquapose.git
```
→ replace with `git clone https://github.com/McGrathLab/AquaPose.git`.

---

## Shared Patterns

### Absolute-URL discipline for README (applies to: `README.md` only, but critical)
**Source:** `pyproject.toml:9` (`readme = "README.md"`) + `pyproject.toml:51-55`
(`[project.urls]`).
Because the README becomes the PyPI long-description, every internal link in the
rewritten README must be an **absolute URL** (either to `github.com/McGrathLab/AquaPose/...`
or to `aquapose.readthedocs.io/...`), never a repo-relative path like
`docs/contributing.md` (which the *current* README still uses at
`See [Contributing](docs/contributing.md)` — this pattern must NOT be carried into
the rewrite, since that section is moving out of the README anyway per D-12).

### GitHub org casing convention (applies to: all files touched by D-13, `pyproject.toml`, `CITATION.cff`)
**Source:** `pyproject.toml:52,54,55`
```toml
Homepage = "https://github.com/McGrathLab/AquaPose"
Repository = "https://github.com/McGrathLab/AquaPose"
Issues = "https://github.com/McGrathLab/AquaPose/issues"
```
Canonical casing is `McGrathLab/AquaPose` — use exactly this casing (not
`mcgrathlab/aquapose` or `McGrathLab/aquapose`) in `CITATION.cff`, the badge row,
and the two D-13 URL fixes, for consistency with what's already committed.

### License consistency triangle (applies to: `README.md`, `CITATION.cff`, badge row)
**Source:** `LICENSE:1`, `pyproject.toml:11`, `LICENSING.md:3-4`
All three already agree on `AGPL-3.0-or-later`. The license badge and the
`CITATION.cff` `license:` field must use the SPDX identifier `AGPL-3.0-or-later`
verbatim (not `AGPL-3.0`, not `GPL-3.0`) to match.

### Human-gated external-service pattern (applies to: Codecov, RTD, Zenodo, PyPI steps)
**Source:** phase context, `code_context` section — Phases 111/113 both treated
Zenodo activation as a `checkpoint:human-action` performed by the maintainer in
their own browser session rather than automated. Follow the same pattern for:
Codecov project linking (D-05), RTD project activation (D-07), Zenodo↔GitHub
webhook (D-09/D-11), and PyPI trusted-publishing credentials (D-02) — the plan's
executable steps stop at "verify this is configured," they do not attempt to
configure it.

## No Analog Found

| File | Role | Reason |
|------|------|--------|
| `CITATION.cff` | metadata file | No `.cff` file exists anywhere in this repo (verified: only `.planning/` and `CHANGELOG.md` hits for old org name, no cff files at all). Use the standard CFF 1.2.0 schema shown above, populated from `pyproject.toml` metadata. |
| Badge row markup itself (shields.io / native badges) | README fragment | No badges exist in the current README (verified: 66-line file has zero badge images). This is genuinely new — Claude's discretion per D-06 on provider/style; base URLs on: Codecov badge (`https://codecov.io/gh/McGrathLab/AquaPose`), RTD badge (`https://readthedocs.org/projects/aquapose/badge/?version=dev`), PyPI version badge (`https://img.shields.io/pypi/v/aquapose`), GitHub Actions badge (`https://github.com/McGrathLab/AquaPose/actions/workflows/test.yml/badge.svg`), Zenodo DOI badge (standard `https://zenodo.org/badge/DOI/<concept-doi>.svg` once minted). |

## Metadata

**Analog search scope:** repo root (`README.md`, `CODE_OF_CONDUCT.md`,
`CHANGELOG.md`, `pyproject.toml`, `.readthedocs.yaml`), `.github/workflows/`,
`docs/` (`index.md`, `contributing.md`, `getting-started/tutorial.md`).
**Files scanned:** 9
**Pattern extraction date:** 2026-09-09
