"""Standalone packaging script for the AquaPose YH tutorial dataset.

Trims and re-encodes 12 camera videos (temporal trim only, no spatial downscale),
assembles the Zenodo deposit tree, copies models and calibration, writes a
platform-neutral config.yaml and README.md, optionally regenerates reference
outputs by running the pipeline, and emits a SHA-256 checksum manifest.

Usage::

    python scripts/package_tutorial_dataset.py \\
        --source-dir D:/AquaPose_Zenodo_staging/YH \\
        --output-dir ./aquapose-tutorial-data [--regenerate-outputs]

Source layout expected::

    <source-dir>/
    ├── videos/core_videos/e3v8*-20260218T145915-150429.mp4  (12 cameras)
    ├── geometry/calibration.json
    ├── training/obb/run_20260318_082016/best_model.pt
    ├── training/pose/run_20260318_013005/best_model.pt
    └── config.yaml  (live YH config — used only to read tuned params)

Deposit tree produced::

    <output-dir>/
    ├── videos/                     # 12 x 30s trimmed, re-encoded H.264
    ├── geometry/calibration.json
    ├── models/{yolo_obb.pt, yolo_pose.pt}
    ├── config.yaml                 # fresh, platform-neutral, relative paths
    ├── README.md
    ├── zenodo-metadata.json
    └── checksums.sha256            # written last, over the complete tree
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_START_OFFSET: float = 30.0
"""Default trim start offset in seconds (a representative segment with fish visible)."""

DEFAULT_DURATION: float = 30.0
"""Default clip duration in seconds (30 s ≈ 900 frames @ 30 fps)."""

DEFAULT_CRF: int = 23
"""Default H.264 CRF value (20-24 valid range; 23 is near-lossless for detection)."""

#: Glob pattern for the 12 YH core camera video files (D-01).
CORE_VIDEO_GLOB: str = "e3v8*-20260218T145915-150429.mp4"

#: Canonical OBB model run directory name (D-02). Never use run_20260310_*.
OBB_RUN: str = "run_20260318_082016"

#: Canonical pose model run directory name (D-02). Never use run_20260310_*.
POSE_RUN: str = "run_20260318_013005"


# ---------------------------------------------------------------------------
# ffmpeg helpers
# ---------------------------------------------------------------------------


def _check_ffmpeg() -> None:
    """Raise RuntimeError if ffmpeg is not found on PATH.

    Raises:
        RuntimeError: If ``shutil.which('ffmpeg')`` returns None.
    """
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg not found on PATH. Install it (e.g. 'winget install Gyan.FFmpeg' "
            "on Windows or 'sudo apt install ffmpeg' on Linux) and ensure it is on PATH."
        )


def _build_ffmpeg_cmd(
    input_path: Path,
    output_path: Path,
    start_offset: float,
    duration: float,
    crf: int,
) -> list[str]:
    """Build the ffmpeg argv list for temporal trim + H.264 re-encode.

    HARD CONSTRAINT (D-05): No spatial scale filter is added. The source is
    already 1600x1200 and calibration intrinsics are bound to that resolution.
    Never append ``-vf scale=...``.

    Args:
        input_path: Path to the source video file.
        output_path: Destination path for the re-encoded clip.
        start_offset: Trim start in seconds (``-ss`` before ``-i`` for fast seek).
        duration: Clip duration in seconds.
        crf: H.264 CRF value (20-24 recommended).

    Returns:
        Argv list suitable for ``subprocess.run``.
    """
    return [
        "ffmpeg",
        "-y",
        "-ss", str(start_offset),
        "-i", str(input_path),
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-an",
        str(output_path),
    ]


def trim_and_encode_videos(
    source_dir: Path,
    output_dir: Path,
    start_offset: float,
    duration: float,
    crf: int,
) -> list[Path]:
    """Temporally trim and H.264 re-encode all 12 core camera videos.

    Globs for ``CORE_VIDEO_GLOB`` under ``source_dir/videos/core_videos/`` and
    writes each re-encoded clip to ``output_dir/videos/<same_name>.mp4``.

    The raw 7.5 GB source files are NEVER copied — only the re-encoded trims
    are written to the deposit tree.

    Args:
        source_dir: Root of the YH staging directory.
        output_dir: Root of the deposit tree being assembled.
        start_offset: Trim start in seconds.
        duration: Clip duration in seconds.
        crf: H.264 CRF value.

    Returns:
        List of output paths for the re-encoded clips.

    Raises:
        RuntimeError: If ffmpeg is not on PATH or any re-encode fails.
        FileNotFoundError: If the source video directory does not exist.
    """
    _check_ffmpeg()

    core_dir = source_dir / "videos" / "core_videos"
    if not core_dir.exists():
        raise FileNotFoundError(f"Source video directory not found: {core_dir}")

    sources = sorted(core_dir.glob(CORE_VIDEO_GLOB))
    if not sources:
        raise FileNotFoundError(
            f"No video files matching '{CORE_VIDEO_GLOB}' found in {core_dir}"
        )

    out_video_dir = output_dir / "videos"
    out_video_dir.mkdir(parents=True, exist_ok=True)

    results: list[Path] = []
    total = len(sources)
    for i, src in enumerate(sources, start=1):
        dest = out_video_dir / src.name
        print(f"[{i}/{total}] Trimming {src.name} ...", end="", flush=True)
        cmd = _build_ffmpeg_cmd(src, dest, start_offset, duration, crf)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            parts = []
            if result.stderr and result.stderr.strip():
                parts.append(result.stderr.strip())
            if result.stdout and result.stdout.strip():
                parts.append(result.stdout.strip())
            error = "\n".join(parts) if parts else f"Exit code {result.returncode}"
            raise RuntimeError(f"ffmpeg failed on {src.name}:\n{error}")
        print(" done")
        results.append(dest)

    return results


# ---------------------------------------------------------------------------
# Checksum helpers
# ---------------------------------------------------------------------------


def _sha256(path: Path) -> str:
    """Return the hex SHA-256 digest of a file.

    Reads in 64 KiB chunks to avoid loading the full file into memory.

    Args:
        path: Path to the file to hash.

    Returns:
        Lowercase hex digest string.
    """
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_checksums(deposit_dir: Path) -> Path:
    """Write a SHA-256 checksum manifest for all files in the deposit tree.

    The manifest format is compatible with ``sha256sum -c``::

        <hex_digest>  <posix_relpath>

    Files are sorted for deterministic output. The manifest itself is skipped.

    Args:
        deposit_dir: Root of the assembled deposit tree.

    Returns:
        Path to the written ``checksums.sha256`` file.
    """
    manifest_path = deposit_dir / "checksums.sha256"
    lines: list[str] = []
    for p in sorted(deposit_dir.rglob("*")):
        if p.is_file() and p != manifest_path:
            rel = p.relative_to(deposit_dir).as_posix()
            lines.append(f"{_sha256(p)}  {rel}")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path


# ---------------------------------------------------------------------------
# Model and calibration copy
# ---------------------------------------------------------------------------


def copy_models_and_calibration(source_dir: Path, output_dir: Path) -> None:
    """Copy canonical models and calibration JSON into the deposit tree.

    Copies:

    - ``training/obb/run_20260318_082016/best_model.pt`` → ``models/yolo_obb.pt``
    - ``training/pose/run_20260318_013005/best_model.pt`` → ``models/yolo_pose.pt``
    - ``geometry/calibration.json`` → ``geometry/calibration.json``

    LUTs are NOT copied (D-03) — they auto-generate on the first pipeline run.

    Args:
        source_dir: Root of the YH staging directory.
        output_dir: Root of the deposit tree being assembled.

    Raises:
        FileNotFoundError: If any required source path does not exist. The error
            message names the missing run directory so the caller can diagnose.
    """
    obb_src = source_dir / "training" / "obb" / OBB_RUN / "best_model.pt"
    pose_src = source_dir / "training" / "pose" / POSE_RUN / "best_model.pt"
    cal_src = source_dir / "geometry" / "calibration.json"

    for path, label in [
        (obb_src, f"OBB model ({OBB_RUN})"),
        (pose_src, f"pose model ({POSE_RUN})"),
        (cal_src, "calibration.json"),
    ]:
        if not path.exists():
            raise FileNotFoundError(
                f"Required source file not found [{label}]: {path}\n"
                "Check that the staging directory is complete and that you are using "
                "the correct canonical run IDs (run_20260318_*)."
            )

    models_dir = output_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    geometry_dir = output_dir / "geometry"
    geometry_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Copying OBB model ({OBB_RUN}) -> models/yolo_obb.pt ...", end="", flush=True)
    shutil.copy2(obb_src, models_dir / "yolo_obb.pt")
    print(" done")

    print(f"  Copying pose model ({POSE_RUN}) -> models/yolo_pose.pt ...", end="", flush=True)
    shutil.copy2(pose_src, models_dir / "yolo_pose.pt")
    print(" done")

    print("  Copying geometry/calibration.json ...", end="", flush=True)
    shutil.copy2(cal_src, geometry_dir / "calibration.json")
    print(" done")


# ---------------------------------------------------------------------------
# Deposit config, README, and Zenodo metadata
# ---------------------------------------------------------------------------


def write_deposit_config(output_dir: Path) -> Path:
    """Write the platform-neutral deposit config.yaml.

    Builds an ordered dict with relative paths and ``project_dir: .`` so the
    config resolves correctly when the user ``cd``s into the deposit root.
    Preserves YH tuned values (n_animals=9, chunk_size=300, backend=
    pose_estimation). Does NOT copy the live YH config — that has absolute paths.

    The written file contains no ``/home/`` or ``D:\\`` substrings (T-111-01).

    Args:
        output_dir: Root of the deposit tree.

    Returns:
        Path to the written ``config.yaml``.
    """
    import yaml  # lazy import — yaml is not stdlib

    data: dict = {
        "project_dir": ".",
        "video_dir": "videos",
        "calibration_path": "geometry/calibration.json",
        "output_dir": "runs",
        "n_animals": 9,
        "chunk_size": 300,
        "detection": {
            "detector_kind": "yolo_obb",
            "weights_path": "models/yolo_obb.pt",
        },
        "pose": {
            "weights_path": "models/yolo_pose.pt",
        },
        "midline": {
            "backend": "pose_estimation",
        },
    }

    header = (
        "# AquaPose tutorial dataset config (CC-BY-4.0 data, AGPL-3.0 models)\n"
        "# Run from the aquapose-tutorial-data/ directory:\n"
        "#   cd aquapose-tutorial-data\n"
        "#   aquapose run --config config.yaml\n\n"
    )
    config_path = output_dir / "config.yaml"
    config_path.write_text(
        header + yaml.dump(data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    return config_path


def write_deposit_readme(output_dir: Path) -> Path:
    """Write the deposit README.md with provenance, license, and usage instructions.

    License section explicitly labels:
    - Videos + calibration: CC-BY-4.0
    - Model weights: AGPL-3.0-derived artifacts (trained with Ultralytics, AGPL-3.0)

    Includes a hard-constraint note that footage must never be spatially downscaled
    (calibration intrinsics are bound to 1600x1200).

    Args:
        output_dir: Root of the deposit tree.

    Returns:
        Path to the written ``README.md``.
    """
    content = """\
# AquaPose YH Tutorial Dataset

A 30-second, 12-camera tutorial clip for [AquaPose](https://github.com/tucklancaster/AquaPose) —
3D fish pose estimation via refractive multi-view triangulation.

## Rig and Subjects

- **Cameras:** 12-camera ring rig at ~0.6 m radius over a 2 m cylindrical tank,
  cameras oriented straight down through a flat air-water interface (no glass).
  Frame rate: 30 fps. Resolution: 1600 x 1200.
- **Subjects:** 9 cichlids (3 male, 6 female), ~10 cm body length.
  Clear water with controlled diffuse lighting.

## Deposit Contents

| Path | Description |
|------|-------------|
| `videos/` | 12 x 30-second H.264-encoded clips (one per camera) |
| `geometry/calibration.json` | Refractive camera calibration (~1.5 MB) |
| `models/yolo_obb.pt` | Oriented bounding-box detection model |
| `models/yolo_pose.pt` | 6-keypoint fish pose estimation model |
| `config.yaml` | Pipeline config (relative paths, `project_dir: .`) |
| `reference_outputs/` | Pre-computed outputs for verification (added by Plan 02) |
| `checksums.sha256` | SHA-256 manifest for all deposit files |

## How to Reproduce

```bash
# Install AquaPose
pip install aquapose

# Change into the deposit directory (config.yaml uses relative paths)
cd aquapose-tutorial-data

# Run the pipeline (generates outputs.h5 + per-chunk diagnostic cache)
aquapose run --config config.yaml

# Produce the 3D animation and overlay mosaic
aquapose viz runs/<run_dir>
```

## Note on Re-encoding Your Own Footage

**HARD CONSTRAINT: Never spatially downscale** video before passing it to
AquaPose. The calibration intrinsics and refractive ray-casting are bound to
the original capture resolution (1600 x 1200). Halving the resolution silently
invalidates every ray cast. Temporal trim and bitrate reduction are safe;
spatial scaling is not.

## License

- **Videos and calibration** (`videos/`, `geometry/calibration.json`): [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
- **Bundled model weights** (`models/yolo_obb.pt`, `models/yolo_pose.pt`): AGPL-3.0-derived artifacts (trained with Ultralytics, AGPL-3.0)
- **AquaPose code**: AGPL-3.0

When using the videos or calibration data, please cite the Zenodo DOI (see below).

## Citation

```bibtex
@dataset{lancaster_aquapose_yh_tutorial_2026,
  title   = {AquaPose YH Tutorial Dataset},
  author  = {Lancaster, Tucker},
  year    = {2026},
  doi     = {<DOI filled after upload>},
  license = {CC-BY-4.0 (data), AGPL-3.0 (models)},
}
```
"""
    readme_path = output_dir / "README.md"
    readme_path.write_text(content, encoding="utf-8")
    return readme_path


def write_zenodo_metadata(output_dir: Path) -> Path:
    """Write the zenodo-metadata.json for Zenodo deposit preparation.

    Args:
        output_dir: Root of the deposit tree.

    Returns:
        Path to the written ``zenodo-metadata.json``.
    """
    metadata: dict = {
        "title": "AquaPose YH Tutorial Dataset",
        "creators": [{"name": "Lancaster, Tucker"}],
        "description": (
            "A 30-second, 12-camera tutorial clip for AquaPose (3D fish pose estimation "
            "via refractive multi-view triangulation). Contains trimmed H.264-encoded "
            "video from all 12 cameras, refractive calibration JSON, trained YOLO "
            "detection and pose estimation weights, a platform-neutral pipeline "
            "config.yaml, and pre-computed reference outputs. Intended to let an "
            "outside researcher reproduce the AquaPose pipeline end-to-end on real data."
        ),
        "keywords": [
            "fish pose estimation",
            "3D tracking",
            "multi-view",
            "refractive",
            "aquarium",
            "cichlid",
        ],
        "license": "cc-by-4.0",
        "upload_type": "dataset",
        "access_right": "open",
    }
    meta_path = output_dir / "zenodo-metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return meta_path


# ---------------------------------------------------------------------------
# Reference output regeneration stub (Plan 02 will implement)
# ---------------------------------------------------------------------------


def regenerate_reference_outputs(output_dir: Path) -> None:
    """Stub for reference-output regeneration — implemented in Plan 02.

    Runs ``aquapose run`` (diagnostic mode) then ``aquapose viz`` on the deposited
    clip and config to produce ``reference_outputs/{outputs.h5, animation_3d.html,
    overlay_mosaic.mp4, timing.txt}``.

    This function is a documented stub. Plan 02 (reference outputs plan) will
    fill in the subprocess invocations. It prints a notice and returns without
    doing anything so the rest of the packaging workflow can complete.

    Args:
        output_dir: Root of the deposit tree (contains config.yaml, videos/, etc.).
    """
    print()
    print("--- Reference Output Regeneration (--regenerate-outputs) ---")
    print("  NOTE: This step is handled by Plan 02 (111-02-PLAN.md).")
    print("  Run again after Plan 02 is complete to generate reference outputs.")
    print("  Skipping for now.")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the packaging script CLI.

    Returns:
        Configured ArgumentParser with all packaging flags.
    """
    parser = argparse.ArgumentParser(
        prog="package_tutorial_dataset",
        description="Package the AquaPose YH tutorial dataset for Zenodo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python scripts/package_tutorial_dataset.py \\
      --source-dir D:/AquaPose_Zenodo_staging/YH \\
      --output-dir ./aquapose-tutorial-data

  python scripts/package_tutorial_dataset.py \\
      --source-dir D:/AquaPose_Zenodo_staging/YH \\
      --output-dir ./aquapose-tutorial-data \\
      --start-offset 45.0 --duration 30.0 --crf 22 \\
      --regenerate-outputs

Defaults:
  --start-offset  {DEFAULT_START_OFFSET} seconds
  --duration      {DEFAULT_DURATION} seconds
  --crf           {DEFAULT_CRF} (valid range 20-24)
        """,
    )
    parser.add_argument(
        "--source-dir",
        metavar="PATH",
        required=True,
        help=(
            "Root of the YH staging directory "
            "(contains videos/core_videos/, geometry/, training/, config.yaml)."
        ),
    )
    parser.add_argument(
        "--output-dir",
        metavar="PATH",
        default="./aquapose-tutorial-data",
        help="Destination deposit tree root (default: ./aquapose-tutorial-data).",
    )
    parser.add_argument(
        "--start-offset",
        type=float,
        default=DEFAULT_START_OFFSET,
        metavar="SECONDS",
        help=(
            f"Trim start offset in seconds (default: {DEFAULT_START_OFFSET}). "
            "Pick a segment where most/all fish are visible and dispersed."
        ),
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=DEFAULT_DURATION,
        metavar="SECONDS",
        help=f"Clip duration in seconds (default: {DEFAULT_DURATION}).",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=DEFAULT_CRF,
        metavar="N",
        help=f"H.264 CRF value (default: {DEFAULT_CRF}; valid range 20-24).",
    )
    parser.add_argument(
        "--regenerate-outputs",
        action="store_true",
        default=False,
        help=(
            "Run aquapose run + viz on the deposited clip to regenerate reference outputs. "
            "Requires a GPU and the full pipeline. Plan 02 implements this step."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Package the AquaPose YH tutorial dataset for Zenodo.

    Orchestrates: ffmpeg trim+re-encode → tree assembly → model/calibration copy
    → deposit config.yaml → README.md → zenodo-metadata.json → (optional)
    reference-output regeneration → checksums.sha256.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    source_dir = Path(args.source_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("AquaPose Tutorial Dataset Packager")
    print("=" * 60)
    print(f"  Source dir : {source_dir}")
    print(f"  Output dir : {output_dir}")
    print(f"  Start      : {args.start_offset}s")
    print(f"  Duration   : {args.duration}s")
    print(f"  CRF        : {args.crf}")
    print(f"  Regen outs : {args.regenerate_outputs}")
    print()

    t0 = time.monotonic()

    try:
        # Step 1: Trim and re-encode all 12 camera videos
        print("--- Step 1: Trim & re-encode videos ---")
        clips = trim_and_encode_videos(
            source_dir=source_dir,
            output_dir=output_dir,
            start_offset=args.start_offset,
            duration=args.duration,
            crf=args.crf,
        )
        print(f"  {len(clips)} clips written to {output_dir / 'videos'}")
        print()

        # Step 2: Copy canonical models and calibration
        print("--- Step 2: Copy models and calibration ---")
        copy_models_and_calibration(source_dir=source_dir, output_dir=output_dir)
        print()

        # Step 3: Write deposit config.yaml
        print("--- Step 3: Write config.yaml ---")
        config_path = write_deposit_config(output_dir=output_dir)
        print(f"  Written: {config_path}")
        print()

        # Step 4: Write README.md
        print("--- Step 4: Write README.md ---")
        readme_path = write_deposit_readme(output_dir=output_dir)
        print(f"  Written: {readme_path}")
        print()

        # Step 5: Write zenodo-metadata.json
        print("--- Step 5: Write zenodo-metadata.json ---")
        meta_path = write_zenodo_metadata(output_dir=output_dir)
        print(f"  Written: {meta_path}")
        print()

        # Step 6: Optionally regenerate reference outputs (Plan 02 stub)
        if args.regenerate_outputs:
            regenerate_reference_outputs(output_dir=output_dir)

        # Step 7: Write checksums over the assembled tree (partial — full manifest in Plan 03)
        print("--- Step 7: Write checksums.sha256 ---")
        manifest = write_checksums(output_dir)
        print(f"  Written: {manifest}")
        print()

    except (FileNotFoundError, RuntimeError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    elapsed = time.monotonic() - t0
    print("=" * 60)
    print(f"Done in {elapsed:.1f}s")
    print(f"Deposit tree: {output_dir}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
