# Concepts

This page explains what AquaPose actually computes, before you run anything.
Read it after [Installation](installation.md) and before running the
pipeline yourself — it gives you the vocabulary and the mental model your
own run's output will make sense against.

## What AquaPose computes

AquaPose takes synchronized video from a ring of top-down cameras looking
into a tank and produces, for every fish in every frame, a 3D midline curve —
a smooth line running from nose to tail through the water — plus a fish
identity that stays stable across cameras and across time. The reference
tutorial dataset was captured on a 12-camera ring rig at roughly 0.6 m
radius, mounted over a 2 m cylindrical tank, with every camera pointed
straight down through a flat air-water interface with no glass in between,
recording at 30 fps and 1600x1200. Nine cichlids swim in that tank for the
tutorial recording.

The rest of this page explains, in order: why a flat water surface makes
this harder than ordinary multi-view triangulation, the five stages the
pipeline runs to go from raw video to 3D midlines, how a fish keeps the same
identity across 12 cameras, and exactly what the pipeline writes out when
it's done.

## Why refraction changes the problem

Ordinary multi-view triangulation assumes light travels in a straight line
from a 3D point to a camera's pixel. That assumption is false here: every
ray from the tank to a camera crosses a flat air-water interface, and light
bends at that interface. A straight line drawn from a pixel back out into
the world is not the path the light actually took — it points somewhere
above the fish, not at it. Naive triangulation that ignores this converges
on the wrong 3D point, and the error grows with the ray's angle to the
water surface.

AquaPose handles this by casting a *refracted* ray for every pixel: it
back-projects the pixel through the camera's pinhole model as usual, finds
where that ray meets the water surface, and then bends the ray at that
crossing point using Snell's law, exactly as the real light did. Because
computing that per pixel, per frame, for 12 cameras would be expensive to
repeat at full pipeline speed, AquaPose precomputes two lookup tables once
per camera setup:

- A **forward LUT** (pixel to ray) that maps each camera's pixel grid to the
  refracted ray — an origin on the water surface and a direction into the
  water — via bilinear interpolation, so no per-frame Snell's-law math is
  needed once it's built.
- An **inverse LUT** (voxel to pixel) that discretizes the tank volume into a
  voxel grid and records, for every voxel, which cameras can see it and
  where it lands in each camera's image. This is also how AquaPose knows
  which pairs of cameras overlap at all, which the association stage below
  depends on.

Both tables are derived from your calibration file and are generated once
per camera setup via `aquapose prep generate-luts` — they are not shipped
with AquaPose or with any dataset, because they are specific to your rig's
geometry. If they are missing, the pipeline fails fast with a
`FileNotFoundError` rather than silently triangulating with straight rays.

## The five pipeline stages

```{mermaid}
flowchart LR
    A["1. Detection"] --> B["2. Pose & Midline extraction"]
    B --> C["3. Tracking (2D, per-camera)"]
    C --> D["4. Cross-Camera Association"]
    D --> E["5. Reconstruction"]
```

### Stage 1 — Detection

**Consumes:** undistorted video frames from every camera.
**Produces:** per-camera oriented bounding boxes around each visible fish,
with confidence scores.

Every camera is processed independently — there is no cross-camera logic
here at all. With 12 cameras only partially overlapping a tank, most cameras
see zero or a few fish in any given frame; that's expected, not a failure.
([API reference](../api/core/detection.rst))

### Stage 2 — Pose & Midline extraction

**Consumes:** each detection's cropped, orientation-aligned image region.
**Produces:** six raw anatomical keypoints per detection — nose, head,
spine1, spine2, spine3, tail — each with pixel coordinates and a confidence
score, written directly onto the detection.

This is where a fish's **midline** — the raw, per-fish body-shape signal
everything downstream is built from — first appears. This stage runs on
every detection from every camera, before tracking or cross-camera
reasoning happens; it does not yet know which detections belong to the same
fish over time or across cameras.
([API reference](../api/core/pose.rst))

### Stage 3 — Tracking

**Consumes:** the keypoint-enriched detections from Stage 2, plus tracker
state carried forward from the previous processing chunk.
**Produces:** per-camera tracklets — short time series of detections — each
carrying a local track ID that has no meaning outside that one camera.

This is **2D Tracking** in the literal sense: each camera's detections are
linked into tracklets independently, using a keypoint-based tracker (a
Kalman filter over each keypoint's position and velocity) with its own
occlusion-recovery logic for when a fish is briefly hidden. A tracklet's
per-frame entries are tagged as either a real detection or a coasted
(predicted, not observed) frame, which the next stage uses to avoid
trusting coasted frames too heavily.
([API reference](../api/core/tracking.rst))

### Stage 4 — Cross-Camera Association

**Consumes:** every camera's tracklets, the camera-overlap graph from the
inverse LUT, and the forward LUT for ray casting.
**Produces:** groups of tracklets — one group per physical fish — each
assigned a **global fish ID** that is authoritative for every stage after
this one.

This is where identity actually gets resolved across cameras. Tracklet pairs
across different cameras are scored by how well their refracted rays agree
in 3D, using all six keypoints rather than a single centroid point, and the
resulting affinity graph is clustered with the Leiden algorithm. This step
is built to handle the two things that make a 12-camera rig hard: a fish is
typically visible in only a handful of the 12 cameras at once (partial
observability), and a single camera's tracklet for one fish can fragment
into several short pieces over a clip. Per-frame confidence signals
(reprojection residual, camera count) are attached to each group here, for
Stage 5 to use.
([API reference](../api/core/association.rst))

### Stage 5 — Reconstruction

**Consumes:** the tracklet groups from Stage 4 (which fix, per fish, which
cameras to trust) and their keypoints.
**Produces:** one 3D midline per fish per frame, or a recorded reason why a
fish could not be reconstructed.

Because Stage 4 already solved cross-view correspondence, reconstruction
does not need RANSAC to figure out which detections match — it triangulates
each fish's keypoints using confidence-weighted DLT across exactly the
cameras known to observe that fish. A fish seen by fewer than a configured
minimum number of cameras (3 by default) cannot be triangulated reliably
and is dropped with a stated reason rather than silently producing a bad
point. See [What comes out](#what-comes-out-the-midline-representation)
below for the exact shape of this stage's output.
([API reference](../api/core/reconstruction.rst))

## Identity: local tracks vs. global fish IDs

Two different stages touch identity, and it's worth keeping them straight:

- **Stage 3 (Tracking)** assigns **local, per-camera track IDs**. These are
  bookkeeping only — camera A's track 3 has no relationship to camera B's
  track 3.
- **Stage 4 (Cross-Camera Association)** assigns the **global fish ID**
  that every later stage, and the output file, actually uses.

A fish's position in a frame's list of detections is not its identity —
only the global fish ID from Stage 4 is.

## What comes out: the midline representation

Per fish, per frame, AquaPose triangulates the six anatomical keypoints from
Stage 2 into 3D and arranges them along the body by arc length. By default,
that's the whole output: six raw 3D keypoints per fish per frame, in the
same anatomical order every time (nose, head, spine1, spine2, spine3, tail),
with no interpolation needed since the keypoint count already matches the
requested sample count.

AquaPose can optionally go one step further and fit a **3D B-spline** to
those triangulated points — a smooth curve described by a small number of
control points, a knot vector, and a degree — which is what the published
tutorial dataset's reference output does. The verified schema from that
dataset's `reference_outputs/outputs.h5` looks like this:

```text
midlines/ (group, attrs: SPLINE_K=3, SPLINE_KNOTS=[0,0,0,0,.25,.5,.75,1,1,1,1])
  points          (900, 9, 6, 3)   # arc-length-sampled 3D points per fish per frame
  control_points  (900, 9, 7, 3)   # B-spline control points
  half_widths     (900, 9, 6)      # body half-width at each sampled point
  z_offsets       (900, 9, 6)
  arc_length      (900, 9)
  centroid_z      (900, 9)
  fish_id         (900, 9)
  frame_index     (900,)
  n_cameras       (900, 9)         # how many cameras contributed to this fish-frame
  mean_residual   (900, 9)         # mean reprojection residual, in pixels
  max_residual    (900, 9)
  is_low_confidence (900, 9)       # flags fish-frames worth distrusting
```

That's 900 frames by up to 9 fish slots by 6 keypoints, in 3D. The quality
fields — `n_cameras`, `mean_residual`, `max_residual`, and
`is_low_confidence` — exist so that you can judge your own run's
reliability directly from the output file, rather than trusting every
number equally. A fish-frame reconstructed from only 2 cameras with a large
reprojection residual is real data, but it deserves less trust than one
reconstructed from 6 cameras with a residual of a couple of pixels — the
quality fields let you make that call yourself.

### A note on the `{p, ψ, κ, s}` state vector

Some project documentation describes AquaPose's fish representation as a
state vector `{p, ψ, κ, s}` — position, heading, curvature, and scale. **No
such structure exists in the production pipeline.** It is a holdover from
an earlier differentiable-rendering (analysis-by-synthesis) architecture
that was shelved for being far too slow (30+ minutes per second of video)
and was never part of the direct-triangulation pipeline described on this
page. Searching the current source for anything resembling a per-fish state
vector finds exactly one candidate — `InitialFishState` in
`aquapose.synthetic.trajectory` — and it is not the same thing: it's a seed
for generating synthetic test trajectories (a 3D position, a heading angle,
and a swim speed), not a per-frame pose representation, and it plays no
role anywhere in reconstruction. What the pipeline actually produces, frame
by frame and fish by fish, is the B-spline midline described immediately
above, with the quality fields that let you judge it.

## Where to go next

- For every configuration field that controls these stages, see the
  [Config Reference](../reference/config.md) — this page deliberately does
  not restate field names or defaults.
- For the exact `aquapose` commands (`prep generate-luts`, `run`, `viz`,
  and the rest), see the [CLI Reference](../reference/cli.rst).
- For the full module-level API, including the research-tier utilities
  (training, evaluation, re-identification, pseudo-labeling) that this page
  intentionally does not cover, see the [API Reference](../api/index.rst).
