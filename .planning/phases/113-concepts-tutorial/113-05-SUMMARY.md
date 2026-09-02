---
phase: 113-concepts-tutorial
plan: 05
subsystem: docs
tags: [zenodo, gpu-verification, timing, measurement, cli-verification]

requires:
  - phase: 113-concepts-tutorial
    provides: "Plan 03's corrected deposit README/config.yaml templates (bare `aquapose run`, bare `aquapose viz`, `midlines.h5` naming, McGrathLab/AquaPose URL) and the 22/22-verified deposit tree this plan executes against"
provides:
  - "A real, measured end-to-end execution of the deposit's documented recipe (prep generate-luts -> run -> viz) on an RTX 4070 Ti, proving the tutorial's central claim rather than asserting it"
  - "The second D-15 hardware timing data point: 224 s pipeline / 85 s viz / 309 s total (vs. the deposit's recorded 786.45 s / 150.85 s / 937.30 s on a GTX 1660 SUPER)"
  - "This run's D-12 expected-result statistics, measured independently from the deposit's own outputs.h5 and recorded side by side with it"
  - "A corrected LUT-generation timing claim in both write_deposit_readme's template and the extracted README.md tree file, plus regenerate_reference_outputs' internal comment (D-06) -- the deposit's '~2-5 min' claim was disproven by a measured 7 s run"
  - "A restored, re-verified 22-file deposit tree (checksums.sha256 re-emitted, verify_deposit() -> [])"
affects: [113-06-zenodo-upload, 113-07-tutorial-page, 114-publication]

actuals:
  tokens: 956
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "End-to-end GPU verification run executed and measured before a permanent record (Zenodo DOI) is frozen, rather than authoring documentation from inference over reference outputs alone"

key-files:
  created: []
  modified:
    - scripts/package_tutorial_dataset.py
    - tests/scripts/test_package_tutorial_dataset.py
    - aquapose-tutorial-data/README.md
    - aquapose-tutorial-data/checksums.sha256

key-decisions:
  - "Corrected the deposit's LUT-generation timing claim ('~600 MB, ~2-5 min') to describe wall time as GPU-dependent rather than assert a fixed range, after measuring 7 s on an RTX 4070 Ti -- an order of magnitude under the claimed lower bound. Applied to both write_deposit_readme's template and regenerate_reference_outputs' internal comment (D-06), locked with a fifth TestDepositDocCorrections assertion."
  - "Judged the per-chunk association 'Non-singleton cluster count != expected fish count' WARNING and the 'more dropped than kept' ReconstructionStage log line as expected, source-confirmed pipeline behavior (not defects) after reading clustering.py's own code comment ('Diagnostic warning -- ignore singletons, orphan tracklets are expected') and confirming the final aggregated output statistics land within D-12's tolerance of the reference dataset. Recorded as tutorial interpretation material rather than corrected, since no README/config claim asserts anything about these per-chunk numbers."
  - "Judged the repeated 'RuntimeWarning: Mean of empty slice' (recovery.py:811-812) as out of this plan's file scope -- it requires editing src/aquapose/core/association/recovery.py, which is not in Task 2's declared <files> list and is excluded by the milestone's no-pipeline-behavior-change scope fence. Flagged for the coordinator to queue as a todo rather than fixed here."
  - "Did not correct the deposit README's omission of the 'trails' (association_mosaic.mp4) viz output from its 'How to Reproduce' comment -- the comment says the step produces 'the 3D animation and overlay mosaic,' which is true but incomplete (bare `aquapose viz` also succeeds at generating trails and gracefully skips 'detections'). Not a false claim, so not a D-06 defect; flagged for Plan 07 to describe all three real outputs."

requirements-completed: [DOCS-07]

coverage:
  - id: D1
    description: "Every command the tutorial will tell a reader to run (prep generate-luts, run, viz) was executed on this machine against the extracted deposit, in the documented order, and each succeeded (exit 0) -- D-14"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "Verbatim command sequence + exit statuses recorded in this SUMMARY's 'Command Sequence' section; midlines.h5 (673 KB) and all three viz artifacts produced"
        status: pass
    human_judgment: false
  - id: D2
    description: "The one-time aquapose prep generate-luts step ran before the pipeline; LUT presence confirmed by geometry/luts/ (597 MB, 12 forward + 1 inverse NPZ) existing after the step, and by the pipeline's association stage running without a LUTs-not-found failure"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "LUT step: exit 0, 7 s wall, geometry/luts/ = 597 MB before finalize_deposit() removed it; pipeline's AssociationStage completed all 3 chunks without FileNotFoundError"
        status: pass
    human_judgment: false
  - id: D3
    description: "A second hardware timing data point (pipeline + viz wall seconds on this machine's GPU) pairs with the deposit's GTX 1660 SUPER numbers for D-15's range"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "Measured: 224 s pipeline / 85 s viz / 309 s total on an RTX 4070 Ti, vs. deposit's recorded 786.45 s / 150.85 s / 937.30 s on a GTX 1660 SUPER -- both recorded in this SUMMARY's 'Two-Point Timing Range' section"
        status: pass
    human_judgment: false
  - id: D4
    description: "The statistics the tutorial will quote as expected results are recomputed from this run's own midlines.h5, not copied from the reference, and both sets are recorded side by side (D-12, D-14)"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "Statistics comparison table in this SUMMARY: this run's 95.9% reconstructed / 2.82px median residual / 3.8% low-confidence vs. reference's 95.2% / 2.84px / 4.0% -- computed independently via a throwaway h5py script over both files"
        status: pass
    human_judgment: false
  - id: D5
    description: "Any command or claim in the deposit README/config.yaml that this run proved wrong is corrected in both scripts/package_tutorial_dataset.py's templates and the extracted tree (D-06)"
    requirement: "DOCS-07"
    verification:
      - kind: unit
        ref: "tests/scripts/test_package_tutorial_dataset.py::TestDepositDocCorrections::test_readme_lut_timing_is_not_a_fixed_minute_range"
        status: pass
    human_judgment: false
  - id: D6
    description: "After the run, the deposit tree is restored to a shippable state: no geometry/luts/, no runs/ directory, verify_deposit() returns [], and sha256sum -c checksums.sha256 reports 22 OK"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "test ! -d geometry/luts && test ! -d runs both pass; verify_deposit(Path('aquapose-tutorial-data')) -> []; sha256sum -c checksums.sha256 -> 22 OK, 0 failed; wc -l checksums.sha256 -> 22"
        status: pass
    human_judgment: false
  - id: D7
    description: "The default hatch environment was not recreated during this plan -- torch remains the CUDA-enabled build that predates Plan 01's wheel-index-pin removal"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "hatch run python -c \"import torch; print(torch.cuda.is_available()); print(torch.__version__)\" -> True / 2.5.1+cu121, identical before and after this plan's run (no hatch env create invoked)"
        status: pass
    human_judgment: false

duration: ~46min
completed: 2026-09-02
status: complete
---

# Phase 113 Plan 05: End-to-End Deposit Verification Run Summary

**Executed the deposit's full documented recipe (prep generate-luts -> run -> viz) on an RTX 4070 Ti against the extracted `aquapose-tutorial-data/` deposit, producing the second D-15 timing data point (224s pipeline / 85s viz vs. the reference's 786s / 151s), independently recomputed D-12 statistics that land within tolerance of the reference (95.9% vs 95.2% reconstructed, 2.82px vs 2.84px median residual), corrected a disproven LUT-generation timing claim, and restored the deposit to a clean, re-verified 22-file tree.**

## Performance

- **Duration:** ~46 min (includes ~7 min waiting on the LUT step + pipeline, ~1.5 min on viz, remainder on measurement/analysis/corrections)
- **Started:** 2026-09-02T12:59:00Z (approx.)
- **Completed:** 2026-09-02T13:45:08Z
- **Tasks:** 2
- **Files modified:** 4 (2 committed template/test files, 2 uncommitted deposit-tree files per `.gitignore`)

## Accomplishments

- Executed all three documented deposit commands from inside `aquapose-tutorial-data/`, in order, each exiting 0: `aquapose prep generate-luts` (7s), `aquapose run` (224s, 3 chunks of 300 frames), `aquapose viz` (85s).
- Confirmed the LUT fail-fast prerequisite is real and load-bearing: the pipeline's `AssociationStage` ran cleanly across all 3 chunks only because LUTs were generated first; `geometry/luts/` measured 597 MB (12 forward NPZ + 1 inverse NPZ), matching the install guide's ~600 MB disk claim.
- Measured the second D-15 hardware timing data point: 224s pipeline + 85s viz = 309s total on an RTX 4070 Ti, versus the deposit's recorded 786.45s / 150.85s / 937.30s on a GTX 1660 SUPER (roughly 3x faster end to end).
- Independently recomputed this run's D-12 statistics directly from its own `midlines.h5` (not copied from the reference) and recorded them side by side with the reference `outputs.h5`'s statistics -- both land within the tolerance ranges D-12 establishes (~95% reconstructed, ~3px median residual, 9 fish median 6-9 visible per frame).
- Investigated three findings surfaced during the run (a clustering-count WARNING, a per-chunk "more dropped than kept" reconstruction line, and a repeated `RuntimeWarning`) by reading the relevant source (`clustering.py`, `reconstruction/stage.py`, `recovery.py`) rather than guessing, and recorded an honest verdict for each in the Deviation Log below.
- Discovered and corrected a genuine documentation defect the run proved wrong: the deposit's claimed "~2-5 min" LUT-generation time was an order of magnitude over the measured 7s. Corrected in both `write_deposit_readme`'s template and `regenerate_reference_outputs`' internal comment (D-06), locked with a new regression test.
- Restored the deposit to a shippable state: removed the `runs/` directory the pipeline wrote, ran `finalize_deposit()` (removed `geometry/luts/`), confirmed `verify_deposit()` returns `[]`, re-emitted `checksums.sha256` (22 files), and confirmed `sha256sum -c` reports 22 OK, 0 failed.
- Confirmed `reference_outputs/` files were never touched (mtimes unchanged since before this session; their manifest digests are byte-identical to the pre-run manifest).
- Confirmed the hatch environment was not recreated: `torch==2.5.1+cu121`, `torch.cuda.is_available()` -> `True`, identical before and after this plan's execution.
- Confirmed `hatch run test` (1379 passed, 1 pre-existing unrelated failure logged in `deferred-items.md`, 3 skipped), `hatch run docs:build` (`sphinx-build -W --keep-going` exit 0), and `hatch run ruff format --check src/ tests/ scripts/` (238 files, all formatted) all stayed green.

## Command Sequence (verbatim, with exit statuses)

Run from inside `aquapose-tutorial-data/`, using `hatch run aquapose ...` per the project's workflow preference (long-running commands run as background/async tasks, not polled in a sleep loop):

| # | Command | Exit | Wall time | Started (UTC) | Finished (UTC) |
|---|---------|------|-----------|----------------|-----------------|
| 1 | `hatch run aquapose prep generate-luts` | 0 | 7 s | 2026-09-02T13:00:46Z | 2026-09-02T13:00:53Z |
| 2 | `hatch run aquapose run` | 0 | 224 s | 2026-09-02T13:01:12Z | 2026-09-02T13:04:56Z |
| 3 | `hatch run aquapose viz` | 0 | 85 s | 2026-09-02T13:27:47Z | 2026-09-02T13:29:12Z |

(No stack traces, exceptions, or non-zero exits appeared in any of the three commands' full stdout/stderr logs.)

### Step 1 output (LUT generation)

```
Generating forward LUTs...
Saved forward LUTs for 12 cameras.
Generating inverse LUT...
Camera coverage histogram:
  1+ cameras: 98.1% of voxels
  ...
  12+ cameras: 0.5% of voxels
LUT memory: inverse 60.7 MB
LUT generation complete. Saved to: .../aquapose-tutorial-data/geometry/luts
```
`geometry/luts/` measured **597 MB** (12x `*_forward.npz` @ ~44 MB each + 1x `inverse.npz` @ ~69 MB) before it was removed by `finalize_deposit()`.

### Step 2 output (pipeline run)

Run directory: `runs/run_20260902_090114/` (now removed per the required cleanup gate; file listing preserved below). Per-chunk progress:

```
Chunk 1/3 (0-299) — 18 fish (18 new), 77s
Chunk 2/3 (300-599) — 16 fish (6 new), 71s
Chunk 3/3 (600-899) — 27 fish (18 new), 73s
```

Final line: `Identity stitching: 9 continued, 18 new`.

### Step 3 output (visualization)

```
Loading midlines from midlines.h5...
Generating overlay mosaic video...
Loading midlines from midlines.h5...
Generating 3D animation...
Generating trail mosaic video...
No diagnostics directory found at .../runs/run_20260902_090114/diagnostics
Succeeded:
  overlay: .../viz/overlay_mosaic.mp4
  animation: .../viz/animation_3d.html
  trails: .../viz
Skipped (failures):
  detections: No chunk caches found in .../runs/run_20260902_090114
```
(`detections` requires per-chunk diagnostic caches that a standard `aquapose run` does not produce -- this is expected, not a failure; see Deviation Log #6. Note the CLI's own success message reports the "trails" generator's return value as the containing `viz/` directory rather than a specific filename, unlike overlay/animation which print exact file paths -- confirmed directly on disk that the actual artifact is `viz/association_mosaic.mp4`, 71.9 MB.)

## Run Directory File Listing (`runs/run_20260902_090114/`, before cleanup)

```
config.yaml           2,275 B
handoff.pkl          348,009 B
timing.txt            1,347 B
midlines.h5          673,024 B
logs/run.log           7,356 B (74 lines)
viz/animation_3d.html          8,987,556 B
viz/overlay_mosaic.mp4        114,854,111 B
viz/association_mosaic.mp4     71,917,520 B
```
Total run directory size: 188 MB (187 MB in `viz/`). Removed as part of the required deposit-cleanup gate; nothing from it is published.

## Two-Point Timing Range (D-15)

| Stage | This run (RTX 4070 Ti) | Reference (GTX 1660 SUPER) | Ratio |
|-------|--------------------------|------------------------------|-------|
| Pipeline | 224 s | 786.45 s | ~3.5x faster |
| Visualization | 85 s | 150.85 s | ~1.8x faster |
| **Total** | **309 s** | **937.30 s** | **~3.0x faster** |

Per-chunk pipeline stage breakdown (this run, chunk 3 of 3 -- representative; chunk 1/2 totals were 76.81s/70.65s):

```
DetectionStage      23.85s (33.0%)
PoseStage           22.17s (30.7%)
TrackingStage        0.76s ( 1.1%)
AssociationStage     9.61s (13.3%)
ReconstructionStage 15.85s (21.9%)
TOTAL               72.24s
```

Plan 07 should quote both endpoints as a range (e.g. "roughly 5-16 minutes end to end depending on GPU") rather than either single figure.

## Statistics Comparison (D-12)

Computed independently by a throwaway `h5py` script (not committed; ran from the project scratchpad) over both files' `midlines` group -- 900 frames x 9 fish slots = 8,100 total fish-frame slots in both:

| Metric | This run (RTX 4070 Ti) | Reference (GTX 1660 SUPER) |
|--------|--------------------------|------------------------------|
| Reconstructed fish-frames | 7,769 / 8,100 (**95.9%**) | 7,711 / 8,100 (95.2%) |
| `mean_residual` median | 2.82 px | 2.84 px |
| `mean_residual` mean | 3.93 px | 3.92 px |
| `mean_residual` p95 | 9.83 px | 9.73 px |
| `n_cameras` median | 4.0 | 4.0 |
| `n_cameras` range | 0-6 | 0-6 |
| `is_low_confidence` fraction | 3.8% | 4.0% |
| Fish per frame (min / median / max) | 6 / 9 / 9 | 6 / 9 / 9 |

**Verdict: both runs are statistically indistinguishable within D-12's tolerance ranges** (~95% reconstructed, ~3px median residual, 9 fish median with 6-9 visible per frame). Despite the alarming-looking per-chunk console warnings (see Deviation Log #3, #4), the final published-quality output is consistent across two different GPUs, two different runs, and roughly 4.5 months apart in wall-clock time.

## Task Commits

1. **Task 1: Execute the deposit's documented recipe end to end and time every stage (D-14, D-15)** - no commit (Task 1's `<files>` scope is run outputs only; no tracked file was modified)
2. **Task 2: Measure this run's results, fix what the run exposed, and restore the deposit to a shippable state** - `cdd7491` (fix)

**Plan metadata:** (this commit, docs-only)

## Files Created/Modified

- `scripts/package_tutorial_dataset.py` - Corrected the LUT-generation timing claim in `write_deposit_readme`'s template and `regenerate_reference_outputs`' internal comment: "~2-5 min" (disproven by this run's measured 7s) replaced with "wall time varies by GPU"
- `tests/scripts/test_package_tutorial_dataset.py` - Added `test_readme_lut_timing_is_not_a_fixed_minute_range` (fifth `TestDepositDocCorrections` assertion)
- `aquapose-tutorial-data/README.md` - Same timing correction applied identically to the extracted tree (not committed, gitignored)
- `aquapose-tutorial-data/checksums.sha256` - Re-emitted after removing `runs/` and `geometry/luts/`; 22 files, `sha256sum -c` reports 22 OK (not committed, gitignored)

## Decisions Made

See `key-decisions` in frontmatter for the four load-bearing calls (LUT-timing correction, clustering-warning verdict, dropped-reconstructions verdict, out-of-scope RuntimeWarning). Full reasoning for each is in the Deviation Log below.

## Deviation Log (full, with verdict on each entry)

**1. [Rule 1 - Bug, FIXED] LUT-generation timing claim disproven by measurement.**
- **Found during:** Task 1, Step 1 (LUT generation).
- **Claim:** Deposit README and `write_deposit_readme`'s template both said `# One-time setup: generate the refractive lookup tables (~600 MB, ~2-5 min)`.
- **Measured:** 7 seconds wall time on an RTX 4070 Ti -- an order of magnitude under the claimed lower bound. `reference_outputs/timing.txt` never recorded a LUT-generation time for the GTX 1660 SUPER, so "~2-5 min" was an unverified author estimate, not a measured figure.
- **Fix:** Corrected the comment in `write_deposit_readme`'s template, `regenerate_reference_outputs`' internal comment, and the extracted tree's `README.md` to describe wall time as GPU-dependent ("seconds on a fast card, a few minutes on a modest one") rather than assert a specific range this run falsifies.
- **Verification:** New `TestDepositDocCorrections::test_readme_lut_timing_is_not_a_fixed_minute_range`, RED before the fix (asserted string still present), GREEN after.
- **Committed in:** `cdd7491`.

**2. [Verdict: documented correctly, no fix needed] `outputs.h5` vs. `midlines.h5` naming.**
- **Found during:** Task 1, Step 2 (pipeline run).
- **Checked:** Whether `aquapose run` writes `outputs.h5` (as an older, already-corrected version of the README once falsely claimed) or `midlines.h5`.
- **Confirmed:** The pipeline wrote `runs/run_20260902_090114/midlines.h5` (673 KB), exactly matching the current README's corrected claim ("generates midlines.h5"). No `outputs.h5` was produced by this run -- consistent with Plan 03's finding that `outputs.h5` is only ever produced by `regenerate_reference_outputs()`'s own rename step for the shipped `reference_outputs/` folder.
- **Action:** None -- already correct from Plan 03.

**3. [Verdict: expected pipeline behavior, not a defect] Association clustering count mismatch WARNING.**
- **Found during:** Task 1, Step 2, chunk 3 of 3.
- **Observed:** `WARNING aquapose.core.association.clustering Non-singleton cluster count 12 != expected fish count 9 (11 singletons excluded)`.
- **Investigated:** Read `src/aquapose/core/association/clustering.py:369-378` directly. The warning fires from code the pipeline's own author labeled `# Diagnostic warning (ignore singletons — orphan tracklets are expected)` -- it is a designed, informational signal that a chunk's Leiden clustering found a different count of confident multi-tracklet groups than the configured `n_animals`, which downstream singleton recovery and cross-chunk identity stitching are built to reconcile.
- **Confirmed not a quality regression:** the final aggregated `midlines.h5` statistics (Statistics Comparison table above) land within tolerance of the reference dataset, which presumably exhibited similar or different per-chunk clustering behavior we cannot directly compare (Phase 111's `reference_outputs/` does not retain a per-chunk log).
- **Verdict:** Expected pipeline behavior under partial occlusion / track fragmentation within a 300-frame chunk, not a bug. No README/config claim asserts anything about this warning, so this is not a D-06 documentation defect. **Recorded here as material for Plan 07's tutorial interpretation section** -- a reader should be told this WARNING can appear and does not by itself indicate a bad run.

**4. [Verdict: expected pipeline behavior, not a defect] ReconstructionStage "more dropped than kept" in chunk 3.**
- **Found during:** Task 1, Step 2, chunk 3 of 3.
- **Observed:** `ReconstructionStage.run: 300 frames, 27 fish, 2519 reconstructions, 5611 dropped, 15.85s` (chunks 1 and 2 had lower drop ratios: 2814/2594 and 2164/2656 respectively).
- **Investigated:** Read `src/aquapose/core/reconstruction/stage.py:264-365`. The "27 fish" and the reconstructed/dropped counts are computed over **local, per-chunk candidate track groups** (most of which are short-lived tracklet fragments produced during association's clustering/recovery passes within that one 300-frame window) times 300 frames -- **not** the same denominator as the tutorial's headline "8,100 total fish-frame slots" (900 frames x 9 *global, post-stitching* fish IDs), which is what D-12's tolerance ranges are defined against. A chunk with more local candidate groups (27 vs. the configured 9) naturally produces a lower "reconstructed / (reconstructed + dropped)" ratio at this internal accounting level, without implying a worse final result.
- **Confirmed not a quality regression:** As in #3, the final `midlines.h5` aggregate statistics land within tolerance of the reference.
- **Verdict:** Explainable by upstream track fragmentation counted at a granularity a tutorial reader will not otherwise expect; not itself an error. No README/config claim needs correcting. **Recorded here as material for Plan 07's tutorial interpretation section** -- worth an explicit note that "more dropped than kept" per chunk in the console log is normal and does not mean the run failed; the numbers that matter for judging a run's quality are the aggregated `midlines.h5` fields (`mean_residual`, `n_cameras`, `is_low_confidence`), not per-chunk console drop counts.

**5. [Verdict: out of this plan's scope, flagged as a todo] Repeated `RuntimeWarning: Mean of empty slice`.**
- **Found during:** Task 1, Step 2 (pipeline run, both occurrences within the same chunk's singleton-recovery pass).
- **Observed:** `.../recovery.py:811: RuntimeWarning: Mean of empty slice` and the matching line 812, printed twice to the run's stdout.
- **Investigated:** Read `src/aquapose/core/association/recovery.py:804-830`. The warning fires from `np.nanmean(residuals[:, :split_idx], axis=1)` when a singleton-recovery candidate group's per-frame residual row is entirely `NaN` over the segment being evaluated for a split point -- an `np.errstate(all="ignore")` context suppresses floating-point warnings but not this one, since NumPy raises "Mean of empty slice" via `warnings.warn`, outside the floating-point error state. Confirmed pre-existing and unrelated to this run: the identical warning reproduces in `tests/unit/core/association/test_recovery.py` (visible in this plan's own `hatch run test` output), so it is not introduced by anything in this plan.
- **Judged out of scope:** Fixing it requires editing `src/aquapose/core/association/recovery.py`, which is not in Task 2's declared `<files>` list (`scripts/package_tutorial_dataset.py`, `aquapose-tutorial-data/{README.md,config.yaml,checksums.sha256}`), and is a pipeline source-code change excluded by the milestone's "no pipeline behavior change" scope fence.
- **Action:** Not fixed. **Flagging for the coordinator to queue as a todo** (per the coordinator's explicit instruction) -- worth a follow-up phase to either short-circuit the nanmean call when a row is all-NaN or filter the specific warning, since it currently prints twice on a stock tutorial run and would confuse a new user watching the console.

**6. [Verdict: omission, not a false claim; noted for Plan 07] Deposit README doesn't mention the "trails" viz output.**
- **Found during:** Task 1, Step 3 (visualization).
- **Observed:** Bare `aquapose viz` succeeds at three outputs (`overlay_mosaic.mp4`, `animation_3d.html`, and `association_mosaic.mp4` for "trails") and gracefully skips a fourth (`detections`, because a standard `aquapose run` does not write the per-chunk diagnostic caches that mosaic needs). The deposit README's "How to Reproduce" comment says the step "produces the 3D animation and overlay mosaic," which is true but only names two of the three real successes.
- **Verdict:** Not a false claim (the comment does not say "only" these two), so not a D-06 defect requiring correction. **Recorded here for Plan 07** to describe all three real outputs in the tutorial's interpretation section and to explain why "detections" is expected to be skipped in a standard run (it is not a failure).

**7. [Confirmed, no action needed] Hatch environment was not recreated.**
- Verified before Task 1 (precondition) and again after Task 2's cleanup: `torch==2.5.1+cu121`, `torch.cuda.is_available()` -> `True`, unchanged. `hatch env create` was never invoked at any point in this plan.

---

**Total deviations:** 1 auto-fixed (Rule 1 - LUT timing claim), 2 investigated-and-confirmed-expected (association clustering count, reconstruction drop ratio -- both source-verified as designed behavior, not bugs), 1 out-of-scope-flagged (RuntimeWarning, queued as a todo), 1 omission noted for the next plan (missing "trails" mention), 1 confirmed-correct-already (outputs.h5 naming), 1 confirmed-unaffected (hatch environment).
**Impact on plan:** The one real documentation defect this run exposed (LUT timing) is fixed in both template and tree per D-06. The two alarming-looking log lines are explained by source, not smoothed over -- their honest verdict is "expected, not a defect," backed by the final aggregate statistics matching the reference within tolerance. No scope creep: no pipeline source file was modified.

## Issues Encountered

- The background monitor task for `aquapose run` did not deliver its completion notification (infrastructure issue with the task-notification channel, not a pipeline failure). The run itself completed successfully in the background; the coordinator relayed the run's details (log tail, timings, per-chunk output) and instructed resuming without re-running the pipeline. All figures in this SUMMARY were independently re-verified against the actual files on disk (file mtimes, `timing.txt`, `logs/run.log`, `midlines.h5` schema) rather than taken solely from the coordinator's relay.
- A similar monitor for `aquapose viz` also did not fire a completion notification before a 10-minute foreground `until`-loop wait timed out; the viz process itself had already exited successfully by then (confirmed via `ps` and the presence of all three output files), and wall time was reconstructed from file mtimes.

## Known Stubs

None. No new placeholder content was introduced; the LUT-timing correction replaces one factual claim with a more accurate one.

## Threat Flags

None new. T-113-15 (deposit tree polluted by run artifacts) is mitigated exactly as the plan's threat model specified: `runs/` was removed, `finalize_deposit()` removed `geometry/luts/`, `verify_deposit()` returned `[]`, and the re-emitted 22-file manifest verifies 22 OK. T-113-16 (repudiation of measured statistics) is mitigated: both this run's and the reference's numbers are recorded side by side above with the GPU model named for each. T-113-17 (`reference_outputs/` tampering) is mitigated: those four files were never written to during this plan (mtimes unchanged since before this session; digests identical in the re-emitted manifest).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 07 (tutorial page) can now quote the two-point D-15 timing range (224s/786.45s pipeline, 85s/150.85s viz) and the D-12 statistics comparison table directly from this SUMMARY, rather than re-deriving them.
- Plan 07 should incorporate the interpretation notes from Deviation Log #3, #4, and #6: the association clustering WARNING and the per-chunk "dropped > reconstructed" line are normal and not failure signals; the viz step's third output ("trails") is a real success worth mentioning; "detections" being skipped in a standard run is expected.
- The `RuntimeWarning: Mean of empty slice` (Deviation Log #5) needs a coordinator-created todo -- it currently prints twice on a stock tutorial run and is not this plan's to fix.
- The deposit tree is back to a verified, publishable 22-file state (`sha256sum -c` -> 22 OK, `verify_deposit()` -> `[]`), ready for Plan 06's Zenodo upload/DOI mint.
- The two committed template fixes (`scripts/package_tutorial_dataset.py`, `tests/scripts/test_package_tutorial_dataset.py`) mean any future regeneration of the deposit from the script will reproduce the corrected LUT-timing wording automatically.
- One pre-existing, unrelated test failure (`test_pseudo_label_cli.py`, logged by Plan 01) remains open and untouched.

## Self-Check: PASSED

- FOUND: scripts/package_tutorial_dataset.py (modified, 2 corrected comment blocks)
- FOUND: tests/scripts/test_package_tutorial_dataset.py (modified, 5th TestDepositDocCorrections assertion)
- FOUND: aquapose-tutorial-data/README.md (modified, gitignored)
- FOUND: aquapose-tutorial-data/checksums.sha256 (re-emitted, 22 lines, gitignored)
- FOUND commit: cdd7491
- CONFIRMED: sha256sum -c checksums.sha256 -> 22 OK, 0 failed (run from inside aquapose-tutorial-data/)
- CONFIRMED: verify_deposit(Path("aquapose-tutorial-data")) -> []
- CONFIRMED: test ! -d aquapose-tutorial-data/geometry/luts (true)
- CONFIRMED: test ! -d aquapose-tutorial-data/runs (true)
- CONFIRMED: hatch run test -> 1379 passed, 1 pre-existing failure, 3 skipped
- CONFIRMED: hatch run docs:build -> exit 0
- CONFIRMED: hatch run python -c "import torch; print(torch.cuda.is_available())" -> True (env not recreated)

---
*Phase: 113-concepts-tutorial*
*Completed: 2026-09-02*
