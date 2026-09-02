---
created: 2026-02-28T22:00:00.000Z
title: Move LUT generation to pre-pipeline setup
area: calibration
files:
  - src/aquapose/core/association/stage.py
  - src/aquapose/calibration/luts.py
  - src/aquapose/engine/pipeline.py
  - src/aquapose/cli.py
---

## Problem

LUT generation currently lives inside `AssociationStage.run()` as lazy initialization. Per GUIDEBOOK Section 5, LUTs are pre-pipeline input materialization — they should be resolved before the pipeline loop starts, alongside frame loading and calibration. Having them inside a stage violates the principle that stages are pure computation with no side effects (the current code uses `print()` for progress because the observer system can't reach it).

## Solution

Move LUT loading/generation to the CLI or pipeline setup layer (before the batch loop). LUTs should be loaded from cache or generated once, then passed into `PipelineContext` alongside calibration data. If LUTs are not present and cannot be generated (e.g. missing calibration), the pipeline should fail early with a clear error message rather than discovering the problem mid-run inside the association stage.

The association stage should receive LUTs as a required input, not generate them internally.

## Filed

**Date:** 2026-09-02
**Reason:** Already implemented — the fix this todo describes is already in place.

Re-verified against the working tree during 113.1-03 (not copied from
113.1-CONTEXT.md's summary). `src/aquapose/core/association/stage.py:76-85`:

```python
        # Load pre-generated LUTs (no lazy generation)
        forward_luts = load_forward_luts(calibration_path, self._config.lut)
        inverse_lut = load_inverse_luts(calibration_path, self._config.lut)

        if forward_luts is None or inverse_lut is None:
            lut_dir = Path(calibration_path).parent / "luts"
            raise FileNotFoundError(
                f"LUTs not found at {lut_dir}. "
                f"Run: aquapose prep generate-luts --config <path>"
            )
```

`AssociationStage.run()` loads pre-generated LUTs from disk and raises
`FileNotFoundError` — naming the exact fix command — when they are missing,
rather than generating them lazily inside the stage. The generation
subcommand itself exists: `training/prep.py:314`,
`@prep_group.command("generate-luts")`. Both halves of the requested
solution (association receives LUTs as a required input; a pre-pipeline
command generates and caches them) are already true of the codebase.
Closing as already-implemented rather than working it.

**Filed by:** Phase 113.1, Plan 03 (113.1-03-PLAN.md, D-03).
