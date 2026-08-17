# Contributing

Thank you for improving TrafficPilot AI. Keep contributions focused, tested, and honest about implemented behavior.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\Activate.ps1         # Windows PowerShell
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

For YOLO/OpenCV detection work, install the optional vision extras:

```bash
python -m pip install -e .[vision,dev]
```

## Checks before opening a PR

```bash
ruff check .
pytest
python -m trafficpilot --help
python -m trafficpilot simulate --scenario mixed --seed 42 --duration 10
python -m trafficpilot benchmark --runs 1 --duration 10
```

## Pull request expectations

- Keep README/docs consistent with `docs/project-facts.md`.
- Do not commit model weights, generated outputs, datasets, secrets, or local environment files.
- Do not claim detection accuracy, mAP, FPS, latency, or traffic improvements unless they are measured and reproducible.
- Include tests for new controller, traffic, metrics, reporting, CLI, or detection behavior.
- Prefer small, reviewable changes with clear commit messages.
