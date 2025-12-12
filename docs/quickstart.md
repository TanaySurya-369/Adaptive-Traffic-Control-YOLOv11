# Quickstart (3-minute)

1. Create a virtual environment and activate it.

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows PowerShell
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Place model weights

```bash
mkdir -p models
# Download weights and save as models/yolo11x.pt
```

4. Run detection demo

```bash
python run.py --mode detect --input sample_videos/simulated_file_1.mp4 --weights models/yolo11x.pt
```

5. Run simulation

```bash
python run.py --mode simulate
```
