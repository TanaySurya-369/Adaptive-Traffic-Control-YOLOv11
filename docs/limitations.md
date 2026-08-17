# Limitations

- Evaluation is simulation-based and not validated on a deployed traffic intersection.
- Video inputs represent CCTV-style footage; live CCTV integration is not implemented.
- The signal controller is deterministic and rule-based, not reinforcement learning.
- No multi-intersection coordination is implemented.
- No pedestrian-aware or emergency-vehicle-priority control is implemented.
- No dashboard is implemented.
- Detection quality depends on input video quality, camera angle, occlusion, tracker behavior, and checkpoint choice.
- If YOLO tracking IDs are missing, untracked detections are counted per frame and may over-count repeated objects.
- No labeled detection dataset is included, so ground-truth precision, recall, F1, mAP, FPS, latency, and accuracy are not reported.
- Fuel and emission calculations are simplified and not calibrated against real traffic-engineering measurements.
- YOLO model weights are not committed; users must download checkpoints separately.
