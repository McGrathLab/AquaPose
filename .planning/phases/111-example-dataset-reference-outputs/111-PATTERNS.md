# Phase 111: Example Dataset & Reference Outputs - Pattern Map

**Mapped:** 2026-09-01
**Files analyzed:** 4 new/modified files
**Analogs found:** 4 / 4

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/package_tutorial_dataset.py` | utility (standalone script) | file-I/O + subprocess | `tools/smoke_test.py` | role-match (both are publication/tooling scripts invoking aquapose as subprocess) |
| `aquapose-tutorial-data/config.yaml` | config | request-response | `src/aquapose/cli.py` `init_cmd` generated config (lines 178–208) | exact (same relative-path convention) |
| `aquapose-tutorial-data/zenodo-metadata.json` | config | transform | no existing analog | none |
| `aquapose-tutorial-data/README.md` | documentation | — | no existing analog | none |

---

## Pattern Assignments

### `scripts/package_tutorial_dataset.py` (utility, file-I/O + subprocess)

**Primary analog:** `tools/smoke_test.py`
**Secondary analog for ffmpeg subprocess:** `src/aquapose/evaluation/viz/animation.py` (lines 290–307)
**Secondary analog for simple main():** `scripts/detect_swaps.py`

---

#### Module docstring + imports pattern

**From** `tools/smoke_test.py` lines 1–31:

```python
"""Standalone packaging script for the AquaPose YH tutorial dataset.

Trims and re-encodes 12 camera videos (temporal trim only, no spatial downscale),
assembles the Zenodo deposit tree, copies models and calibration, writes a
platform-neutral config.yaml and README.md, optionally regenerates reference
outputs by running the pipeline, and emits a SHA-256 checksum manifest.

Usage::

    python scripts/package_tutorial_dataset.py --source-dir D:/AquaPose_Zenodo_staging/YH \
        --output-dir ./aquapose-tutorial-data [--regenerate-outputs]
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import time
from pathlib import Path
```

Key conventions to copy:
- `from __future__ import annotations` always first
- stdlib only in the top-level import block (no aquapose imports at module level — import lazily inside functions, as `detect_swaps.py` does for `aquapose.*`)
- `argparse`, `subprocess`, `sys`, `shutil`, `hashlib`, `Path` are all pure stdlib and belong at the top

---

#### argparse / CLI entry-point pattern

**From** `tools/smoke_test.py` lines 616–704:

```python
def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the packaging script CLI.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="package_tutorial_dataset",
        description="Package the AquaPose YH tutorial dataset for Zenodo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/package_tutorial_dataset.py --source-dir D:/staging/YH --output-dir ./deposit
  python scripts/package_tutorial_dataset.py --source-dir ... --output-dir ... --regenerate-outputs
        """,
    )
    parser.add_argument(
        "--source-dir",
        metavar="PATH",
        required=True,
        help="Root of the YH staging directory (contains videos/core_videos/, config.yaml, etc.).",
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
        default=None,
        metavar="SECONDS",
        help="Trim start offset in seconds (default: auto-selected documented value).",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        metavar="SECONDS",
        help="Clip duration in seconds (default: 30).",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=23,
        metavar="N",
        help="H.264 CRF value (default: 23; valid range 20-24).",
    )
    parser.add_argument(
        "--regenerate-outputs",
        action="store_true",
        default=False,
        help="Run aquapose run + viz on the deposited clip to regenerate reference outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for CLI invocation.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    # ... orchestration logic ...
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Key conventions:
- Separate `_build_parser()` helper returning `ArgumentParser` — never inline it in `main()`
- `main(argv: list[str] | None = None) -> int` signature (testable, returns exit code)
- `if __name__ == "__main__": sys.exit(main())` — exact boilerplate from `smoke_test.py` line 703
- `argparse.RawDescriptionHelpFormatter` for multi-line epilog examples

---

#### subprocess invocation pattern — invoking `aquapose run` / `aquapose viz`

**From** `tools/smoke_test.py` lines 229–288:

```python
# Locate the `aquapose` console-script entry point next to sys.executable.
# Falls back to `python -c "from aquapose.cli import main; main()"` if not found.
aquapose_script = Path(sys.executable).parent / "aquapose"
if sys.platform == "win32":
    aquapose_script = aquapose_script.with_suffix(".exe")
if aquapose_script.exists():
    invoke: list[str] = [str(aquapose_script)]
else:
    invoke = [
        sys.executable,
        "-c",
        "from aquapose.cli import main; main()",
    ]

cmd = [
    *invoke,
    "run",
    "--config",
    str(config_path),
    "--set",
    f"output_dir={out_dir}",
    "--mode",
    "diagnostic",
]

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=SUBPROCESS_TIMEOUT,
)
if result.returncode != 0:
    parts = []
    if result.stderr and result.stderr.strip():
        parts.append(result.stderr.strip())
    if result.stdout and result.stdout.strip():
        parts.append(result.stdout.strip())
    error = "\n".join(parts) if parts else f"Exit code {result.returncode}"
    raise RuntimeError(f"aquapose run failed:\n{error}")
```

Apply to: `--regenerate-outputs` block calling `aquapose run` (diagnostic mode) then `aquapose viz --animation --overlay`.

CLI shape for reference-output generation (from `src/aquapose/cli.py` lines 41–144, 418–568):
```
aquapose run --config <deposit_dir>/config.yaml \
    --set output_dir=<deposit_dir>/reference_outputs \
    --mode diagnostic

aquapose viz <run_dir> --animation --overlay \
    --output-dir <deposit_dir>/reference_outputs
```

`aquapose viz` takes a positional `run` argument (resolved by `resolve_run`) and `--output-dir`. The `--animation` flag produces interactive HTML; `--overlay` produces the mosaic MP4.

---

#### ffmpeg subprocess pattern — temporal trim + re-encode

**From** `src/aquapose/evaluation/viz/animation.py` lines 256–307:

```python
if not shutil.which("ffmpeg"):
    raise RuntimeError(
        "ffmpeg not found on PATH. Install it (e.g. 'sudo apt install ffmpeg')."
    )

cmd = [
    "ffmpeg",
    "-y",                        # overwrite without prompt
    "-ss", str(start_offset),    # seek before -i for fast trim
    "-i", str(input_path),
    "-t", str(duration),         # clip duration
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", str(crf),            # default 23; range 20-24
    "-pix_fmt", "yuv420p",
    "-vf", "scale=1600:1200",    # HARD CONSTRAINT: no spatial downscale
                                 # pass-through only; omit if source is already 1600x1200
    "-an",                       # strip audio
    str(output_path),
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")
```

Key constraints from D-05:
- `-ss` before `-i` (fast seek / keyframe seek is acceptable for trim; exact would require `-ss` after `-i` but is slower)
- `-c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p`
- `-an` to strip audio
- **Never** add a spatial scale filter that changes 1600x1200
- ffmpeg availability checked via `shutil.which("ffmpeg")` before processing

---

#### SHA-256 checksum manifest pattern

No exact analog in codebase. Use stdlib `hashlib`:

```python
import hashlib

def _sha256(path: Path) -> str:
    """Return hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def write_checksums(deposit_dir: Path) -> Path:
    """Write checksums.sha256 for all files in deposit_dir.

    Format is compatible with ``sha256sum -c``:
        <hex_digest>  <relpath>
    """
    manifest_path = deposit_dir / "checksums.sha256"
    lines: list[str] = []
    for p in sorted(deposit_dir.rglob("*")):
        if p.is_file() and p != manifest_path:
            rel = p.relative_to(deposit_dir).as_posix()
            lines.append(f"{_sha256(p)}  {rel}")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path
```

---

#### Progress reporting pattern

**From** `scripts/detect_swaps.py` lines 88–99 and `tools/smoke_test.py` lines 259–286:

```python
# Use print() with "=" * 60 section headers and indented status lines.
# No logging module setup needed for a standalone packaging script.
print("=" * 60)
print("AquaPose Tutorial Dataset Packager")
print("=" * 60)
print(f"  Source dir: {source_dir}")
print(f"  Output dir: {output_dir}")
print()

# Per-file progress:
print(f"[1/12] Trimming {src.name} ...", end="", flush=True)
# ... work ...
print(" done")
```

Key conventions from both analogs:
- `print()` not `logging` for standalone scripts
- `flush=True` on in-progress lines so terminal updates mid-operation
- Section headers: `"=" * 60` / `"--- Section ---"` pattern
- Summary block at end with key metrics

---

### `aquapose-tutorial-data/config.yaml` (config, request-response)

**Analog:** `src/aquapose/cli.py` `init_cmd` (lines 178–208), which is the canonical source for how `aquapose init` generates a platform-neutral config with relative paths.

**Relative-path convention** (from `cli.py` lines 182–194 and `engine/config.py` lines 741–761):

```yaml
# AquaPose pipeline config — tutorial dataset (CC-BY-4.0 data, AGPL-3.0 models)
# Run from the aquapose-tutorial-data/ directory, or pass project_dir explicitly.

project_dir: .                    # tells load_config to resolve sibling paths
video_dir: videos
calibration_path: geometry/calibration.json
output_dir: runs

n_animals: 9
chunk_size: 300

detection:
  detector_kind: yolo_obb
  weights_path: models/yolo_obb.pt

pose:
  weights_path: models/yolo_pose.pt

midline:
  backend: pose_estimation        # YH uses pose_estimation, not triangulation

mode: diagnostic                  # diagnostic mode for reference-output generation
```

Key facts from `engine/config.py` lines 741–761:
- `project_dir` is the anchor for resolving relative `video_dir`, `calibration_path`, `output_dir`, and sub-config `weights_path` fields
- Setting `project_dir: .` (or the absolute deposit root) makes all sibling relative paths resolve correctly regardless of working directory
- The packager script writes `project_dir` as the absolute path of the deposit root so the config is self-contained when run from any working directory; OR it sets `project_dir: "."` and instructs users to `cd` into the deposit first (per tutorial UX)

**Config authoring** (from `cli.py` lines 200–208):
```python
import yaml

data: dict = {
    "project_dir": ".",
    "video_dir": "videos",
    "calibration_path": "geometry/calibration.json",
    "output_dir": "runs",
    "n_animals": 9,
    "chunk_size": 300,
    "detection": {"detector_kind": "yolo_obb", "weights_path": "models/yolo_obb.pt"},
    "pose": {"weights_path": "models/yolo_pose.pt"},
    "midline": {"backend": "pose_estimation"},
    "mode": "diagnostic",
}
header = "# AquaPose tutorial dataset config\n# Relative paths resolve from project_dir\n\n"
(deposit_dir / "config.yaml").write_text(
    header + yaml.dump(data, default_flow_style=False, sort_keys=False),
    encoding="utf-8",
)
```

---

### `aquapose-tutorial-data/zenodo-metadata.json` (config, transform)

**No analog in codebase.** Use Zenodo REST API schema (standard JSON). The script writes this file; no existing codebase pattern to copy. Use `json.dumps(..., indent=2)`.

Minimal required fields:
```json
{
  "title": "AquaPose YH Tutorial Dataset",
  "creators": [{"name": "Lancaster, Tucker", "orcid": "..."}],
  "description": "...",
  "keywords": ["fish pose estimation", "3D tracking", "multi-view", "aquarium"],
  "license": "cc-by-4.0",
  "upload_type": "dataset",
  "access_right": "open"
}
```

---

## Shared Patterns

### ffmpeg availability guard
**Source:** `src/aquapose/evaluation/viz/animation.py` line 256
**Apply to:** All ffmpeg subprocess calls in `package_tutorial_dataset.py`

```python
if not shutil.which("ffmpeg"):
    raise RuntimeError(
        "ffmpeg not found on PATH. Install it (e.g. 'sudo apt install ffmpeg')."
    )
```

### subprocess error handling
**Source:** `tools/smoke_test.py` lines 275–284
**Apply to:** All `subprocess.run()` calls (ffmpeg trim, aquapose run, aquapose viz)

```python
result = subprocess.run(cmd, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT)
if result.returncode != 0:
    parts = []
    if result.stderr and result.stderr.strip():
        parts.append(result.stderr.strip())
    if result.stdout and result.stdout.strip():
        parts.append(result.stdout.strip())
    error = "\n".join(parts) if parts else f"Exit code {result.returncode}"
    raise RuntimeError(f"Command failed: {error}")
```

### aquapose console-script discovery
**Source:** `tools/smoke_test.py` lines 229–240
**Apply to:** All `aquapose run` / `aquapose viz` subprocess invocations

```python
aquapose_script = Path(sys.executable).parent / "aquapose"
if sys.platform == "win32":
    aquapose_script = aquapose_script.with_suffix(".exe")
invoke = [str(aquapose_script)] if aquapose_script.exists() else [
    sys.executable, "-c", "from aquapose.cli import main; main()"
]
```

### Relative-path config authoring
**Source:** `src/aquapose/cli.py` `init_cmd` lines 178–208 + `src/aquapose/engine/config.py` lines 741–761
**Apply to:** `config.yaml` written by `package_tutorial_dataset.py`

`project_dir` anchors all relative path resolution. Setting it to `.` (and documenting that users must `cd` into the deposit root) or an absolute path both work. The deposit config must NOT contain absolute `/home/tlancaster6/...` paths.

### Path handling
**Source:** `tools/smoke_test.py` lines 192–198, `tools/import_boundary_checker.py` lines 493–499
**Apply to:** All path arguments in `package_tutorial_dataset.py`

```python
source_dir = Path(args.source_dir).expanduser().resolve()
output_dir = Path(args.output_dir).expanduser().resolve()
output_dir.mkdir(parents=True, exist_ok=True)
```

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `aquapose-tutorial-data/zenodo-metadata.json` | config | transform | Zenodo schema; no existing JSON metadata files in codebase |
| `aquapose-tutorial-data/README.md` | documentation | — | First deposit README; no existing deposit-level README to copy from |
| `checksums.sha256` generation | utility | file-I/O | No checksum generation exists in codebase; use stdlib `hashlib` pattern above |

---

## Metadata

**Analog search scope:** `scripts/`, `tools/`, `src/aquapose/cli.py`, `src/aquapose/engine/config.py`, `src/aquapose/evaluation/viz/animation.py`
**Files scanned:** 7 source files read
**Pattern extraction date:** 2026-09-01
