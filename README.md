# Adaptive-Traffic-Control-YOLOv11

![license](https://img.shields.io/badge/license-MIT-blue.svg) ![python](https://img.shields.io/badge/python-3.10%2B-orange.svg) ![build](https://img.shields.io/badge/build-passing-brightgreen) ![repo size](https://img.shields.io/github/repo-size/your-username/Adaptive-Traffic-Control-YOLOv11)

Vision-based adaptive traffic signal control using YOLOv11 and Pygame simulation.

## Table of contents
- [Demo](#demo)
- [Motivation](#motivation)
- [What's included](#whats-included)
- [Quickstart](#quickstart)
- [Usage examples](#usage-examples)
- [Project structure](#project-structure)
- [Dataset & model weights](#dataset--model-weights)
- [Metrics and demo results](#metrics-and-demo-results)
- [How it works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)
- [Contact / Authors](#contact--authors)
- [Citation](#citation)
- [Screenshots](#screenshots)

## Demo

If you have a short GIF at `README_ASSETS/demo.gif` it will be displayed here. Otherwise, a thumbnail image is shown instead.

![Demo Thumbnail](README_ASSETS/demo.gif)

If the GIF is not present, run the demo locally to create one (see Quickstart).

## Motivation

Road congestion increases travel times, fuel consumption and emissions. This project demonstrates a vision-based adaptive signal control system using YOLOv11 detections to estimate traffic density and allocate green-time dynamically. The goal is to reduce waiting time, fuel consumption, and CO2 emissions in urban intersections.

## What's included
- `images/` — thumbnails and visual assets used in the README and demo.
- `sample_videos/` — simulated video clips for testing detection and simulation.
- `papers/` — PDFs describing the methodology and reported results.
- `Merges.py` — main integrated detection + simulation program.
- `scripts/` — helper scripts for setup, checking files, and weight download instructions.
- `examples/` — copy/paste demo commands.
- `docs/` — architecture diagram and quickstart docs.

## Quickstart

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place YOLO weights
mkdir -p models
# Download yolo11x weights from <PUT_YOUR_WEIGHT_URL_HERE> and save as models/yolo11x.pt
# DO NOT commit or upload model weights to this repo.

# 4. Run detection demo on a sample video
python Merges.py --input sample_videos/simulated_file_1.mp4 --mode detect

# 5. Run the Pygame simulation
python Merges.py --mode simulate
```

Troubleshooting tips:
- If you see codec errors, install `ffmpeg` and ensure your OpenCV build supports the video codec.
- Ensure `models/yolo11x.pt` exists and is readable.
- On Windows PowerShell, use the PowerShell activate command shown above.

## Usage examples

```bash
# Detect on one or multiple input files (comma-separated)
python run.py --mode detect --input sample_videos/simulated_file_1.mp4 --weights models/yolo11x.pt

# Run simulation only
python run.py --mode simulate
```

## Project structure

- images/: visual assets
- sample_videos/: demo videos
- papers/: project papers and reports
- Merges.py: main program (detection + simulation)
- run.py: lightweight CLI wrapper
- scripts/: helper scripts
- docs/: architecture and quickstart

## Dataset & model weights

Model weights are large and not included. Download the weights manually and place them in `models/yolo11x.pt`.

Download placeholder:

```
# Download weights and save as models/yolo11x.pt
# URL: <PUT_YOUR_WEIGHT_URL_HERE>
```

## Metrics and demo results

The included paper reports roughly 25% wait-time reduction and 15% fuel savings for the tested scenarios — see `papers/Paper Final.pdf` for methodology.

## How it works

Video frames → YOLO detection → counting and density estimation → rule-based adaptive timing → Pygame simulation for validation. See `docs/architecture.md` for details.

## Contributing

See `CONTRIBUTING.md` for how to run locally, style suggestions and how to make PRs.

## License

This project is licensed under the MIT License — see `LICENSE`.

## Contact / Authors

- Tanay Surya Vaikuntapu
- Tulasi S. Prasad
- Goli Jahnavi
- Tanay Surya Vardhan
- Shaik Salman

## Citation

Please cite the included paper and/or this repository if you use this work.

BibTeX skeleton:

```bibtex
@misc{adaptive-yolo11-2025,
  title={Adaptive Traffic Control using YOLOv11},
  author={Tanay Surya Vaikuntapu and Tulasi S. Prasad and Goli Jahnavi and others},
  year={2025},
  howpublished={\url{https://github.com/<your-username>/Adaptive-Traffic-Control-YOLOv11}}
}
```

## Screenshots

See `images/` for screenshots used in the demo. Example: `images/mod_int.png`.
