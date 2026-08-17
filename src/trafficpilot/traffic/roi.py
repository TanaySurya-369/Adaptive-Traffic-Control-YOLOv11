from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

Point: TypeAlias = tuple[int, int]
Polygon: TypeAlias = list[Point]


@dataclass(frozen=True)
class LaneROI:
    """Polygon describing one lane/region of interest."""

    lane_id: int
    polygon: Polygon

    def contains_point(self, point: tuple[float, float]) -> bool:
        return point_in_polygon(point, self.polygon)


def point_in_polygon(point: tuple[float, float], polygon: Polygon) -> bool:
    """Return True when a point is inside or on the boundary of a polygon."""
    x, y = point
    inside = False
    n = len(polygon)
    if n < 3:
        return False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if min(p1y, p2y) <= y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            else:
                xinters = p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def bbox_center(xyxy: tuple[float, float, float, float]) -> tuple[float, float]:
    x1, y1, x2, y2 = xyxy
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def validate_polygon(raw_polygon: object, lane_id: int) -> Polygon:
    if not isinstance(raw_polygon, list):
        raise ValueError(f"ROI lane {lane_id} must be a list of points")
    if len(raw_polygon) < 3:
        raise ValueError(f"ROI lane {lane_id} contains fewer than 3 polygon points")
    polygon: Polygon = []
    for point_index, point in enumerate(raw_polygon):
        if not isinstance(point, list | tuple) or len(point) != 2:
            raise ValueError(f"ROI lane {lane_id} point {point_index} must be [x, y]")
        x, y = point
        if not isinstance(x, int | float) or not isinstance(y, int | float):
            raise ValueError(
                f"ROI lane {lane_id} point {point_index} must contain numeric coordinates"
            )
        if x < 0 or y < 0:
            raise ValueError(
                f"ROI lane {lane_id} point {point_index} contains negative coordinates"
            )
        polygon.append((int(x), int(y)))
    return polygon


def load_rois(path: str | Path, expected_lanes: int | None = None) -> list[LaneROI]:
    roi_path = Path(path)
    if not roi_path.exists():
        raise FileNotFoundError(f"ROI file not found: {roi_path}")
    try:
        data = json.loads(roi_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid ROI JSON: {roi_path}: {exc}") from exc
    lanes = data.get("lanes")
    if not isinstance(lanes, list):
        raise ValueError("ROI file must contain a 'lanes' list")
    if expected_lanes is not None and len(lanes) != expected_lanes:
        raise ValueError(f"ROI file must contain exactly {expected_lanes} lane polygons")
    rois: list[LaneROI] = []
    seen_lane_ids: set[int] = set()
    for index, lane in enumerate(lanes):
        if isinstance(lane, dict):
            lane_id = int(lane.get("lane_id", index))
            polygon_raw = lane.get("polygon")
        else:
            lane_id = index
            polygon_raw = lane
        if lane_id in seen_lane_ids:
            raise ValueError(f"Duplicate ROI lane_id: {lane_id}")
        seen_lane_ids.add(lane_id)
        rois.append(LaneROI(lane_id=lane_id, polygon=validate_polygon(polygon_raw, lane_id)))
    return sorted(rois, key=lambda roi: roi.lane_id)


def full_frame_rois(width: int, height: int, lane_count: int) -> list[LaneROI]:
    if width <= 0 or height <= 0:
        raise ValueError("Video dimensions must be positive")
    if lane_count <= 0:
        raise ValueError("lane_count must be positive")
    return [
        LaneROI(
            lane_id=i, polygon=[(0, 0), (width - 1, 0), (width - 1, height - 1), (0, height - 1)]
        )
        for i in range(lane_count)
    ]
