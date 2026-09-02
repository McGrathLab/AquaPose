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
