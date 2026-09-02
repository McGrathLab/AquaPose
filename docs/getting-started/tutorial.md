# Tutorial: End-to-End Run on the Sample Dataset

This page walks you from a freshly installed AquaPose to an interpreted 3D
fish midline, using a real 30-second, 12-camera dataset. Every command below
was actually executed, in this order, on this dataset — twice, on two
different GPUs — before this page was written. Every timing and statistic you
will see quoted here is a measured number, not an estimate.

Read [Installation](installation.md) first if you have not already, and see
[Concepts](concepts.md) for what each pipeline stage computes — this page
does not re-explain the stages, only what to run and what to expect.

## 1. Before you start

**Hardware.** The tutorial dataset was run end to end on two real machines:

| Stage | GTX 1660 SUPER (6.4 GB) | RTX 4070 Ti |
|---|---|---|
| Pipeline (`aquapose run`) | 786.45 s | 224 s |
| Visualization (`aquapose viz`) | 150.85 s | 85 s |
| **Total** | **937.30 s (~15.6 min)** | **309 s (~5.2 min)** |

Locate your own GPU somewhere between these two points. A GTX 1660 SUPER with
6.4 GB of VRAM is a reasonable practical floor — if your card has less memory
than that, expect to need `--max-chunks` (see step 4) to process a smaller
slice at a time.

**Disk.** Budget **215 MB** for the dataset itself, plus roughly **600 MB**
for the refractive lookup tables you will generate in step 3 (they are not
shipped with the dataset — see below).

**Software.** You should already have `aquapose` importable and
`torch.cuda.is_available()` returning `True` from the
[Installation](installation.md) page, including `ffmpeg` on `PATH` (needed
for MP4 export in step 5).

## 2. Get the dataset

:::{note}
The dataset archive is being prepared for publication on Zenodo. The DOI and
a public download link will be added at every site marked below, in place of
this note, once the record is live.
:::

<!-- ZENODO-DOI-PENDING -->

Once published, the archive will be a single download that extracts to a
directory named `aquapose-tutorial-data/` — that directory name is stable
across publication and is what every command on this page assumes. After
extracting it, verify the download before doing anything else:

```bash
cd aquapose-tutorial-data
sha256sum -c checksums.sha256
```

All 22 files should report `OK`. If any file fails, re-download rather than
proceeding — a corrupted video or model file fails confusingly deep into the
pipeline rather than up front.

The archive contains:

| Path | Description |
|---|---|
| `videos/` | 12 x 30-second H.264 clips, one per camera |
| `geometry/calibration.json` | Refractive camera calibration |
| `models/yolo_obb.pt` | Detection model |
| `models/yolo_pose.pt` | 6-keypoint pose model |
| `config.yaml` | Pipeline config (relative paths, `project_dir: .`) |
| `reference_outputs/` | Pre-computed outputs for comparison |
| `checksums.sha256` | This SHA-256 manifest |

**Citation.** Once published, cite the dataset with:

```bibtex
@dataset{lancaster_aquapose_yh_tutorial_2026,
  title   = {AquaPose YH Tutorial Dataset},
  author  = {Lancaster, Tucker},
  year    = {2026},
  doi     = {<!-- ZENODO-DOI-PENDING -->},
  license = {CC-BY-4.0 (data), AGPL-3.0 (models)},
}
```

The entry becomes citable once the record is published and the `doi` field
above is filled in.

**If you need the data today.** This page is being used before the archive
is public. In the interim, the deposit can be obtained directly from the
AquaPose maintainers — it is not yet available at a public URL, so no link is
given here; ask the maintainers for the current tutorial dataset and they
will provide it directly.

## 3. Generate the refractive lookup tables

Refractive ray-casting (see [Concepts](concepts.md))
needs two lookup tables — a forward LUT and an inverse LUT — computed once
per camera setup from your calibration file. They are **not** shipped with
the dataset because they are specific to this rig's geometry, and they
consume roughly 600 MB on disk. Generate them once, from inside the extracted
directory:

```bash
cd aquapose-tutorial-data
aquapose prep generate-luts
```

Wall time is entirely GPU-dependent: this step took **7 seconds** on an
RTX 4070 Ti. An earlier draft of the deposit's own documentation quoted
"2-5 minutes" for this step — that figure was an unverified estimate, not a
measurement, and this run disproved it by an order of magnitude. Expect
seconds on a fast card and low minutes on a modest one, not a fixed number.

**If you skip this step**, the pipeline does not degrade silently — it
fails fast the moment the association stage needs the LUTs:

```text
FileNotFoundError: LUTs not found. Run: aquapose prep generate-luts --config <path>
```

That is the intended behavior: a missing LUT means every subsequent ray cast
would be wrong, so the pipeline refuses to produce silently-invalid output.

## 4. Run the pipeline

From the same directory:

```bash
aquapose run
```

No `--config` flag is needed — the `run` command has none. `aquapose`
resolves the active project by walking the current directory upward looking
for `config.yaml`, which is why `cd`-ing into the extracted directory first
matters (see `resolve_project` in the [CLI Reference](../reference/cli.rst)
for the full resolution rule).

This processes the dataset in three chunks of 300 frames each and writes,
under a new `runs/run_<timestamp>/` directory: `midlines.h5` (the 3D midline
output you will inspect in step 7), `handoff.pkl` (state carried between
chunks), `timing.txt`, and `logs/run.log`. Wall time was **786.45 s** on the
GTX 1660 SUPER reference and **224 s** on the RTX 4070 Ti verification run.

Two options are worth knowing by name for your first run — see the
[CLI Reference](../reference/cli.rst) for full details on each:

- `-v` / `--verbose` for more detailed console output.
- `--max-chunks N` to process only the first `N` chunks, useful for a quick
  smoke run before committing to the full dataset.

For what each configuration field in `config.yaml` controls, see the
[Config Reference](../reference/config.md) — this page does not restate
field meanings.

## 5. Visualize

```bash
aquapose viz
```

With no arguments, `viz` operates on the most recently created run directory.
(An earlier, now-corrected version of the deposit's own README suggested
`aquapose viz runs/<run_dir>` — that form double-nests the path and fails;
always use the bare form shown here.) It reads `midlines.h5` and produces, in
`runs/run_<timestamp>/viz/`:

- `animation_3d.html` — an interactive 3D midline animation.
- `overlay_mosaic.mp4` — a 2D reprojection overlay mosaic across all 12
  cameras.
- `association_mosaic.mp4` — a "trails" mosaic showing tracked reprojections
  over time.

MP4 export needs `ffmpeg` on `PATH` (see [Installation](installation.md)
prerequisites). Wall time was **150.85 s** on the GTX 1660 SUPER reference
and **85 s** on the RTX 4070 Ti verification run.

A fourth possible output, `detections`, is skipped on a standard run — it
needs per-chunk diagnostic caches that `aquapose run` does not produce by
default. That skip is expected, not a failure.

## 6. Check your results

This is the step that tells you whether your run succeeded. Because GPU
nondeterminism means your run will not match any reference bit-for-bit,
expected results are given here as approximate values with a tolerance
range, not exact figures. **Landing exactly on a quoted boundary counts as a
pass, not a failure** — for example, a median reprojection residual of
exactly the quoted figure, or a frame with exactly the minimum quoted number
of fish visible, is within expectation, not a sign that something regressed.

Measured independently on two GPUs, roughly 4.5 months apart, and
statistically indistinguishable within these ranges:

| Metric | What to expect |
|---|---|
| Fish-frames reconstructed | roughly 95% of all 900 x 9 = 8,100 slots (measured 95.2% and 95.9%) |
| Median reprojection residual (`mean_residual`) | around 3 px (measured 2.82-2.84 px); the mean runs a bit higher (~3.9 px) and the 95th percentile substantially higher (~9.7-9.8 px) |
| Cameras contributing per reconstructed fish (`n_cameras`) | median around 4, out of 12 total |
| Fish-frames flagged low confidence (`is_low_confidence`) | a few percent (measured 3.8-4.0%) |
| Fish visible per frame | 6 to 9, with 9 typical (measured min 6 / median 9 / max 9) |

Run this snippet against your own `midlines.h5` to compute the same numbers
mechanically, rather than eyeballing the visualization:

```python
import h5py
import numpy as np

with h5py.File("runs/run_<timestamp>/midlines.h5", "r") as f:
    grp = f["midlines"]
    fish_id = grp["fish_id"][:]
    mean_residual = grp["mean_residual"][:]
    n_cameras = grp["n_cameras"][:]
    is_low_confidence = grp["is_low_confidence"][:]

reconstructed = fish_id >= 0
total_slots = fish_id.size
print(f"Reconstructed: {reconstructed.sum()}/{total_slots} "
      f"({100 * reconstructed.mean():.1f}%)")
print(f"Median residual: {np.nanmedian(mean_residual[reconstructed]):.2f} px")
print(f"Median n_cameras: {np.nanmedian(n_cameras[reconstructed]):.1f}")
print(f"Low confidence: {100 * is_low_confidence[reconstructed].mean():.1f}%")
print(f"Fish per frame: min={reconstructed.sum(axis=1).min()}, "
      f"median={np.median(reconstructed.sum(axis=1)):.0f}, "
      f"max={reconstructed.sum(axis=1).max()}")
```

**Note on console output during the run.** You may see a `WARNING` from the
association stage reading something like `Non-singleton cluster count N !=
expected fish count 9`, and per-chunk reconstruction lines where the dropped
count exceeds the kept count. Both are normal, source-confirmed diagnostic
behavior from partial occlusion and track fragmentation within a single
300-frame chunk — they describe internal, per-chunk candidate-group counts,
not the final aggregated result. Judge your run by the table above, computed
from the final `midlines.h5`, not by these per-chunk console numbers.

## 7. Read the output

`midlines.h5` has one group, `midlines`, with attributes `SPLINE_K=3` (the
B-spline degree) and `SPLINE_KNOTS` (an 11-element knot vector), and these
datasets, each shaped `(900 frames, 9 fish slots, ...)`:

```text
points          (900, 9, 6, 3)   # arc-length-sampled 3D keypoints per fish per frame
control_points  (900, 9, 7, 3)   # B-spline control points
half_widths     (900, 9, 6)      # body half-width at each sampled point
z_offsets       (900, 9, 6)
arc_length      (900, 9)
centroid_z      (900, 9)
fish_id         (900, 9)
frame_index     (900,)
n_cameras       (900, 9)         # cameras contributing to this fish-frame
mean_residual   (900, 9)         # mean reprojection residual, in pixels
max_residual    (900, 9)
is_low_confidence (900, 9)       # flags fish-frames worth distrusting
```

`n_cameras`, `mean_residual`, `max_residual`, and `is_low_confidence` are the
quality fields step 6 computed statistics from — use them to judge trust in
any individual fish-frame, not just the run as a whole.

**Identity comes from `fish_id`, not from position.** A fish's slot index
within a frame (the second axis, 0-8) is not a stable identity across
frames — a given fish can occupy slot 2 in one frame and slot 5 in the next.
Always look up a fish by its `fish_id` value, never by row order.

Load and plot one fish's 3D midline for one frame:

```python
import h5py
import matplotlib.pyplot as plt
import numpy as np

with h5py.File("runs/run_<timestamp>/midlines.h5", "r") as f:
    grp = f["midlines"]
    fish_id = grp["fish_id"][:]
    points = grp["points"][:]

frame_idx = 0
target_fish = fish_id[frame_idx, fish_id[frame_idx] >= 0][0]  # first fish present
slot = np.where(fish_id[frame_idx] == target_fish)[0][0]
midline = points[frame_idx, slot]  # (6, 3)

fig = plt.figure()
ax = fig.add_subplot(projection="3d")
ax.plot(midline[:, 0], midline[:, 1], midline[:, 2], marker="o")
ax.set_title(f"Fish {target_fish}, frame {frame_idx}")
plt.show()
```

## 8. Reduce z jitter with `smooth-z`

The `reference_outputs/` shipped with the dataset — and the comparison you
just ran in step 6 — were both produced by `aquapose run` followed by
`aquapose viz` only, with **no** smoothing pass. That is deliberate: it keeps
steps 6 and 7 an apples-to-apples comparison. If you smooth first and then
compare against the reference, your numbers will diverge from the reference
and that is expected, not a regression.

**Why jitter exists.** Depth along a camera's viewing ray is the
weakest-constrained axis in a refractive multi-view reconstruction (see
[Concepts](concepts.md)), so per-frame z estimates scatter more than x and y.
`smooth-z` is the recommended step that makes 3D trajectories usable for
downstream kinematics.

Run it against your own run:

```bash
aquapose smooth-z --dry-run
```

`--dry-run` reports the jitter reduction without writing anything, so you can
confirm the improvement before committing to it. On the verification run, at
the default `--sigma-frames 3`, mean frame-to-frame centroid-z jitter fell
from approximately **0.500 cm to 0.082 cm** across 13 fish and 7,769
fish-frames — roughly a 6x reduction. Treat this as an approximate
improvement subject to the same tolerance discipline as step 6, not an exact
target.

Once you are satisfied, drop `--dry-run` to write the result:

```bash
aquapose smooth-z
```

**`smooth-z` never edits your input file.** It reads `midlines_stitched.h5`
if present, otherwise `midlines.h5`, and writes a **new** file —
`{stem}_smoothed.h5` — by copying the input (`shutil.copy2`) and then
modifying only the copy. Your original `midlines.h5` is always preserved, so
the before/after comparison in the next step costs nothing.

**Visualizing the smoothed result is automatic, and this is easy to miss.**
`aquapose viz` prefers a smoothed file over its unsmoothed counterpart
whenever one exists: it looks for `midlines_stitched_smoothed.h5`, then
`midlines_stitched.h5`, then `midlines_smoothed.h5`, then finally
`midlines.h5`. So after running `smooth-z`, a bare `aquapose viz` renders the
**smoothed** reconstruction with no extra flag — nothing in the command
output tells you this happened.

Because `viz` writes to `{run_dir}/viz/` by default, re-running it after
`smooth-z` will **overwrite** the pre-smoothing renders you made in step 5.
To keep both side by side for comparison, redirect the second render:

```bash
aquapose viz -o runs/run_<timestamp>/viz_smoothed
```

Then open the two `animation_3d.html` files together — that side-by-side
comparison is the honest visual confirmation the step worked.

**A one-way edge to know about.** Once `midlines_smoothed.h5` exists, there
is no flag that forces `viz` back to the unsmoothed file. `--unstitched`
only skips the *stitched* variants and still prefers `midlines_smoothed.h5`
over `midlines.h5`. If you want an unsmoothed render again after smoothing,
either move or rename the smoothed file, or rely on the `-o`-redirected
copy you already made above.

See the [CLI Reference](../reference/cli.rst) for the full `smooth-z` option
surface.

## 9. What is normal and what is not

Several outcomes look alarming the first time you see them but are the
expected result of partial camera coverage, not a bug:

**Normal, expected outcomes:**

- A camera reporting no detections in a given frame — with 12 cameras only
  partially overlapping the tank, this happens routinely.
- A frame with fewer than all 9 fish reconstructed (as low as 6 in the
  measured data).
- A fish-frame flagged `is_low_confidence` (a few percent of all fish-frames,
  by design — see step 6).
- A fish-frame dropped entirely because fewer than the configured minimum
  number of cameras (3 by default) observed it.
- The console `WARNING` about cluster count mismatch and per-chunk "more
  dropped than kept" reconstruction lines described in step 6.

**Genuine signs of a problem**, by contrast:

- A `FileNotFoundError: LUTs not found` failure (step 3 was skipped or
  failed).
- A residual distribution far above the ranges quoted in step 6 (for
  example, a median well above 3 px rather than exactly at or near it).
- Zero fish reconstructed in the entire run.

## 10. Using your own footage

**HARD CONSTRAINT: never spatially downscale your video before running
AquaPose.** The calibration intrinsics and refractive ray-casting are bound
to the capture resolution — this dataset was captured at **1600 x 1200**, and
halving that resolution silently invalidates every ray cast, producing
confidently wrong 3D output with no error raised. Temporal trimming and
bitrate reduction are safe; spatial resizing is not.

To set up a new project with your own footage and calibration, see the
[CLI Reference](../reference/cli.rst) for the full command surface and the
[Config Reference](../reference/config.md) for every field your `config.yaml`
can set.
