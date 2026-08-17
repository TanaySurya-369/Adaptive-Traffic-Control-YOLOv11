from __future__ import annotations

import random
from collections.abc import Sequence


def classify_scenario(
    counts: Sequence[int], off_peak_max_total: int = 39, peak_min_total: int = 101
) -> str:
    total = sum(counts)
    if total <= off_peak_max_total:
        return "off-peak"
    if total >= peak_min_total:
        return "peak"
    return "mixed"


def generate_scenario_counts(
    scenario: str, lane_count: int = 4, seed: int | None = None
) -> list[int]:
    rng = random.Random(seed)
    if lane_count != 4:
        raise ValueError(
            "The built-in scenario generator currently supports the four-lane prototype."
        )
    if scenario == "peak":
        return [rng.randint(20, 50), rng.randint(15, 40), rng.randint(25, 45), rng.randint(18, 35)]
    if scenario == "off-peak":
        return [rng.randint(5, 15) for _ in range(4)]
    if scenario == "mixed":
        return [rng.randint(10, 30), rng.randint(5, 25), rng.randint(15, 35), rng.randint(8, 22)]
    raise ValueError("scenario must be one of: off-peak, mixed, peak")
