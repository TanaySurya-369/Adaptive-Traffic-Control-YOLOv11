from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean


@dataclass
class ControllerMetrics:
    total_wait_time: float = 0.0
    avg_wait_time: float = 0.0
    fuel_consumption: float = 0.0
    throughput: int = 0
    co2_emissions: float = 0.0
    avg_queue_length: float = 0.0
    signal_utilization: float = 0.0


def calculate_improvement(
    adaptive_value: float, fixed_value: float, higher_is_better: bool = False
) -> float:
    if fixed_value == 0:
        return 0.0
    if higher_is_better:
        return ((adaptive_value - fixed_value) / fixed_value) * 100
    return ((fixed_value - adaptive_value) / fixed_value) * 100


def fuel_used(wait_time: float, move_time: float, idle_rate: float, moving_rate: float) -> float:
    return wait_time * idle_rate + move_time * moving_rate


def co2_emissions(fuel_liters: float, kg_per_liter: float) -> float:
    return fuel_liters * kg_per_liter


def aggregate(values: list[float]) -> float:
    return mean(values) if values else 0.0


def to_dict(metrics: ControllerMetrics) -> dict[str, float | int]:
    return asdict(metrics)
