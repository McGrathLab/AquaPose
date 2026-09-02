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
        args = parser.parse_args(
            [
                "--source-dir",
                "/staging",
                "--output-dir",
                "/deposit",
                "--start-offset",
                "45.0",
                "--duration",
                "30.0",
                "--crf",
                "22",
                "--regenerate-outputs",
            ]
        )
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
        with (
            patch("shutil.which", return_value=None),
            pytest.raises(RuntimeError, match="ffmpeg"),
        ):
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
        lines = (
            (deposit_dir / "checksums.sha256").read_text(encoding="utf-8").splitlines()
        )
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
        assert (
            "AGPL-3.0-derived artifacts (trained with Ultralytics, AGPL-3.0)" in content
        )

    def test_no_downscale_note(self, deposit_dir: Path) -> None:
        """Hard constraint note about never spatially downscaling must be present."""
        pkg.write_deposit_readme(deposit_dir)
        content = (deposit_dir / "README.md").read_text(encoding="utf-8")
        assert (
            "never spatially downscale" in content.lower()
            or "Never spatially downscale" in content
        )

    def test_returns_path(self, deposit_dir: Path) -> None:
        result = pkg.write_deposit_readme(deposit_dir)
        assert isinstance(result, Path)
        assert result.name == "README.md"


class TestDepositDocCorrections:
    """Regression tests for the D-05/D-06 deposit factual corrections.

    Locks two confirmed factual errors (config header's ``--config`` flag and
    the README's wrong GitHub org) plus two errors discovered empirically
    during Phase 113 Plan 03: the README's ``aquapose viz runs/<run_dir>``
    form (double-nests under ``resolve_run``) and its claim that ``aquapose
    run`` generates ``outputs.h5`` (the real pipeline writes ``midlines.h5``;
    ``outputs.h5`` is only produced by this script's own reference-output
    rename step).
    """

    def test_config_header_has_bare_run_no_config_flag(self, deposit_dir: Path) -> None:
        """D-05.1: header must show a bare `aquapose run`, no --config flag."""
        pkg.write_deposit_config(deposit_dir)
        raw = (deposit_dir / "config.yaml").read_text(encoding="utf-8")
        assert "cd aquapose-tutorial-data" in raw
        assert "aquapose run\n" in raw
        assert "run --config" not in raw

    def test_readme_links_mcgrathlab_not_tucklancaster(self, deposit_dir: Path) -> None:
        """D-05.2: README must link McGrathLab/AquaPose, never tucklancaster."""
        pkg.write_deposit_readme(deposit_dir)
        content = (deposit_dir / "README.md").read_text(encoding="utf-8")
        assert "McGrathLab/AquaPose" in content
        assert "tucklancaster" not in content

    def test_readme_viz_command_does_not_double_nest(self, deposit_dir: Path) -> None:
        """Third defect (confirmed): `aquapose viz runs/<run_dir>` double-nests
        under `resolve_run` (project_dir/runs/runs/<run_dir>). The corrected
        form relies on CWD-based project resolution and defaults to the most
        recent run, matching the rest of the "How to Reproduce" block.
        """
        pkg.write_deposit_readme(deposit_dir)
        content = (deposit_dir / "README.md").read_text(encoding="utf-8")
        assert "aquapose viz\n" in content
        assert "aquapose viz runs/<run_dir>" not in content

    def test_readme_run_step_names_real_output_file(self, deposit_dir: Path) -> None:
        """Fourth defect (confirmed): `aquapose run` writes `midlines.h5`, not
        `outputs.h5` — `outputs.h5` is only produced by this script's own
        `regenerate_reference_outputs` rename step, never by a user's own run.
        """
        pkg.write_deposit_readme(deposit_dir)
        content = (deposit_dir / "README.md").read_text(encoding="utf-8")
        assert "generates midlines.h5" in content
        assert "generates outputs.h5" not in content

    def test_readme_lut_timing_is_not_a_fixed_minute_range(
        self, deposit_dir: Path
    ) -> None:
        """Fifth defect (confirmed by Phase 113 Plan 05's GPU verification run):
        the README claimed LUT generation takes "~2-5 min". Measured 7 s on an
        RTX 4070 Ti — an order of magnitude under the claimed lower bound. The
        claim is corrected to note wall time varies by GPU instead of asserting
        an unverified fixed range.
        """
        pkg.write_deposit_readme(deposit_dir)
        content = (deposit_dir / "README.md").read_text(encoding="utf-8")
        assert "~2-5 min" not in content
        assert "varies by GPU" in content


class TestWriteZenodoMetadata:
    """Tests for write_zenodo_metadata()."""

    def _load(self, deposit_dir: Path) -> dict:
        pkg.write_zenodo_metadata(deposit_dir)
        return json.loads(
            (deposit_dir / "zenodo-metadata.json").read_text(encoding="utf-8")
        )

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


class TestRegenerateReferenceOutputs:
    """Tests for regenerate_reference_outputs() — mocked subprocess, no GPU."""

    def _make_fake_run(self, ref_dir: Path) -> Path:
        """Create a fake run directory with midlines.h5 under ref_dir."""
        run_dir = ref_dir / "run_20260901_120000"
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "midlines.h5").write_bytes(b"fake-midlines")
        return run_dir

    def _fake_subprocess_run(
        self,
        ref_dir: Path,
        calls: list[list[str]],
        cmd: list[str],
        *,
        capture_output: bool = False,
        text: bool = False,
        cwd: str | None = None,
    ) -> object:
        """Fake subprocess.run: records the call and side-effects by call type."""
        calls.append(list(cmd))
        # aquapose run (diagnostic mode): create the fake run dir + midlines.h5
        if any(tok == "run" for tok in cmd) and "--mode" in cmd:
            self._make_fake_run(ref_dir)
        # aquapose viz: create animation + overlay files
        if "--animation" in cmd:
            (ref_dir / "animation_3d.html").write_bytes(b"<html>animation</html>")
            (ref_dir / "overlay_mosaic.mp4").write_bytes(b"fake-mp4")
        # ffmpeg re-encode: create the destination file so replace() works
        if cmd and cmd[0] == "ffmpeg" and "-crf" in cmd:
            dst = Path(cmd[-1])
            dst.write_bytes(b"re-encoded-mp4")

        class _Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Result()

    def _get_pipeline_call(self, calls: list[list[str]]) -> list[str]:
        """Return the aquapose run (diagnostic) call from the recorded calls."""
        for c in calls:
            if "run" in c and "--mode" in c:
                return c
        raise AssertionError(f"No aquapose run call found in: {calls}")

    def _get_viz_call(self, calls: list[list[str]]) -> list[str]:
        """Return the aquapose viz call from the recorded calls."""
        for c in calls:
            if "viz" in c:
                return c
        raise AssertionError(f"No aquapose viz call found in: {calls}")

    def test_pipeline_argv_contains_run_config_mode_diagnostic(
        self, tmp_path: Path
    ) -> None:
        """Pipeline subprocess argv must contain 'run', '--mode', 'diagnostic'."""
        deposit_dir = tmp_path / "deposit"
        deposit_dir.mkdir()
        ref_dir = deposit_dir / "reference_outputs"
        calls: list[list[str]] = []

        with patch(
            "subprocess.run",
            side_effect=lambda cmd, **kw: self._fake_subprocess_run(
                ref_dir, calls, cmd, **kw
            ),
        ):
            pkg.regenerate_reference_outputs(deposit_dir)

        assert calls, "subprocess.run was never called"
        pipeline_call = self._get_pipeline_call(calls)
        assert "run" in pipeline_call, f"'run' not in pipeline argv: {pipeline_call}"
        assert "--mode" in pipeline_call, (
            f"'--mode' not in pipeline argv: {pipeline_call}"
        )
        assert "diagnostic" in pipeline_call, (
            f"'diagnostic' not in pipeline argv: {pipeline_call}"
        )

    def test_pipeline_argv_contains_output_dir_override(self, tmp_path: Path) -> None:
        """Pipeline argv must contain '--set' and an output_dir=...reference_outputs token."""
        deposit_dir = tmp_path / "deposit"
        deposit_dir.mkdir()
        ref_dir = deposit_dir / "reference_outputs"
        calls: list[list[str]] = []

        with patch(
            "subprocess.run",
            side_effect=lambda cmd, **kw: self._fake_subprocess_run(
                ref_dir, calls, cmd, **kw
            ),
        ):
            pkg.regenerate_reference_outputs(deposit_dir)

        pipeline_call = self._get_pipeline_call(calls)
        assert "--set" in pipeline_call, (
            f"'--set' not in pipeline argv: {pipeline_call}"
        )
        joined = " ".join(str(t) for t in pipeline_call)
        assert "reference_outputs" in joined, (
            f"output_dir override not in pipeline argv: {pipeline_call}"
        )

    def test_viz_argv_contains_animation_and_overlay(self, tmp_path: Path) -> None:
        """Viz subprocess argv must contain 'viz', '--animation', '--overlay'."""
        deposit_dir = tmp_path / "deposit"
        deposit_dir.mkdir()
        ref_dir = deposit_dir / "reference_outputs"
        calls: list[list[str]] = []

        with patch(
            "subprocess.run",
            side_effect=lambda cmd, **kw: self._fake_subprocess_run(
                ref_dir, calls, cmd, **kw
            ),
        ):
            pkg.regenerate_reference_outputs(deposit_dir)

        viz_call = self._get_viz_call(calls)
        assert "viz" in viz_call, f"'viz' not in viz argv: {viz_call}"
        assert "--animation" in viz_call, f"'--animation' not in viz argv: {viz_call}"
        assert "--overlay" in viz_call, f"'--overlay' not in viz argv: {viz_call}"

    def test_timing_txt_is_written(self, tmp_path: Path) -> None:
        """timing.txt must be written into reference_outputs/."""
        deposit_dir = tmp_path / "deposit"
        deposit_dir.mkdir()
        ref_dir = deposit_dir / "reference_outputs"
        calls: list[list[str]] = []

        with patch(
            "subprocess.run",
            side_effect=lambda cmd, **kw: self._fake_subprocess_run(
                ref_dir, calls, cmd, **kw
            ),
        ):
            pkg.regenerate_reference_outputs(deposit_dir)

        timing_txt = ref_dir / "timing.txt"
        assert timing_txt.exists(), "timing.txt was not written to reference_outputs/"
        content = timing_txt.read_text(encoding="utf-8")
        assert "pipeline_wall_seconds" in content
        assert "viz_wall_seconds" in content

    def test_outputs_h5_is_copied(self, tmp_path: Path) -> None:
        """outputs.h5 must be copied from the run dir's midlines.h5."""
        deposit_dir = tmp_path / "deposit"
        deposit_dir.mkdir()
        ref_dir = deposit_dir / "reference_outputs"
        calls: list[list[str]] = []

        with patch(
            "subprocess.run",
            side_effect=lambda cmd, **kw: self._fake_subprocess_run(
                ref_dir, calls, cmd, **kw
            ),
        ):
            pkg.regenerate_reference_outputs(deposit_dir)

        outputs_h5 = ref_dir / "outputs.h5"
        assert outputs_h5.exists(), "outputs.h5 was not written to reference_outputs/"
        assert outputs_h5.stat().st_size > 0

    def test_raises_on_subprocess_failure(self, tmp_path: Path) -> None:
        """RuntimeError is raised when any subprocess (including prep-luts) returns non-zero."""
        deposit_dir = tmp_path / "deposit"
        deposit_dir.mkdir()

        class _FailResult:
            returncode = 1
            stdout = ""
            stderr = "CUDA error: device not found"

        with (
            patch("subprocess.run", return_value=_FailResult()),
            pytest.raises(RuntimeError),
        ):
            pkg.regenerate_reference_outputs(deposit_dir)


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


# ---------------------------------------------------------------------------
# Plan 03 Task 1 tests: write_checksums (full), verify_deposit, finalize_deposit,
# regenerate_reference_outputs (prep-luts + overlay re-encode)
# ---------------------------------------------------------------------------


class TestWriteChecksumsComplete:
    """Additional write_checksums tests for Plan 03 (regex format, one-per-file)."""

    def test_line_regex_format(self, deposit_dir: Path) -> None:
        """Every manifest line matches ^[0-9a-f]{64}  .+$."""
        import re

        (deposit_dir / "file1.txt").write_bytes(b"alpha")
        (deposit_dir / "file2.bin").write_bytes(b"beta")
        sub = deposit_dir / "sub"
        sub.mkdir()
        (sub / "file3.dat").write_bytes(b"gamma")
        pkg.write_checksums(deposit_dir)
        lines = (
            (deposit_dir / "checksums.sha256").read_text(encoding="utf-8").splitlines()
        )
        pattern = re.compile(r"^[0-9a-f]{64}  .+$")
        for line in lines:
            assert pattern.match(line), f"Line does not match expected format: {line!r}"

    def test_one_line_per_file(self, deposit_dir: Path) -> None:
        """Manifest has exactly one line per deposit file (excluding itself)."""
        files = ["a.txt", "b.txt", "c.bin"]
        for name in files:
            (deposit_dir / name).write_bytes(b"x")
        pkg.write_checksums(deposit_dir)
        lines = (
            (deposit_dir / "checksums.sha256").read_text(encoding="utf-8").splitlines()
        )
        assert len(lines) == len(files), (
            f"Expected {len(files)} manifest lines, got {len(lines)}"
        )

    def test_subdirectory_files_included(self, deposit_dir: Path) -> None:
        """Files in subdirectories use posix relpaths in the manifest."""
        sub = deposit_dir / "reference_outputs"
        sub.mkdir()
        (sub / "outputs.h5").write_bytes(b"h5data")
        pkg.write_checksums(deposit_dir)
        content = (deposit_dir / "checksums.sha256").read_text(encoding="utf-8")
        assert "reference_outputs/outputs.h5" in content

    def test_sorted_order(self, deposit_dir: Path) -> None:
        """Manifest lines are in sorted order (deterministic output)."""
        for name in ["z.txt", "a.txt", "m.txt"]:
            (deposit_dir / name).write_bytes(b"x")
        pkg.write_checksums(deposit_dir)
        lines = (
            (deposit_dir / "checksums.sha256").read_text(encoding="utf-8").splitlines()
        )
        paths = [line.split("  ", 1)[1] for line in lines]
        assert paths == sorted(paths), "Manifest lines are not in sorted order"

    def test_manifest_uses_lf_newlines(self, deposit_dir: Path) -> None:
        """Manifest must use LF (no CR) so `sha256sum -c` works cross-platform.

        On Windows the default text-mode write would emit CRLF, leaving a trailing
        \\r on each filename and breaking verification everywhere.
        """
        (deposit_dir / "a.txt").write_bytes(b"x")
        (deposit_dir / "b.txt").write_bytes(b"y")
        pkg.write_checksums(deposit_dir)
        raw = (deposit_dir / "checksums.sha256").read_bytes()
        assert b"\r" not in raw, (
            "checksums.sha256 contains CR bytes (should be LF-only)"
        )


def _make_complete_deposit(tmp_path: Path) -> Path:
    """Create a minimal but complete fake deposit tree for verify_deposit tests."""
    d = tmp_path / "deposit"
    d.mkdir()

    # videos/ with 12 fake mp4s
    videos = d / "videos"
    videos.mkdir()
    for i in range(12):
        (videos / f"cam{i:02d}.mp4").write_bytes(b"fake-video")

    # geometry/calibration.json (no luts/)
    geo = d / "geometry"
    geo.mkdir()
    (geo / "calibration.json").write_bytes(b"{}")

    # models
    models = d / "models"
    models.mkdir()
    (models / "yolo_obb.pt").write_bytes(b"fake-obb")
    (models / "yolo_pose.pt").write_bytes(b"fake-pose")

    # config.yaml (relative paths only)
    (d / "config.yaml").write_text(
        "project_dir: .\nvideo_dir: videos\n",
        encoding="utf-8",
    )

    # README.md with required license strings
    (d / "README.md").write_text(
        "# AquaPose YH Tutorial Dataset\n\n"
        "License: CC-BY-4.0\n"
        "AGPL-3.0-derived artifacts (trained with Ultralytics, AGPL-3.0)\n",
        encoding="utf-8",
    )

    # zenodo-metadata.json
    import json as _json

    (d / "zenodo-metadata.json").write_text(
        _json.dumps({"license": "cc-by-4.0", "upload_type": "dataset"}),
        encoding="utf-8",
    )

    # reference_outputs/
    ref = d / "reference_outputs"
    ref.mkdir()
    (ref / "outputs.h5").write_bytes(b"fake-h5")
    (ref / "animation_3d.html").write_bytes(b"<html/>")
    (ref / "overlay_mosaic.mp4").write_bytes(b"fake-mp4")
    (ref / "timing.txt").write_text("pipeline_wall_seconds: 1.0\n", encoding="utf-8")

    return d


class TestVerifyDeposit:
    """Tests for verify_deposit()."""

    def test_empty_on_complete_correct_tree(self, tmp_path: Path) -> None:
        """Returns empty list for a complete, correctly licensed deposit."""
        d = _make_complete_deposit(tmp_path)
        problems = pkg.verify_deposit(d)
        assert problems == [], f"Unexpected problems: {problems}"

    def test_fails_on_missing_reference_output(self, tmp_path: Path) -> None:
        """Returns a problem string when outputs.h5 is missing."""
        d = _make_complete_deposit(tmp_path)
        (d / "reference_outputs" / "outputs.h5").unlink()
        problems = pkg.verify_deposit(d)
        assert any("outputs.h5" in p for p in problems), (
            f"Expected problem about outputs.h5, got: {problems}"
        )

    def test_fails_on_missing_animation(self, tmp_path: Path) -> None:
        """Returns a problem string when animation_3d.html is missing."""
        d = _make_complete_deposit(tmp_path)
        (d / "reference_outputs" / "animation_3d.html").unlink()
        problems = pkg.verify_deposit(d)
        assert any("animation_3d.html" in p for p in problems)

    def test_fails_on_missing_overlay(self, tmp_path: Path) -> None:
        """Returns a problem string when overlay_mosaic.mp4 is missing."""
        d = _make_complete_deposit(tmp_path)
        (d / "reference_outputs" / "overlay_mosaic.mp4").unlink()
        problems = pkg.verify_deposit(d)
        assert any("overlay_mosaic.mp4" in p for p in problems)

    def test_fails_on_absolute_path_home_in_config(self, tmp_path: Path) -> None:
        """Returns a problem when config.yaml has a /home/ path."""
        d = _make_complete_deposit(tmp_path)
        (d / "config.yaml").write_text(
            "project_dir: /home/user/aquapose\n",
            encoding="utf-8",
        )
        problems = pkg.verify_deposit(d)
        assert any("/home/" in p for p in problems), (
            f"Expected problem about /home/, got: {problems}"
        )

    def test_fails_on_absolute_path_windows_in_config(self, tmp_path: Path) -> None:
        """Returns a problem when config.yaml has a D:\\ path."""
        d = _make_complete_deposit(tmp_path)
        (d / "config.yaml").write_text(
            "project_dir: D:\\AquaPose_Zenodo_staging\n",
            encoding="utf-8",
        )
        problems = pkg.verify_deposit(d)
        assert any("D:\\" in p for p in problems), (
            f"Expected problem about D:\\, got: {problems}"
        )

    def test_fails_on_wrong_video_count(self, tmp_path: Path) -> None:
        """Returns a problem when videos/ has fewer than 12 mp4 files."""
        d = _make_complete_deposit(tmp_path)
        # Remove one video
        next(iter(d.glob("videos/*.mp4"))).unlink()
        problems = pkg.verify_deposit(d)
        assert any(
            ("12" in p and "mp4" in p.lower()) or "videos" in p for p in problems
        ), f"Expected problem about video count, got: {problems}"

    def test_fails_when_luts_dir_present(self, tmp_path: Path) -> None:
        """Returns a problem when geometry/luts/ is present (must be excluded, D-03)."""
        d = _make_complete_deposit(tmp_path)
        luts = d / "geometry" / "luts"
        luts.mkdir()
        (luts / "fake_lut.npy").write_bytes(b"lut_data")
        problems = pkg.verify_deposit(d)
        assert any("luts" in p.lower() for p in problems), (
            f"Expected problem about geometry/luts/, got: {problems}"
        )

    def test_fails_when_run_cache_dir_present(self, tmp_path: Path) -> None:
        """Returns a problem when reference_outputs/run_*/ cache dir is present."""
        d = _make_complete_deposit(tmp_path)
        cache = d / "reference_outputs" / "run_20260101_000000"
        cache.mkdir()
        (cache / "cache.pkl").write_bytes(b"pkl_data")
        problems = pkg.verify_deposit(d)
        assert any("run_20260101_000000" in p for p in problems), (
            f"Expected problem about run_* cache dir, got: {problems}"
        )

    def test_fails_on_missing_readme_license(self, tmp_path: Path) -> None:
        """Returns a problem when README.md lacks CC-BY-4.0."""
        d = _make_complete_deposit(tmp_path)
        (d / "README.md").write_text("# AquaPose\nNo license info.\n", encoding="utf-8")
        problems = pkg.verify_deposit(d)
        assert any("CC-BY-4.0" in p for p in problems)

    def test_fails_on_missing_agpl_label(self, tmp_path: Path) -> None:
        """Returns a problem when README.md lacks the AGPL-3.0-derived label."""
        d = _make_complete_deposit(tmp_path)
        (d / "README.md").write_text("# AquaPose\nCC-BY-4.0\n", encoding="utf-8")
        problems = pkg.verify_deposit(d)
        assert any("AGPL-3.0" in p for p in problems)

    def test_fails_on_wrong_zenodo_license(self, tmp_path: Path) -> None:
        """Returns a problem when zenodo-metadata.json has wrong license value."""
        import json as _json

        d = _make_complete_deposit(tmp_path)
        (d / "zenodo-metadata.json").write_text(
            _json.dumps({"license": "mit", "upload_type": "dataset"}),
            encoding="utf-8",
        )
        problems = pkg.verify_deposit(d)
        assert any("license" in p.lower() for p in problems)

    def test_fails_on_invalid_zenodo_json(self, tmp_path: Path) -> None:
        """Returns a problem when zenodo-metadata.json is not valid JSON."""
        d = _make_complete_deposit(tmp_path)
        (d / "zenodo-metadata.json").write_text("{invalid json", encoding="utf-8")
        problems = pkg.verify_deposit(d)
        assert any("not valid JSON" in p or "JSON" in p for p in problems)

    def test_multiple_problems_reported(self, tmp_path: Path) -> None:
        """Multiple issues are all reported, not just the first."""
        d = _make_complete_deposit(tmp_path)
        (d / "reference_outputs" / "outputs.h5").unlink()
        (d / "reference_outputs" / "timing.txt").unlink()
        problems = pkg.verify_deposit(d)
        assert len(problems) >= 2


class TestFinalizeDeposit:
    """Tests for finalize_deposit()."""

    def test_removes_luts_dir(self, deposit_dir: Path) -> None:
        """finalize_deposit removes geometry/luts/ if present."""
        luts = deposit_dir / "geometry" / "luts"
        luts.mkdir(parents=True)
        (luts / "forward.npy").write_bytes(b"lut")
        pkg.finalize_deposit(deposit_dir)
        assert not luts.exists(), "geometry/luts/ was not removed by finalize_deposit"

    def test_removes_run_cache_dirs(self, deposit_dir: Path) -> None:
        """finalize_deposit removes reference_outputs/run_*/ dirs."""
        ref = deposit_dir / "reference_outputs"
        ref.mkdir()
        cache = ref / "run_20260901_120000"
        cache.mkdir()
        (cache / "cache.pkl").write_bytes(b"pkl")
        pkg.finalize_deposit(deposit_dir)
        assert not cache.exists(), (
            "run_*/ cache dir was not removed by finalize_deposit"
        )

    def test_leaves_canonical_artifacts(self, deposit_dir: Path) -> None:
        """finalize_deposit does not remove canonical reference output files."""
        ref = deposit_dir / "reference_outputs"
        ref.mkdir()
        outputs_h5 = ref / "outputs.h5"
        outputs_h5.write_bytes(b"h5data")
        animation = ref / "animation_3d.html"
        animation.write_bytes(b"<html/>")
        overlay = ref / "overlay_mosaic.mp4"
        overlay.write_bytes(b"mp4data")
        pkg.finalize_deposit(deposit_dir)
        assert outputs_h5.exists(), "outputs.h5 was incorrectly removed"
        assert animation.exists(), "animation_3d.html was incorrectly removed"
        assert overlay.exists(), "overlay_mosaic.mp4 was incorrectly removed"

    def test_noop_when_nothing_to_remove(self, deposit_dir: Path) -> None:
        """finalize_deposit does not raise when there is nothing to remove."""
        pkg.finalize_deposit(deposit_dir)  # should not raise

    def test_removes_multiple_run_dirs(self, deposit_dir: Path) -> None:
        """finalize_deposit removes all run_*/ dirs, not just the first."""
        ref = deposit_dir / "reference_outputs"
        ref.mkdir()
        cache1 = ref / "run_20260901_100000"
        cache1.mkdir()
        cache2 = ref / "run_20260901_120000"
        cache2.mkdir()
        pkg.finalize_deposit(deposit_dir)
        assert not cache1.exists()
        assert not cache2.exists()


class TestRegenerateReferenceOutputsPlan03:
    """Plan 03 additions to regenerate_reference_outputs tests (prep-luts + re-encode)."""

    def _make_fake_run(self, ref_dir: Path) -> Path:
        """Create a fake run directory with midlines.h5 under ref_dir."""
        run_dir = ref_dir / "run_20260901_120000"
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "midlines.h5").write_bytes(b"fake-midlines")
        return run_dir

    def _fake_subprocess_run(
        self,
        ref_dir: Path,
        calls: list[list[str]],
        cmd: list[str],
        *,
        capture_output: bool = False,
        text: bool = False,
        cwd: str | None = None,
    ) -> object:
        """Record calls; side-effect: create fake run dir and artifact files."""
        calls.append(list(cmd))
        if any(tok == "run" for tok in cmd) and "--mode" in cmd:
            self._make_fake_run(ref_dir)
        if "--animation" in cmd:
            (ref_dir / "animation_3d.html").write_bytes(b"<html/>")
            (ref_dir / "overlay_mosaic.mp4").write_bytes(b"fake-mp4")
        # ffmpeg re-encode: create the tmp output so replace() works
        if "ffmpeg" in cmd and "-crf" in cmd:
            # argv: [..., -crf, 28, ..., <dst>]
            dst = Path(cmd[-1])
            dst.write_bytes(b"re-encoded-mp4")

        class _Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Result()

    def test_prep_generate_luts_called_before_run(self, tmp_path: Path) -> None:
        """argv sequence: prep+generate-luts BEFORE the run call."""
        deposit_dir = tmp_path / "deposit"
        deposit_dir.mkdir()
        ref_dir = deposit_dir / "reference_outputs"
        calls: list[list[str]] = []

        with patch(
            "subprocess.run",
            side_effect=lambda cmd, **kw: self._fake_subprocess_run(
                ref_dir, calls, cmd, **kw
            ),
        ):
            pkg.regenerate_reference_outputs(deposit_dir)

        # Find indices
        luts_idx = next(
            (i for i, c in enumerate(calls) if "prep" in c and "generate-luts" in c),
            None,
        )
        run_idx = next(
            (i for i, c in enumerate(calls) if "run" in c and "--mode" in c),
            None,
        )
        assert luts_idx is not None, f"No prep generate-luts call found in: {calls}"
        assert run_idx is not None, f"No aquapose run call found in: {calls}"
        assert luts_idx < run_idx, (
            f"prep generate-luts (call {luts_idx}) must come before run (call {run_idx})"
        )

    def test_overlay_reencode_argv_contains_crf_28(self, tmp_path: Path) -> None:
        """The overlay re-encode ffmpeg argv contains -crf and 28."""
        deposit_dir = tmp_path / "deposit"
        deposit_dir.mkdir()
        ref_dir = deposit_dir / "reference_outputs"
        calls: list[list[str]] = []

        with (
            patch(
                "subprocess.run",
                side_effect=lambda cmd, **kw: self._fake_subprocess_run(
                    ref_dir, calls, cmd, **kw
                ),
            ),
            patch("shutil.which", return_value="/usr/bin/ffmpeg"),
        ):
            pkg.regenerate_reference_outputs(deposit_dir)

        ffmpeg_calls = [c for c in calls if c and c[0] == "ffmpeg"]
        assert ffmpeg_calls, f"No ffmpeg call found in: {calls}"
        reencode_calls = [c for c in ffmpeg_calls if "-crf" in c and "28" in c]
        assert reencode_calls, (
            f"No ffmpeg call with -crf 28 found. ffmpeg calls: {ffmpeg_calls}"
        )

    def test_all_three_phases_called_in_order(self, tmp_path: Path) -> None:
        """Call order: prep generate-luts, aquapose run, aquapose viz."""
        deposit_dir = tmp_path / "deposit"
        deposit_dir.mkdir()
        ref_dir = deposit_dir / "reference_outputs"
        calls: list[list[str]] = []

        with patch(
            "subprocess.run",
            side_effect=lambda cmd, **kw: self._fake_subprocess_run(
                ref_dir, calls, cmd, **kw
            ),
        ):
            pkg.regenerate_reference_outputs(deposit_dir)

        non_ffmpeg = [c for c in calls if not (c and c[0] == "ffmpeg")]
        luts_idx = next(
            (
                i
                for i, c in enumerate(non_ffmpeg)
                if "prep" in c and "generate-luts" in c
            ),
            None,
        )
        run_idx = next(
            (i for i, c in enumerate(non_ffmpeg) if "run" in c and "--mode" in c),
            None,
        )
        viz_idx = next(
            (i for i, c in enumerate(non_ffmpeg) if "viz" in c),
            None,
        )
        assert luts_idx is not None, "prep generate-luts call not found"
        assert run_idx is not None, "aquapose run call not found"
        assert viz_idx is not None, "aquapose viz call not found"
        assert luts_idx < run_idx < viz_idx, (
            f"Expected luts({luts_idx}) < run({run_idx}) < viz({viz_idx})"
        )
