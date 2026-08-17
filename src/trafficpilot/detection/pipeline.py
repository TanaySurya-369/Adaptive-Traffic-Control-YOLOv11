from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from trafficpilot.reporting import write_json_report
from trafficpilot.traffic.counting import assign_detection_to_lane, validate_lane_inputs
from trafficpilot.traffic.density import calculate_density
from trafficpilot.traffic.roi import LaneROI, full_frame_rois, load_rois

from .detector import Detection, UltralyticsDetector

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DetectionRunConfig:
    model_path: str
    input_paths: list[str]
    output_dir: str
    roi_path: str | None = None
    confidence: float = 0.5
    iou: float = 0.5
    image_size: int = 640
    device: str | None = None
    tracker: str = "bytetrack.yaml"
    vehicle_classes: tuple[int, ...] = (2, 3, 5, 7)
    density_road_length: float = 100.0
    save_annotated: bool = False
    max_frames: int | None = None


@dataclass(frozen=True)
class DetectionRunResult:
    report_path: Path
    annotated_paths: list[Path]
    lane_counts: dict[int, int]
    lane_densities: dict[int, float]
    frames_processed: int
    detections_processed: int
    elapsed_seconds: float


def _import_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required for detection. Install vision dependencies with: "
            "python -m pip install -e .[vision]"
        ) from exc
    return cv2


def _video_writer(cv2: Any, output: Path, fps: float, size: tuple[int, int]) -> Any:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output), fourcc, fps or 20.0, size)
    if not writer.isOpened():
        raise RuntimeError(f"Could not open annotated video writer: {output}")
    return writer


def _draw_annotations(
    cv2: Any, frame: Any, detections: list[Detection], rois: list[LaneROI]
) -> None:
    import numpy as np

    for roi in rois:
        cv2.polylines(frame, [np.array(roi.polygon, dtype=np.int32)], True, (0, 255, 0), 2)
        x, y = roi.polygon[0]
        cv2.putText(
            frame, f"lane {roi.lane_id}", (x, y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
        )
    for detection in detections:
        x1, y1, x2, y2 = [int(v) for v in detection.xyxy]
        label = f"{detection.class_name} {detection.confidence:.2f}"
        if detection.track_id is not None:
            label += f" id={detection.track_id}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 160, 0), 2)
        cv2.putText(
            frame, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 160, 0), 2
        )


def _load_rois_for_capture(
    roi_path: str | None, width: int, height: int, lane_count: int
) -> list[LaneROI]:
    if roi_path:
        rois = load_rois(roi_path)
    else:
        rois = full_frame_rois(width, height, lane_count)
    for roi in rois:
        for x, y in roi.polygon:
            if x >= width or y >= height:
                raise ValueError(
                    f"ROI lane {roi.lane_id} coordinate {(x, y)} exceeds video dimensions {(width, height)}"
                )
    return rois


def run_detection(config: DetectionRunConfig) -> DetectionRunResult:
    """Run YOLO tracking, lane/ROI association, unique counting, and report export."""
    input_paths = validate_lane_inputs(config.input_paths)
    model_path = Path(config.model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"YOLO model not found: {model_path}")
    cv2 = _import_cv2()

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    detector = UltralyticsDetector(str(model_path), config.device)
    vehicle_classes = set(config.vehicle_classes)
    lane_counts: dict[int, int] = {}
    seen_by_lane: dict[int, set[int | str]] = {}
    annotated_paths: list[Path] = []
    frames_processed = 0
    detections_processed = 0
    start = perf_counter()

    for input_index, input_path in enumerate(input_paths):
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise RuntimeError(f"Input video/image could not be opened: {input_path}")
        writer = None
        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 20.0)
            if width <= 0 or height <= 0:
                raise RuntimeError(f"Input has invalid dimensions: {input_path}")
            lane_count = 1 if len(input_paths) > 1 else 4
            rois = _load_rois_for_capture(config.roi_path, width, height, lane_count)
            if len(input_paths) > 1 and config.roi_path is None:
                rois = [LaneROI(lane_id=input_index, polygon=rois[0].polygon)]
            for roi in rois:
                lane_counts.setdefault(roi.lane_id, 0)
                seen_by_lane.setdefault(roi.lane_id, set())

            if config.save_annotated:
                annotated_path = output_dir / f"{input_path.stem}_annotated.mp4"
                writer = _video_writer(cv2, annotated_path, fps, (width, height))
                annotated_paths.append(annotated_path)

            while True:
                if config.max_frames is not None and frames_processed >= config.max_frames:
                    break
                ok, frame = cap.read()
                if not ok:
                    break
                detections = detector.track(
                    frame,
                    classes=config.vehicle_classes,
                    confidence=config.confidence,
                    iou=config.iou,
                    image_size=config.image_size,
                    tracker=config.tracker,
                )
                frames_processed += 1
                detections_processed += len(detections)
                for detection_index, detection in enumerate(detections):
                    if detection.class_id not in vehicle_classes:
                        continue
                    lane_id = assign_detection_to_lane(detection, rois)
                    if lane_id is None:
                        continue
                    object_id: int | str = (
                        detection.track_id
                        if detection.track_id is not None
                        else f"untracked:{input_index}:{frames_processed}:{detection_index}"
                    )
                    if object_id not in seen_by_lane[lane_id]:
                        seen_by_lane[lane_id].add(object_id)
                        lane_counts[lane_id] += 1
                if writer is not None:
                    _draw_annotations(cv2, frame, detections, rois)
                    writer.write(frame)
        finally:
            cap.release()
            if writer is not None:
                writer.release()

    elapsed = perf_counter() - start
    lane_densities = {
        lane_id: calculate_density(count, config.density_road_length)
        for lane_id, count in sorted(lane_counts.items())
    }
    report = {
        "model": {
            "path": config.model_path,
            "confidence": config.confidence,
            "iou": config.iou,
            "image_size": config.image_size,
            "device": config.device,
            "tracker": config.tracker,
            "vehicle_classes": list(config.vehicle_classes),
        },
        "inputs": config.input_paths,
        "roi_path": config.roi_path,
        "lane_counts": {str(k): v for k, v in sorted(lane_counts.items())},
        "lane_density_indicators": {str(k): v for k, v in sorted(lane_densities.items())},
        "frames_processed": frames_processed,
        "detections_processed": detections_processed,
        "elapsed_seconds": elapsed,
        "annotated_outputs": [str(path) for path in annotated_paths],
        "config": asdict(config),
        "notes": [
            "Counts are unique per lane when tracking IDs are available.",
            "Untracked detections are counted per frame and can over-count repeated objects.",
            "No ground-truth detection accuracy, precision, recall, or mAP is computed by this command.",
        ],
    }
    report_path = write_json_report(report, output_dir / "detection_report.json")
    LOGGER.info("Wrote detection report: %s", report_path)
    return DetectionRunResult(
        report_path=report_path,
        annotated_paths=annotated_paths,
        lane_counts=lane_counts,
        lane_densities=lane_densities,
        frames_processed=frames_processed,
        detections_processed=detections_processed,
        elapsed_seconds=elapsed,
    )
