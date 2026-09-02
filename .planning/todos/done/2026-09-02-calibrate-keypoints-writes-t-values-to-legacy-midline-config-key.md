---
created: 2026-09-02T00:00:00.000Z
title: calibrate-keypoints writes keypoint_t_values to the legacy midline key, which pose silently overrides
area: training
files:
  - src/aquapose/training/prep.py
  - src/aquapose/engine/config.py
  - tests/unit/test_calibrate_keypoints.py
---

## Problem

`aquapose prep calibrate-keypoints` writes its result into a `midline:` section
of the project config (`src/aquapose/training/prep.py:205-207`):

```python
if "midline" not in config_data:
    config_data["midline"] = {}
config_data["midline"]["keypoint_t_values"] = t_values_list
```

But `keypoint_t_values` is a field of `PoseConfig`
(`src/aquapose/engine/config.py:115`), documented under `pose:` in
`docs/reference/config.md:73`. `midline:` survives only as a **backward-compat
alias**, and `load_config` merges it *before* `pose:`
(`src/aquapose/engine/config.py:693-698`):

```python
# Accept old names ("segmentation", "midline") for backward compat; new name ("pose") takes precedence
pose_kwargs = _merge_stage_config(pose_kwargs, yaml_nested.get("segmentation", {}))
pose_kwargs = _merge_stage_config(pose_kwargs, yaml_nested.get("midline", {}))
pose_kwargs = _merge_stage_config(pose_kwargs, yaml_nested.get("pose", {}))
```

`_merge_stage_config` is a plain `dict.update` (`config.py:517-531`), so if the
config already carries `pose.keypoint_t_values` -- from a previous run, a
hand-edit, or a config copied from a tuned project -- the freshly calibrated
values are **silently discarded**. The command still prints
`Computed t-values: [...]` and `Updated config: <path>`, both true of the file
on disk and both misleading about what the pipeline will use.

The same precedence applies to the CLI override layer (`config.py:718-724`).

## Why it matters

The failure is silent and inverted: the more a project has been tuned, the more
likely `pose.keypoint_t_values` already exists, and the more likely calibration
is a no-op. The user's only signal is a success message. Because the affected
value feeds pseudo-label generation
(`src/aquapose/training/pseudo_labels.py:50-95`), a user can generate a whole
round of training data believing it reflects a calibration that never took
effect.

Scope note: the merge is a shallow `dict.update`, so a `pose:` section that
lacks `keypoint_t_values` does **not** clobber the legacy key -- the value
survives. The silent discard requires `pose.keypoint_t_values` to be explicitly
present. That is exactly the state a project reaches after someone follows the
config reference (`docs/reference/config.md:73`, which documents the field under
`pose:`) and sets it by hand, or copies a tuned config forward.

Both spellings are live in the wild today: the scaffold from `init_cmd` writes a
`pose:` section (`src/aquapose/cli.py:193-195`) with the comment "Run 'aquapose
prep calibrate-keypoints' to set keypoint_t_values" injected directly above it
(`src/aquapose/cli.py:204-207`),
while the command then creates a *separate* `midline:` section -- so the file
ends up contradicting its own guidance. The production YH config
(`.../projects/YH/config.yaml`) uses `midline:` only. `init_cmd` advertises this
command as a standard setup step (`src/aquapose/cli.py:210-217`), so it is on
the documented new-project path.

## Solution

1. Write to `pose:` instead of `midline:` in `prep.py:205-207` -- the canonical
   key, matching `PoseConfig` and the config reference.
2. Handle a pre-existing legacy `midline.keypoint_t_values` rather than leaving
   a stale shadow behind. Deleting the legacy key when present is the clean
   outcome (`pose:` wins anyway, so removing it changes no behavior and removes
   a contradiction between two sections of the same file). If deletion is judged
   too aggressive for a hand-maintained file, warn on stdout that a legacy
   `midline.keypoint_t_values` was found and is now dead.

Note the config writer already round-trips through `yaml.safe_load` /
`yaml.dump` (`prep.py:200-210`), so comments in the user's config are dropped on
every invocation regardless -- worth noting if the fix is extended, but not part
of this todo.

Terminal gate: after running the command against a config that **already
contains** `pose.keypoint_t_values`, `load_config(path).pose.keypoint_t_values`
must equal the newly computed values. That assertion is the point of the fix --
a test that only checks the written YAML would pass today. Extend
`tests/unit/test_calibrate_keypoints.py`; `test_updates_config_yaml_in_place`
(line 104) and `test_creates_midline_section_if_missing` (line 139) both encode
the current `midline:` behavior and need updating with the rename.

## Notes

Found while auditing which of the YH `training_data` archives to feed
`--annotations`. Pairs with
`2026-09-02-calibrate-keypoints-yolo-path-measures-arc-length-in-normalized-space.md`
-- same command, independent defects. Fix this one first, or the corrected
t-values from that one may never reach the pipeline.

## Fixed

**Date:** 2026-09-02
**Fixed by:** Phase 113.1, Plan 01 (`113.1-01-PLAN.md`, D-06).
**Evidence:** The config writer in `src/aquapose/training/prep.py` now targets
`config_data["pose"]["keypoint_t_values"]` and deletes a stale
`midline.keypoint_t_values` if present, printing a removal notice. Proven
through `load_config(...).pose.keypoint_t_values` (not just the raw written
YAML) by
`tests/unit/test_calibrate_keypoints.py::TestCalibrateKeypointsConfig::test_writes_to_pose_key_and_overrides_existing_pose_value`
and `test_removes_stale_legacy_midline_keypoint_t_values`. Commit `421d327`.
