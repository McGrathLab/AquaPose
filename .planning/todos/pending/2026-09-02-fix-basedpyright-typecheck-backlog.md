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
