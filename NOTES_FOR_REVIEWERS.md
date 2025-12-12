# Notes for Reviewers

- YOLO weights are intentionally not included. Please place `models/yolo11x.pt` manually.
- CI smoke test (`scripts/check_files.py`) checks for `images/`, `sample_videos/`, `papers/`, `models/`.
- `Merges.py` was refactored to lazy-load model weights via `load_model()` to avoid heavy imports at module import time.
- The `run.py` wrapper provides a simpler CLI interface (see `run.py --help`).
- Missing items: no external weight URLs included; please provide your own private weight URL.
