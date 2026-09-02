---
created: 2026-09-02T00:00:00.000Z
title: h5py read idiom inconsistency — cast() vs. the checked require_* helper
area: core
files:
  - src/aquapose/core/reid/swap_detector.py:291-294,804-805
  - src/aquapose/core/stitching.py:80-86,363-365,673,707-708
  - src/aquapose/core/reid/runner.py:74-76
  - src/aquapose/core/reid/miner.py:214-219,271-274
  - src/aquapose/io/midline_writer.py:220,223,288-299,307,314
---

## Problem

Phase 113.2 (`.planning/phases/113.2-typecheck-backlog/`) closed the
basedpyright typecheck backlog by adding `src/aquapose/core/h5.py`
(`require_group`/`require_dataset`) — a narrowing helper that performs a
real `isinstance` check and raises `TypeError` naming the key and file on
mismatch — and applying it at every h5py read site that basedpyright
flagged as unnarrowed (`Group | Dataset | Datatype` union errors).

**The codebase now has two idioms for the same operation, and the
clean-looking one is the unsafe one.** 46 pre-existing
`cast(h5py.Dataset, ...)` / `cast(h5py.Group, ...)` sites remain across
5 files, doing the identical job (narrow an h5py subscript read to a
concrete type) with `typing.cast`, which is **purely a static-analysis
annotation** — it performs no runtime check at all. If the object at that
key is not actually the cast-to type (e.g. a malformed or partially
written HDF5 file, wrong dataset renamed to a group, etc.), `cast(...)`
silently returns the wrong-shaped object and the failure surfaces later
and less legibly (an `AttributeError`/`TypeError` deep in downstream code
using the mistyped object, with no indication of which h5py read produced
it) — whereas `require_dataset`/`require_group` raise immediately, at the
read site, naming the key and file.

A reader skimming the diff sees `cast(h5py.Dataset, grp["frame_index"])`
and `require_dataset(grp, "frame_index")` side by side in the *same file*
(`core/stitching.py`, `core/reid/runner.py`, `core/reid/swap_detector.py`
all now mix both idioms) with no indication that one is checked and the
other is not — the more verbose one (`require_dataset`) is actually the
safer one, which is the opposite of the usual "verbose = careful" reading
cue.

## Why Phase 113.2 left this in place

D-06 (`113.2-CONTEXT.md`) scopes the phase to typing fixes only — no
behavior change. Converting a `cast(h5py.X, ...)` site (which already
typechecks clean) to `require_dataset`/`require_group` **adds a runtime
raise path that did not exist before**: a read that previously would
silently proceed with a wrong-typed object now raises `TypeError`. That
is a real behavior change (new failure mode on malformed input), not a
typing change, so plans 01/04/05 each deliberately left every pre-existing
`cast(h5py...)` site unconverted, even in files they otherwise fully
migrated to the checked helper. This is recorded identically in
113.2-01-SUMMARY.md, 113.2-04-SUMMARY.md, and 113.2-05-SUMMARY.md as a
named, intentional carry-forward for this todo.

## Exact remaining `cast(h5py` sites (measured 2026-09-02, post-Phase-113.2)

`grep -rn 'cast(h5py' src/aquapose/ --include=*.py | wc -l` → **46**

Touched by Phase 113.2 (now mixing both idioms in the same file):

- `src/aquapose/core/reid/swap_detector.py:291,292,293,294` — constructor
  read-only block (`grp`, `_frame_index`, `_fish_id`, `_points`)
- `src/aquapose/core/reid/swap_detector.py:804,805` — repair block (`grp`,
  `fish_id_ds`)
- `src/aquapose/core/stitching.py:80,81,82,83,84,85,86` — read block
  (`grp`, `frame_index`, `fish_id`, `points`, `arc_length`, `n_cameras`,
  `mean_residual`)
- `src/aquapose/core/stitching.py:363,364,365` — a second read block
  (`grp`, `fish_id_ds`, `n_cameras_ds`)
- `src/aquapose/core/stitching.py:673` — `grp` in a third block
- `src/aquapose/core/stitching.py:707,708` — `apply_swap_repairs`'s
  `grp`/`fish_id_ds` (the `frame_index` read in this same function was
  converted to `require_dataset` in 113.2-04; `grp`/`fish_id_ds` were not)
- `src/aquapose/core/reid/runner.py:74,75,76` — a first read block (`grp`,
  `frame_index`, `fish_id_arr`); the four ID-mapping reads in
  `_build_prestitch_to_stitched_map` were converted to `require_dataset`
  in 113.2-04, this earlier block was not

Not touched by Phase 113.2 (already typechecked clean before the phase
started, no mixed idiom within these files — but same unchecked pattern):

- `src/aquapose/core/reid/miner.py:214,215,216,217,218,219` and `:271,272,273,274`
- `src/aquapose/io/midline_writer.py:220,223,288,291,292,293,294,295,296,297,298,299,307,314`

## Also folded into this todo: the unreachable `points is None` guard

**`src/aquapose/core/stitching.py:563`** — `if points is None:` — found
unreachable during 113.2-04. Once the preceding read is
`points = require_dataset(grp, "points")[:]`, `points` is always an
`ndarray` (`require_dataset` returns or raises, never `None`; `[:]`
subscript on a `Dataset` yields an array). The guard cannot trigger.

Not deleted in Phase 113.2 (D-06 scope: typing fixes only, no logic
changes) — deleting it is a genuine logic edit, and it changes the
function's defensive posture toward a malformed/legacy H5 file (the
guard was written when the read's static type could plausibly be
`None`-shaped to a reader, even though `f["midlines"]["points"]` raises
`KeyError` rather than returning `None` at runtime — so the guard never
actually protected against a real `None` value, only a hypothetical
one implied by the old union type). Recommend removing it as part of
this todo's cleanup, once the broader `cast()` -> `require_*` conversion
decision below is made (removing dead code alongside the read-site
change it depends on, rather than as a separate isolated edit).

## Solution

Not scoped for immediate action — options to weigh when this is picked
up:

1. **Convert all remaining `cast(h5py...)` sites to `require_dataset`/
   `require_group`.** Makes the idiom uniform and every h5py read
   fail-fast with a real error. This is a genuine behavior change (new
   raise paths on malformed files) and needs its own review/testing pass,
   not a typing-phase drive-by — probably worth doing under whatever the
   Phase 113.2 D-07 tightening decision produces (same "re-measure, don't
   assume" discipline), since a stricter `typeCheckingMode` may itself
   start flagging some of these `cast()` sites for other reasons.
2. **Leave `cast()` as the intentional idiom for read paths considered
   "trusted" (files this codebase always writes itself)** and document
   the split explicitly in `core/h5.py`'s module docstring, so a future
   reader understands the distinction is deliberate rather than
   incomplete migration. Lower effort, but keeps the fail-fast/silent-cast
   inconsistency live in the codebase.
3. Some hybrid: convert only the sites reading external/legacy-format
   files (higher malformation risk) and leave `cast()` for freshly-created
   in-pipeline files.

Whichever option is chosen, remove `stitching.py:563`'s unreachable guard
as part of the same change (it depends on the read site's type, so they
should move together).

## Notes

Filed by `113.2-06` (the Phase 113.2 closing plan), consolidating findings
from `113.2-01-SUMMARY.md` (scope decision, `_compute_reproj_stats`
lossless-`int()`-coercion note — unrelated finding, already resolved
in-plan, not carried here), `113.2-04-SUMMARY.md` (unreachable guard,
`cast()` scope decision) and `113.2-05-SUMMARY.md` (`cast()` scope
decision, confirmed the pattern spans all touched h5py-heavy files).
