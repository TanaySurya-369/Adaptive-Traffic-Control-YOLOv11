from __future__ import annotations


def calculate_density(vehicle_count: int, road_length: float = 100.0) -> float:
    if vehicle_count < 0:
        raise ValueError("vehicle_count must be non-negative")
    if road_length <= 0:
        raise ValueError("road_length must be positive")
    return vehicle_count / road_length
