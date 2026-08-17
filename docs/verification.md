# Verification log

Environment used for the latest local verification:

- OS: Linux container
- Python: 3.14.4
- GPU: not used
- YOLO weights: not available in repository
- GUI/display: not required for tested commands

| Command | Result | Notes |
| --- | --- | --- |
| `python -m pip install -e .[dev]` | PASS | Core package and development tools installed. |
| `ruff check .` | PASS | Static linting passed. |
| `pytest` | PASS | Unit and CLI integration tests passed. |
| `python -m trafficpilot --help` | PASS | CLI help rendered successfully. |
| `python -m trafficpilot simulate --scenario mixed --seed 42 --duration 10 --output /tmp/tp_sim.json` | PASS | Headless simulation report generated. |
| `python -m trafficpilot benchmark --runs 1 --duration 10 --output-json /tmp/tp_bench.json --output-csv /tmp/tp_bench.csv` | PASS | Headless benchmark JSON/CSV generated. |
| `python scripts/check_files.py` | PASS | Required repository paths exist. |
| `python -m trafficpilot detect --input "$tmpdir/lane0.mp4" "$tmpdir/lane1.mp4" "$tmpdir/lane2.mp4" "$tmpdir/lane3.mp4" --roi configs/rois/example.json --dry-run` | PASS | Temporary placeholder files validated path/extension/ROI handling without loading YOLO. |
| `python -c "import trafficpilot; print(trafficpilot.__version__)"` | PASS | Package imports and version prints. |
| `git diff --check` | PASS | No whitespace errors. |
| Real YOLO inference | NOT RUN | Model weights and suitable sample video are not committed to the repository. |

Do not convert the `NOT RUN` detection smoke-test row to PASS unless a real local model checkpoint and compatible video input are used.
