from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionEvaluationSummary:
    precision: float | None = None
    recall: float | None = None
    f1_score: float | None = None
    map50: float | None = None
    map50_95: float | None = None
    fps: float | None = None
    latency_ms: float | None = None
    note: str = "Ground-truth detection benchmarking is not currently included."
