---
created: 2026-09-02T00:00:00.000Z
title: calibrate-keypoints config update is a non-atomic read-modify-write
area: training
files:
  - src/aquapose/training/prep.py
---

## Problem

`calibrate_keypoints` (`src/aquapose/training/prep.py`, config writer around
lines 288-306) updates `config.yaml` via a read-then-write round trip:

```python
    with config_path.open() as fh:
        config_data = yaml.safe_load(fh) or {}

    if "pose" not in config_data:
        config_data["pose"] = {}
    config_data["pose"]["keypoint_t_values"] = t_values_list
    # ... (legacy `midline.keypoint_t_values` deletion) ...

    with config_path.open("w") as fh:
        yaml.dump(config_data, fh, default_flow_style=False, sort_keys=False)
```

Between the read and the write, `config_path` is open, closed, then reopened
in truncate mode (`"w"`). If the process is interrupted (killed, crashes,
`Ctrl-C`) between the `yaml.safe_load` and the `yaml.dump` completing, or if a
concurrent writer touches the same file, the user's `config.yaml` can be left
truncated or corrupted — the read happened, but the write clobbered the file
before or without completing.

## Solution

Write to a temporary file in the same directory, then atomically rename it
over `config_path` (`os.replace` / `Path.replace`), the standard
temp-file-plus-atomic-rename shape:

```python
    tmp_path = config_path.with_suffix(config_path.suffix + ".tmp")
    with tmp_path.open("w") as fh:
        yaml.dump(config_data, fh, default_flow_style=False, sort_keys=False)
    tmp_path.replace(config_path)
```

This makes the write atomic from the filesystem's perspective: readers
either see the old complete file or the new complete file, never a partial
one.

## Notes

Found during Phase 113.1's read of `prep.py`'s config writer while filing the
already-implemented LUT-generation todo (113.1-03, D-03). Recorded as a
backstop concern in `113.1-01-PLAN.md`'s `concurrency` edge rather than an
acceptance criterion for that plan, and not fixed there or here — this todo
tracks the remaining fix.
