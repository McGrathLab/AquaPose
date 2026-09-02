---
created: 2026-09-02T00:00:00.000Z
title: Evaluate tightening basedpyright typeCheckingMode beyond basic
area: qa
files:
  - pyproject.toml
---

## Problem

Phase 113.2 closed the entire `hatch run typecheck` backlog (98 -> 0 errors)
under `pyproject.toml`'s committed `typeCheckingMode = "basic"`
(`[tool.basedpyright]`). The originating todo
(`.planning/todos/done/2026-09-02-fix-basedpyright-typecheck-backlog.md`,
step 3 of its "Solution") asked whether `typeCheckingMode` should stay
`basic` or be tightened (e.g. to `standard` or `strict`) now that the tree
is green.

**D-07** (`.planning/phases/113.2-typecheck-backlog/113.2-CONTEXT.md`)
decided this explicitly: `typeCheckingMode` **stays `basic` for Phase
113.2**. Whether to tighten it is a separate decision, deliberately
deferred rather than made. This todo is that deferred decision, recorded
so it does not silently vanish once the phase archives.

## What tightening would involve

`basic` mode is more permissive than `standard` (basedpyright's own
default) or `strict`. Moving up a tier would very likely resurface a new
error backlog, not on the file/error content already closed by Phase
113.2 (which is already narrowed at the h5py boundary, root-caused, not
suppressed) but on real inference gaps `basic` mode currently tolerates
and `standard`/`strict` would flag — most plausibly:

- Missing/incomplete parameter and return type annotations that `basic`
  does not require but `standard` does (`reportMissingParameterType`,
  `reportUnknownParameterType`, etc. are more assertive under `standard`).
- The 155 type-position `Any` escape-hatch annotations across
  `src/aquapose/` (measured 2026-09-02, unchanged by Phase 113.2) — under
  `standard`/`strict`, several of basedpyright's `Unknown`-adjacent rules
  (`reportUnknownMemberType`, `reportUnknownVariableType`) start firing on
  code that currently resolves silently to `Any`.
- The 49 `cast(` calls in `src/aquapose/` (46 of which are the
  `cast(h5py.X, ...)` narrowing sites tracked by the sibling todo
  `2026-09-02-h5py-read-idiom-inconsistency-cast-vs-checked-helper.md`) —
  a stricter mode may treat some of these narrowing casts differently,
  particularly around third-party libraries (`h5py`, `pytorch_metric_learning`)
  that ship no `py.typed` marker.
- The two `# pyright: ignore[reportArgumentType]` suppressions in
  `training/reid_training.py` (added in 113.2-02, bounding an untyped
  `pytorch_metric_learning.MultiSimilarityLoss.__init__`) would need
  re-verification under the new mode's inference behavior.

## What must be re-measured first

Before starting this work, re-run the same measurement discipline Phase
113.2 used (CONTEXT: "verify against source," the fourth instance in
three phases of a planning document disagreeing with the code):

1. Flip `typeCheckingMode` to `standard` locally (not committed) and run
   `hatch run typecheck` to get a fresh baseline error count and file/rule
   distribution — do not assume the shape from this todo's list above.
2. Re-run the four Phase 113.2 anti-suppression gates against the new
   baseline before any fix work starts: suppression-directive count,
   `Any` escape-hatch count, `cast(` count, and the CI `typecheck` job
   command — so this todo's eventual closure can prove the same "zero
   reached honestly" standard Phase 113.2 established, not merely
   "zero reached."
3. Decide scope: this could be its own phase (the same shape Phase 113.2
   was) rather than a quick todo, if the resurfaced backlog is
   comparably sized.

## Solution

Not scoped yet — the re-measurement above determines whether this is a
small follow-up or its own phase. Do not tighten `typeCheckingMode` as a
side effect of unrelated work; this decision needs its own visibility per
D-06/D-07's "surface, don't fold in" principle.

## Notes

Filed by `113.2-06` (the Phase 113.2 closing plan) per ROADMAP criterion 4
and D-07. `pyproject.toml` was not touched to create this todo — the
decision is recorded, not acted on.
