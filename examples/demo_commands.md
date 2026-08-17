# Demo commands

Run deterministic simulation without YOLO weights:

```bash
python -m trafficpilot simulate --scenario mixed --seed 42 --duration 60
```

Run benchmark across built-in scenarios:

```bash
python -m trafficpilot benchmark --runs 3 --duration 60 --seed 42
```

Run benchmark and generate a real chart from the benchmark rows:

```bash
python -m pip install -e .[plots,dev]
python -m trafficpilot benchmark --runs 3 --duration 60 --seed 42 --plot outputs/reports/benchmark.png
```

Validate detection paths/ROI without loading a model:

```bash
python -m trafficpilot detect --input lane0.mp4 lane1.mp4 lane2.mp4 lane3.mp4 --roi configs/rois/example.json --dry-run
```

Run YOLO detection when model weights and a video are available:

```bash
python -m pip install -e .[vision,dev]
python -m trafficpilot detect --input path/to/video.mp4 --roi configs/rois/example.json --model models/yolo11x.pt --annotate --output outputs/detections
```
