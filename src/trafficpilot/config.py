from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ModelConfig:
    path: str = "models/yolo11x.pt"
    confidence: float = 0.5
    iou: float = 0.5
    image_size: int = 640
    device: str | None = None
    tracker: str = "bytetrack.yaml"


@dataclass(frozen=True)
class TrafficConfig:
    lane_count: int = 4
    vehicle_classes: tuple[int, ...] = (2, 3, 5, 7)
    density_road_length: float = 100.0


@dataclass(frozen=True)
class ControllerConfig:
    min_green: float = 10.0
    extra_green_per_vehicle: float = 1.0
    max_green: float = 50.0
    yellow_duration: float = 3.0
    fixed_green_duration: float = 30.0


@dataclass(frozen=True)
class SimulationConfig:
    duration_seconds: float = 120.0
    time_step_seconds: float = 1.0
    fps: int = 60
    speed: float = 30.0
    seed: int = 42
    off_peak_max_total: int = 39
    peak_min_total: int = 101


@dataclass(frozen=True)
class MetricsConfig:
    fuel_idle_rate_lps: float = 0.0008
    fuel_moving_rate_lps: float = 0.0012
    co2_kg_per_liter: float = 2.3


@dataclass(frozen=True)
class OutputConfig:
    reports_dir: str = "outputs/reports"
    detections_dir: str = "outputs/detections"


@dataclass(frozen=True)
class AppConfig:
    model: ModelConfig = ModelConfig()
    traffic: TrafficConfig = TrafficConfig()
    controller: ControllerConfig = ControllerConfig()
    simulation: SimulationConfig = SimulationConfig()
    metrics: MetricsConfig = MetricsConfig()
    outputs: OutputConfig = OutputConfig()


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    return data.get(name, {}) or {}



def validate_config(config: AppConfig) -> None:
    if config.traffic.lane_count <= 0:
        raise ValueError("traffic.lane_count must be greater than zero")
    if config.traffic.density_road_length <= 0:
        raise ValueError("traffic.density_road_length must be greater than zero")
    if config.controller.min_green < 0:
        raise ValueError("controller.min_green must be non-negative")
    if config.controller.max_green < config.controller.min_green:
        raise ValueError("controller.max_green must be greater than or equal to controller.min_green")
    if config.controller.yellow_duration < 0:
        raise ValueError("controller.yellow_duration must be non-negative")
    if config.controller.fixed_green_duration <= 0:
        raise ValueError("controller.fixed_green_duration must be greater than zero")
    if config.simulation.duration_seconds <= 0:
        raise ValueError("simulation.duration_seconds must be greater than zero")
    if config.simulation.time_step_seconds <= 0:
        raise ValueError("simulation.time_step_seconds must be greater than zero")
    if config.model.confidence < 0 or config.model.confidence > 1:
        raise ValueError("model.confidence must be between 0 and 1")
    if config.model.iou < 0 or config.model.iou > 1:
        raise ValueError("model.iou must be between 0 and 1")

def load_config(path: str | Path = "configs/default.yaml") -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    data = yaml.safe_load(config_path.read_text()) or {}
    model = ModelConfig(**_section(data, "model"))
    traffic_data = _section(data, "traffic")
    if "vehicle_classes" in traffic_data:
        traffic_data["vehicle_classes"] = tuple(traffic_data["vehicle_classes"])
    traffic = TrafficConfig(**traffic_data)
    sim_data = _section(data, "simulation")
    thresholds = sim_data.pop("scenario_thresholds", {}) or {}
    simulation = SimulationConfig(
        **sim_data,
        off_peak_max_total=thresholds.get("off_peak_max_total", 39),
        peak_min_total=thresholds.get("peak_min_total", 101),
    )
    config = AppConfig(
        model=model,
        traffic=traffic,
        controller=ControllerConfig(**_section(data, "controller")),
        simulation=simulation,
        metrics=MetricsConfig(**_section(data, "metrics")),
        outputs=OutputConfig(**_section(data, "outputs")),
    )
    validate_config(config)
    return config
