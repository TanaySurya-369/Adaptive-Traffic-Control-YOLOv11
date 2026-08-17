"""Small deterministic simulation example that does not require YOLO weights."""

from trafficpilot.cli import main

if __name__ == "__main__":
    raise SystemExit(
        main(["simulate", "--counts", "12", "8", "15", "10", "--duration", "60", "--seed", "42"])
    )
