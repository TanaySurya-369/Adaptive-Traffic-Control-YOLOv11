from pathlib import Path

import pytest

from trafficpilot.config import load_config
from trafficpilot.control import AdaptiveController, FixedTimeController
from trafficpilot.detection import Detection
from trafficpilot.metrics import calculate_improvement, co2_emissions, fuel_used
from trafficpilot.simulation import SimulationParameters, simulate_controller
from trafficpilot.traffic.counting import (
    assign_detection_to_lane,
    count_unique_detections,
    validate_lane_inputs,
)
from trafficpilot.traffic.density import calculate_density
from trafficpilot.traffic.roi import LaneROI, load_rois
from trafficpilot.traffic.scenarios import classify_scenario, generate_scenario_counts


def test_density_calculation():
    assert calculate_density(25, 100) == 0.25
    with pytest.raises(ValueError):
        calculate_density(1, 0)


def test_scenario_classification():
    assert classify_scenario([5, 5, 5, 5]) == "off-peak"
    assert classify_scenario([20, 20, 20, 20]) == "mixed"
    assert classify_scenario([30, 30, 30, 20]) == "peak"


def test_adaptive_green_time_and_priority():
    controller = AdaptiveController(min_green=10, extra_green_per_vehicle=2, max_green=20)
    assert controller.green_time(3) == 16
    assert controller.green_time(10) == 20
    assert controller.prioritize_lanes([3, 10, 2, 8]) == [1, 3, 0, 2]


def test_fixed_time_controller():
    controller = FixedTimeController(green_duration=30)
    assert controller.green_time(99) == 30
    assert controller.next_lane(3, 4) == 0


def test_improvement_fuel_and_co2():
    assert calculate_improvement(75, 100) == 25
    assert calculate_improvement(120, 100, higher_is_better=True) == 20
    assert fuel_used(10, 5, 0.1, 0.2) == 2.0
    assert co2_emissions(2, 2.3) == 4.6


def test_config_loading():
    config = load_config("configs/default.yaml")
    assert config.traffic.lane_count == 4
    assert config.model.path == "models/yolo11x.pt"


def test_roi_loading():
    rois = load_rois("configs/rois/example.json", expected_lanes=4)
    assert len(rois) == 4
    assert len(rois[0].polygon) == 4


def test_lane_input_validation(tmp_path: Path):
    files = []
    for idx in range(4):
        file = tmp_path / f"lane{idx}.mp4"
        file.write_text("placeholder")
        files.append(str(file))
    assert len(validate_lane_inputs(files)) == 4
    with pytest.raises(FileNotFoundError):
        validate_lane_inputs([str(tmp_path / "missing.mp4")])


def test_deterministic_scenario_generation():
    assert generate_scenario_counts("mixed", seed=42) == generate_scenario_counts("mixed", seed=42)


def test_simulation_metrics_are_generated():
    adaptive = AdaptiveController()
    metrics = simulate_controller([5, 4, 3, 2], adaptive, SimulationParameters(duration_seconds=30))
    assert metrics.throughput >= 0
    assert metrics.fuel_consumption >= 0
    assert metrics.co2_emissions >= 0


def test_roi_lane_assignment_and_unique_counting():
    rois = [
        LaneROI(0, [(0, 0), (100, 0), (100, 100), (0, 100)]),
        LaneROI(1, [(101, 0), (200, 0), (200, 100), (101, 100)]),
    ]
    car_a = Detection((10, 10, 30, 30), class_id=2, class_name="car", confidence=0.9, track_id=7)
    car_a_repeat = Detection(
        (15, 10, 35, 30), class_id=2, class_name="car", confidence=0.88, track_id=7
    )
    bus_b = Detection((120, 10, 150, 40), class_id=5, class_name="bus", confidence=0.8, track_id=8)
    person = Detection(
        (20, 20, 30, 40), class_id=0, class_name="person", confidence=0.9, track_id=9
    )

    assert assign_detection_to_lane(car_a, rois) == 0
    assert assign_detection_to_lane(bus_b, rois) == 1
    counts = count_unique_detections([[car_a, bus_b], [car_a_repeat, person]], rois, {2, 3, 5, 7})
    assert counts == {0: 1, 1: 1}


def test_untracked_detections_are_counted_per_frame():
    rois = [LaneROI(0, [(0, 0), (100, 0), (100, 100), (0, 100)])]
    detection = Detection(
        (10, 10, 30, 30), class_id=2, class_name="car", confidence=0.9, track_id=None
    )
    counts = count_unique_detections([[detection], [detection]], rois, {2})
    assert counts == {0: 2}


def test_invalid_config_is_rejected(tmp_path: Path):
    config_file = tmp_path / "bad.yaml"
    config_file.write_text("simulation:\n  duration_seconds: 0\n")
    with pytest.raises(ValueError, match="simulation.duration_seconds"):
        load_config(config_file)
