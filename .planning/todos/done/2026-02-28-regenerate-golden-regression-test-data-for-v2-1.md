---
created: 2026-02-28T12:44:13.357Z
title: Regenerate golden regression test data for v2.1
area: testing
files:
  - tests/golden/test_stage_harness.py
  - tests/golden/conftest.py
  - scripts/generate_golden_data.py
---

## Problem

The 8 golden regression tests in `tests/golden/test_stage_harness.py` are permanently skip-marked because their `.pt` fixture files were pickled from v1.0 modules (`aquapose.tracking.tracker.FishTrack`, `aquapose.segmentation.CropRegion`, etc.) that were deleted or restructured in v2.1. Python's unpickler fails on import, so the tests can't even collect.

## Solution

1. Rewrite `scripts/generate_golden_data.py` to use v2.1 stage boundaries (Detection → 2D Tracking → Association → Midline → Reconstruction)
2. Run on reference data to produce new `.pt` fixtures
3. Update `test_stage_harness.py` assertions for new stage outputs
4. Remove the `pytest.mark.skip` from the test module

## Filed

**Date:** 2026-09-02
**Reason:** Obsolete — the tests and script this todo asks to fix no longer exist.

Re-verified against the working tree during 113.1-03 (not copied from
113.1-CONTEXT.md's summary):

```
$ test -e tests/golden && echo EXISTS || echo ABSENT
ABSENT
$ test -e scripts/generate_golden_data.py && echo EXISTS || echo ABSENT
ABSENT
```

`tests/golden/test_stage_harness.py`, `tests/golden/conftest.py`, and
`scripts/generate_golden_data.py` — every file this todo names — are all
absent from the repository. There is nothing left to regenerate data for or
rewrite; the golden-regression harness itself was removed at some point
after this todo was filed. Closing as obsolete rather than working it.

**Filed by:** Phase 113.1, Plan 03 (113.1-03-PLAN.md, D-03).
