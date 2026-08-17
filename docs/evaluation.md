# Evaluation

## Traffic-control evaluation

The `benchmark` command compares the rule-based adaptive controller and fixed-time controller across off-peak, mixed, and peak scenarios. Each controller receives the same initial lane counts for each run. Each run records:

- total waiting time;
- average waiting time;
- throughput;
- fuel consumption estimate;
- CO₂ estimate;
- average queue length;
- signal utilization;
- improvement percentages.

Scenario counts are generated deterministically from a seed. Repeated runs report mean, median, and standard deviation for wait-time reduction.

## Improvement formulas

For lower-is-better metrics:

```text
improvement = (fixed_time - adaptive) / fixed_time * 100
```

For throughput:

```text
improvement = (adaptive - fixed_time) / fixed_time * 100
```

## Detection evaluation

The `detect` command performs YOLO inference/tracking, ROI association, unique counting, density-indicator calculation, optional annotation, and JSON reporting. It does not compute precision, recall, F1, mAP@50, mAP@50:95, FPS, latency, or accuracy because the repository does not include labeled ground-truth annotations.

Ground-truth detection benchmarking is not currently included.

## Simulation limitations

Fuel and CO₂ values use simple constants and should be interpreted as comparative prototype metrics, not calibrated transportation-engineering estimates.
