from pathlib import Path

import pytest

from trafficpilot.detection.pipeline import DetectionRunConfig, run_detection


def test_detection_missing_model_fails_before_inference(tmp_path: Path):
    input_path = tmp_path / "lane0.mp4"
    input_path.write_text("placeholder")
    config = DetectionRunConfig(
        model_path=str(tmp_path / "missing.pt"),
        input_paths=[str(input_path)],
        output_dir=str(tmp_path / "out"),
    )
    with pytest.raises(FileNotFoundError, match="YOLO model not found"):
        run_detection(config)


def test_detection_invalid_input_extension(tmp_path: Path):
    input_path = tmp_path / "lane0.txt"
    input_path.write_text("placeholder")
    config = DetectionRunConfig(
        model_path=str(tmp_path / "missing.pt"),
        input_paths=[str(input_path)],
        output_dir=str(tmp_path / "out"),
    )
    with pytest.raises(ValueError, match="Unsupported input extension"):
        run_detection(config)
