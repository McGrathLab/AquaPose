---
created: 2026-09-02T00:00:00.000Z
title: Close the core/reid/ import boundary exemptions
area: core
files:
  - src/aquapose/core/reid/cli.py:9
  - src/aquapose/core/reid/cli.py:16
  - src/aquapose/core/reid/cli.py:267
  - src/aquapose/core/reid/cli.py:434
  - src/aquapose/core/reid/swap_detector.py:323
---

## Problem

While closing the `core/` import boundary for `aquapose.io` in Phase 113.1
(plan `113.1-04`, which relocated `discover_camera_videos` into
`core/types/video_discovery.py`), the AST-based guard test
(`tests/unit/core/test_import_boundary.py`) surfaced a second, pre-existing
class of violation that `113.1-CONTEXT.md` did not list: `core/reid/`
imports upper-layer packages in five places.

`113.1-CONTEXT.md`'s "Established Patterns" section claimed
`core/types/frame_source.py:25` was "the only module-level runtime
violation (verified 2026-09-02)." That claim was incomplete. The full scan
against source (not against the claim) found:

- `src/aquapose/core/reid/cli.py:9` — module-level
  `from aquapose.cli_utils import get_project_dir, resolve_run`.
- `src/aquapose/core/reid/cli.py:16` — `TYPE_CHECKING`-guarded
  `from aquapose.training.reid_training import ...` (annotation-only,
  never executes at runtime, but still a Layer-1-to-Layer-3 name
  dependency the guard test treats as in-scope per the phase's own
  "however it is spelled" wording).
- `src/aquapose/core/reid/cli.py:267` — function-local
  `from aquapose.training.reid_training import ...` (executes on call).
- `src/aquapose/core/reid/cli.py:434` — function-local
  `from aquapose.training.reid_training import ...` (executes on call).
- `src/aquapose/core/reid/swap_detector.py:323` — function-local
  `from aquapose.training.reid_training import ...` (executes on call).

All five were deliberately **not fixed** in Phase 113.1 — `113.1-CONTEXT.md`
D-02 fences that phase to the one named import-boundary todo
(`2026-03-06-fix-core-import-boundary-violation-in-frame-source.md`,
already closed by plan `113.1-04`) and forbids widening scope to other
pending todos. Instead, `tests/unit/core/test_import_boundary.py`
allowlists these five entries in its `_KNOWN_EXCEPTIONS` mapping, each with
an inline comment naming this todo, and a second test
(`test_import_boundary_allowlist_has_no_stale_entries`) asserts the
allowlist cannot silently outlive its subject: once these imports are
removed, that test goes red and the allowlist entries must be deleted in
the same change.

## Why this matters

`core/reid/` (RE-ID swap detection, mining, and its CLI) currently has a
hard runtime dependency on `aquapose.training` (for `reid_training`) and
on `aquapose.cli_utils` (for `get_project_dir`/`resolve_run`), both of
which are outside Layer 1. This is the same class of architectural
violation the frame_source fix addressed, just in a module the earlier
audit missed.

## Solution

Options (pick one, following the same reasoning `113.1-04-PLAN.md` used
for `discover_camera_videos`):

1. **Relocate the shared logic into `core/`** if `reid_training`'s
   relevant functions and `get_project_dir`/`resolve_run` are (or can be
   made) pure enough to live in Layer 1 without pulling in engine/CLI
   dependencies of their own. Mirrors the `discover_camera_videos` fix.
2. **Move the CLI-only pieces out of `core/reid/`** — `cli.py`'s role is a
   click command surface, which arguably belongs in `cli/` or `engine/`
   rather than `core/reid/`, in which case only the pure RE-ID logic stays
   in `core/` and the CLI wrapper moves up a layer.
3. **Introduce a Protocol/injection point** so `core/reid/` receives the
   training and project-resolution behavior as constructor arguments,
   mirroring how `ChunkFrameSource` takes pre-resolved objects rather than
   performing discovery itself.

Read the actual call sites before picking — do not assume Option 1 is
correct without checking whether `reid_training` itself has upstream
dependencies that would make relocation relocate the violation rather
than remove it, exactly as `113.1-04-PLAN.md` found for the earlier
`Option 1 vs Option 3` decision on `discover_camera_videos`.

## Verification

- `git diff --stat src/aquapose/core/reid/` before this todo is worked
  is empty (D-02 in Phase 113.1) — this todo is the tracked follow-up.
- After the fix, remove the five corresponding entries from
  `tests/unit/core/test_import_boundary.py`'s `_KNOWN_EXCEPTIONS`. The
  `test_import_boundary_allowlist_has_no_stale_entries` test will fail
  loudly if an entry is left in place after its subject import is gone —
  removing the entries is not optional cleanup, it's required for that
  test to keep passing.
