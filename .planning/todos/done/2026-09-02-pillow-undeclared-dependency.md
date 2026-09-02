---
created: 2026-09-02T00:00:00.000Z
title: pillow is imported directly but not a declared dependency
area: tooling
files:
  - pyproject.toml
  - src/aquapose/training/coco_interchange.py
  - src/aquapose/training/labelstudio_export.py
  - src/aquapose/training/prep.py
---

## Problem

`pillow` (imported as `PIL`) is imported at module level by three
`training/` modules, but `pyproject.toml`'s `dependencies` list (lines
26-45) does not include `pillow`:

```
$ grep -n "^from PIL\|^import PIL" src/aquapose/training/*.py
src/aquapose/training/coco_interchange.py:10:from PIL import Image
src/aquapose/training/labelstudio_export.py:10:from PIL import Image
src/aquapose/training/prep.py:19:from PIL import Image, UnidentifiedImageError
```

Today this resolves only transitively, through `ultralytics` and
`torchvision` both depending on `pillow`. If either of those dependencies
ever drops or narrows its own `pillow` requirement, all three importing
modules break with an `ImportError` that gives no hint the real cause is a
missing direct dependency declaration.

## Solution

Add `"pillow>=..."` to `dependencies` in `pyproject.toml` (pin a floor
version compatible with the currently-resolved transitive version). One-line
fix — deliberately not made in 113.1-03, whose fences forbid running `hatch
env create` / `env prune` / `env remove` (declaring a new direct dependency
would invite an environment rebuild to verify resolution, which those fences
block for this phase).

## Notes

Found during Phase 113.1 (113.1-03, D-03) while verifying evidence for the
LUT-generation todo's closure and cross-checking `prep.py`'s imports after
113.1-01 added a third `PIL` import there (`_resolve_sibling_image`, D-08's
arc-length fix).

## Fixed

Fixed in Phase 113.1, plan 07 (113.1-07). Added `"pillow>=10.0"` to
`dependencies` in `pyproject.toml`. The floor was chosen above every real
constraint rather than at the bare minimum: the code's own API floor is
7.0.0 (`UnidentifiedImageError`, imported in `prep.py`), `ultralytics`
declares `pillow>=7.1.2`, and `torchvision` declares
`pillow!=8.3.*,>=5.3.0` (both read from installed package metadata via
`importlib.metadata.requires(...)`, not assumed). The installed version in
the working environment is 12.1.1, comfortably satisfying `>=10.0`.
`hatch run lint` and `hatch run docs:build` both exit 0 with the new
dependency declared; no `hatch env` command was run to verify resolution.
