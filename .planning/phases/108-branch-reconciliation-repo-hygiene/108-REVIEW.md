---
phase: 108-branch-reconciliation-repo-hygiene
reviewed: 2026-08-17T00:00:00Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - .github/workflows/docs.yml
  - .gitignore
  - LICENSE
  - LICENSING.md
  - README.md
  - docs/api/engine.rst
  - docs/api/evaluation.rst
  - docs/api/index.rst
  - docs/api/optimization.rst
  - docs/api/segmentation.rst
  - docs/api/synthetic.rst
  - docs/api/training.rst
  - docs/conf.py
  - docs/index.md
  - pyproject.toml
  - src/aquapose/core/context.py
  - src/aquapose/engine/observers.py
  - src/aquapose/synthetic/fish.py
  - src/aquapose/synthetic/scenarios.py
findings:
  critical: 1
  warning: 8
  info: 9
  total: 18
status: issues_found
---

# Phase 108: Code Review Report

**Reviewed:** 2026-08-17
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

Phase 108 reconciled `dev` against `main`, relicensed MIT → AGPL-3.0-or-later, and
repaired the Sphinx docs tree. The relicense itself is textually consistent: `LICENSE`
carries the full AGPLv3 text with a correct copyright line, `README.md` no longer
claims MIT, and a repo-wide grep for MIT surfaces only the intentional historical
references in `LICENSING.md` / `CHANGELOG.md`. The four `src/` files were confirmed
behavior-neutral — the diff is exclusively RST double-backtick escaping and blank lines
before enumerated lists in docstrings, with zero executable change. The docs API tree is
now internally consistent: `optimization.rst`/`segmentation.rst` were deleted and their
toctree entries removed; every remaining toctree target (`calibration`, `core`, `engine`,
`evaluation`, `io`, `synthetic`, `training`) exists on disk, as do
`docs/contributing.md` and `docs/reports/z_uncertainty_report.md`.

The material problem is in packaging metadata. I generated the core metadata directly
with `hatchling>=1.27` against this `pyproject.toml` and confirmed it emits **both**
`License-Expression: AGPL-3.0-or-later` **and** a `License ::` trove classifier. PEP 639
declares those mutually exclusive and PyPI's Warehouse rejects the upload. Since
`.github/workflows/publish.yml` fires on `v[0-9]+.[0-9]+.[0-9]+` tags and publishes via
`pypa/gh-action-pypi-publish`, the first real `v1.2.0` tag will fail at the TestPyPI
step. This is precisely the "packaging-metadata error ships to PyPI" risk the phase
flagged, and it is live.

Secondary concerns: the `autodoc_mock_imports` list was described as "re-derived against
dev's import surface" but 4 of its 22 entries name modules that appear nowhere in `src/`;
`LICENSING.md` makes a verifiably false claim about what is on PyPI; the relicense never
reached source headers or the contributor guide; and the docs CI gate does not run on
pull requests targeting `dev`, which is the branch where this phase's own lost-docstring
regression originated.

## Structural Findings (fallow)

No structural pre-pass was provided for this review.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: PEP 639 license expression and `License ::` classifier are mutually exclusive — PyPI will reject the v1.2.0 upload

**File:** `pyproject.toml:11,18`

**Issue:** The relicense set `license = "AGPL-3.0-or-later"` (PEP 639 SPDX string form,
which is correct) but *kept* a `License :: OSI Approved :: ...` trove classifier
alongside it. PEP 639 states that a project using `License-Expression` MUST NOT also
supply `License ::` classifiers, and Warehouse enforces this at upload time.

I verified the emitted metadata empirically by running hatchling's metadata constructor
against this exact file. Both fields are present in the built distribution:

```
Metadata-Version: 2.5
License-Expression: AGPL-3.0-or-later
License-File: LICENSE
...
Classifier: License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)
```

This is not theoretical. `.github/workflows/publish.yml` triggers on tags matching
`v[0-9]+.[0-9]+.[0-9]+` and runs `pypa/gh-action-pypi-publish` against TestPyPI and then
PyPI. The current `v1.2.0-dev.1` tag does not match that pattern, which is the only
reason this has not blown up yet — the first `v1.2.0` tag will fail the publish job
after the test and build jobs have already run.

Note also that hatchling emits `Metadata-Version: 2.5` here, which compounds the risk:
older Warehouse metadata validators reject unrecognised metadata versions outright. That
is a hatchling-version concern rather than a phase-108 defect, but it argues for pinning
the build backend (see WR-01).

**Fix:** Drop the classifier. The SPDX expression is the canonical, machine-readable
license declaration under PEP 639; the classifier is now redundant and forbidden.

```toml
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    # License is declared via the PEP 639 `license` SPDX expression above.
    # A `License ::` classifier here is mutually exclusive with License-Expression
    # and causes PyPI to reject the upload.
    "Programming Language :: Python :: 3",
    ...
]
```

Verify after the change with `python -m build && twine check dist/*`, and prefer a dry
run against TestPyPI before cutting the `v1.2.0` tag.

## Warnings

### WR-01: `build-system.requires` is unpinned, but the SPDX string license needs hatchling >= 1.27

**File:** `pyproject.toml:2`

**Issue:** `requires = ["hatchling"]` places no floor on the backend version. The
`license = "AGPL-3.0-or-later"` string form introduced by this phase is only accepted by
hatchling 1.27+; earlier hatchling versions validate `project.license` as a table and
raise `Field 'project.license' must be a table`. Anyone building from a cached or pinned
older hatchling (offline builds, corporate mirrors, `pip install --no-build-isolation`
into an environment with an old hatchling) gets a hard build failure with a message that
does not obviously point at the relicense. CI happens to resolve the latest hatchling
from PyPI, which masks the problem.

**Fix:**

```toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"
```

### WR-02: `LICENSING.md` makes a false factual claim about what is published on PyPI

**File:** `LICENSING.md:58-59`

**Issue:** The document states:

> The v1.1.0 and v1.1.1 releases are **not** being yanked from PyPI. They remain
> available under their original MIT terms.

Querying the PyPI JSON API for `aquapose` returns exactly one release: `1.0.0` (with
`license: MIT`). Neither `1.1.0` nor `1.1.1` was ever published — they exist only as git
tags. Meanwhile the one release that *is* publicly distributed under MIT, `v1.0.0`, is
not mentioned anywhere in the document.

This matters more than a typo would. `LICENSING.md` is the project's public statement of
the relicense boundary, and an incorrect assertion about which artifacts are in
distribution under which terms undermines the document's purpose. Downstream users
auditing the license boundary will look for v1.1.x on PyPI, not find it, and be unable to
reconcile the record.

**Fix:** Correct the paragraph to describe the actual distribution state, e.g.:

```markdown
The only release published to PyPI under the MIT License is **v1.0.0**; it is **not**
being yanked and remains available under its original MIT terms. Versions v1.1.0 and
v1.1.1 exist as git tags only and were never uploaded to PyPI. Their MIT grant likewise
stands for anyone who obtained them from the repository.
```

Apply the same correction to the matching paragraph in `CHANGELOG.md:5-8` (regenerated,
so update the semantic-release changelog template/header source rather than the generated
file).

### WR-03: Relicense never reached source files or the contributor guide

**File:** `LICENSE`, `src/**/*.py`, `docs/contributing.md`

**Issue:** The relicense is confined to `LICENSE`, `LICENSING.md`, `README.md`, and
`pyproject.toml`. Grepping `src/` for `GNU Affero` or `SPDX-License-Identifier` returns
zero matches — not a single module carries a license notice. Grepping
`docs/contributing.md` and `CODE_OF_CONDUCT.md` for any form of "licen[cs]e" returns zero
matches, so contributors are never told that their contributions are being accepted under
AGPL-3.0-or-later.

The AGPL's own "How to Apply These Terms" section (reproduced at the tail of `LICENSE`)
explicitly instructs attaching a notice to each source file. For a network-copyleft
license whose §13 obligation is the entire point of the switch, having the grant rest on
a single root `LICENSE` file with no in-file notices and no contributor-facing statement
leaves the relicense functionally half-finished. It also means a file extracted from the
repo in isolation carries no license signal at all.

**Fix:**
1. Add an SPDX header to each module (cheap, greppable, tool-friendly):
   ```python
   # SPDX-License-Identifier: AGPL-3.0-or-later
   # Copyright (C) 2026 Tucker Lancaster and the McGrath Lab at the
   # Georgia Institute of Technology
   ```
   This is mechanisable with a `reuse` or `licenseheaders` pre-commit hook so it does not
   drift.
2. Add a "License" section to `docs/contributing.md` stating that contributions are
   accepted under AGPL-3.0-or-later, and link `LICENSING.md`.

### WR-04: Four `autodoc_mock_imports` entries name modules that are never imported

**File:** `docs/conf.py:102-125`

**Issue:** The commit that introduced this list describes it as "re-derive autodoc mock
imports against dev's import surface." It was not fully re-derived. Enumerating every
`import X` / `from X import` across `src/` (including nested and function-local imports)
gives this third-party set:

```
PIL aquacal click cv2 h5py igraph leidenalg matplotlib numpy plotly
pycocotools pytorch_metric_learning scipy shapely sklearn timm torch
ultralytics yaml
```

Four mocked entries do not appear anywhere in `src/`:

- `boxmot` — zero references in `src/` (the README still describes OC-SORT tracking, but
  no module imports boxmot)
- `loguru` — zero references; the project uses stdlib `logging` via `src/aquapose/logging.py`
- `skimage` — zero references, despite `scikit-image` being a declared runtime dependency
- `torchvision` — appears only inside a prose docstring at
  `src/aquapose/training/datasets.py:218`, never as an import

The good news is the inverse check is clean: every module actually imported is either
mocked or genuinely installed in the docs env (`numpy`). So the `-W` build passing is not
accidental. But a mock list carrying 18% dead entries is exactly the kind of config that
silently rots — the next person to read it will assume boxmot and loguru are live
dependencies.

**Fix:** Remove the four stale entries and add a note on how to regenerate:

```python
# Regenerate with:
#   grep -rhoE "^[[:space:]]*(from|import) +[a-zA-Z_][a-zA-Z0-9_]*" --include=*.py src/ \
#     | awk '{print $2}' | sort -u
autodoc_mock_imports = [
    "aquacal",
    "click",
    "cv2",
    "h5py",
    "igraph",
    "leidenalg",
    "matplotlib",
    "plotly",
    "PIL",
    "pycocotools",
    "pytorch_metric_learning",
    "scipy",
    "shapely",
    "sklearn",
    "timm",
    "torch",
    "ultralytics",
    "yaml",
]
```

Note that `torchvision` should stay mocked *if* WR-08 is resolved by keeping it as a
declared dependency and it is expected to be imported later; as written today it is dead.

### WR-05: `docs.yml` declares no `permissions:` block

**File:** `.github/workflows/docs.yml:14-16`

**Issue:** The `build-docs` job inherits the repository-default `GITHUB_TOKEN`
permissions. On repositories whose default is still "read and write", this hands a
write-capable token to a job that runs `pip install hatch` and then executes an arbitrary
dependency tree (sphinx, furo, myst-parser, nbsphinx, sphinxcontrib-mermaid and their
transitive closure) fetched unpinned from PyPI. A compromised or typosquatted transitive
dependency in a docs toolchain would inherit push access to the repo.

Note that `publish.yml` gets this right — it scopes `permissions: id-token: write` on the
publishing jobs. `docs.yml` should be at least as careful, and it needs strictly less.

**Fix:** The docs build needs nothing but checkout.

```yaml
jobs:
  build-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: read
```

### WR-06: Docs CI does not gate pull requests into `dev`

**File:** `.github/workflows/docs.yml:3-7`

**Issue:** The triggers are asymmetric:

```yaml
on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]
```

`dev` is the active integration branch — `[tool.semantic_release.branches.dev]` cuts
prereleases from it, and the repo's working branch is `dev`. But a pull request targeting
`dev` does not run the docs build at all. Docs breakage is only detected *after* merge, on
the push event, when it is already on the shared branch.

This is not hypothetical for this phase specifically: 108's own premise was that
docstring repairs from `a66287a` were dropped by a merge and had to be forward-ported.
A post-merge-only docs gate is the class of CI configuration that lets exactly that kind
of regression land.

**Fix:**

```yaml
on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]
```

### WR-07: README Quick Start commands do not exist

**File:** `README.md:19-25`

**Issue:** Both documented commands are wrong against the actual Click CLI in
`src/aquapose/cli.py`:

```bash
aquapose init-config my_project              # no such command
aquapose run --config path/to/config.yaml    # `run` has no --config option
```

- The scaffold command is registered as `@cli.command("init")` (`cli.py:147`), not
  `init-config`. `aquapose init-config` exits with Click's "No such command" error.
- `run` (`cli.py:41`) accepts `--mode/-m`, `--set`, `--add-observer`, `--stop-after`,
  `--verbose/-v`, `--max-chunks` — there is no `--config`. The project is selected via the
  *top-level* `--project/-p` option on the group (`cli.py:27-33`), before the subcommand,
  which the README never mentions. `CLAUDE.md` documents the real form
  (`aquapose -p YH run`), so the README is the only place carrying the broken invocation.

A README whose first two copy-pasteable commands both fail is a real onboarding defect,
and this file is also the PyPI long description — the same broken commands appear on the
package page.

**Fix:**

```bash
# Initialize a project (creates ~/aquapose/projects/my_project/)
aquapose init my_project

# Run the pipeline (project selected with the top-level -p flag)
aquapose -p my_project run
```

### WR-08: Declared dependencies drifted from actual imports

**File:** `pyproject.toml:27-45`

**Issue:** Cross-referencing the declared runtime dependencies against the real import
surface of `src/` shows drift in both directions:

Declared but never imported:
- `scikit-image>=0.21` — `skimage` appears nowhere in `src/`
- `torchvision>=0.15` — appears only in a docstring at `training/datasets.py:218`

Imported but not declared (currently satisfied only transitively):
- `matplotlib` — imported in `src/`; available today only because `ultralytics` depends
  on it
- `sklearn` — imported in `src/`; available today only because `pytorch-metric-learning`
  depends on `scikit-learn`
- `PIL` — imported in `src/`; available today only via `torchvision`/`ultralytics`

Relying on transitive dependencies is fragile: if Ultralytics drops matplotlib, or
pytorch-metric-learning drops scikit-learn, `aquapose` breaks at import time with an
error that points at neither project. Conversely, `scikit-image` is a heavy unused
install forced on every user. This also interacts with WR-04 — the same drift is what
left `skimage` and `torchvision` in the mock list.

**Fix:** Declare what is used, drop what is not.

```toml
dependencies = [
    "torch>=2.0",
    "numpy>=1.24",
    "opencv-python>=4.8",
    "scipy>=1.11",
    "scikit-learn>=1.3",
    "matplotlib>=3.7",
    "pillow>=10.0",
    "h5py>=3.9",
    ...
]
```

Confirm `torchvision` is genuinely unused before removing it — Ultralytics pulls it in
regardless, so its removal is safe from a runtime perspective but should be a deliberate
call.

## Info

### IN-01: Copyright year hardcoded, regressing from an auto-updating value

**File:** `docs/conf.py:34-36`

**Issue:** The previous config computed `copyright = f"{datetime.now().year}, ..."`. It
is now the literal string `"2026, Tucker Lancaster and the McGrath Lab..."`. The
attribution change is correct and desirable, but freezing the year means the footer of
every rendered page silently goes stale in January.

**Fix:** Keep the new attribution, restore the dynamic year:

```python
from datetime import datetime

_ORG = "Tucker Lancaster and the McGrath Lab at the Georgia Institute of Technology"
copyright = f"2026-{datetime.now().year}, {_ORG}" if datetime.now().year > 2026 else f"2026, {_ORG}"
```

### IN-02: README claims a 13-camera rig; the rest of the project says 12

**File:** `README.md:3`

**Issue:** "using a 13-camera aquarium rig with refractive calibration". `CLAUDE.md`
describes a "12-camera aquarium rig", and the project notes record 12 core video
cameras with one (`e3v8250`, top-down wide-angle) deliberately skipped. Whichever number
is right, the two documents disagree, and this line is also the PyPI package summary.

**Fix:** Reconcile with `CLAUDE.md`. If the rig physically has 13 cameras but one is
excluded from the pipeline, say so explicitly rather than letting the two docs contradict.

### IN-03: README Documentation section is an empty commented-out placeholder

**File:** `README.md:58-61`

**Issue:** The section body is entirely HTML comments with a `TODO: Uncomment once docs
are deployed`. But `.readthedocs.yaml` exists and is configured, `pyproject.toml:49`
already advertises `Documentation = "https://aquapose.readthedocs.io"`, and this phase
added a docs build to CI. The README renders a "## Documentation" heading with nothing
under it — on GitHub and on PyPI.

**Fix:** Either uncomment the link (if the RTD project is live) or remove the empty
section until it is. Do not ship a heading with no body.

### IN-04: Package metadata authorship does not match the new copyright holder

**File:** `pyproject.toml:12`

**Issue:** `LICENSE` and `docs/conf.py` now attribute copyright to "Tucker Lancaster and
the McGrath Lab at the Georgia Institute of Technology", but
`authors = [{name = "Tucker Lancaster"}]` was left unchanged, so the published package
metadata credits only the individual.

**Fix:** Align with the copyright line, e.g. add a second author entry or a
`maintainers` entry for the lab.

### IN-05: CI actions pinned to mutable major tags, and no job timeout

**File:** `.github/workflows/docs.yml:18,20`

**Issue:** `actions/checkout@v6` and `actions/setup-python@v6` are mutable major-version
tags — a compromised or force-moved tag silently changes what executes. `publish.yml` has
the same pattern, so this is a repo-wide convention rather than a phase-108 regression,
but the phase touched this file. Additionally there is no `timeout-minutes`, so a hung
sphinx build burns the full 6-hour default runner budget.

**Fix:** Pin to full commit SHAs with a version comment (Dependabot updates these
automatically), and add `timeout-minutes: 15` to the job.

### IN-06: MIT-to-AGPL boundary statement does not address the legacy v2.x/v3.x tags

**File:** `LICENSING.md:49-59`

**Issue:** The boundary is framed purely in terms of v1.1.1 → v1.2.0. But the repository
also carries tags `v2.0`, `v2.1`, `v3.1`, `v3.2`, `v3.5`, `v3.6`, `v3.8`, `v3.9`, `v3.10`
(dated March 2026, predating the current v1.x semantic-release scheme). A reader
comparing tag names to the stated boundary will reasonably conclude that `v3.10` is
"after" `v1.1.1` and therefore AGPL, which is the opposite of the intent.

**Fix:** Add a sentence noting that the `v2.x`/`v3.x` tags belong to a superseded internal
versioning scheme, predate the v1.x semantic-release line, and fall on the MIT side of the
boundary. Or delete the obsolete tags if they carry no historical value.

### IN-07: Stray untracked directories left in the working tree after a hygiene phase

**File:** repository root

**Issue:** `git status` reports two untracked entries at the repo root: `11.0/` and `~/`.
Both are almost certainly shell-redirect accidents (a literal `~` directory is the classic
result of a quoted `> ~/...` on Windows, and `11.0` of a stray `2>11.0`-style redirect).
Neither is covered by `.gitignore`, so they show up as untracked noise for every developer
and are one careless `git add -A` away from being committed. For a phase whose explicit
goal was repo hygiene, these are worth sweeping.

**Fix:** Delete both directories after confirming they hold nothing of value. If the
tooling that creates them cannot be fixed, add them to `.gitignore`.

### IN-08: `cli` and `logging` modules absent from the API toctree

**File:** `docs/api/index.rst:4-13`

**Issue:** The repaired toctree covers `calibration`, `core`, `engine`, `evaluation`,
`io`, `synthetic`, `training` — but `src/aquapose/` also contains `cli.py`,
`cli_utils.py`, and `logging.py`, which have no API page. The CLI is the primary user
entry point (`[project.scripts] aquapose = "aquapose.cli:main"`) and is entirely
undocumented in the API reference.

**Fix:** Add `docs/api/cli.rst` (consider `sphinx-click` for proper Click command
rendering rather than raw `automodule`), and add it to the toctree.

### IN-09: `_resolve_release` silently degrades to "0.0.0"

**File:** `docs/conf.py:15-29`

**Issue:** Both fallback paths are silent. If the installed-metadata lookup misses *and*
the `pyproject.toml` read fails, the docs render with `release = "0.0.0"` and
`version = "0.0"` with no signal that version resolution broke — the build still exits 0
even under `-W`. The broad `except (OSError, KeyError, tomllib.TOMLDecodeError)` also
swallows a genuine malformed-pyproject condition.

Note the surrounding refactor is correct and the accompanying comment at lines 39-41 is
accurate: renaming the `importlib.metadata.version` import to `_package_version` genuinely
does fix the bug where the module-level name `version` stayed bound to a function and
corrupted the objects.inv dump. That part is a good catch.

**Fix:** Emit a warning on the final fallback so a silent misconfiguration is visible in
the build log:

```python
    except (OSError, KeyError, tomllib.TOMLDecodeError) as exc:
        print(f"WARNING: could not resolve aquapose version ({exc}); using 0.0.0")
        return "0.0.0"
```

---

## Confirmed Clean

- **`src/aquapose/core/context.py`, `src/aquapose/engine/observers.py`,
  `src/aquapose/synthetic/fish.py`, `src/aquapose/synthetic/scenarios.py`** — verified
  behavior-neutral. The diffs consist solely of wrapping `*_cache.pkl` and
  `radius=1/|curvature|` in double backticks (preventing RST from interpreting `*` and
  `|` as emphasis/substitution markup) and inserting blank lines before enumerated and
  bulleted lists so docutils parses them as lists rather than literal text. No executable
  statement changed. No finding.
- **Relicense text consistency** — a repo-wide grep for `MIT` outside `.planning/` returns
  only intentional historical references in `LICENSING.md` and `CHANGELOG.md`, plus false
  positives from `DEFAULT_FRAME_LIMIT` in `tools/smoke_test.py`. No lingering MIT grant.
  `LICENSE` contains the complete 663-line AGPLv3 text with a correct leading copyright
  line.
- **Docs tree integrity** — `optimization.rst` and `segmentation.rst` were deleted and
  simultaneously removed from `docs/api/index.rst`; no dangling toctree references
  remain. Every toctree target resolves, including the newly added
  `reports/z_uncertainty_report`. `docs/api/engine.rst`'s `:exclude-members:` list
  (`PipelineContext`, `Stage`, `ChunkHandoff`, `load_chunk_cache`) correctly avoids
  duplicate-object warnings under `-W`: all four are genuinely re-exported by both
  `aquapose.core` and `aquapose.engine`, and all four are defined in
  `aquapose.core.context`, so `core.rst` remains their canonical documentation site.
- **`.gitignore`** — the `.planning/` removal is deliberate and safe for distribution:
  `[tool.hatch.build.targets.sdist] exclude` still lists `.planning/`, and the wheel
  target packages only `src/aquapose`. The added `_readthedocs/` entry correctly matches
  the output directory created by `.readthedocs.yaml`'s `cp -r` command.

---

_Reviewed: 2026-08-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
