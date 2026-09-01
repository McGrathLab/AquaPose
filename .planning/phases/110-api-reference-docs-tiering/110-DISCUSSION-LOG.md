# Phase 110: API Reference & Docs Tiering - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-01
**Phase:** 110-api-reference-docs-tiering
**Areas discussed:** Tier taxonomy & boundaries, Tier presentation & status labels, API reference structure (IA), Generation mechanism

---

## Tier taxonomy & boundaries

Roadmap already fixed tier-1 (detection/tracking/association/pose/reconstruction/
calibration/engine) and tier-2 (training/evaluation/core.reid/pseudo-labeling). Open
question was where cross-cutting modules land.

| Option | Description | Selected |
|--------|-------------|----------|
| Runtime = tier-1, tooling = tier-2 | core/types/, io/, cli.py, engine observers join tier-1; synthetic/ and evaluation/viz/ go tier-2. Tier line = "can an outside user run the pipeline." | ✓ |
| Minimal tier-1 | Strictly the 5 stages + calibration + engine core; core/types/, io/, cli.py, synthetic/ all tier-2. | |
| You decide | Claude classifies each module by the run/consume heuristic. | |

**User's choice:** Runtime = tier-1, tooling = tier-2
**Notes:** Sets the tier line at "needed to run or consume the production pipeline."

---

## Tier presentation & status labels

| Option | Description | Selected |
|--------|-------------|----------|
| Two top-level sections | API index splits into "Core Pipeline" and "Research Utilities" toctrees; split visible in sidebar. | ✓ |
| One list + per-page banners | Single flat module list, tier-2 pages carry a status admonition. | |
| Both: sections + banners | Two sections AND per-page banners. | |

**User's choice:** Two top-level sections

| Option | Description | Selected |
|--------|-------------|----------|
| "Research utility — not part of the supported pipeline API" | Honest, provided-as-is, not sounding broken. | ✓ |
| "Internal / unstable API" | Shorter, but "internal" undersells real user-facing research tools. | |
| You decide the exact wording | Claude drafts honest tier-2 status text. | |

**User's choice:** "Research utility — not part of the supported pipeline API"
**Notes:** Because sections (not per-page banners) were chosen, the label lands as a
section-level note on the Research Utilities index rather than on every page.

---

## API reference structure (IA)

| Option | Description | Selected |
|--------|-------------|----------|
| By pipeline stage narrative | Detection → Tracking → Association → Pose → Reconstruction, framed by calibration/engine/types/io; matches GUIDEBOOK. | ✓ |
| Mirror src/ package layout | Reference tree mirrors src/aquapose/ alphabetically; mechanical but loses narrative. | |
| You decide | Stage narrative where it helps, package layout for framing modules. | |

**User's choice:** By pipeline stage narrative

| Option | Description | Selected |
|--------|-------------|----------|
| One page per package/subpackage | e.g. one "Association" page for all of core/association/*. | ✓ |
| One page per module | Every .py its own page (~120 pages). | |
| You decide | Per-package default, split only where large. | |

**User's choice:** One page per package/subpackage

---

## Generation mechanism

Framed with the note that the chosen narrative + per-package IA makes
`autosummary --recursive` (per-module, package-order) a poor fit.

| Option | Description | Selected |
|--------|-------------|----------|
| Curated toctree + per-package automodule rst | Hand-authored curated index + one rst per package that automodules its submodules; ~15-20 files; full control, stable under -W. | ✓ |
| sphinx-apidoc generated, then curated | Mechanical rst gen then hand-edit; regeneration overwrites curation and drifts. | |
| autosummary --recursive | Auto-generated stubs, near-zero upkeep, but per-module + package-order fights the chosen IA. | |

**User's choice:** Curated toctree + per-package automodule rst

---

## Claude's Discretion

- Exact per-package page splits within a large package (allowed by the per-package decision).
- Precise rst wording/headings and how framing modules thread around the stage narrative.
- Whether to keep or drop the existing engine.rst `:exclude-members:` list once submodules are documented.

## Deferred Ideas

- CLI command reference + config-field reference — Phase 112 (DOCS-05/06).
- Concepts page, install guide, tutorial — Phase 113 (DOCS-03/04/07).
- README, badges, hero media, docs landing redesign — Phase 114.
- `pip install aquapose[research]` extra for tier-two — future requirement PKG-01.

## Process note

User paused the dialogue before context generation to enable remote-control, then
resumed with "ready". No decisions changed during the pause.
