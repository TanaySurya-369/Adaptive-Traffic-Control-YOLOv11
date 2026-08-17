#!/usr/bin/env python3
"""Repository smoke check used by humans and CI."""

import sys
from pathlib import Path

required = [
    "src/trafficpilot",
    "src/trafficpilot/detection/pipeline.py",
    "configs/default.yaml",
    "configs/rois/example.json",
    "README.md",
    "tests",
]
missing = [path for path in required if not Path(path).exists()]
if missing:
    print("ERROR: missing required project paths:", ", ".join(missing))
    sys.exit(2)
print("OK: required project paths are present.")
