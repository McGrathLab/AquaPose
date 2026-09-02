---
created: 2026-09-02T00:00:00.000Z
title: Fix the 98-error basedpyright typecheck backlog blocking CI
area: qa
files:
  - src/aquapose/core/reid/runner.py
  - src/aquapose/evaluation/stages/smoothing.py
  - src/aquapose/training/reid_training.py
  - .github/workflows/test.yml
---

## Problem

The `typecheck` job in `.github/workflows/test.yml` has **never passed on `dev`** —
it fails on every run examined (33620368943 on 2026-09-02, 32053867530 and
32051262651 on 2026-08-17). `hatch run typecheck` (basedpyright, `basic` mode)
reports **98 errors, 0 warnings**.

This is a long-standing backlog, not a regression from any recent push. It was
explicitly *not* folded into Phase 113 (a documentation phase) because it is far
too large and touches unrelated subsystems.

Because it fails unconditionally, the Tests workflow can never go fully green,
which blocks the honest **README-02 badge row** in Phase 114.

### Representative error clusters

- `src/aquapose/core/reid/runner.py:120-123` — `"__getitem__" method not defined
  on type "Datatype"` (`reportIndexIssue`); h5py `Dataset`/`Datatype` narrowing.
- `src/aquapose/core/reid/runner.py` — h5py `Dataset` passed where `SupportsInt` /
  `SupportsIndex` / buffer protocol is expected (`reportArgumentType`).
- `src/aquapose/evaluation/stages/smoothing.py:414-415` — `float | Literal[0]`
  passed to `int` parameters `reproj_n_fish_frames` / `reproj_n_residuals`.
- `src/aquapose/training/reid_training.py:197` — `_EmbedderConfig` fails the
  `ReidConfigLike` protocol: the protocol declares writable attributes
  (`model_name`, `batch_size`, `crop_size`, `device`) but the frozen dataclass
  provides read-only ones.
- `src/aquapose/training/reid_training.py:475,811` — `float` passed to `int`
  parameters `alpha` / `beta`.
- A `str` passed to a `Literal['seeded', 'scan']` `mode` parameter.

## Solution

Deserves its own phase. Suggested shape:

1. Capture the exact baseline (`hatch run typecheck` → 98 errors) and group by
   root cause — the clusters above look like perhaps 6–10 underlying issues, not
   98 independent ones.
2. Fix at root cause, not by blanket `# type: ignore`. Most look like genuine
   annotation problems: h5py's `Dataset | Datatype | Group` union needs narrowing,
   `ReidConfigLike` should declare read-only properties to match the frozen
   dataclasses, and several `int` annotations should be `float`.
3. Decide whether `typeCheckingMode` stays `basic` (`pyproject.toml`
   `[tool.basedpyright]`) or is tightened once green.
4. Terminal gate: `hatch run typecheck` exits 0 and the CI `typecheck` job passes.

## Notes

Three sibling CI failures from the same run **were** folded into Phase 113 and
are handled there — do not re-fix them here:

- `pre-commit` / `ruff format` on the two Phase 111 files — fixed in `39a1bf1`.
- Environment-creation `503`s from the cu121 extra index (Phase 113 **D-08**
  removes `UV_EXTRA_INDEX_URL`).
- `test_forward_lut_cast_ray_matches_model` ill-conditioned `acos` (Phase 113
  **D-17/D-18**).

## Fixed

Fixed in Phase 113.2 (`113.2-typecheck-backlog`, plans 01-06). `hatch run
typecheck` went **98 -> 0 errors, 0 warnings, 0 notes**, verified against
the measured pre-phase baseline (commit `d3e6073`) rather than assumed.

**Outcome, gate by gate:**

- Root cause was one dominant cluster, not 98 independent errors (D-01/D-02):
  h5py's `Group.__getitem__`/`File.__getitem__` returns the union
  `Group | Dataset | Datatype`, unnarrowed at the read site, producing
  ~89 of the 98 errors across 5 files. Fixed with a new typed narrowing
  helper, `src/aquapose/core/h5.py` (`require_group`/`require_dataset`),
  raising a real `TypeError` (not a stripped-under-`-O` `assert`) — applied
  at every unnarrowed h5py read in `evaluation/stages/smoothing.py` (43),
  `core/reid/runner.py` (27), `core/stitching.py` (12), and
  `core/reid/swap_detector.py` (7).
- Short-tail errors (~9) fixed at root cause: `ReidConfigLike` protocol
  converted from writable attributes to read-only `@property` stubs to
  match its frozen-dataclass implementers (`training/reid_training.py`,
  5 errors); a click `--mode` value narrowed to a `Literal` via a runtime
  `click.BadParameter` check (`core/reid/cli.py`); a duplicated type
  annotation removed (`core/reconstruction/backends/dlt.py`); a
  heterogeneous dict retyped as a `TypedDict`
  (`evaluation/stages/reconstruction.py`, propagating cleanly into
  `evaluation/runner.py` with zero edits there).
- **Suppression budget: exactly 2 directives added, both rule-scoped
  (`# pyright: ignore[reportArgumentType]`), both in
  `training/reid_training.py`, both attributed inline to
  `pytorch_metric_learning`'s untyped `MultiSimilarityLoss.__init__`
  inferring `int` from integer defaults where the library documents
  `float` hyperparameters.** Repo-wide suppression count: 71 -> 73,
  matching the phase's declared budget exactly. No blanket `# type:
  ignore` anywhere (D-05).
- **D-07 (step 3 of this todo's "Solution"): `typeCheckingMode` stays
  `basic`.** Recorded as its own decision in `PROJECT.md`'s Key Decisions
  table and as a deferred-evaluation todo
  (`2026-09-02-evaluate-tightening-basedpyright-typecheckingmode.md`) —
  not acted on. `pyproject.toml` has a zero-line diff against `d3e6073`.
- Suite stayed at the pre-phase baseline plus exactly one addition: `git
  diff --name-status d3e6073 -- tests/` is a single `A` line for
  `tests/unit/core/test_h5.py` (the new helper's own test, 7 cases). No
  existing test was edited, weakened, skipped or deleted. `hatch run
  test`: 1410 passed (1403 baseline + 7 new), 3 skipped, 17 deselected,
  0 failures.
- `.github/workflows/test.yml`'s `typecheck` job is unchanged (zero-line
  diff against `d3e6073`) and passes on `dev` — confirmed at the
  phase-closing plan's human-verify checkpoint (113.2-06 Task 3).
- Type-position `Any` escape-hatch annotation count: unchanged at 155
  (measured via the exact regex `(:[[:space:]]*Any\b|->[[:space:]]*Any\b|\[Any\b|\bAny\])`
  across `src/aquapose/`) — no error was closed by widening.
- `cast(` call count: unchanged at 49 repo-wide. 46 of these are
  pre-existing `cast(h5py.X, ...)` sites left deliberately unconverted
  (converting a clean `cast()` site to the checked helper adds a runtime
  raise path that did not exist, a behavior change out of scope for a
  typing-only phase per D-06) — tracked as its own finding in
  `2026-09-02-h5py-read-idiom-inconsistency-cast-vs-checked-helper.md`.

**Correction to this todo's own scope (recorded for the honesty of the
record, per this project's standing "verify against source" lesson —
D-01 in `113.2-CONTEXT.md`):** this todo's `files:` frontmatter and
"Representative error clusters" section did not mention
`src/aquapose/core/stitching.py`, which in fact carried **12 of the 98
errors** (the third-largest cluster, larger than `training/reid_training.py`'s
5). The todo's clusters also undercounted `evaluation/stages/smoothing.py`
at "representative" rather than naming it the single largest cluster (43
of 98 — nearly half the backlog). This is the fourth instance in three
phases of a planning document disagreeing with the code (per
`113.2-CONTEXT.md`'s `<specifics>` section); planning against this todo's
file list without re-measuring would have under-scoped the work by 12
errors and mis-prioritized the largest cluster.
