# Third-party notices

TrafficPilot AI source code is licensed under the repository `LICENSE`. Runtime dependencies and model checkpoints have separate licenses and obligations. Review upstream terms before redistribution or commercial use.

Dependency groups:

- Core: PyYAML for configuration loading.
- Vision extras: Ultralytics for YOLO model loading/tracking, OpenCV for video/image I/O and annotation, NumPy for polygon drawing arrays. Ultralytics may install PyTorch and related packages.
- GUI extras: Pygame, retained only for users who build their own graphical experiments outside the headless canonical pipeline.
- Plot extras: Matplotlib for optional benchmark charts.
- Development: pytest and Ruff.

Model checkpoints are not committed to this repository. Users are responsible for obtaining checkpoints and datasets from sources they are licensed to use.
