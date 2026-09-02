"""Tests for calibrate-keypoints CLI and PoseEstimationBackend fail-fast."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from PIL import Image

from aquapose.cli import cli


@pytest.fixture
def coco_annotations(tmp_path: Path) -> Path:
    """Create a minimal COCO annotations file with 2 annotations."""
    data = {
        "annotations": [
            {
                "id": 1,
                "keypoints": [
                    10.0,
                    20.0,
                    2,  # kp0 visible
                    30.0,
                    20.0,
                    2,  # kp1 visible
                    50.0,
                    20.0,
                    2,  # kp2 visible
                    70.0,
                    20.0,
                    2,  # kp3 visible
                    90.0,
                    20.0,
                    2,  # kp4 visible
                    110.0,
                    20.0,
                    2,  # kp5 visible
                ],
            },
            {
                "id": 2,
                "keypoints": [
                    10.0,
                    40.0,
                    2,
                    30.0,
                    40.0,
                    2,
                    50.0,
                    40.0,
                    2,
                    70.0,
                    40.0,
                    2,
                    90.0,
                    40.0,
                    2,
                    110.0,
                    40.0,
                    2,
                ],
            },
        ]
    }
    path = tmp_path / "annotations.json"
    path.write_text(json.dumps(data))
    return path


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a minimal project directory with config.yaml."""
    proj = tmp_path / "test_project"
    proj.mkdir()
    config_data = {
        "project_dir": str(proj),
        "n_animals": 1,
        "video_dir": "videos",
        "calibration_path": "geometry/calibration.json",
        "detection": {"detector_kind": "yolo_obb"},
        "midline": {"backend": "pose_estimation"},
    }
    (proj / "config.yaml").write_text(
        yaml.dump(config_data, default_flow_style=False, sort_keys=False)
    )
    return proj


@pytest.fixture
def monkeypatch_project(monkeypatch: pytest.MonkeyPatch, project_dir: Path) -> Path:
    """Patch resolve_project so --project test resolves to project_dir."""
    monkeypatch.setattr(
        "aquapose.cli_utils.resolve_project",
        lambda name: project_dir,
    )
    return project_dir


class TestCalibrateKeypointsConfig:
    """Test calibrate-keypoints --config flag and YAML in-place update."""

    def test_updates_config_yaml_in_place(
        self,
        coco_annotations: Path,
        monkeypatch_project: Path,
    ) -> None:
        """calibrate-keypoints writes keypoint_t_values into pose: in YAML."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(coco_annotations),
            ],
        )
        assert result.exit_code == 0, result.output

        # Verify YAML was updated
        config_yaml = monkeypatch_project / "config.yaml"
        updated = yaml.safe_load(config_yaml.read_text())
        assert "pose" in updated
        assert "keypoint_t_values" in updated["pose"]
        t_values = updated["pose"]["keypoint_t_values"]
        assert len(t_values) == 6
        # First should be 0.0, last should be 1.0
        assert t_values[0] == pytest.approx(0.0, abs=0.01)
        assert t_values[-1] == pytest.approx(1.0, abs=0.01)

        # Other fields should be preserved
        assert updated["detection"]["detector_kind"] == "yolo_obb"
        assert updated["midline"]["backend"] == "pose_estimation"

    def test_creates_pose_section_if_missing(
        self,
        coco_annotations: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """calibrate-keypoints creates pose section if config lacks it."""
        proj = tmp_path / "minimal_project"
        proj.mkdir()
        (proj / "config.yaml").write_text(
            yaml.dump(
                {"project_dir": str(proj), "video_dir": "videos"},
                default_flow_style=False,
            )
        )
        monkeypatch.setattr(
            "aquapose.cli_utils.resolve_project",
            lambda name: proj,
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(coco_annotations),
            ],
        )
        assert result.exit_code == 0, result.output

        updated = yaml.safe_load((proj / "config.yaml").read_text())
        assert "pose" in updated
        assert "keypoint_t_values" in updated["pose"]

    def test_null_pose_section_is_treated_as_missing(
        self,
        coco_annotations: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A `pose:` key present but with no mapping (YAML null) is handled.

        `yaml.safe_load("pose:\\n")` parses to ``{"pose": None}`` -- the key
        is present but its value is not a dict. This is what a config
        scaffolded from a template with a bare `pose:` placeholder left in
        place (or hand-edited to comment out the block's contents) produces.
        The writer must treat this the same as a missing `pose:` key rather
        than crashing with `TypeError: 'NoneType' object does not support
        item assignment` when it tries `config_data["pose"][...] = ...`.
        """
        proj = tmp_path / "null_pose_project"
        proj.mkdir()
        (proj / "config.yaml").write_text(
            yaml.dump(
                {"project_dir": str(proj), "video_dir": "videos", "pose": None},
                default_flow_style=False,
            )
        )
        monkeypatch.setattr(
            "aquapose.cli_utils.resolve_project",
            lambda name: proj,
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(coco_annotations),
            ],
        )
        assert result.exit_code == 0, result.output

        updated = yaml.safe_load((proj / "config.yaml").read_text())
        assert "pose" in updated
        assert "keypoint_t_values" in updated["pose"]

    def test_removes_stale_legacy_midline_keypoint_t_values(
        self,
        coco_annotations: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A stale midline.keypoint_t_values is removed with a stdout notice.

        midline.backend must survive the round trip -- only the one legacy
        key is removed, not the whole midline section.
        """
        proj = tmp_path / "legacy_project"
        proj.mkdir()
        config_data = {
            "project_dir": str(proj),
            "midline": {
                "backend": "pose_estimation",
                "keypoint_t_values": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
            },
        }
        config_path = proj / "config.yaml"
        config_path.write_text(
            yaml.dump(config_data, default_flow_style=False, sort_keys=False)
        )
        monkeypatch.setattr(
            "aquapose.cli_utils.resolve_project",
            lambda name: proj,
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(coco_annotations),
            ],
        )
        assert result.exit_code == 0, result.output
        assert (
            f"Removed legacy midline.keypoint_t_values from {config_path} "
            "(superseded by pose.keypoint_t_values)." in result.output
        )

        updated = yaml.safe_load(config_path.read_text())
        assert "keypoint_t_values" not in updated["midline"]
        assert updated["midline"]["backend"] == "pose_estimation"
        assert "keypoint_t_values" in updated["pose"]

    def test_writes_to_pose_key_and_overrides_existing_pose_value(
        self,
        coco_annotations: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """COCO-path twin of the YOLO-path terminal gate (format-independent).

        Proves the writer fix through load_config on the COCO path, the
        same way the YOLO path is proven in
        test_pixel_space_t_values_reach_load_config_through_pose_key.
        """
        from aquapose.engine.config import load_config

        proj = tmp_path / "override_project"
        proj.mkdir()
        config_data = {
            "project_dir": str(proj),
            "n_animals": 1,
            "pose": {"keypoint_t_values": [0.05, 0.1, 0.3, 0.5, 0.7, 0.9]},
        }
        config_path = proj / "config.yaml"
        config_path.write_text(
            yaml.dump(config_data, default_flow_style=False, sort_keys=False)
        )
        monkeypatch.setattr(
            "aquapose.cli_utils.resolve_project",
            lambda name: proj,
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(coco_annotations),
            ],
        )
        assert result.exit_code == 0, result.output

        loaded = load_config(config_path)
        t_values = loaded.pose.keypoint_t_values
        assert t_values is not None
        assert t_values[0] == pytest.approx(0.0, abs=0.01)
        assert t_values[-1] == pytest.approx(1.0, abs=0.01)
        assert t_values != pytest.approx([0.05, 0.1, 0.3, 0.5, 0.7, 0.9])


class TestCalibrateKeypointsYolo:
    """Test calibrate-keypoints with YOLO-format label directories."""

    @pytest.fixture
    def yolo_labels_dir(self, tmp_path: Path) -> Path:
        """Create a YOLO label directory with train/ and val/ subdirs.

        Every label file gets a matching 128x64 image under the mirrored
        images/ tree the resolution rule expects (_resolve_sibling_image).
        """
        # Evenly spaced keypoints along x-axis (normalized coords)
        # class cx cy w h x1 y1 v1 x2 y2 v2 ... (6 keypoints)
        kps = " ".join(f"{x:.4f} 0.5 2" for x in [0.1, 0.28, 0.46, 0.64, 0.82, 1.0])
        line = f"0 0.5 0.5 0.8 0.3 {kps}"

        train_labels_dir = tmp_path / "labels" / "train"
        train_labels_dir.mkdir(parents=True)
        (train_labels_dir / "img001.txt").write_text(line + "\n")
        (train_labels_dir / "img002.txt").write_text(line + "\n")

        val_labels_dir = tmp_path / "labels" / "val"
        val_labels_dir.mkdir(parents=True)
        (val_labels_dir / "img003.txt").write_text(line + "\n")

        train_images_dir = tmp_path / "images" / "train"
        train_images_dir.mkdir(parents=True)
        Image.new("RGB", (128, 64)).save(train_images_dir / "img001.jpg")
        Image.new("RGB", (128, 64)).save(train_images_dir / "img002.jpg")

        val_images_dir = tmp_path / "images" / "val"
        val_images_dir.mkdir(parents=True)
        Image.new("RGB", (128, 64)).save(val_images_dir / "img003.jpg")

        return tmp_path / "labels"

    def test_yolo_labels_detected_and_parsed(
        self,
        yolo_labels_dir: Path,
        monkeypatch_project: Path,
    ) -> None:
        """Directory input auto-detects YOLO format and computes t-values."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(yolo_labels_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "YOLO" in result.output

        config_yaml = monkeypatch_project / "config.yaml"
        updated = yaml.safe_load(config_yaml.read_text())
        t_values = updated["pose"]["keypoint_t_values"]
        assert len(t_values) == 6
        assert t_values[0] == pytest.approx(0.0, abs=0.01)
        assert t_values[-1] == pytest.approx(1.0, abs=0.01)

    def test_yolo_processes_all_subdirs(
        self,
        yolo_labels_dir: Path,
        monkeypatch_project: Path,
    ) -> None:
        """YOLO mode recurses into train/ and val/ subdirectories."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(yolo_labels_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Processed 3 annotations" in result.output

    def test_pixel_space_t_values_reach_load_config_through_pose_key(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Both terminal gates in one path, proven through load_config.

        Keypoints trace a zigzag path (alternating pure-x and pure-y 20px
        segments) on a non-square 128x64 canvas, evenly spaced IN PIXELS.
        On a 2:1 aspect-ratio image this path is NOT evenly spaced in raw
        normalized coordinates (x-segments measure 0.15625 raw, y-segments
        measure 0.3125 raw -- a 2x difference), so a purely horizontal or
        purely vertical fixture would be invariant to the arc-length bug;
        this zigzag (varies on both axes) is not. The assertion reads back
        through load_config(...).pose.keypoint_t_values, not the raw YAML,
        which is the only way to prove the writer targets the canonical
        `pose:` key (a config that already carries a *different*
        pose.keypoint_t_values is used, so a no-op writer would be caught
        too).
        """
        from aquapose.engine.config import load_config

        img_w, img_h = 128, 64

        # Pixel-space keypoints, each consecutive pair exactly 20px apart:
        # (0,0) -> (20,0) -> (20,20) -> (40,20) -> (40,40) -> (60,40)
        px_points = [(0, 0), (20, 0), (20, 20), (40, 20), (40, 40), (60, 40)]
        norm_points = [(x / img_w, y / img_h) for x, y in px_points]

        kps = " ".join(f"{x:.6f} {y:.6f} 2" for x, y in norm_points)
        line = f"0 0.5 0.5 0.5 0.5 {kps}"

        labels_dir = tmp_path / "labels" / "train"
        labels_dir.mkdir(parents=True)
        (labels_dir / "img001.txt").write_text(line + "\n", encoding="utf-8")

        images_dir = tmp_path / "images" / "train"
        images_dir.mkdir(parents=True)
        Image.new("RGB", (img_w, img_h)).save(images_dir / "img001.jpg")

        proj = tmp_path / "gate_project"
        proj.mkdir()
        # This config ALREADY carries a pose.keypoint_t_values that is
        # deliberately wrong -- the writer must overwrite it, proving the
        # legacy-key gate (D-06) and the arc-length gate (D-08) together.
        config_data = {
            "project_dir": str(proj),
            "n_animals": 1,
            "pose": {"keypoint_t_values": [0.05, 0.1, 0.3, 0.5, 0.7, 0.9]},
        }
        (proj / "config.yaml").write_text(
            yaml.dump(config_data, default_flow_style=False, sort_keys=False)
        )
        monkeypatch.setattr(
            "aquapose.cli_utils.resolve_project",
            lambda name: proj,
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(tmp_path / "labels"),
            ],
        )
        assert result.exit_code == 0, result.output

        loaded = load_config(proj / "config.yaml")
        t_values = loaded.pose.keypoint_t_values
        assert t_values is not None
        assert t_values == pytest.approx([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], abs=1e-3)

    def test_label_without_sibling_image_is_skipped_with_warning(
        self,
        tmp_path: Path,
        monkeypatch_project: Path,
    ) -> None:
        """A label with no resolvable sibling image is skipped, not fatal.

        Three labels are written, only two get a sibling image. The
        command must still succeed, processing the two resolvable labels.
        """
        kps = " ".join(f"{x:.4f} 0.5 2" for x in [0.1, 0.28, 0.46, 0.64, 0.82, 1.0])
        line = f"0 0.5 0.5 0.8 0.3 {kps}"

        labels_dir = tmp_path / "labels" / "train"
        labels_dir.mkdir(parents=True)
        for stem in ("img001", "img002", "img003"):
            (labels_dir / f"{stem}.txt").write_text(line + "\n")

        images_dir = tmp_path / "images" / "train"
        images_dir.mkdir(parents=True)
        # img003 deliberately has no sibling image.
        Image.new("RGB", (128, 64)).save(images_dir / "img001.jpg")
        Image.new("RGB", (128, 64)).save(images_dir / "img002.jpg")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(tmp_path / "labels"),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Processed 2 annotations" in result.output

    def test_fails_when_no_label_resolves_an_image(
        self,
        tmp_path: Path,
        monkeypatch_project: Path,
    ) -> None:
        """When labels exist but none resolves an image, the command fails.

        The failure message must be the unresolved-sibling message, not
        the pre-existing no-valid-annotations message -- the two failure
        modes must stay distinguishable so a missing images/ directory is
        never reported as an annotation-quality problem.
        """
        kps = " ".join(f"{x:.4f} 0.5 2" for x in [0.1, 0.28, 0.46, 0.64, 0.82, 1.0])
        line = f"0 0.5 0.5 0.8 0.3 {kps}"

        labels_dir = tmp_path / "labels" / "train"
        labels_dir.mkdir(parents=True)
        (labels_dir / "img001.txt").write_text(line + "\n")
        # No images/ directory at all -- nothing can resolve.

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(tmp_path / "labels"),
            ],
        )
        assert result.exit_code != 0
        assert "No images resolved for any label file" in result.output
        assert "No valid keypoint annotations" not in result.output

    def test_coincident_keypoints_share_t_value(
        self,
        tmp_path: Path,
        monkeypatch_project: Path,
    ) -> None:
        """Two coincident keypoints inside an instance get equal t-values.

        Pixel path: (0,0) -> (20,0) -> (40,0) -> (40,0) -> (60,0) -> (80,0).
        Keypoints 2 and 3 sit at the identical pixel (40,0), a 0px segment.
        Segment lengths: 20, 20, 0, 20, 20 (total 80).
        Cumulative:      0, 20, 40, 40, 60, 80.
        t = cumulative / 80 = [0.0, 0.25, 0.5, 0.5, 0.75, 1.0].
        """
        img_w, img_h = 128, 64
        px_points = [(0, 0), (20, 0), (40, 0), (40, 0), (60, 0), (80, 0)]
        norm_points = [(x / img_w, y / img_h) for x, y in px_points]
        kps = " ".join(f"{x:.6f} {y:.6f} 2" for x, y in norm_points)
        line = f"0 0.5 0.5 0.5 0.5 {kps}"

        labels_dir = tmp_path / "labels" / "train"
        labels_dir.mkdir(parents=True)
        (labels_dir / "img001.txt").write_text(line + "\n", encoding="utf-8")

        images_dir = tmp_path / "images" / "train"
        images_dir.mkdir(parents=True)
        Image.new("RGB", (img_w, img_h)).save(images_dir / "img001.jpg")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(tmp_path / "labels"),
            ],
        )
        assert result.exit_code == 0, result.output

        config_yaml = monkeypatch_project / "config.yaml"
        updated = yaml.safe_load(config_yaml.read_text())
        t_values = updated["pose"]["keypoint_t_values"]
        assert not any(v != v for v in t_values)  # no NaN (v != v is NaN test)
        assert t_values[2] == pytest.approx(0.5, abs=1e-3)
        assert t_values[3] == pytest.approx(0.5, abs=1e-3)
        assert t_values[2] == pytest.approx(t_values[3], abs=1e-9)

    def test_degenerate_all_coincident_instance_is_excluded(
        self,
        tmp_path: Path,
        monkeypatch_project: Path,
    ) -> None:
        """An all-coincident instance is excluded from the mean, not NaN'd.

        Two labels: one normal instance, one where all six keypoints sit
        at the same pixel (total chord length below 1e-6). Only the
        non-degenerate instance is counted.
        """
        img_w, img_h = 128, 64

        normal_kps = " ".join(
            f"{x:.4f} 0.5 2" for x in [0.1, 0.28, 0.46, 0.64, 0.82, 1.0]
        )
        normal_line = f"0 0.5 0.5 0.8 0.3 {normal_kps}"

        degenerate_px = (10, 10)
        degenerate_norm = (degenerate_px[0] / img_w, degenerate_px[1] / img_h)
        degenerate_kps = " ".join(
            f"{degenerate_norm[0]:.6f} {degenerate_norm[1]:.6f} 2" for _ in range(6)
        )
        degenerate_line = f"0 0.5 0.5 0.5 0.5 {degenerate_kps}"

        labels_dir = tmp_path / "labels" / "train"
        labels_dir.mkdir(parents=True)
        (labels_dir / "img001.txt").write_text(normal_line + "\n", encoding="utf-8")
        (labels_dir / "img002.txt").write_text(degenerate_line + "\n", encoding="utf-8")

        images_dir = tmp_path / "images" / "train"
        images_dir.mkdir(parents=True)
        Image.new("RGB", (img_w, img_h)).save(images_dir / "img001.jpg")
        Image.new("RGB", (img_w, img_h)).save(images_dir / "img002.jpg")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(tmp_path / "labels"),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Processed 1 annotations" in result.output

    def test_repeat_runs_are_deterministic(
        self,
        yolo_labels_dir: Path,
        monkeypatch_project: Path,
    ) -> None:
        """Running the command twice over the same corpus is byte-identical.

        Traversal is a sorted rglob(...) and the per-keypoint mean does
        not depend on instance order, so repeat runs over the same corpus
        must produce identical t-values -- compared here for exact
        equality, not approximate.
        """
        from aquapose.engine.config import load_config

        config_path = monkeypatch_project / "config.yaml"
        runner = CliRunner()

        result1 = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(yolo_labels_dir),
            ],
        )
        assert result1.exit_code == 0, result1.output
        t_values_1 = load_config(config_path).pose.keypoint_t_values

        result2 = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(yolo_labels_dir),
            ],
        )
        assert result2.exit_code == 0, result2.output
        t_values_2 = load_config(config_path).pose.keypoint_t_values

        assert t_values_1 == t_values_2

    def test_yolo_empty_dir_fails(
        self,
        tmp_path: Path,
        monkeypatch_project: Path,
    ) -> None:
        """YOLO mode with empty directory reports error."""
        empty_dir = tmp_path / "empty_labels"
        empty_dir.mkdir()
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project",
                "test",
                "prep",
                "calibrate-keypoints",
                "--annotations",
                str(empty_dir),
            ],
        )
        assert result.exit_code != 0
        assert "No valid keypoint annotations" in result.output


class TestPoseEstimationBackendFailFast:
    """Test PoseEstimationBackend raises when keypoint_t_values is None."""

    def test_raises_when_keypoint_t_values_is_none(self) -> None:
        """PoseEstimationBackend accepts None keypoint_t_values (v3.7 — t_values unused)."""
        from aquapose.core.pose.backends.pose_estimation import (
            PoseEstimationBackend,
        )

        # In v3.7, keypoint_t_values is accepted but not validated (no midline upsampling)
        backend = PoseEstimationBackend(
            weights_path=None,
            keypoint_t_values=None,
        )
        assert backend is not None

    def test_accepts_explicit_keypoint_t_values(self) -> None:
        """PoseEstimationBackend accepts explicit keypoint_t_values without raising."""
        from aquapose.core.pose.backends.pose_estimation import (
            PoseEstimationBackend,
        )

        # Should not raise
        backend = PoseEstimationBackend(
            weights_path=None,
            keypoint_t_values=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        )
        assert backend is not None
