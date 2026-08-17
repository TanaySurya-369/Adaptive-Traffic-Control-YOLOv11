from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Detection:
    xyxy: tuple[float, float, float, float]
    class_id: int
    class_name: str
    confidence: float
    track_id: int | None = None


class UltralyticsDetector:
    """Thin YOLO detector wrapper supporting any Ultralytics-compatible checkpoint."""

    def __init__(self, model_path: str, device: str | None = None) -> None:
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Model checkpoint not found: {path}. Download weights separately or pass --model."
            )
        from ultralytics import YOLO

        self.model = YOLO(str(path))
        self.device = device
        self.names = self.model.names

    def track(
        self,
        frame: Any,
        classes: list[int] | tuple[int, ...],
        confidence: float = 0.5,
        iou: float = 0.5,
        image_size: int = 640,
        tracker: str = "bytetrack.yaml",
    ) -> list[Detection]:
        results = self.model.track(
            frame,
            persist=True,
            classes=list(classes),
            conf=confidence,
            iou=iou,
            imgsz=image_size,
            device=self.device,
            tracker=tracker,
            verbose=False,
        )
        if not results or results[0].boxes is None or len(results[0].boxes) == 0:
            return []
        boxes = results[0].boxes
        ids = boxes.id.int().cpu().tolist() if boxes.id is not None else [None] * len(boxes)
        return [
            Detection(
                xyxy=tuple(float(x) for x in box),
                class_id=int(class_id),
                class_name=str(self.names[int(class_id)]),
                confidence=float(conf),
                track_id=track_id,
            )
            for box, class_id, conf, track_id in zip(
                boxes.xyxy.cpu().tolist(),
                boxes.cls.cpu().tolist(),
                boxes.conf.cpu().tolist(),
                ids,
                strict=True,
            )
        ]
