# Config Reference

AquaPose configuration is a frozen dataclass hierarchy loaded in four layers,
from lowest to highest priority:

1. **Dataclass defaults** — values baked into each `@dataclass(frozen=True)` field
2. **YAML file** — your project's `config.yaml` (resolved via `project_dir`)
3. **CLI `--set` overrides** — per-run key=value pairs on the `run` command,
   e.g. `--set detection.detector_kind=yolo_obb` or `--set n_animals=9`
4. **Freeze** — the resulting config is frozen; no mutation during execution

Once loaded, the config is written as the first artifact of every run for
reproducibility.

For the full auto-generated API documentation of the config module, see the
[engine module reference](../api/engine.rst).

---

## Essential fields

These are the fields that `aquapose init` scaffolds into every new project's
`config.yaml`. You must set or verify all of them before your first run.

| Field | Type | Default | What to set it to |
|---|---|---|---|
| `project_dir` | `str` | `""` | Absolute path to your project root. Relative paths for `video_dir`, `calibration_path`, and `output_dir` are resolved against this directory. |
| `video_dir` | `str` | `""` | Path (absolute, or relative to `project_dir`) to the directory containing input video files. |
| `calibration_path` | `str` | `""` | Path to the AquaCal calibration JSON file (e.g. `geometry/calibration.json`). |
| `output_dir` | `str` | `""` | Root directory for run artifacts. Each run creates a timestamped sub-directory inside this path. |
| `n_animals` | `int` | `0` (required) | Number of fish in the tank. **Must be set to a positive integer** — the default sentinel value 0 raises an error. Propagates to `association.expected_fish_count` and `synthetic.fish_count`. |
| `detection.detector_kind` | `str` | `"yolo"` | Detector backend: `"yolo"` (axis-aligned bounding box) or `"yolo_obb"` (oriented bounding box, recommended for elongated fish). |
| `detection.weights_path` | `str \| None` | `None` | Path to YOLO detection model weights (`.pt` file). Relative paths are resolved against `project_dir`. |
| `pose.weights_path` | `str \| None` | `None` | Path to YOLO-pose model weights (`.pt` file). Relative paths are resolved against `project_dir`. |
| `mode` | `str` | `"production"` | Execution mode preset: `"production"`, `"diagnostic"`, `"synthetic"`, or `"benchmark"`. |

---

## Advanced fields

The sections below cover every remaining field across all ten configuration
dataclasses, ordered by pipeline stage. Use these when you need to tune beyond
the defaults.

### Detection (`detection:`)

The `detection` key in your YAML maps to `DetectionConfig`. Fields in the
Essential table (`detector_kind`, `weights_path`) are also shown here for
completeness.

| Field | Type | Default | Effect |
|---|---|---|---|
| `detector_kind` | `str` | `"yolo"` | Detector backend: `"yolo"` or `"yolo_obb"`. Only these two values are accepted; others raise `ValueError`. |
| `conf_threshold` | `float` | `0.05` | Minimum detection confidence score. Detections below this value are discarded at inference time. |
| `iou_threshold` | `float` | `0.45` | IoU threshold for geometric polygon NMS. Detections with polygon IoU above this value are suppressed in favour of the higher-confidence detection. |
| `weights_path` | `str \| None` | `None` | Path to model weights for the active detection backend. Relative paths are resolved against `project_dir`. |
| `crop_size` | `list[int]` | `[128, 64]` | Output size `[width, height]` in pixels for affine crops. Used when `detector_kind` is `"yolo_obb"`. Stored as a list for clean YAML round-trips. |
| `detection_batch_frames` | `int` | `0` | Maximum frames per YOLO detection batch. `0` means no limit (batch all frames in the chunk). |
| `extra` | `dict` | `{}` | Catch-all dict for detector-specific kwargs not covered by the fields above. |

### Pose (`pose:`)

The `pose` key maps to `PoseConfig`. The pose stage runs YOLO-pose inference
on all detections and writes anatomical keypoints onto Detection objects.

| Field | Type | Default | Effect |
|---|---|---|---|
| `backend` | `str` | `"pose_estimation"` | Pose backend name. Only `"pose_estimation"` is supported; retained for config file compatibility. |
| `confidence_threshold` | `float` | `0.5` | YOLO detection confidence threshold for `model.predict()`. Detections below this score are discarded. |
| `weights_path` | `str \| None` | `None` | Path to YOLO-pose model weights file. Relative paths resolved against `project_dir`. |
| `detection_tolerance` | `float` | `50.0` | Maximum pixel distance for matching a tracklet centroid to a detection. |
| `n_keypoints` | `int` | `6` | Number of anatomical keypoints expected from the pose model. |
| `keypoint_t_values` | `list[float] \| None` | `None` | Per-keypoint arc-fraction values in `[0, 1]` from nose (0.0) to tail (1.0). If `None`, defaults to uniform spacing. Run `aquapose prep calibrate-keypoints` to calibrate. |
| `keypoint_confidence_floor` | `float` | `0.3` | Minimum per-keypoint confidence to treat as visible. |
| `min_observed_keypoints` | `int` | `3` | Minimum number of visible keypoints required for a valid pose result. |
| `pose_batch_crops` | `int` | `0` | Maximum crops per YOLO pose batch. `0` means no limit. |

### Tracking (`tracking:`)

The `tracking` key maps to `TrackingConfig`. Controls the per-camera 2D fish
tracker.

| Field | Type | Default | Effect |
|---|---|---|---|
| `tracker_kind` | `str` | `"keypoint_oks"` | Tracker backend. Only `"keypoint_oks"` (single-pass keypoint tracker with ORU/OCR recovery) is supported. |
| `max_coast_frames` | `int` | `30` | Maximum frames to coast (Kalman predict with no observation) before dropping a track. |
| `n_init` | `int` | `3` | Minimum matched detection frames before a track is confirmed and included in stage output. |
| `det_thresh` | `float` | `0.05` | Floor detection confidence — anything below is discarded entirely. |
| `track_thresh` | `float` | `0.3` | Confidence split between high and low detections. High-confidence detections (>= `track_thresh`) enter Phase 1 matching; low-confidence detections enter Phase 2. |
| `birth_thresh` | `float` | `0.5` | Minimum confidence for an unmatched Phase 1 detection to birth a new track. |
| `base_r` | `float` | `10.0` | Kalman filter base measurement noise variance. |
| `lambda_ocm` | `float` | `0.2` | OCM weight in the cost matrix. |
| `max_gap_frames` | `int` | `5` | Maximum gap size (frames) for spline interpolation. |
| `match_cost_threshold` | `float` | `1.2` | Maximum cost for Hungarian assignment match acceptance. Cells above this threshold are gated to infinity before the solver runs. |
| `ocr_threshold` | `float` | `0.5` | Minimum OKS similarity for observation-centric recovery (OCR). Tracks that coast and then find a detection with OKS above this threshold are re-acquired. |
| `max_match_distance` | `float` | `75.0` | Maximum pixel distance between predicted and detected spine1 keypoints for a match to be considered. Pairs exceeding this are gated to infinity, preventing cross-tank ID swaps. |
| `merger_distance_px` | `float` | `30.0` | Spine1 pixel distance below which an unmatched track is considered merged with a nearby matched track. |
| `merger_max_coast_frames` | `int` | `90` | Maximum coast frames for a track in merger state, replacing the normal `max_coast_frames` limit (90 = ~3 s at 30 fps). |

### Association (`association:`)

The `association` key maps to `AssociationConfig`. Controls pairwise
cross-camera tracklet scoring, Leiden clustering, and post-clustering group
validation for fish identity assignment.

| Field | Type | Default | Effect |
|---|---|---|---|
| `ray_distance_threshold` | `float` | `0.01` | Maximum ray-ray closest-point distance (metres) to classify a frame as an inlier. |
| `score_min` | `float` | `0.3` | Minimum affinity score to create a graph edge. |
| `t_min` | `int` | `3` | Minimum shared frames for a tracklet pair to be scored. |
| `t_saturate` | `int` | `100` | Frame count at which overlap reliability saturates. |
| `early_k` | `int` | `10` | Number of initial frames for early termination check. |
| `expected_fish_count` | `int` | `9` | Number of fish in the tank. Auto-populated from top-level `n_animals` when not explicitly set. |
| `min_shared_voxels` | `int` | `100` | Minimum shared voxels for camera pair adjacency. |
| `leiden_resolution` | `float` | `1.0` | Resolution parameter for Leiden clustering. Higher values yield finer-grained clusters. |
| `eviction_reproj_threshold` | `float` | `0.02` | Maximum ray-ray distance (metres) for a frame to be classified as consistent during group validation. Also used as the confidence normalisation denominator. |
| `min_cameras_validate` | `int` | `2` | Minimum unique cameras in a group for validation to run. Groups below this threshold are returned unchanged. |
| `validation_enabled` | `bool` | `True` | Toggle to skip group validation entirely. |
| `min_segment_length` | `int` | `10` | Minimum frames per segment after a changepoint split (~0.3 s at 30 fps). |
| `centroid_keypoint_index` | `int` | `2` | Index into Detection.keypoints for tracklet centroid: 0=nose, 1=head, 2=spine1, 3=spine2, 4=spine3, 5=tail. Falls back to OBB centroid when the keypoint is absent or low-confidence. |
| `centroid_confidence_floor` | `float` | `0.3` | Minimum keypoint confidence to use the keypoint as centroid; below threshold falls back to OBB centroid. |
| `keypoint_confidence_floor` | `float` | `0.2` | Minimum keypoint confidence for scoring participation. Keypoints below this on either tracklet are excluded from the frame's distance computation. |
| `aggregation_method` | `str` | `"mean"` | Method to aggregate per-keypoint distances within a frame. Currently only `"mean"` is supported. |
| `recovery_enabled` | `bool` | `True` | Toggle to skip singleton recovery entirely. |
| `recovery_residual_threshold` | `float` | `0.025` | Maximum mean ray-to-3D residual (metres) for a singleton to be assigned to a group. |
| `recovery_min_shared_frames` | `int` | `3` | Minimum shared frames between singleton and group for scoring to be attempted. |
| `recovery_min_segment_length` | `int` | `10` | Minimum frames per segment for the binary split-assign sweep. Singletons shorter than twice this value skip the sweep. |
| `use_multi_keypoint_scoring` | `bool` | `True` | Toggle scoring method: `True` uses multi-keypoint ray distances (v3.8); `False` uses single centroid rays (v3.7 baseline). |

### Reconstruction (`reconstruction:`)

The `reconstruction` key maps to `ReconstructionConfig`. Controls Stage 5
(confidence-weighted DLT triangulation with single-pass outlier rejection).

> **Note:** `z_denoising` is a nested sub-config under `ReconstructionConfig`.
> In YAML it appears as `reconstruction.z_denoising.enabled: true`.

| Field | Type | Default | Effect |
|---|---|---|---|
| `backend` | `str` | `"dlt"` | Reconstruction backend. Only `"dlt"` (confidence-weighted DLT triangulation) is supported. |
| `outlier_threshold` | `float` | `10.0` | Maximum reprojection error (pixels) for DLT backend outlier rejection during triangulation. |
| `min_cameras` | `int` | `3` | Minimum cameras observing a fish in a frame to attempt triangulation. Frames with fewer cameras are dropped. |
| `max_interp_gap` | `int` | `5` | Maximum consecutive dropped frames to interpolate (~167 ms at 30 fps). Gaps longer than this are left as missing data. |
| `n_control_points` | `int` | `7` | Fixed B-spline control point count per fish per frame. |
| `n_sample_points` | `int` | `6` | Number of sample points along each midline for triangulation output. Propagated from top-level `n_sample_points` when not explicitly overridden. |
| `spline_enabled` | `bool` | `False` | Whether to fit a B-spline to the triangulated body points. When `False` (default), raw triangulated keypoints are returned. When `True`, `Midline3D.control_points` is populated. |
| `z_denoising` | `ZDenoisingConfig` | see below | Nested z-denoising config (see table below). |

#### Z-denoising (`reconstruction.z_denoising:`)

`ZDenoisingConfig` is nested under `ReconstructionConfig`. When enabled, all
triangulated body points are flattened to their centroid z before spline
fitting, eliminating z-axis noise that the camera geometry cannot resolve.

| Field | Type | Default | Effect |
|---|---|---|---|
| `enabled` | `bool` | `True` | Whether to apply z-flattening during reconstruction. |

### LUT (`lut:`)

The `lut` key maps to `LutConfig`. Controls refractive lookup table generation
(tank geometry and grid resolution).

| Field | Type | Default | Effect |
|---|---|---|---|
| `tank_diameter` | `float` | `2.0` | Cylindrical tank diameter in metres. |
| `tank_height` | `float` | `1.0` | Tank depth (water column height) in metres. |
| `voxel_resolution_m` | `float` | `0.02` | Voxel grid spacing in metres (default 2 cm). |
| `margin_fraction` | `float` | `0.1` | Fractional margin beyond tank dimensions for LUT coverage (default 10%). |
| `forward_grid_step` | `int` | `1` | Pixel step size for forward LUT grid (1 = every pixel). |

### Synthetic (`synthetic:`)

The `synthetic` key maps to `SyntheticConfig`. Only active when `mode` is
`"synthetic"`.

| Field | Type | Default | Effect |
|---|---|---|---|
| `fish_count` | `int` | `3` | Number of synthetic fish to generate. Auto-populated from top-level `n_animals` when not explicitly set. |
| `frame_count` | `int` | `30` | Number of frames to simulate. |
| `noise_std` | `float` | `0.0` | Standard deviation of Gaussian noise added to 2D projections (pixels). `0` = no noise. |
| `seed` | `int` | `42` | Random seed for reproducible generation. |

### ReID (`reid:`)

The `reid` key maps to `ReidConfig`. Controls the MegaDescriptor backbone
wrapper used for cross-chunk identity matching.

| Field | Type | Default | Effect |
|---|---|---|---|
| `model_name` | `str` | `"hf-hub:BVRA/MegaDescriptor-T-224"` | timm model identifier for the embedding backbone (Swin-Tiny, 768-dim output). |
| `batch_size` | `int` | `32` | Maximum number of crops per GPU forward pass. |
| `crop_size` | `int` | `224` | Square input size in pixels for the embedding model. MegaDescriptor-T expects 224×224 inputs. |
| `device` | `str` | `"cuda:0"` | Torch device string (e.g. `"cuda:0"`, `"cpu"`). |
| `embedding_dim` | `int` | `768` | Expected output embedding dimension. Used for shape validation at construction time. |

### Top-level pipeline fields (`PipelineConfig`)

These fields sit at the top level of your `config.yaml` (no stage prefix).
The Essential fields (`n_animals`, `video_dir`, `calibration_path`,
`output_dir`, `project_dir`, `mode`) are already covered above.

| Field | Type | Default | Effect |
|---|---|---|---|
| `run_id` | `str` | `""` (auto-generated) | Unique run identifier. Defaults to a timestamp string of the form `run_YYYYMMDD_HHMMSS`. Override to give a run a stable name. |
| `device` | `str` | auto-detected | Compute device for all stages (e.g. `"cuda:0"`, `"cpu"`). Auto-detected: `"cuda:0"` when CUDA is available, otherwise `"cpu"`. Propagates to Detection and Pose stages. |
| `n_sample_points` | `int` | `6` | Number of 2D midline points produced per detection and used throughout the reconstruction pipeline. Propagates to `reconstruction.n_sample_points` when not explicitly overridden there. |
| `chunk_size` | `int \| None` | `300` | Number of frames per processing chunk. `None` or `0` means process the entire video as a single chunk. |
| `stop_after` | `str \| None` | `None` | If set, truncate the stage list after the named stage. Valid values: `"detection"`, `"pose"`, `"tracking"`, `"association"`, or `None` (run all stages). |
| `detection` | `DetectionConfig` | see above | Detection stage config container — see [Detection](#detection-detection) above. |
| `pose` | `PoseConfig` | see above | Pose stage config container — see [Pose](#pose-pose) above. |
| `tracking` | `TrackingConfig` | see above | Tracking stage config container — see [Tracking](#tracking-tracking) above. |
| `association` | `AssociationConfig` | see above | Association stage config container — see [Association](#association-association) above. |
| `reconstruction` | `ReconstructionConfig` | see above | Reconstruction stage config container — see [Reconstruction](#reconstruction-reconstruction) above. |
| `synthetic` | `SyntheticConfig` | see above | Synthetic data config container — see [Synthetic](#synthetic-synthetic) above. |
| `lut` | `LutConfig` | see above | LUT config container — see [LUT](#lut-lut) above. |
