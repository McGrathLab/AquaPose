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
    ├── geometry/calibration.json   # LUTs omitted (regenerate with prep generate-luts)
    ├── models/{yolo_obb.pt, yolo_pose.pt}
    ├── config.yaml                 # fresh, platform-neutral, relative paths
    ├── README.md
    ├── zenodo-metadata.json
    ├── reference_outputs/          # outputs.h5, animation_3d.html, overlay_mosaic.mp4, timing.txt
    └── checksums.sha256            # written last, over the complete tree

Note on LUTs (D-03):
    The refractive lookup tables (~597 MB) are NOT shipped. They are deterministic
    from calibration.json and are regenerated with ``aquapose prep generate-luts``
    before the first pipeline run. The --regenerate-outputs path runs this step
    automatically to keep maintainer regeneration self-contained.
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
        "-ss",
        str(start_offset),
        "-i",
        str(input_path),
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        str(crf),
        "-pix_fmt",
        "yuv420p",
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
    # Force LF newlines (newline="") so `sha256sum -c` works cross-platform — on
    # Windows the default text-mode translation would emit CRLF, leaving a trailing
    # \r on every filename and breaking verification everywhere.
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
    return manifest_path


# ---------------------------------------------------------------------------
# Deposit verification and cleanup
# ---------------------------------------------------------------------------


def verify_deposit(deposit_dir: Path) -> list[str]:
    """Check the deposit tree for completeness and correct licensing.

    Returns a list of human-readable problem strings. An empty list means the
    deposit passes all checks and is ready for checksumming and Zenodo upload.

    Checks performed:

    - (a) Required paths exist: ``videos/`` has 12 ``.mp4`` files,
      ``geometry/calibration.json``, ``models/yolo_obb.pt``,
      ``models/yolo_pose.pt``, ``config.yaml``, ``README.md``,
      ``zenodo-metadata.json``, and ``reference_outputs/{outputs.h5,
      animation_3d.html, overlay_mosaic.mp4, timing.txt}``.
    - (b) ``config.yaml`` contains no ``/home/`` or ``D:\\`` absolute-path
      substrings (T-111-09 — username / Windows path leak prevention).
    - (c) ``README.md`` contains both ``"CC-BY-4.0"`` and the exact string
      ``"AGPL-3.0-derived artifacts (trained with Ultralytics, AGPL-3.0)"``.
    - (d) ``zenodo-metadata.json`` parses as valid JSON and declares
      ``"license": "cc-by-4.0"`` (T-111-10 — licensing gate).
    - (e) ``geometry/luts/`` is ABSENT — the 597 MB transient LUT directory
      must not be shipped (D-03 corrected).
    - (f) No ``reference_outputs/run_*/`` diagnostic cache directories remain
      (they are transient pipeline artifacts, not deliverables).

    Args:
        deposit_dir: Root of the assembled deposit tree.

    Returns:
        List of problem description strings. Empty list means all checks pass.
    """
    problems: list[str] = []

    # (a) Required paths
    required_files = [
        "geometry/calibration.json",
        "models/yolo_obb.pt",
        "models/yolo_pose.pt",
        "config.yaml",
        "README.md",
        "zenodo-metadata.json",
        "reference_outputs/outputs.h5",
        "reference_outputs/animation_3d.html",
        "reference_outputs/overlay_mosaic.mp4",
        "reference_outputs/timing.txt",
    ]
    for rel in required_files:
        if not (deposit_dir / rel).exists():
            problems.append(f"Missing required file: {rel}")

    videos_dir = deposit_dir / "videos"
    if not videos_dir.exists():
        problems.append("Missing required directory: videos/")
    else:
        mp4_files = list(videos_dir.glob("*.mp4"))
        if len(mp4_files) != 12:
            problems.append(
                f"Expected 12 .mp4 files in videos/, found {len(mp4_files)}"
            )

    # (b) No absolute paths in config.yaml
    config_path = deposit_dir / "config.yaml"
    if config_path.exists():
        config_text = config_path.read_text(encoding="utf-8")
        if "/home/" in config_text:
            problems.append(
                "config.yaml contains absolute path '/home/' — replace with relative paths (D-07)"
            )
        if "D:\\" in config_text:
            problems.append(
                "config.yaml contains absolute path 'D:\\' — replace with relative paths (D-07)"
            )

    # (c) README licensing strings
    readme_path = deposit_dir / "README.md"
    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8")
        if "CC-BY-4.0" not in readme_text:
            problems.append("README.md missing required string 'CC-BY-4.0' (D-12)")
        if (
            "AGPL-3.0-derived artifacts (trained with Ultralytics, AGPL-3.0)"
            not in readme_text
        ):
            problems.append(
                "README.md missing required AGPL-3.0 label: "
                "'AGPL-3.0-derived artifacts (trained with Ultralytics, AGPL-3.0)' (D-12)"
            )

    # (d) zenodo-metadata.json license field
    meta_path = deposit_dir / "zenodo-metadata.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta.get("license") != "cc-by-4.0":
                problems.append(
                    f"zenodo-metadata.json 'license' must be 'cc-by-4.0', "
                    f"got {meta.get('license')!r} (T-111-10)"
                )
        except json.JSONDecodeError as exc:
            problems.append(f"zenodo-metadata.json is not valid JSON: {exc}")

    # (e) geometry/luts/ must be absent (D-03 corrected — LUTs not shipped)
    luts_dir = deposit_dir / "geometry" / "luts"
    if luts_dir.exists():
        problems.append(
            "geometry/luts/ is present — transient LUTs must be excluded from the shipped tree (D-03)"
        )

    # (f) No reference_outputs/run_*/ cache directories
    ref_dir = deposit_dir / "reference_outputs"
    if ref_dir.exists():
        cache_dirs = [
            d for d in ref_dir.iterdir() if d.is_dir() and d.name.startswith("run_")
        ]
        if cache_dirs:
            names = ", ".join(d.name for d in sorted(cache_dirs))
            problems.append(
                f"reference_outputs/ contains pipeline cache dir(s): {names} — "
                "remove before shipping (run finalize_deposit)"
            )

    return problems


def finalize_deposit(deposit_dir: Path) -> None:
    """Remove transient build artifacts that must not appear in the shipped tree.

    Removes, if present:

    - ``geometry/luts/`` — the ~597 MB refractive lookup tables. Deterministic
      from ``calibration.json`` so they are NOT shipped (D-03 corrected). Users
      regenerate them with ``aquapose prep generate-luts`` before their first run.
    - Any ``reference_outputs/run_*/`` directories — intermediate diagnostic
      cache dirs (per-chunk pickles and manifests) written by the pipeline.
      They are not deliverables and must not appear in the checksum manifest.

    Call this in ``main`` AFTER ``--regenerate-outputs`` and BEFORE
    ``verify_deposit``/``write_checksums`` so the manifest never covers these
    transient artifacts.

    Args:
        deposit_dir: Root of the assembled deposit tree.
    """
    # Remove geometry/luts/ if present
    luts_dir = deposit_dir / "geometry" / "luts"
    if luts_dir.exists():
        print(f"  Removing transient LUTs: {luts_dir} ...", end="", flush=True)
        shutil.rmtree(luts_dir)
        print(" done")

    # Remove any reference_outputs/run_*/ cache directories
    ref_dir = deposit_dir / "reference_outputs"
    if ref_dir.exists():
        cache_dirs = sorted(
            d for d in ref_dir.iterdir() if d.is_dir() and d.name.startswith("run_")
        )
        for cache_dir in cache_dirs:
            print(
                f"  Removing pipeline cache dir: {cache_dir.name} ...",
                end="",
                flush=True,
            )
            shutil.rmtree(cache_dir)
            print(" done")


# ---------------------------------------------------------------------------
# Model and calibration copy
# ---------------------------------------------------------------------------


def copy_models_and_calibration(source_dir: Path, output_dir: Path) -> None:
    """Copy canonical models and calibration JSON into the deposit tree.

    Copies:

    - ``training/obb/run_20260318_082016/best_model.pt`` → ``models/yolo_obb.pt``
    - ``training/pose/run_20260318_013005/best_model.pt`` → ``models/yolo_pose.pt``
    - ``geometry/calibration.json`` → ``geometry/calibration.json``

    LUTs are NOT copied (D-03) — they are ~597 MB and are deterministic from
    calibration.json. Users regenerate them with ``aquapose prep generate-luts``
    before the first pipeline run (the pipeline fail-fasts if LUTs are absent).

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

    print(
        f"  Copying OBB model ({OBB_RUN}) -> models/yolo_obb.pt ...", end="", flush=True
    )
    shutil.copy2(obb_src, models_dir / "yolo_obb.pt")
    print(" done")

    print(
        f"  Copying pose model ({POSE_RUN}) -> models/yolo_pose.pt ...",
        end="",
        flush=True,
    )
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

# One-time setup: generate the refractive lookup tables (~600 MB, ~2-5 min)
# The LUTs are deterministic from calibration.json and are NOT shipped with the deposit.
# The pipeline will fail-fast with an error if you skip this step.
aquapose prep generate-luts

# Run the pipeline (generates outputs.h5 + per-chunk diagnostic cache)
aquapose run

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
# Console-script discovery
# ---------------------------------------------------------------------------


def _aquapose_invoke() -> list[str]:
    """Return the argv prefix to invoke the ``aquapose`` console-script.

    Uses the console-script entry-point installed next to ``sys.executable``
    (``Scripts/aquapose.exe`` on Windows, ``bin/aquapose`` on POSIX).  Falls
    back to an inline ``python -c`` import when the entry-point is absent (e.g.
    editable installs in some environments).

    Returns:
        List of one or more strings to prepend to an ``aquapose`` subprocess
        command, e.g. ``["aquapose"]`` or ``[sys.executable, "-c", "..."]``.
    """
    aquapose_script = Path(sys.executable).parent / "aquapose"
    if sys.platform == "win32":
        aquapose_script = aquapose_script.with_suffix(".exe")
    if aquapose_script.exists():
        return [str(aquapose_script)]
    return [sys.executable, "-c", "from aquapose.cli import main; main()"]


def _run_subprocess(cmd: list[str], cwd: Path, label: str) -> None:
    """Run a subprocess command, raising RuntimeError on failure.

    Args:
        cmd: Command argv list.
        cwd: Working directory for the subprocess.
        label: Human-readable label for error messages.

    Raises:
        RuntimeError: If the subprocess exits with a non-zero return code.
    """
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    if result.returncode != 0:
        parts = []
        if result.stderr and result.stderr.strip():
            parts.append(result.stderr.strip())
        if result.stdout and result.stdout.strip():
            parts.append(result.stdout.strip())
        error = "\n".join(parts) if parts else f"Exit code {result.returncode}"
        raise RuntimeError(f"{label} failed:\n{error}")


# ---------------------------------------------------------------------------
# Reference output regeneration (Plan 02)
# ---------------------------------------------------------------------------


def regenerate_reference_outputs(deposit_dir: Path) -> None:
    """Run the pipeline in diagnostic mode then viz on the deposited tree.

    Produces ``reference_outputs/{outputs.h5, animation_3d.html,
    overlay_mosaic.mp4, timing.txt}`` by:

    - **Step A**: Running ``aquapose run --set output_dir=reference_outputs
      --mode diagnostic`` from ``cwd=deposit_dir`` so the relative
      ``project_dir: .`` in the deposited ``config.yaml`` resolves correctly.
      The pipeline writes ``midlines.h5`` into the new run directory.
    - **Step B**: Running ``aquapose viz <run_dir> --animation --overlay
      --output-dir <deposit_dir>/reference_outputs`` to produce the 3D
      animation HTML and the overlay mosaic MP4.
    - **Step C**: Renaming ``midlines.h5`` to the canonical ``outputs.h5``,
      writing ``timing.txt`` with wall-clock durations, and printing a summary
      of the four reference-output artifacts.

    The deposit tree must already contain ``config.yaml``, ``videos/``, and
    ``models/`` before this function is called.

    Args:
        deposit_dir: Root of the assembled deposit tree (absolute path).
            Must contain ``config.yaml`` with ``project_dir: .``.

    Raises:
        RuntimeError: If the pipeline or viz subprocess exits non-zero, or if
            no run directory is found in ``reference_outputs/`` after the
            pipeline completes.
    """
    ref_dir = deposit_dir / "reference_outputs"
    ref_dir.mkdir(parents=True, exist_ok=True)

    invoke = _aquapose_invoke()

    print()
    print("--- Reference Output Regeneration (--regenerate-outputs) ---")

    # ------------------------------------------------------------------
    # Step A0: Generate refractive LUTs (required before pipeline run)
    # The pipeline fail-fasts with FileNotFoundError if LUTs are absent.
    # LUTs are deterministic from calibration.json (~597 MB, ~2-5 min).
    # They will be removed by finalize_deposit() before checksumming.
    # ------------------------------------------------------------------
    print("  Step A0: Running aquapose prep generate-luts ...")
    luts_cmd = [
        *invoke,
        "prep",
        "generate-luts",
    ]
    _run_subprocess(luts_cmd, cwd=deposit_dir, label="aquapose prep generate-luts")
    print("  LUTs generated")

    # ------------------------------------------------------------------
    # Step A: Run the pipeline in diagnostic mode
    # ------------------------------------------------------------------
    print("  Step A: Running aquapose run (diagnostic mode) ...")
    pipeline_cmd = [
        *invoke,
        "run",
        "--set",
        f"output_dir={ref_dir}",
        "--mode",
        "diagnostic",
    ]
    t0_pipeline = time.perf_counter()
    _run_subprocess(pipeline_cmd, cwd=deposit_dir, label="aquapose run")
    pipeline_elapsed = time.perf_counter() - t0_pipeline
    print(f"  Pipeline done in {pipeline_elapsed:.1f}s")

    # ------------------------------------------------------------------
    # Locate the run directory produced under reference_outputs/
    # ------------------------------------------------------------------
    run_dirs = sorted(
        [d for d in ref_dir.iterdir() if d.is_dir() and d.name.startswith("run_")],
        key=lambda p: p.name,
    )
    if not run_dirs:
        raise RuntimeError(
            f"No run_* directory found in {ref_dir} after pipeline completed. "
            "Check that the pipeline wrote its output to the expected location."
        )
    run_dir = run_dirs[-1]
    print(f"  Run directory: {run_dir.name}")

    # ------------------------------------------------------------------
    # Step B: Generate 3D animation + overlay mosaic via aquapose viz
    # ------------------------------------------------------------------
    print("  Step B: Running aquapose viz (--animation --overlay) ...")
    viz_cmd = [
        *invoke,
        "viz",
        str(run_dir),
        "--animation",
        "--overlay",
        "--output-dir",
        str(ref_dir),
    ]
    t0_viz = time.perf_counter()
    _run_subprocess(viz_cmd, cwd=deposit_dir, label="aquapose viz")
    viz_elapsed = time.perf_counter() - t0_viz
    print(f"  Viz done in {viz_elapsed:.1f}s")

    # ------------------------------------------------------------------
    # Step B1: Re-encode overlay_mosaic.mp4 at CRF 28 to shrink it
    # The viz-produced overlay can be ~110 MB; CRF 28 yields ~12 MB.
    # Re-encode in-place: write to a temp path, then replace the original.
    # ------------------------------------------------------------------
    overlay_src = ref_dir / "overlay_mosaic.mp4"
    if overlay_src.exists() and shutil.which("ffmpeg"):
        print(
            "  Step B1: Re-encoding overlay_mosaic.mp4 at CRF 28 ...",
            end="",
            flush=True,
        )
        overlay_tmp = ref_dir / "overlay_mosaic_crf28.mp4"
        reencode_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(overlay_src),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "28",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(overlay_tmp),
        ]
        result = subprocess.run(reencode_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            parts = []
            if result.stderr and result.stderr.strip():
                parts.append(result.stderr.strip())
            if result.stdout and result.stdout.strip():
                parts.append(result.stdout.strip())
            error = "\n".join(parts) if parts else f"Exit code {result.returncode}"
            raise RuntimeError(f"ffmpeg overlay re-encode failed:\n{error}")
        overlay_tmp.replace(overlay_src)
        print(" done")
    elif not shutil.which("ffmpeg"):
        print("  Step B1: ffmpeg not found on PATH — skipping overlay re-encode")

    # ------------------------------------------------------------------
    # Step C: Normalize filenames + write timing.txt
    # ------------------------------------------------------------------
    print("  Step C: Normalizing artifacts ...")

    # Rename midlines.h5 (or midlines_stitched.h5) to outputs.h5 in ref_dir
    midlines_h5 = run_dir / "midlines_stitched.h5"
    if not midlines_h5.exists():
        midlines_h5 = run_dir / "midlines.h5"
    if not midlines_h5.exists():
        raise RuntimeError(
            f"Expected midlines.h5 or midlines_stitched.h5 in {run_dir} "
            "but neither was found."
        )
    outputs_h5 = ref_dir / "outputs.h5"
    shutil.copy2(midlines_h5, outputs_h5)

    # animation_3d.html and overlay_mosaic.mp4 are already at canonical names
    # in ref_dir (written by viz --output-dir)
    animation_html = ref_dir / "animation_3d.html"
    overlay_mp4 = ref_dir / "overlay_mosaic.mp4"

    # Write timing.txt
    timing_txt = ref_dir / "timing.txt"
    timing_txt.write_text(
        f"pipeline_wall_seconds: {pipeline_elapsed:.2f}\n"
        f"viz_wall_seconds: {viz_elapsed:.2f}\n"
        f"total_wall_seconds: {pipeline_elapsed + viz_elapsed:.2f}\n",
        encoding="utf-8",
    )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    artifacts = [
        ("outputs.h5", outputs_h5),
        ("animation_3d.html", animation_html),
        ("overlay_mosaic.mp4", overlay_mp4),
        ("timing.txt", timing_txt),
    ]
    print()
    print("  Reference outputs:")
    for name, path in artifacts:
        size_kb = path.stat().st_size / 1024 if path.exists() else 0.0
        status = f"{size_kb:,.1f} KB" if path.exists() else "MISSING"
        print(f"    {name}: {status}")
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
    reference-output regeneration → finalize_deposit (remove transient artifacts)
    → verify_deposit gate → checksums.sha256.

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

        # Step 6: Optionally regenerate reference outputs (Plan 02)
        if args.regenerate_outputs:
            regenerate_reference_outputs(deposit_dir=output_dir)

        # Step 6b: Remove transient build artifacts before verify + manifest
        # Removes geometry/luts/ (~597 MB) and reference_outputs/run_*/ cache dirs.
        print("--- Step 6b: Finalize deposit (remove transient artifacts) ---")
        finalize_deposit(output_dir)
        print()

        # Step 7: Verify deposit completeness + licensing before checksumming
        print("--- Step 7: Verify deposit tree ---")
        problems = verify_deposit(output_dir)
        if problems:
            print("  DEPOSIT VERIFICATION FAILED:", file=sys.stderr)
            for problem in problems:
                print(f"    - {problem}", file=sys.stderr)
            return 1
        print("  All checks passed")
        print()

        # Step 8: Write checksums over the complete, verified tree (D-10)
        print("--- Step 8: Write checksums.sha256 ---")
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
