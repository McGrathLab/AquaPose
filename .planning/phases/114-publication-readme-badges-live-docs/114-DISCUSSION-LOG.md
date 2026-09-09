# Phase 114: Publication — README, Badges, Live Docs - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-09
**Phase:** 114-publication-readme-badges-live-docs
**Areas discussed:** Badge row & what's actually live, Hero media, Citation & which DOI, README structure & depth, Release sequencing

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Badge row & what's actually live | Which badges appear and how each becomes honestly green — PyPI needs a real release, coverage needs Codecov linked, docs needs RTD activated | ✓ |
| Hero media — what and how | What the hero shows, what format, where it's hosted | ✓ |
| Citation & which DOI | Software DOI vs the existing dataset DOI; CITATION.cff vs BibTeX | ✓ |
| README structure & depth | How much lives in README vs Read the Docs | ✓ |

**User's choice:** All four areas.

---

## Badge row & what's actually live

### Q1 — PyPI badge honesty

| Option | Description | Selected |
|--------|-------------|----------|
| Cut a real release this phase | Bump to a full version, tag, let publish.yml push to PyPI, then add the badge | |
| TestPyPI first, then real | Validate wheel/sdist and metadata on TestPyPI, then cut the real release | ✓ |
| Omit the PyPI badge for now | Ship other badges, revert install docs to a source install | |

**User's choice:** TestPyPI first, then real.
**Notes:** **Later reversed** — see Release sequencing Q2 below. Final decision is
publish straight to PyPI (CONTEXT.md D-02).

### Q2 — Version number for the first release

| Option | Description | Selected |
|--------|-------------|----------|
| v1.2.0 — follow pyproject | Drop the `-dev.6` suffix, keep semantic-release's chain intact | |
| v0.1.0 — signal alpha | Match the "Development Status :: 3 - Alpha" classifier | |
| v4.0.0 — align to milestone | Match the GSD milestone; one-time semantic-release reset + CHANGELOG note | ✓ |

**User's choice:** v4.0.0 — align to milestone.
**Notes:** Resolves a long-standing split between `pyproject.toml` (1.2.0-dev.6)
and the `v3.x` milestone tags — none of which matched publish.yml's trigger,
which is why nothing had ever published.

### Q3 — Coverage badge

| Option | Description | Selected |
|--------|-------------|----------|
| Codecov badge, whatever it reads | Verify the link, embed the live badge, publish the real number | ✓ |
| Codecov + a codecov.yml floor | Same badge plus a committed project target so coverage can't erode | |
| Drop coverage from the badge row | Trim README-02 | |

**User's choice:** Codecov badge, whatever it reads.

### Q4 — Read the Docs build weight

| Option | Description | Selected |
|--------|-------------|----------|
| Try as-is, add a lean fallback | Activate, build, fall back to a docs-only install if it OOMs | |
| Switch to a lean docs env now | Define a minimal RTD dependency set up front | ✓ |
| Keep hatch, no fallback | Use the existing config unchanged | |

**User's choice:** Switch to a lean docs env now.
**Notes:** **Premise corrected after the answer.** The `docs` hatch env is already
`detached = true` with only Sphinx + extensions + numpy
(`pyproject.toml:88-103`) — it never installs the project or torch, so the OOM
risk described in the question does not exist. The user's intent is already the
live state; the decision reduces to activating RTD with default version `dev`,
with no `pyproject.toml` change (CONTEXT.md D-07, D-08).

---

## Hero media

| Option | Description | Selected |
|--------|-------------|----------|
| 3D reconstruction animation | Looping clip of reconstructed 3D midlines, rendered from Phase 111's animation_3d data | |
| Overlay mosaic (input → evidence) | Crop of the 12-camera overlay grid with predicted midlines on real video | |
| Both: overlay + 3D side by side | Two-panel hero telling the whole story | |

**User's choice:** *Other* — "defer for now, drop hero image from the requirements".
**Notes:** Recorded as a deliberate requirement trim, deferred rather than
deleted. README-03 and ROADMAP success criterion 3 to be marked deferred and a
backlog todo filed. Source assets remain available in the Zenodo deposit.

---

## Citation & which DOI

### Q1 — Which DOI represents the software

| Option | Description | Selected |
|--------|-------------|----------|
| Mint a software DOI too | Zenodo↔GitHub release integration auto-archives on tag; concept DOI stays stable | ✓ |
| Use the dataset DOI for everything | Cite 10.5281/zenodo.22264079 as the project DOI | |
| Software DOI only, later | Ship with no DOI badge and add it at the next release | |

**User's choice:** Mint a software DOI too.
**Notes:** Keeps the dataset DOI with the tutorial where it belongs. Composes
with the v4.0.0 release already decided.

### Q2 — Form of the citation

| Option | Description | Selected |
|--------|-------------|----------|
| CITATION.cff + BibTeX in README | .cff drives the cite button and Zenodo metadata; BibTeX for copy-paste | |
| CITATION.cff only | Single source of truth; README links to the cite button | ✓ |
| BibTeX in README only | One visible block, no new file format | |

**User's choice:** CITATION.cff only.
**Notes:** The existing BibTeX block at `docs/getting-started/tutorial.md:85`
cites the *dataset* and stays as-is.

---

## README structure & depth

### Q1 — How much the README carries

| Option | Description | Selected |
|--------|-------------|----------|
| Tight landing page, funnel to docs | Badges, one-paragraph pitch, quick start, links out, citation, license | ✓ |
| Standard OSS README | The above plus pipeline breakdown, hardware expectations, outputs inline | |
| Full README, docs as reference | Development setup and GPU notes stay in the README | |

**User's choice:** Tight landing page, funnel to docs.
**Notes:** Development and GPU-Support sections move into docs. The GPU section
is now factually wrong following Phase 113's D-08 (cu121 pin removed), so it
cannot simply be carried over.

### Q2 — Stale `tlancaster6` URL cleanup (Phase 113 carry-in)

| Option | Description | Selected |
|--------|-------------|----------|
| Fix live docs, leave CHANGELOG | Correct CODE_OF_CONDUCT.md and docs/contributing.md only | ✓ |
| Fix everything including CHANGELOG | Sweep all ~831 occurrences | |
| Defer the whole cleanup | Keep 114 to README/badges/citation/RTD only | |

**User's choice:** Fix live docs, leave CHANGELOG.

---

## Release sequencing

### Q1 — The circular DOI dependency

| Option | Description | Selected |
|--------|-------------|----------|
| Two passes — backfill after release | Pass A: .cff without DOI + webhook + tag → Zenodo mints. Pass B: backfill the concept DOI | ✓ |
| Manual deposit, reserve DOI first | Hand-created draft with a reserved DOI; correct in one pass but manual forever | |
| You decide | Let the planner pick at execution time | |

**User's choice:** Two passes — backfill after release.
**Notes:** Accepted consequence — the v4.0.0 tagged snapshot does not itself
carry the DOI. The concept DOI never changes again, so it's a one-time cost.

### Q2 — TestPyPI dry run mechanics

| Option | Description | Selected |
|--------|-------------|----------|
| Local build + twine upload | Manual TestPyPI upload, verify install, then tag | |
| Add a workflow_dispatch TestPyPI job | Extend publish.yml so the dry run exercises the real path | |
| Skip TestPyPI, go straight to PyPI | Tag and publish directly, accepting immutable-filename risk | ✓ |

**User's choice:** Skip TestPyPI, go straight to PyPI.
**Notes:** **Reverses the earlier "TestPyPI first" selection.** The immutable-
filename risk (a bad first upload burns v4.0.0 and forces v4.0.1) was stated
before the choice and accepted. Compensating rigor moves to pre-tag local
verification.

---

## Claude's Discretion

- Badge providers (shields.io vs native), ordering, and style.
- Whether the tests badge targets `test.yml` on `dev` or `main`, and whether the
  `typecheck` job gets its own badge.
- Exact wording and length of the README's opening framing paragraph.
- Whether RTD also publishes a `stable` version alongside the `dev` default.
- The pre-tag verification checklist compensating for the no-TestPyPI decision.

## Deferred Ideas

- Hero media (README-03 + ROADMAP criterion 3) — deferred, not deleted.
- A `codecov.yml` coverage floor/target.
- A `workflow_dispatch` TestPyPI job in `publish.yml`.
- The ~829 historical `tlancaster6` links in `CHANGELOG.md`.
- An RTD `stable` version tracking release tags.
