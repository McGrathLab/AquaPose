---
phase: 112-config-cli-reference
plan: "02"
subsystem: docs
tags: [sphinx, sphinx-click, cli, reference]
dependency_graph:
  requires: [112-01]
  provides: [docs/reference/cli.rst]
  affects: []
tech_stack:
  added: []
  patterns: [sphinx-click directive page, RST directive-page shape, generic CLI placeholder examples]
key_files:
  created:
    - docs/reference/cli.rst
  modified: []
decisions:
  - "Directive targets aquapose.cli:cli (the Click group object), not main() — sphinx-click requires the group"
  - "All worked examples use generic aquapose -p myproject placeholder style per D-09 threat mitigation"
  - ":nested: full recurses into all five registered subgroups (data/train/prep/pseudo-label/reid)"
metrics:
  duration: "~10m"
  completed: "2026-09-01"
  tasks_completed: 1
  tasks_total: 1
  files_created: 1
  files_modified: 0
---

# Phase 112 Plan 02: CLI Reference Page Summary

## One-liner

sphinx-click directive page for all AquaPose CLI commands with worked examples per group in generic placeholder style.

## What Was Built

Created `docs/reference/cli.rst` — the user-facing CLI reference page that auto-renders every command and subcommand via the `sphinx-click` directive, interleaved with hand-authored worked examples for all command groups.

### Task 1: Create docs/reference/cli.rst (commit e333b62)

**Files created:**
- `docs/reference/cli.rst` — RST page with:
  - RST title `CLI Reference` with `=` underline
  - Intro paragraph noting `--project/-p` is a top-level argument placed before the subcommand
  - `:doc:` cross-reference to `../api/cli`
  - `.. click:: aquapose.cli:cli` directive with `:prog: aquapose` and `:nested: full`
  - 13 `.. code-block:: bash` worked examples covering all command groups: `run`, `init`, `eval`, `eval-compare`, `tune`, `viz`, `stitch`, `smooth-z`, `data`, `train`, `prep`, `pseudo-label`, `reid`
  - All examples use `aquapose -p myproject ...` generic placeholder style

## Deviations from Plan

None — plan executed exactly as written.

## Verification

- `docs/reference/cli.rst` exists: confirmed
- Contains `.. click:: aquapose.cli:cli`: confirmed
- Contains `:prog: aquapose`: confirmed
- Contains `:nested: full`: confirmed
- Contains `aquapose -p myproject`: confirmed (13 code-block examples)
- Contains `:doc:` cross-reference to `../api/cli`: confirmed
- No tutorial-specific paths: confirmed
- `docs/api/cli.rst` unmodified: confirmed (git diff empty)

## Known Stubs

None. This is a documentation-only page; no data stubs apply.

## Threat Flags

None. Documentation-only page. All worked examples use generic placeholder paths (`aquapose -p myproject`) with no real credentials, tokens, or dataset-specific absolute paths — T-112-02-I mitigation applied as planned.

## Self-Check: PASSED

- `docs/reference/cli.rst` exists: FOUND
- Commit e333b62 exists: FOUND
