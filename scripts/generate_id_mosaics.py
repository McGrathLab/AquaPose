"""Generate 3x3 fish ID mosaics for manual swap-rate estimation.

For each sampled frame, projects 3D midline keypoints into camera views,
crops around each fish, and assembles a 3x3 grid ordered by fish ID.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import cv2
import numpy as np
import scipy.interpolate
import torch

from aquapose.calibration.loader import (
    compute_undistortion_maps,
    load_calibration_data,
)
from aquapose.calibration.projection import RefractiveProjectionModel
from aquapose.core.types.frame_source import VideoFrameSource
from aquapose.evaluation.viz._loader import (
    H5Spline,
    load_midlines_from_h5,
    read_config_yaml,
    resolve_h5_path,
)

logger = logging.getLogger(__name__)

_N_SPLINE_EVAL = 50
_T_VALS = np.linspace(0.0, 1.0, _N_SPLINE_EVAL)

# Minimum crop half-width in pixels (prevents degenerate thin crops).
_MIN_CROP_HALF_PX = 40


def _eval_spline_pts(spline: H5Spline) -> np.ndarray | None:
    """Evaluate B-spline control points to dense 3D points."""
    cp = np.asarray(spline.control_points, dtype=np.float64)
    if not np.all(np.isnan(cp)):
        try:
            bspl = scipy.interpolate.BSpline(
                np.asarray(spline.knots, dtype=np.float64),
                cp,
                spline.degree,
            )
            return bspl(_T_VALS)
        except Exception:
            pass
    if spline.points is not None:
        pts = np.asarray(spline.points, dtype=np.float64)
        if pts.ndim == 2 and pts.shape[1] == 3:
            return pts
    return None


def _pick_best_camera(
    pts_3d: np.ndarray,
    models: dict[str, RefractiveProjectionModel],
    frame_sizes: dict[str, tuple[int, int]],
) -> tuple[str | None, np.ndarray | None]:
    """Choose the camera where the fish centroid is closest to frame center.

    Returns (cam_id, pixels) or (None, None) if no camera has valid projection.
    """
    best_cam = None
    best_pixels = None
    best_dist = float("inf")

    pts_tensor = torch.tensor(pts_3d, dtype=torch.float32)

    for cam_id, model in models.items():
        pixels, valid = model.project(pts_tensor.to(model.C.device))
        pixels_np = pixels.cpu().numpy()
        valid_np = valid.cpu().numpy()

        if not valid_np.any():
            continue

        valid_px = pixels_np[valid_np]
        w, h = frame_sizes[cam_id]
        center = np.array([w / 2, h / 2])
        centroid = valid_px.mean(axis=0)
        dist = np.linalg.norm(centroid - center)

        if dist < best_dist:
            best_dist = dist
            best_cam = cam_id
            best_pixels = pixels_np
    return best_cam, best_pixels


def _crop_letterbox(
    frame: np.ndarray,
    pixels: np.ndarray,
    valid: np.ndarray | None,
    crop_size: int,
) -> np.ndarray:
    """Axis-aligned square crop around projected keypoints, letterboxed.

    Args:
        frame: BGR uint8 image.
        pixels: (N, 2) projected pixel coords.
        valid: (N,) bool mask; if None, all are valid.
        crop_size: Output square side length.

    Returns:
        (crop_size, crop_size, 3) BGR uint8 image.
    """
    if valid is not None:
        pixels = pixels[valid]

    # Filter NaN
    mask = ~np.isnan(pixels).any(axis=1)
    pixels = pixels[mask]

    if len(pixels) == 0:
        return np.zeros((crop_size, crop_size, 3), dtype=np.uint8)

    h, w = frame.shape[:2]

    x_min, y_min = pixels.min(axis=0)
    x_max, y_max = pixels.max(axis=0)

    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    half = max((x_max - x_min) / 2, (y_max - y_min) / 2, _MIN_CROP_HALF_PX)
    # Add 20% padding
    half *= 1.2

    # Source rect (may extend outside frame)
    src_x0 = int(np.floor(cx - half))
    src_y0 = int(np.floor(cy - half))
    src_x1 = int(np.ceil(cx + half))
    src_y1 = int(np.ceil(cy + half))
    src_w = src_x1 - src_x0
    src_h = src_y1 - src_y0
    side = max(src_w, src_h)

    # Recenter to make square
    src_x0 = round(cx - side / 2)
    src_y0 = round(cy - side / 2)
    src_x1 = src_x0 + side
    src_y1 = src_y0 + side

    # Extract with border handling
    # Clamp to frame
    fx0 = max(src_x0, 0)
    fy0 = max(src_y0, 0)
    fx1 = min(src_x1, w)
    fy1 = min(src_y1, h)

    if fx1 <= fx0 or fy1 <= fy0:
        return np.zeros((crop_size, crop_size, 3), dtype=np.uint8)

    roi = frame[fy0:fy1, fx0:fx1]

    # Place into square canvas (letterbox)
    canvas = np.zeros((side, side, 3), dtype=np.uint8)
    ox = fx0 - src_x0
    oy = fy0 - src_y0
    canvas[oy : oy + roi.shape[0], ox : ox + roi.shape[1]] = roi

    return cv2.resize(canvas, (crop_size, crop_size), interpolation=cv2.INTER_AREA)


def generate_mosaics(
    run_dir: Path,
    frame_step: int = 1800,
    crop_size: int = 256,
    n_fish: int = 9,
) -> Path:
    """Generate 3x3 fish ID mosaics at sampled frames.

    Args:
        run_dir: Pipeline run directory.
        frame_step: Sample every N frames.
        crop_size: Square side length per fish crop.
        n_fish: Expected number of fish (fills grid).

    Returns:
        Output directory path.
    """
    # Use midlines_stitched.h5 explicitly (not smoothed, which may be stale).
    h5_path = run_dir / "midlines_stitched.h5"
    if not h5_path.exists():
        h5_path = resolve_h5_path(run_dir)
    if h5_path is None:
        raise RuntimeError(f"No midlines HDF5 found in {run_dir}")

    sys.stderr.write(f"Loading midlines from {h5_path.name}...\n")
    all_midlines = load_midlines_from_h5(h5_path)
    total_frames = len(all_midlines)
    sys.stderr.write(f"Loaded {total_frames} frames\n")

    # Load calibration and build projection models.
    config = read_config_yaml(run_dir)
    calib_path = Path(config["calibration_path"])
    if not calib_path.is_absolute():
        for base in (run_dir, run_dir.parent):
            candidate = base / calib_path
            if candidate.exists():
                calib_path = candidate
                break

    calib_data = load_calibration_data(str(calib_path))
    models: dict[str, RefractiveProjectionModel] = {}
    frame_sizes: dict[str, tuple[int, int]] = {}

    for cam_id in sorted(calib_data.cameras):
        cam = calib_data.cameras[cam_id]
        if cam.is_auxiliary:
            continue
        undist = compute_undistortion_maps(cam)
        models[cam_id] = RefractiveProjectionModel(
            K=undist.K_new,
            R=cam.R,
            t=cam.t,
            water_z=calib_data.water_z,
            normal=calib_data.interface_normal,
            n_air=calib_data.n_air,
            n_water=calib_data.n_water,
        )
        frame_sizes[cam_id] = cam.image_size

    # Open videos.
    video_dir = Path(config["video_dir"])
    if not video_dir.is_absolute():
        for base in (run_dir, run_dir.parent):
            candidate = base / video_dir
            if candidate.exists():
                video_dir = candidate
                break

    out_dir = run_dir / "id_mosaics"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Grid layout: 3x3, with labels.
    grid_cols = 3
    grid_rows = 3
    label_h = 24
    cell_h = crop_size + label_h
    cell_w = crop_size
    mosaic_w = grid_cols * cell_w
    mosaic_h = grid_rows * cell_h

    frame_indices = list(range(0, total_frames, frame_step))
    sys.stderr.write(
        f"Generating {len(frame_indices)} mosaics (step={frame_step}) -> {out_dir}\n"
    )

    with VideoFrameSource(video_dir, calib_path) as frame_source:
        for count, fi in enumerate(frame_indices):
            if fi >= len(frame_source):
                break

            frames = frame_source.read_frame(fi)
            frame_dict = all_midlines[fi]

            mosaic = np.zeros((mosaic_h, mosaic_w, 3), dtype=np.uint8)

            for fish_id in range(n_fish):
                row = fish_id // grid_cols
                col = fish_id % grid_cols

                if fish_id in frame_dict:
                    spline = frame_dict[fish_id]
                    pts_3d = _eval_spline_pts(spline)

                    if pts_3d is not None:
                        cam_id, pixels = _pick_best_camera(pts_3d, models, frame_sizes)
                        if cam_id is not None and cam_id in frames:
                            valid = ~np.isnan(pixels).any(axis=1)
                            crop = _crop_letterbox(
                                frames[cam_id], pixels, valid, crop_size
                            )
                        else:
                            crop = np.zeros((crop_size, crop_size, 3), dtype=np.uint8)
                    else:
                        crop = np.zeros((crop_size, crop_size, 3), dtype=np.uint8)
                else:
                    crop = np.zeros((crop_size, crop_size, 3), dtype=np.uint8)

                # Place crop.
                y0 = row * cell_h + label_h
                x0 = col * cell_w
                mosaic[y0 : y0 + crop_size, x0 : x0 + cell_w] = crop

                # Draw label.
                label = f"Fish {fish_id}"
                label_y = row * cell_h + label_h - 6
                cv2.putText(
                    mosaic,
                    label,
                    (x0 + 4, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

            # Frame number label at top-left.
            cv2.putText(
                mosaic,
                f"Frame {fi}",
                (4, 14),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1,
                cv2.LINE_AA,
            )

            filename = f"mosaic_{fi:07d}.jpg"
            cv2.imwrite(str(out_dir / filename), mosaic)

            if (count + 1) % 10 == 0 or count == 0:
                sys.stderr.write(f"  [{count + 1}/{len(frame_indices)}] frame {fi}\n")

    sys.stderr.write(f"Done. {len(frame_indices)} mosaics saved to {out_dir}\n")
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 3x3 fish ID mosaics for swap-rate estimation."
    )
    parser.add_argument(
        "run_dir",
        type=Path,
        help="Pipeline run directory (e.g. ~/aquapose/projects/YH/runs/run_...)",
    )
    parser.add_argument(
        "--frame-step",
        type=int,
        default=1800,
        help="Sample every N frames (default: 1800).",
    )
    parser.add_argument(
        "--crop-size",
        type=int,
        default=256,
        help="Square crop side in pixels (default: 256).",
    )
    parser.add_argument(
        "--n-fish",
        type=int,
        default=9,
        help="Number of fish IDs (default: 9).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    generate_mosaics(
        run_dir=args.run_dir,
        frame_step=args.frame_step,
        crop_size=args.crop_size,
        n_fish=args.n_fish,
    )


if __name__ == "__main__":
    main()
