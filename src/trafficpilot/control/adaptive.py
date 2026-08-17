from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdaptiveController:
    min_green: float = 10.0
    extra_green_per_vehicle: float = 1.0
    max_green: float = 50.0
    yellow_duration: float = 3.0

    def green_time(self, vehicle_count: int) -> float:
        if vehicle_count < 0:
            raise ValueError("vehicle_count must be non-negative")
        return min(self.max_green, self.min_green + vehicle_count * self.extra_green_per_vehicle)

    def prioritize_lanes(self, queue_lengths: list[int]) -> list[int]:
        return sorted(range(len(queue_lengths)), key=lambda lane: queue_lengths[lane], reverse=True)

    def cycle_allocations(self, queue_lengths: list[int]) -> list[float]:
        return [self.green_time(count) for count in queue_lengths]
