# Phase 112: Config & CLI Reference - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-01
**Phase:** 112-config-cli-reference
**Areas discussed:** Generation mechanism, Config tiering scheme, CLI scope & tier mirror, IA & page placement

---

## Generation mechanism — CLI

| Option | Description | Selected |
|--------|-------------|----------|
| sphinx-click (auto) | Add sphinx-click; render every command/group with options auto-pulled from Click. Always in sync. Hand-author worked examples. | ✓ |
| Hand-authored pages | Curated pages per command group, matching Phase 110 D-08; full control but manual sync (drift risk). | |
| Hybrid | sphinx-click for argument tables wrapped in hand-authored section pages. | |

**User's choice:** sphinx-click (auto)
**Notes:** CLI help text lives on the command and can't drift from it — so auto-gen here doesn't hit the concern Phase 110 had for module API docs.

## Generation mechanism — Config

| Option | Description | Selected |
|--------|-------------|----------|
| Curated tiered pages | Hand-authored config reference organized by tier; text adapted from existing docstrings. Only option that cleanly satisfies DOCS-06 tiering. | ✓ |
| Auto-generated from source | Build-time script introspects dataclasses, emits reference tables; tiering via curated field→tier map. | |
| autodoc + curated overlay | Keep autodoc full detail in API ref; add a separate curated 'essential fields' tier page. | |

**User's choice:** Curated tiered pages
**Notes:** Flat autodoc can't produce the DOCS-06 tiering; curation matches Phase 110 D-08.

## Generation mechanism — Drift guard

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — add a test | pytest introspects the 9 dataclasses and asserts every field appears in the reference. | |
| No — keep it simple | Ship curated pages without an automated check; rely on reviewers. | ✓ |
| You decide | Let planner/researcher weigh it. | |

**User's choice:** No — keep it simple

---

## Config tiering scheme — tier structure

| Option | Description | Selected |
|--------|-------------|----------|
| Two tiers | Essential vs Advanced; maps onto what `init` scaffolds vs what you tune. | ✓ |
| Three tiers | Essential / Tunable / Expert. | |
| By-stage + essentials callout | Per-stage pages with an 'essential fields' quick-reference up top. | |

**User's choice:** Two tiers

## Config tiering scheme — page layout

| Option | Description | Selected |
|--------|-------------|----------|
| Essential table + Advanced by stage | Tier 1 = flat 'Essential fields' table; Tier 2 = per-stage subsections. | ✓ |
| Both tiers grouped by stage | All fields under stage subsections; essentials marked with a badge. | |
| You decide | Let planner choose layout. | |

**User's choice:** Essential table + Advanced by stage

## Config tiering scheme — coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Everything (all ~86) | Document all 9 stage dataclasses + top-level PipelineConfig (18) + ReidConfig. | ✓ |
| 9 dataclasses only | Only the 9 stage configs per roadmap literal; top-level separately. | |
| You decide | Let researcher reconcile the inventory. | |

**User's choice:** Everything (all ~86)
**Notes:** Roadmap's "71 across 9 dataclasses" is an undercount; essential fields like `n_animals` live on PipelineConfig.

---

## CLI scope & tier mirror — tiering

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror the 110 split | Two sections: Core Pipeline commands vs Research/Training commands. | |
| Flat, grouped by Click group | One section, commands by natural Click grouping; sphinx-click structure drives it. | ✓ |
| You decide | Let planner choose. | |

**User's choice:** Flat, grouped by Click group

## CLI scope & tier mirror — worked examples

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 111 tutorial dataset | Runnable commands against the published dataset; soft dependency on Phase 111. | |
| Generic illustrative | Placeholder project/paths; self-contained, not coupled to Phase 111. | ✓ |
| You decide | Per-command decision by planner. | |

**User's choice:** Generic illustrative examples

---

## IA & page placement — placement

| Option | Description | Selected |
|--------|-------------|----------|
| New top-level 'Reference' section | CLI + Config Reference pages alongside 'API Reference'. | ✓ |
| Fold into API Reference | Add pages inside the existing API Reference section. | |
| You decide | Let planner choose. | |

**User's choice:** New top-level 'Reference' section

## IA & page placement — overlap with Phase 110 pages

| Option | Description | Selected |
|--------|-------------|----------|
| Keep both, cross-link | Leave api/ automodule pages as-is (serve DOCS-02); cross-link to the new Reference pages. | ✓ |
| Trim API pages to avoid dupe | Slim api/cli.rst and api/engine.rst; risks reopening DOCS-02 guarantee. | |
| You decide | Let planner decide cross-link vs trim. | |

**User's choice:** Keep both, cross-link

---

## Claude's Discretion

- Exact sphinx-click directive form and where worked examples attach.
- Reference landing-page wording and Essential-table columns.
- Whether the two Reference pages share an index page; cross-link phrasing.
- Per-stage subsection ordering within the Advanced config tier.
- Any `autodoc_mock_imports` additions needed to keep `-W` green.

## Deferred Ideas

- Runnable, dataset-anchored examples → Phase 113 tutorial.
- Automated config-doc drift-guard → declined (D-03); revisit if config churn increases.
- Read the Docs publish / docs landing redesign → Phase 114.
