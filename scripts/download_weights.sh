#!/usr/bin/env bash
echo "This script explains how to obtain YOLO weights."
echo "Do NOT include model weights in the repository."
echo "
1) Create a 'models' directory: mkdir -p models
2) Download the weights (from your provider) and save as models/yolo11x.pt
   Example URL placeholder: <PUT_YOUR_WEIGHT_URL_HERE>
3) Once placed, run the demo: python Merges.py --mode detect --weights models/yolo11x.pt
"
