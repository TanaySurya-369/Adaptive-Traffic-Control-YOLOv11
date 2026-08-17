#!/usr/bin/env bash
set -euo pipefail
cat <<'MSG'
TrafficPilot AI does not commit YOLO model weights.

1. Create the local model directory:
   mkdir -p models
2. Download an Ultralytics-compatible YOLO11 checkpoint, for example yolo11x.pt,
   from the official Ultralytics distribution or your approved model source.
3. Save it locally, for example:
   models/yolo11x.pt
4. Run a dry validation first:
   python -m trafficpilot detect --input lane0.mp4 lane1.mp4 lane2.mp4 lane3.mp4 --roi configs/rois/example.json --dry-run
5. Run model loading when weights are available:
   python -m trafficpilot detect --input lane0.mp4 lane1.mp4 lane2.mp4 lane3.mp4 --roi configs/rois/example.json --model models/yolo11x.pt
MSG
