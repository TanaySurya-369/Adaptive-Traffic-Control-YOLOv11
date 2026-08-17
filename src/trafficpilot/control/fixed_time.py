from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FixedTimeController:
    green_duration: float = 30.0
    yellow_duration: float = 3.0

    def green_time(self, _: int = 0) -> float:
        return self.green_duration

    def next_lane(self, current_lane: int, lane_count: int) -> int:
        if lane_count <= 0:
            raise ValueError("lane_count must be positive")
        return (current_lane + 1) % lane_count
