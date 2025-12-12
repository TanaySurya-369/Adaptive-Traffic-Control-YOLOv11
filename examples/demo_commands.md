# Demo commands

Run detection on a single sample video:

```bash
python run.py --mode detect --input sample_videos/simulated_file_1.mp4 --weights models/yolo11x.pt
```

Run simulation only:

```bash
python run.py --mode simulate
```

Keyboard commands used by the program (from `Merges.py`):
- `q`: quit the display
- `r`: reset polygon selection or reset frame during polygon selection
- `n`: skip frame during polygon selection
