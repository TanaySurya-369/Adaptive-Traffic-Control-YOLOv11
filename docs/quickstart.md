# Quickstart

## Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python -m trafficpilot --help
python -m trafficpilot simulate --scenario mixed --seed 42 --duration 60
python -m trafficpilot benchmark --runs 3 --duration 60 --seed 42
```

## Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python -m trafficpilot --help
python -m trafficpilot simulate --scenario mixed --seed 42 --duration 60
python -m trafficpilot benchmark --runs 3 --duration 60 --seed 42
```

## Detection

Install optional vision dependencies and pass a local model checkpoint:

```bash
python -m pip install -e .[vision,dev]
python -m trafficpilot detect --input path/to/video.mp4 --roi configs/rois/example.json --model models/yolo11x.pt --output outputs/detections
```

Use `--dry-run` to validate paths and ROI JSON without loading YOLO:

```bash
python -m trafficpilot detect --input lane0.mp4 lane1.mp4 lane2.mp4 lane3.mp4 --roi configs/rois/example.json --dry-run
```
