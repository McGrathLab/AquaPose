---
phase: 112-config-cli-reference
reviewed: 2026-09-01T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - docs/reference/cli.rst
  - docs/reference/config.md
  - docs/reference/index.md
  - docs/index.md
  - docs/api/cli.rst
  - docs/api/engine.rst
  - docs/conf.py
  - pyproject.toml
findings:
  critical: 5
  warning: 3
  info: 2
  total: 10
status: issues_found
---

# Phase 112: Code Review Report

**Reviewed:** 2026-09-01
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the Phase 112 CLI/config reference docs against the two sources of
truth: `src/aquapose/cli.py` (plus the sub-group CLIs in
`src/aquapose/training/` and `src/aquapose/core/reid/`) and
`src/aquapose/engine/config.py`.

**Config reference (`config.md`) is in good shape.** Every spot-checked default
and type matches the actual dataclass *field values*, including two fields where
the docs correctly use the real value while the config docstrings are stale
(`association.eviction_reproj_threshold` = `0.02`, `tracking.max_match_distance`
= `75.0`). The four-layer precedence description, `n_animals` sentinel behavior,
and `n_sample_points` / `expected_fish_count` / `fish_count` propagation all
match `load_config`. No config-accuracy defects found.

**The CLI reference (`cli.rst`) "Worked Examples" section is the problem area.**
The auto-generated `.. click::` directive is trustworthy, but the hand-authored
worked examples contain five commands that would fail on copy-paste because they
use options that do not exist or omit options the command marks `required=True`.
These are the primary blockers: the entire point of a worked-example section is
that users can paste and run the commands.

Cross-references, toctree wiring, MyST/`sphinx-design` grid syntax, `conf.py`
extension registration, and the `sphinx-click` dependency addition are all
correct. RST title-underline lengths were measured and all match their titles.
The `hatch run docs:build -W` gate was independently verified green, consistent
with these findings (all blockers are semantic/factual, not build-breaking).

## Critical Issues

### CR-01: `data import` example uses non-existent `--input` flag and wrong description

**File:** `docs/reference/cli.rst:106-107`
**Issue:** The example
`aquapose -p myproject data import --store obb --input labels.json` is invalid.
The `data import` command (`src/aquapose/training/data_cli.py:26-68`) has **no**
`--input` option. It requires three options, all `required=True`: `--store`,
`--source` (`manual`|`corrected`|`pseudo`), and `--input-dir` (a YOLO-format
directory with `images/` and `labels/`, **not** a JSON file). The comment
"Import labelled samples from a Label Studio export" is also wrong — Label Studio
ingestion is a different command (`pseudo-label from-labelstudio`). A user
copy-pasting this gets `Error: Missing option '--source'` / `No such option:
--input`.
**Fix:**
```rst
    # Import a YOLO-format labelled dataset into the OBB store
    aquapose -p myproject data import --store obb --source manual \
        --input-dir path/to/yolo_export
```

### CR-02: `data exclude` example uses `--id` (singular) but the flag is `--ids`

**File:** `docs/reference/cli.rst:116`
**Issue:** `aquapose -p myproject data exclude --store obb --id 42` fails with
`No such option: --id`. The actual option
(`src/aquapose/training/data_cli.py:723`) is `--ids` (plural, `multiple=True`).
**Fix:**
```rst
    # Exclude a problematic sample by ID
    aquapose -p myproject data exclude --store obb --ids 42
```

### CR-03: `data status` example passes `--store`, which the command does not accept

**File:** `docs/reference/cli.rst:112-113`
**Issue:** `aquapose -p myproject data status --store obb` fails with
`No such option: --store`. `data status`
(`src/aquapose/training/data_cli.py:613-615`) takes **no** options; it prints a
cross-store summary of both OBB and pose stores. The description "(counts, class
distribution)" is also inaccurate — there is no class-distribution output.
**Fix:**
```rst
    # Show cross-store training-data summary (OBB + pose)
    aquapose -p myproject data status
```

### CR-04: `tune` example omits the required `-s/--stage` option

**File:** `docs/reference/cli.rst:75-79`
**Issue:** `aquapose -p myproject tune` fails with `Error: Missing option
'--stage' / '-s'`. In `src/aquapose/cli.py:311-317` the `tune` command declares
`--stage` / `-s` as `required=True` with choices `association`|`reconstruction`.
The bare example cannot run.
**Fix:**
```rst
    # Sweep association-stage parameters on the most recent run
    aquapose -p myproject tune --stage association
```

### CR-05: `train compare run_a run_b` example omits the required `--model-type` option

**File:** `docs/reference/cli.rst:131-132`
**Issue:** `aquapose -p myproject train compare run_a run_b` fails with
`Error: Missing option '--model-type'`. The `compare` command
(`src/aquapose/training/cli.py:199-205`) declares `--model-type`
(`obb`|`seg`|`pose`) as `required=True`. The two run paths are also
`type=click.Path(exists=True)` positional args, so placeholder names like
`run_a` will additionally fail path validation, but the missing required option
is the copy-paste blocker.
**Fix:**
```rst
    # Compare two OBB training runs
    aquapose -p myproject train compare --model-type obb \
        path/to/run_a path/to/run_b
```

## Warnings

### WR-01: `viz` documented as "with no flags" but example shows the bare form only

**File:** `docs/reference/cli.rst:81-85`
**Issue:** The `viz` example `aquapose -p myproject viz` is valid (bare `viz`
generates all visualizations — `src/aquapose/cli.py:530-531`), but the one-line
worked example hides the substantial flag surface (`--overlay`, `--animation`,
`--trails`, `--detections`, `--mp4`, `--stride`, etc.). Since every other root
command in this section shows representative options, `viz` reads as
under-documented relative to its actual capability, and a reader may assume it
takes no options. Non-blocking (the command runs), but worth expanding for
parity.
**Fix:** Add at least one flagged example, e.g.
`aquapose -p myproject viz --animation --mp4 --fps 30`.

### WR-02: `smooth-z` description says "Kalman smoother" but implementation is a Gaussian filter

**File:** `docs/reference/cli.rst:93`
**Issue:** The one-liner calls `smooth-z` a "Kalman smoother." The command
(`src/aquapose/cli.py:706-877`, via `smooth_centroid_z` with a `--sigma-frames`
Gaussian sigma) applies **Gaussian** temporal smoothing to centroid z, not a
Kalman smoother. Misleading for users choosing between smoothing strategies.
**Fix:** "Post-process z-coordinates with a Gaussian temporal smoother."

### WR-03: `init` next-steps and doc omit that `n_animals` is scaffolded as the sentinel string `"SET_ME"`

**File:** `docs/reference/config.md:31` and `docs/reference/cli.rst:49-57`
**Issue:** `config.md` states `n_animals` default is `0` (correct for the
dataclass) and that the sentinel `0` raises. However `aquapose init`
(`src/aquapose/cli.py:186`) writes the literal string `n_animals: "SET_ME"` into
the scaffolded `config.yaml`, not `0`. A user who runs the scaffolded config
without editing hits a *different* failure than the documented "sentinel value 0
raises an error" — `load_config` compares `"SET_ME" <= 0`, which raises
`TypeError` (str vs int), not the friendly `ValueError("n_animals is required
and must be > 0")`. The docs describe the dataclass-default path; the scaffold
path behaves differently. Worth a one-line note in the `init` example or the
`n_animals` row that the scaffold requires replacing `SET_ME` with a positive
integer.
**Fix:** In the `init` worked example, add a comment: "# then edit config.yaml:
replace n_animals: SET_ME with a positive integer before the first run."

## Info

### IN-01: `detection.iou_threshold` documented without noting it is tracking-context deprecated

**File:** `docs/reference/config.md:55`
**Issue:** `iou_threshold` is a live field on `DetectionConfig` (config.py:62),
so documenting it is correct. However `iou_threshold` also appears in
`_RENAME_HINTS` (config.py:600) mapping to "removed (OC-SORT only)". This hint
only fires for *tracking* YAML, but a reader skimming both may be confused about
whether `iou_threshold` is supported. Optional: add a half-sentence clarifying it
is valid under `detection:` but not under `tracking:`.
**Fix:** Optional clarifying note; not required for correctness.

### IN-02: `eval-compare` writes JSON to the second run dir — undocumented side effect

**File:** `docs/reference/cli.rst:69-73`
**Issue:** The `eval-compare` example is syntactically correct. For completeness,
note that the command writes a comparison JSON into `run_b`'s directory
(`src/aquapose/cli.py:305-306` passes `run_b_dir` as the output dir). Purely a
documentation-completeness nit; the example runs as shown.
**Fix:** Optional: mention the comparison JSON output location.

---

_Reviewed: 2026-09-01_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
