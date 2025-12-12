# Architecture

High-level flow:

1. Video input is read from `sample_videos/` or user-supplied videos.
2. YOLOv11 detection (see `Merges.py`) performs object detection and tracking.
3. Detections inside user-defined polygons are counted to estimate density.
4. Density feeds a rule-based adaptive signal controller that allocates green time.
5. Pygame simulation (`AdaptiveTrafficSim` and `FixedTimeTrafficSim` in `Merges.py`) validates performance and records metrics.

See also `papers/Paper Final.pdf` for diagrams and methodology (refer to pages 2–3 of the paper for architecture diagrams).

Files referenced:
- `Merges.py`: detection and simulation code.
- `run.py`: CLI wrapper to run detection or simulation.
- `scripts/check_files.py`: ensures required assets exist before running CI.
