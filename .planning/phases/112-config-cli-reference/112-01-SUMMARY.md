---
phase: 112-config-cli-reference
plan: "01"
subsystem: docs
tags: [sphinx, sphinx-click, docs-build, autodoc]
dependency_graph:
  requires: []
  provides: [sphinx-click extension wired, docs env resolved, CLI import graph verified]
  affects: [docs/conf.py, pyproject.toml]
tech_stack:
  added: [sphinx-click]
  patterns: [detached hatch docs env, autodoc_mock_imports]
key_files:
  modified:
    - pyproject.toml
    - docs/conf.py
decisions:
  - "sphinx-click added as docs-only build-time dependency (hyphenated PyPI name); registered as sphinx_click.ext (underscore dotted import name)"
  - "autodoc_mock_imports already complete — no additions needed; CLI import graph (click, yaml, cv2, numpy, torch, timm, pytorch_metric_learning, ultralytics, scipy, shapely, sklearn, etc.) fully covered by existing list"
metrics:
  duration: ~10m
  completed: "2026-09-02"
  tasks_completed: 2
  files_modified: 2
---

# Phase 112 Plan 01: sphinx-click Foundation Summary

Wire `sphinx-click` into the detached docs build so the CLI reference page can auto-render every Click command group. Confirms that `autodoc_mock_imports` fully covers `aquapose.cli:cli` import graph before any `.. click::` directive is rendered.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Add sphinx-click to docs env; register sphinx_click.ext extension | ac916c9 | pyproject.toml, docs/conf.py |
| 2 | Verify autodoc_mock_imports covers aquapose.cli:cli import graph | (no changes needed) | — |

## What Was Done

### Task 1: sphinx-click dependency and extension registration

Added `sphinx-click` (hyphenated) to the `[tool.hatch.envs.docs].dependencies` list in `pyproject.toml`, after `sphinxcontrib-mermaid`. Added `"sphinx_click.ext"` (underscored, `.ext` submodule) to the `extensions` list in `docs/conf.py`, after `"sphinxcontrib.mermaid"`. Removed the docs env (`hatch env remove docs`) to force reinstallation with the new package. `hatch run docs:build` exits 0 with no warnings — the extension loads cleanly.

### Task 2: autodoc_mock_imports verification

Cross-read the CLI import chain:
- `cli.py` top-level: `click`, `yaml`, `aquapose.cli_utils`, `aquapose.core.reid.cli`, `aquapose.engine`, `aquapose.engine.orchestrator`, five training subgroups
- `core/reid/cli.py`: uses `TYPE_CHECKING` guard for `numpy`, `timm` (only `click` and first-party at runtime)
- `training/cli.py`: `click` only (first-party only otherwise)
- `training/data_cli.py`: `click`, `logging`, stdlib only at runtime (TYPE_CHECKING guard for store)
- `training/prep.py`: `click`, `numpy`, `yaml`
- `training/pseudo_label_cli.py`: `click`, `cv2`, `numpy` plus first-party training modules

All third-party top-level imports reachable at runtime (`click`, `yaml`, `cv2`, `numpy`, `torch`, `timm`, `pytorch_metric_learning`, `ultralytics`, `scipy`, `shapely`, `sklearn`, `skimage`, `h5py`, `plotly`, `PIL`, `igraph`, `leidenalg`, `loguru`, `aquacal`, `pycocotools`, `matplotlib`, `boxmot`) are already present in `autodoc_mock_imports`. No additions were required. `hatch run docs:build` exits 0 with zero import warnings.

## Verification

- `hatch run docs:build` exits 0 — confirmed twice (initial build + re-run)
- `pyproject.toml` contains `sphinx-click` in docs dependencies
- `docs/conf.py` contains `"sphinx_click.ext"` in extensions list
- No `WARNING` or `No module named` messages in either build log
- `sphinx-click` noted in build output: `[extensions changed ('sphinx_click.ext')] 23 added`

## Deviations from Plan

None — plan executed exactly as written. The mock list was already complete; Task 2 required no code changes.

## Threat Flags

None. `sphinx-click` is a docs-build-time-only dependency; no runtime attack surface introduced. Supply-chain risk (T-112-SC) is accepted as [TRUSTED] per the threat model — `sphinx-click` is a mature, widely-used Sphinx extension.

## Self-Check: PASSED

- [x] `pyproject.toml` modified — confirmed (contains `sphinx-click`)
- [x] `docs/conf.py` modified — confirmed (contains `sphinx_click.ext`)
- [x] Commit ac916c9 exists — confirmed
- [x] `hatch run docs:build` exits 0 — verified twice
- [x] No import warnings in build log — verified
