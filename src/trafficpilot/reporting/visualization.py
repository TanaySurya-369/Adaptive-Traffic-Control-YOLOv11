from __future__ import annotations

from pathlib import Path
from typing import Any


def write_benchmark_plot(rows: list[dict[str, Any]], path: str | Path) -> Path:
    """Create a benchmark bar chart from actual benchmark rows."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Matplotlib is required for plots. Install with: python -m pip install -e .[plots]"
        ) from exc

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    scenarios = [str(row["scenario"]) for row in rows]
    adaptive_wait = [float(row["adaptive_avg_wait_time"]) for row in rows]
    fixed_wait = [float(row["fixed_avg_wait_time"]) for row in rows]
    x_positions = range(len(rows))
    width = 0.4

    fig, ax = plt.subplots(figsize=(max(8, len(rows) * 1.2), 5))
    ax.bar([x - width / 2 for x in x_positions], adaptive_wait, width=width, label="Adaptive")
    ax.bar([x + width / 2 for x in x_positions], fixed_wait, width=width, label="Fixed-time")
    ax.set_ylabel("Average waiting time (simulation seconds)")
    ax.set_title("TrafficPilot benchmark: adaptive vs fixed-time wait")
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(scenarios, rotation=30, ha="right")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)
    return output
