#!/usr/bin/env python3
"""Simple CI smoke test to ensure required folders/files exist."""
import os
import sys

required = ["images", "sample_videos", "papers", "models"]
missing = []
for name in required:
    if not os.path.exists(name):
        missing.append(name)

if missing:
    print("ERROR: Missing required files or directories:", ", ".join(missing))
    print("Create the missing directories or place required files before running the demo.")
    sys.exit(2)

print("OK: All required directories exist.")
sys.exit(0)
