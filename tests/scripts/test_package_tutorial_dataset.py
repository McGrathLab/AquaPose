"""Unit tests for scripts/package_tutorial_dataset.py.

Tests cover:
- Parser construction (flags present, defaults, required --source-dir)
- ffmpeg command construction (libx264, CRF, -an, yuv420p; NO scale token)
- ffmpeg availability guard (RuntimeError when shutil.which -> None)
- SHA-256 helper correctness
- deposit config authoring (relative paths, n_animals, no absolute paths)
- deposit README authoring (license strings, no-downscale note)
- deposit zenodo-metadata.json authoring (valid JSON, license, upload_type)
- copy_models_and_calibration (correct run IDs, raises on missing source)
"""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml

# ---------------------------------------------------------------------------
# Module import via path insertion
# ---------------------------------------------------------------------------

# Insert the project root so ``scripts.package_tutorial_dataset`` is importable.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

pkg = importlib.import_module("scripts.package_tutorial_dataset")


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def deposit_dir(tmp_path: Path) -> Path:
    """Return a fresh temporary deposit directory."""
    d = tmp_path / "deposit"
    d.mkdir()
    return d


@pytest.fixture
def source_dir(tmp_path: Path) -> Path:
    """Return a minimal staging directory with all expected source files."""
    staging = tmp_path / "staging"
    # videos/core_videos
    core = staging / "videos" / "core_videos"
    core.mkdir(parents=True)
    # geometry
    geo = staging / "geometry"
    geo.mkdir()
    (geo / "calibration.json").write_bytes(b"{}")

    # canonical model paths (D-02)
    obb_dir = staging / "training" / "obb" / pkg.OBB_RUN
    obb_dir.mkdir(parents=True)
    (obb_dir / "best_model.pt").write_bytes(b"fake-obb")

    pose_dir = staging / "training" / "pose" / pkg.POSE_RUN
    pose_dir.mkdir(parents=True)
    (pose_dir / "best_model.pt").write_bytes(b"fake-pose")

    return staging


# ---------------------------------------------------------------------------
# Task 1 tests: parser, ffmpeg command, sha256
# ---------------------------------------------------------------------------


class TestParser:
    """Tests for _build_parser()."""

    def test_required_source_dir(self) -> None:
        """main([]) raises SystemExit because --source-dir is required."""
        with pytest.raises(SystemExit) as exc:
            pkg.main([])
        assert exc.value.code != 0

    def test_default_output_dir(self) -> None:
        """--output-dir defaults to ./aquapose-tutorial-data."""
        parser = pkg._build_parser()
        args = parser.parse_args(["--source-dir", "/some/path"])
        assert args.output_dir == "./aquapose-tutorial-data"

    def test_default_duration(self) -> None:
        """--duration defaults to 30.0."""
        parser = pkg._build_parser()
        args = parser.parse_args(["--source-dir", "/some/path"])
        assert args.duration == 30.0

    def test_default_crf(self) -> None:
        """--crf defaults to 23."""
        parser = pkg._build_parser()
        args = parser.parse_args(["--source-dir", "/some/path"])
        assert args.crf == 23

    def test_regenerate_outputs_default_false(self) -> None:
        """--regenerate-outputs defaults to False (store_true)."""
        parser = pkg._build_parser()
        args = parser.parse_args(["--source-dir", "/some/path"])
        assert args.regenerate_outputs is False

    def test_parser_accepts_all_flags(self) -> None:
        """All documented flags parse without error."""
        parser = pkg._build_parser()
        args = parser.parse_args([
            "--source-dir", "/staging",
            "--output-dir", "/deposit",
            "--start-offset", "45.0",
            "--duration", "30.0",
            "--crf", "22",
            "--regenerate-outputs",
        ])
        assert args.start_offset == 45.0
        assert args.crf == 22
        assert args.regenerate_outputs is True


class TestBuildFfmpegCmd:
    """Tests for _build_ffmpeg_cmd()."""

    def _cmd_str(self, **kwargs: Any) -> str:
        defaults: dict[str, Any] = {
            "input_path": Path("/in/video.mp4"),
            "output_path": Path("/out/video.mp4"),
            "start_offset": 30.0,
            "duration": 30.0,
            "crf": 23,
        }
        defaults.update(kwargs)
        cmd = pkg._build_ffmpeg_cmd(**defaults)
        return " ".join(str(t) for t in cmd)

    def test_contains_libx264(self) -> None:
        assert "libx264" in self._cmd_str()

    def test_contains_crf_value(self) -> None:
        cmd = pkg._build_ffmpeg_cmd(
            input_path=Path("/in.mp4"),
            output_path=Path("/out.mp4"),
            start_offset=0.0,
            duration=30.0,
            crf=23,
        )
        assert "-crf" in cmd
        assert "23" in cmd

    def test_contains_an(self) -> None:
        """Audio-strip flag -an must be present."""
        assert "-an" in self._cmd_str()

    def test_contains_yuv420p(self) -> None:
        assert "yuv420p" in self._cmd_str()

    def test_no_scale_filter(self) -> None:
        """HARD CONSTRAINT (D-05): no spatial scale filter token."""
        cmd_str = self._cmd_str()
        assert "scale" not in cmd_str, (
            "ffmpeg command must NOT contain 'scale' — spatial downscale "
            "invalidates 1600x1200 calibration intrinsics."
        )

    def test_no_vf_flag(self) -> None:
        """No -vf flag of any kind should appear."""
        assert "-vf" not in self._cmd_str()

    def test_ss_before_i(self) -> None:
        """Fast-seek: -ss must appear before -i in the argv list."""
        cmd = pkg._build_ffmpeg_cmd(
            input_path=Path("/in.mp4"),
            output_path=Path("/out.mp4"),
            start_offset=10.0,
            duration=30.0,
            crf=23,
        )
        assert "-ss" in cmd
        assert "-i" in cmd
        assert cmd.index("-ss") < cmd.index("-i")

    def test_contains_preset_slow(self) -> None:
        cmd = pkg._build_ffmpeg_cmd(
            input_path=Path("/in.mp4"),
            output_path=Path("/out.mp4"),
            start_offset=0.0,
            duration=30.0,
            crf=23,
        )
        assert "-preset" in cmd
        assert "slow" in cmd

    def test_returns_list_of_strings(self) -> None:
        cmd = pkg._build_ffmpeg_cmd(
            input_path=Path("/in.mp4"),
            output_path=Path("/out.mp4"),
            start_offset=0.0,
            duration=30.0,
            crf=23,
        )
        assert isinstance(cmd, list)
        assert all(isinstance(t, str) for t in cmd)


class TestFfmpegGuard:
    """Tests for the ffmpeg availability check."""

    def test_raises_when_ffmpeg_missing(self) -> None:
        """RuntimeError with 'ffmpeg' in message when shutil.which returns None."""
        with patch("shutil.which", return_value=None), pytest.raises(RuntimeError, match="ffmpeg"):
            pkg._check_ffmpeg()

    def test_no_raise_when_ffmpeg_present(self) -> None:
        """No error raised when shutil.which returns a path."""
        with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
            pkg._check_ffmpeg()  # should not raise


class TestSha256:
    """Tests for _sha256()."""

    def test_correct_digest(self, tmp_path: Path) -> None:
        """_sha256 returns the same digest as hashlib.sha256 on the same bytes."""
        data = b"AquaPose tutorial dataset checksum test\n" * 100
        f = tmp_path / "test.bin"
        f.write_bytes(data)
        expected = hashlib.sha256(data).hexdigest()
        assert pkg._sha256(f) == expected

    def test_returns_str(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_bytes(b"hello")
        result = pkg._sha256(f)
        assert isinstance(result, str)
        assert len(result) == 64  # hex SHA-256 is always 64 chars


class TestWriteChecksums:
    """Tests for write_checksums()."""

    def test_manifest_created(self, deposit_dir: Path) -> None:
        (deposit_dir / "a.txt").write_text("hello", encoding="utf-8")
        manifest = pkg.write_checksums(deposit_dir)
        assert manifest.exists()
        assert manifest.name == "checksums.sha256"

    def test_manifest_not_included_in_itself(self, deposit_dir: Path) -> None:
        (deposit_dir / "a.txt").write_text("hello", encoding="utf-8")
        pkg.write_checksums(deposit_dir)
        content = (deposit_dir / "checksums.sha256").read_text(encoding="utf-8")
        assert "checksums.sha256" not in content

    def test_line_format(self, deposit_dir: Path) -> None:
        (deposit_dir / "b.txt").write_bytes(b"data")
        pkg.write_checksums(deposit_dir)
        lines = (deposit_dir / "checksums.sha256").read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        digest, path = lines[0].split("  ", 1)
        assert len(digest) == 64
        assert path == "b.txt"


# ---------------------------------------------------------------------------
# Task 2 tests: config, README, zenodo metadata, model copy
# ---------------------------------------------------------------------------


class TestWriteDepositConfig:
    """Tests for write_deposit_config()."""

    def test_project_dir_is_dot(self, deposit_dir: Path) -> None:
        pkg.write_deposit_config(deposit_dir)
        data = yaml.safe_load((deposit_dir / "config.yaml").read_text(encoding="utf-8"))
        assert data["project_dir"] == "."

    def test_relative_weights_paths(self, deposit_dir: Path) -> None:
        pkg.write_deposit_config(deposit_dir)
        data = yaml.safe_load((deposit_dir / "config.yaml").read_text(encoding="utf-8"))
        assert data["detection"]["weights_path"] == "models/yolo_obb.pt"
        assert data["pose"]["weights_path"] == "models/yolo_pose.pt"

    def test_n_animals_and_chunk_size(self, deposit_dir: Path) -> None:
        pkg.write_deposit_config(deposit_dir)
        data = yaml.safe_load((deposit_dir / "config.yaml").read_text(encoding="utf-8"))
        assert data["n_animals"] == 9
        assert data["chunk_size"] == 300

    def test_no_absolute_paths(self, deposit_dir: Path) -> None:
        """T-111-01: config must contain no /home/ or D:\\ substrings."""
        pkg.write_deposit_config(deposit_dir)
        raw = (deposit_dir / "config.yaml").read_text(encoding="utf-8")
        assert "/home/" not in raw, "config.yaml must not contain /home/ absolute paths"
        assert "D:\\" not in raw, "config.yaml must not contain D:\\ absolute paths"

    def test_returns_path(self, deposit_dir: Path) -> None:
        result = pkg.write_deposit_config(deposit_dir)
        assert isinstance(result, Path)
        assert result.name == "config.yaml"

    def test_midline_backend(self, deposit_dir: Path) -> None:
        pkg.write_deposit_config(deposit_dir)
        data = yaml.safe_load((deposit_dir / "config.yaml").read_text(encoding="utf-8"))
        assert data["midline"]["backend"] == "pose_estimation"


class TestWriteDepositReadme:
    """Tests for write_deposit_readme()."""

    def test_cc_by_license_present(self, deposit_dir: Path) -> None:
        pkg.write_deposit_readme(deposit_dir)
        content = (deposit_dir / "README.md").read_text(encoding="utf-8")
        assert "CC-BY-4.0" in content

    def test_agpl_derived_label(self, deposit_dir: Path) -> None:
        """D-12: weights must be labeled as AGPL-3.0-derived artifacts."""
        pkg.write_deposit_readme(deposit_dir)
        content = (deposit_dir / "README.md").read_text(encoding="utf-8")
        assert "AGPL-3.0-derived artifacts (trained with Ultralytics, AGPL-3.0)" in content

    def test_no_downscale_note(self, deposit_dir: Path) -> None:
        """Hard constraint note about never spatially downscaling must be present."""
        pkg.write_deposit_readme(deposit_dir)
        content = (deposit_dir / "README.md").read_text(encoding="utf-8")
        assert "never spatially downscale" in content.lower() or "Never spatially downscale" in content

    def test_returns_path(self, deposit_dir: Path) -> None:
        result = pkg.write_deposit_readme(deposit_dir)
        assert isinstance(result, Path)
        assert result.name == "README.md"


class TestWriteZenodoMetadata:
    """Tests for write_zenodo_metadata()."""

    def _load(self, deposit_dir: Path) -> dict:
        pkg.write_zenodo_metadata(deposit_dir)
        return json.loads((deposit_dir / "zenodo-metadata.json").read_text(encoding="utf-8"))

    def test_valid_json(self, deposit_dir: Path) -> None:
        data = self._load(deposit_dir)
        assert isinstance(data, dict)

    def test_license_cc_by(self, deposit_dir: Path) -> None:
        data = self._load(deposit_dir)
        assert data["license"] == "cc-by-4.0"

    def test_upload_type_dataset(self, deposit_dir: Path) -> None:
        data = self._load(deposit_dir)
        assert data["upload_type"] == "dataset"

    def test_access_right_open(self, deposit_dir: Path) -> None:
        data = self._load(deposit_dir)
        assert data["access_right"] == "open"

    def test_title_present(self, deposit_dir: Path) -> None:
        data = self._load(deposit_dir)
        assert "AquaPose" in data["title"]

    def test_keywords_present(self, deposit_dir: Path) -> None:
        data = self._load(deposit_dir)
        assert isinstance(data["keywords"], list)
        assert len(data["keywords"]) > 0


class TestCopyModelsAndCalibration:
    """Tests for copy_models_and_calibration()."""

    def test_copies_obb_model(self, source_dir: Path, deposit_dir: Path) -> None:
        pkg.copy_models_and_calibration(source_dir, deposit_dir)
        assert (deposit_dir / "models" / "yolo_obb.pt").exists()

    def test_copies_pose_model(self, source_dir: Path, deposit_dir: Path) -> None:
        pkg.copy_models_and_calibration(source_dir, deposit_dir)
        assert (deposit_dir / "models" / "yolo_pose.pt").exists()

    def test_copies_calibration(self, source_dir: Path, deposit_dir: Path) -> None:
        pkg.copy_models_and_calibration(source_dir, deposit_dir)
        assert (deposit_dir / "geometry" / "calibration.json").exists()

    def test_raises_on_missing_obb(self, tmp_path: Path, deposit_dir: Path) -> None:
        """FileNotFoundError when OBB model source is absent."""
        staging = tmp_path / "partial_staging"
        staging.mkdir()
        # Only create pose, not OBB
        pose_dir = staging / "training" / "pose" / pkg.POSE_RUN
        pose_dir.mkdir(parents=True)
        (pose_dir / "best_model.pt").write_bytes(b"pose")
        geo = staging / "geometry"
        geo.mkdir()
        (geo / "calibration.json").write_bytes(b"{}")
        with pytest.raises(FileNotFoundError, match=pkg.OBB_RUN):
            pkg.copy_models_and_calibration(staging, deposit_dir)

    def test_canonical_run_ids(self) -> None:
        """D-02: module constants reference run_20260318_* not run_20260310_*."""
        assert "20260318" in pkg.OBB_RUN
        assert "20260318" in pkg.POSE_RUN
        assert "20260310" not in pkg.OBB_RUN
        assert "20260310" not in pkg.POSE_RUN

    def test_obb_content_preserved(self, source_dir: Path, deposit_dir: Path) -> None:
        pkg.copy_models_and_calibration(source_dir, deposit_dir)
        content = (deposit_dir / "models" / "yolo_obb.pt").read_bytes()
        assert content == b"fake-obb"

    def test_pose_content_preserved(self, source_dir: Path, deposit_dir: Path) -> None:
        pkg.copy_models_and_calibration(source_dir, deposit_dir)
        content = (deposit_dir / "models" / "yolo_pose.pt").read_bytes()
        assert content == b"fake-pose"


class TestModuleLevelImports:
    """Verify lazy import discipline (D-09)."""

    def test_no_top_level_yaml_import(self) -> None:
        """yaml must NOT be imported at module top level."""
        import scripts.package_tutorial_dataset as m
        # yaml is not in the module's global namespace unless called
        assert "yaml" not in vars(m), (
            "yaml was imported at module level — must be lazy (inside write_deposit_config)"
        )

    def test_no_top_level_aquapose_import(self) -> None:
        """aquapose must NOT be imported at module top level."""
        import scripts.package_tutorial_dataset as m
        assert "aquapose" not in vars(m), (
            "aquapose was imported at module level — must be lazy"
        )
