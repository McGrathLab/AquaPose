"""Generate short video clips for each auto-corrected swap event.

For each swap, picks the camera where the two involved fish are most central and
renders a clip with reprojected midlines and corrected ID labels overlaid.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import h5py
import numpy as np
import scipy.interpolate
import torch
import yaml

# Clip half-length in frames (±3 sec at 30 fps = 6 sec total).
_HALF_WINDOW = 90
_N_SPLINE_EVAL = 50
_T_VALS = np.linspace(0.0, 1.0, _N_SPLINE_EVAL)

# BGR palette matching overlay.py.
_PALETTE_BGR: list[tuple[int, int, int]] = [
    (112, 48, 0),
    (76, 211, 234),
    (153, 170, 68),
    (238, 204, 102),
    (51, 136, 34),
    (51, 153, 153),
    (119, 102, 238),
    (170, 153, 238),
    (119, 51, 170),
    (136, 34, 51),
    (51, 119, 238),
    (17, 51, 204),
    (85, 34, 136),
    (119, 51, 238),
    (153, 68, 170),
    (170, 119, 68),
    (221, 170, 119),
    (119, 204, 221),
    (51, 204, 187),
    (102, 136, 238),
]


def _fish_color(fish_id: int) -> tuple[int, int, int]:
    return _PALETTE_BGR[fish_id % len(_PALETTE_BGR)]


def _eval_spline(cp: np.ndarray, knots: np.ndarray, degree: int) -> np.ndarray | None:
    """Evaluate B-spline from control points, returning (N, 3) array."""
    if np.all(np.isnan(cp)):
        return None
    try:
        bspl = scipy.interpolate.BSpline(knots, cp.astype(np.float64), degree)
        return bspl(_T_VALS)
    except Exception:
        return None


def _get_fish_points(
    grp: h5py.Group,
    row: int,
    fish_id: int,
    knots: np.ndarray,
    degree: int,
) -> np.ndarray | None:
    """Get 3D midline points for a fish at a given row index."""
    fids = grp["fish_id"][row]
    slot = np.where(fids == fish_id)[0]
    if len(slot) == 0:
        return None
    s = slot[0]
    cp = grp["control_points"][row, s].astype(np.float64)
    pts = _eval_spline(cp, knots, degree)
    if pts is not None:
        return pts
    raw = grp["points"][row, s].astype(np.float64)
    if not np.all(np.isnan(raw)):
        return raw
    return None


def _find_row(frame_index: np.ndarray, target_frame: int) -> int | None:
    """Binary search for the row matching target_frame."""
    idx = np.searchsorted(frame_index, target_frame)
    if idx < len(frame_index) and frame_index[idx] == target_frame:
        return int(idx)
    return None


def _project_points(
    pts_3d: np.ndarray,
    model: object,
) -> np.ndarray | None:
    """Project (N, 3) world points to (M, 2) pixel coords via refractive model."""
    t = torch.tensor(pts_3d, dtype=torch.float32, device=model.C.device)
    pixels, valid = model.project(t)
    px = pixels.cpu().numpy()
    v = valid.cpu().numpy()
    px = px[v]
    return px.astype(np.float32) if len(px) >= 2 else None


def _pick_best_camera(
    grp: h5py.Group,
    frame_index: np.ndarray,
    frame: int,
    fish_a: int,
    fish_b: int,
    knots: np.ndarray,
    degree: int,
    models: dict,
    img_w: int,
    img_h: int,
) -> str | None:
    """Pick the camera where both fish project closest to frame centre."""
    row = _find_row(frame_index, frame)
    if row is None:
        return None

    pts_a = _get_fish_points(grp, row, fish_a, knots, degree)
    pts_b = _get_fish_points(grp, row, fish_b, knots, degree)
    if pts_a is None and pts_b is None:
        return None

    cx, cy = img_w / 2.0, img_h / 2.0
    best_cam = None
    best_score = float("inf")

    for cam_id, model in models.items():
        dists = []
        for pts in (pts_a, pts_b):
            if pts is None:
                continue
            px = _project_points(pts, model)
            if px is None:
                continue
            centroid = px.mean(axis=0)
            dists.append(np.hypot(centroid[0] - cx, centroid[1] - cy))

        if not dists:
            continue
        score = max(dists)  # worst-case distance from centre
        if score < best_score:
            best_score = score
            best_cam = cam_id

    return best_cam


def _draw_overlay(
    frame: np.ndarray,
    pts_2d: np.ndarray,
    fish_id: int,
    thickness: int = 3,
) -> None:
    """Draw midline polyline + head dot + ID label on a frame."""
    color = _fish_color(fish_id)
    pts_int = pts_2d.astype(np.int32)
    if len(pts_int) >= 2:
        cv2.polylines(frame, [pts_int], False, color, thickness)
    # Head dot.
    cv2.circle(frame, tuple(pts_int[0]), 6, (0, 0, 255), -1)
    # ID label with background.
    label = f"Fish {fish_id}"
    lx, ly = int(pts_int[0][0]) + 10, int(pts_int[0][1]) - 10
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    cv2.rectangle(frame, (lx - 2, ly - th - 4), (lx + tw + 2, ly + 4), (0, 0, 0), -1)
    cv2.putText(frame, label, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def _draw_hud(
    frame: np.ndarray,
    frame_idx: int,
    swap_frame: int,
    fish_a: int,
    fish_b: int,
    cam_id: str,
) -> None:
    """Draw frame counter + swap marker HUD at bottom of frame."""
    h, w = frame.shape[:2]
    delta = frame_idx - swap_frame
    sign = "+" if delta >= 0 else ""
    text = f"frame {frame_idx}  ({sign}{delta})  cam:{cam_id}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.rectangle(frame, (0, h - th - 12), (tw + 16, h), (0, 0, 0), -1)
    cv2.putText(
        frame, text, (8, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
    )
    # Flash "SWAP" at the swap frame.
    if frame_idx == swap_frame:
        sw_text = f"SWAP  Fish {fish_a} <-> Fish {fish_b}"
        (stw, sth), _ = cv2.getTextSize(sw_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        sx = (w - stw) // 2
        sy = 40
        cv2.rectangle(
            frame, (sx - 8, sy - sth - 8), (sx + stw + 8, sy + 8), (0, 0, 180), -1
        )
        cv2.putText(
            frame,
            sw_text,
            (sx, sy),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "run_dir",
        type=Path,
        help="Pipeline run directory (contains midlines_stitched.h5 and config.yaml)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: <run_dir>/viz/swap_events/)",
    )
    parser.add_argument(
        "--half-window",
        type=int,
        default=_HALF_WINDOW,
        help=f"Frames before/after swap (default: {_HALF_WINDOW})",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=30.0,
        help="Output video frame rate (default: 30)",
    )
    args = parser.parse_args()

    run_dir: Path = args.run_dir
    out_dir: Path = args.output_dir or run_dir / "viz" / "swap_events"
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- Resolve H5 path (prefer stitched) ---
    h5_path = None
    for name in ("midlines_stitched.h5", "midlines.h5"):
        p = run_dir / name
        if p.exists():
            h5_path = p
            break
    if h5_path is None:
        sys.exit("No midlines HDF5 found in run directory")

    # --- Load config ---
    config_path = run_dir / "config.yaml"
    if not config_path.exists():
        sys.exit("config.yaml not found in run directory")
    config = yaml.safe_load(config_path.read_text())

    # --- Resolve paths ---
    calib_path = Path(config["calibration_path"])
    if not calib_path.is_absolute():
        for base in (run_dir, run_dir.parent):
            if (base / calib_path).exists():
                calib_path = base / calib_path
                break

    video_dir = Path(config["video_dir"])
    if not video_dir.is_absolute():
        for base in (run_dir, run_dir.parent):
            if (base / video_dir).exists():
                video_dir = base / video_dir
                break

    # --- Discover available video cameras ---
    from aquapose.io import discover_camera_videos

    video_paths = discover_camera_videos(video_dir)
    available_cams = set(video_paths.keys())
    print(f"Available video cameras: {sorted(available_cams)}")

    # --- Load calibration + build projection models (only for cameras with video) ---
    from aquapose.calibration.loader import (
        compute_undistortion_maps,
        load_calibration_data,
        undistort_image,
    )
    from aquapose.calibration.projection import RefractiveProjectionModel

    calib = load_calibration_data(str(calib_path))

    models: dict[str, RefractiveProjectionModel] = {}
    undist_maps = {}
    for cam_id in available_cams:
        if cam_id not in calib.cameras:
            continue
        cam = calib.cameras[cam_id]
        um = compute_undistortion_maps(cam)
        undist_maps[cam_id] = um
        models[cam_id] = RefractiveProjectionModel(
            K=um.K_new,
            R=cam.R,
            t=cam.t,
            water_z=calib.water_z,
            normal=calib.interface_normal,
            n_air=calib.n_air,
            n_water=calib.n_water,
        )
    img_w, img_h = next(
        calib.cameras[c].image_size for c in available_cams if c in calib.cameras
    )
    print(f"Built {len(models)} projection models, frame size {img_w}x{img_h}")

    # --- Open video captures ---
    captures: dict[str, cv2.VideoCapture] = {}
    for cam_id, vpath in video_paths.items():
        if cam_id in models:
            cap = cv2.VideoCapture(str(vpath))
            if cap.isOpened():
                captures[cam_id] = cap

    def read_frame(cam_id: str, frame_idx: int) -> np.ndarray | None:
        if cam_id not in captures:
            return None
        cap = captures[cam_id]
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            return None
        if cam_id in undist_maps:
            frame = undistort_image(frame, undist_maps[cam_id])
        return frame

    # --- Process swap events ---
    try:
        with h5py.File(h5_path, "r") as h5:
            grp = h5["midlines"]
            swap_events = grp["swap_events"][:]
            frame_index = grp["frame_index"][:]
            knots = np.asarray(grp.attrs["SPLINE_KNOTS"], dtype=np.float64)
            degree = int(grp.attrs["SPLINE_K"])
            max_frame = int(frame_index[-1])

            auto = swap_events[swap_events["auto_corrected"]]
            print(f"{len(auto)} auto-corrected swap events to render")

            for i, ev in enumerate(auto):
                swap_frame = int(ev["frame"])
                fish_a = int(ev["fish_a"])
                fish_b = int(ev["fish_b"])
                best_cam = _pick_best_camera(
                    grp,
                    frame_index,
                    swap_frame,
                    fish_a,
                    fish_b,
                    knots,
                    degree,
                    models,
                    img_w,
                    img_h,
                )
                if best_cam is None:
                    print(f"  [{i + 1}/{len(auto)}] SKIP (no projection)")
                    continue

                model = models[best_cam]
                f_start = max(swap_frame - args.half_window, 0)
                f_end = min(swap_frame + args.half_window, max_frame)

                out_path = (
                    out_dir
                    / f"swap_{i + 1:03d}_f{swap_frame}_fish{fish_a}_fish{fish_b}.mp4"
                )
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(
                    str(out_path), fourcc, args.fps, (img_w, img_h)
                )

                for fi in range(f_start, f_end + 1):
                    img = read_frame(best_cam, fi)
                    if img is None:
                        continue

                    row = _find_row(frame_index, fi)
                    if row is not None:
                        for fid in (fish_a, fish_b):
                            pts_3d = _get_fish_points(grp, row, fid, knots, degree)
                            if pts_3d is None:
                                continue
                            px = _project_points(pts_3d, model)
                            if px is not None:
                                _draw_overlay(img, px, fid)

                    _draw_hud(img, fi, swap_frame, fish_a, fish_b, best_cam)
                    writer.write(img)

                writer.release()
                n_frames = f_end - f_start + 1
                dur = n_frames / args.fps
                print(
                    f"  [{i + 1}/{len(auto)}] {out_path.name}  "
                    f"({best_cam}, {n_frames}f, {dur:.1f}s)"
                )

    finally:
        for cap in captures.values():
            cap.release()

    print(f"\nDone — clips saved to {out_dir}")


if __name__ == "__main__":
    main()
