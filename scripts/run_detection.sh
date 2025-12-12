#!/usr/bin/env bash
# Lightweight helper to setup venv and run detection demo
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "To run detection demo, execute (example):"
echo "python Merges.py --input sample_videos/simulated_file_1.mp4 --mode detect --weights models/yolo11x.pt"
