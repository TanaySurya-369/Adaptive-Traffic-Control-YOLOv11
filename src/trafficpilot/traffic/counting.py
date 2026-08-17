from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

from trafficpilot.detection.tracker import UniqueTrackCounter

if TYPE_CHECKING:
    from trafficpilot.detection.detector import Detection

from .roi import LaneROI, bbox_center, load_rois

SUPPORTED_INPUT_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".jpg", ".jpeg", ".png"}


def validate_lane_inputs(paths: list[str]) -> list[Path]:
    if not paths:
        raise ValueError("At least one input image/video path is required")
    resolved: list[Path] = []
    for value in paths:
        path = Path(value)
        if not path.exists():
            raise FileNotFoundError(f"Input video/image does not exist: {path}")
        if path.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
            raise ValueError(
                f"Unsupported input extension for {path}. Supported: {sorted(SUPPORTED_INPUT_EXTENSIONS)}"
            )
        resolved.append(path)
    return resolved


def assign_detection_to_lane(detection: Detection, rois: list[LaneROI]) -> int | None:
    center = bbox_center(detection.xyxy)
    for roi in rois:
        if roi.contains_point(center):
            return roi.lane_id
    return None


def count_unique_detections(
    detections_by_frame: list[list[Detection]],
    rois: list[LaneROI],
    vehicle_classes: set[int],
) -> dict[int, int]:
    """Count unique tracked vehicles by lane using ROI center-point assignment."""
    counter = UniqueTrackCounter()
    lane_counts: Counter[int] = Counter({roi.lane_id: 0 for roi in rois})
    fallback_index = 0
    for frame_index, detections in enumerate(detections_by_frame):
        for detection_index, detection in enumerate(detections):
            if detection.class_id not in vehicle_classes:
                continue
            lane_id = assign_detection_to_lane(detection, rois)
            if lane_id is None:
                continue
            object_id: int | str
            if detection.track_id is None:
                object_id = f"untracked:{frame_index}:{detection_index}:{fallback_index}"
                fallback_index += 1
            else:
                object_id = detection.track_id
            if counter.mark_seen(lane_id, object_id):
                lane_counts[lane_id] += 1
    return dict(lane_counts)


__all__ = [
    "SUPPORTED_INPUT_EXTENSIONS",
    "assign_detection_to_lane",
    "count_unique_detections",
    "load_rois",
    "validate_lane_inputs",
]
