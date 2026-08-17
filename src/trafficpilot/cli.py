from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict
from statistics import mean, median, stdev
from typing import Any

from . import __version__
from .config import AppConfig, load_config
from .control import AdaptiveController, FixedTimeController
from .metrics import calculate_improvement, to_dict
from .reporting import timestamp, write_benchmark_csv, write_json_report
from .simulation import SimulationParameters, simulate_controller
from .traffic.counting import validate_lane_inputs
from .traffic.density import calculate_density
from .traffic.roi import load_rois
from .traffic.scenarios import classify_scenario, generate_scenario_counts

LOGGER = logging.getLogger("trafficpilot")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trafficpilot", description="TrafficPilot AI CLI")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    sim = sub.add_parser("simulate", help="Run a deterministic controller simulation")
    sim.add_argument("--scenario", choices=["off-peak", "mixed", "peak"], default="mixed")
    sim.add_argument("--counts", nargs="+", type=int, help="Explicit lane vehicle counts")
    sim.add_argument("--duration", type=float, help="Simulation duration in seconds")
    sim.add_argument("--seed", type=int, help="Random seed")
    sim.add_argument("--output", default="outputs/reports/simulation.json")

    bench = sub.add_parser("benchmark", help="Compare adaptive and fixed-time controllers")
    bench.add_argument("--runs", type=int, default=3)
    bench.add_argument("--duration", type=float, help="Simulation duration in seconds")
    bench.add_argument("--seed", type=int, default=42)
    bench.add_argument("--output-json", default="outputs/reports/benchmark.json")
    bench.add_argument("--output-csv", default="outputs/reports/benchmark.csv")
    bench.add_argument("--plot", default=None, help="Optional benchmark plot PNG path")

    det = sub.add_parser("detect", help="Validate detection inputs and optional ROI config")
    det.add_argument(
        "--input", nargs="+", required=True, help="One video with lane ROIs, or one file per lane"
    )
    det.add_argument("--roi", help="Saved ROI JSON file with lane polygons")
    det.add_argument("--model", help="Ultralytics checkpoint path, e.g. models/yolo11x.pt")
    det.add_argument("--confidence", type=float, help="Detection confidence threshold")
    det.add_argument("--iou", type=float, help="Detection IoU threshold")
    det.add_argument("--image-size", type=int, help="Inference image size")
    det.add_argument("--device", help="Ultralytics device string")
    det.add_argument(
        "--tracker", help="Ultralytics tracker config, e.g. bytetrack.yaml or botsort.yaml"
    )
    det.add_argument("--output", default="outputs/detections", help="Detection output directory")
    det.add_argument("--annotate", action="store_true", help="Write annotated MP4 output")
    det.add_argument("--max-frames", type=int, help="Optional frame limit for smoke tests")
    det.add_argument("--dry-run", action="store_true", help="Validate inputs without loading YOLO")
    return parser


def _controllers(config: AppConfig) -> tuple[AdaptiveController, FixedTimeController]:
    return (
        AdaptiveController(
            min_green=config.controller.min_green,
            extra_green_per_vehicle=config.controller.extra_green_per_vehicle,
            max_green=config.controller.max_green,
            yellow_duration=config.controller.yellow_duration,
        ),
        FixedTimeController(
            green_duration=config.controller.fixed_green_duration,
            yellow_duration=config.controller.yellow_duration,
        ),
    )


def _sim_params(config: AppConfig, duration: float | None) -> SimulationParameters:
    return SimulationParameters(
        duration_seconds=duration or config.simulation.duration_seconds,
        time_step_seconds=config.simulation.time_step_seconds,
        idle_fuel_rate_lps=config.metrics.fuel_idle_rate_lps,
        moving_fuel_rate_lps=config.metrics.fuel_moving_rate_lps,
        co2_kg_per_liter=config.metrics.co2_kg_per_liter,
    )


def _simulation_report(
    counts: list[int], scenario: str, config: AppConfig, duration: float | None, seed: int
) -> dict[str, Any]:
    adaptive, fixed = _controllers(config)
    params = _sim_params(config, duration)
    adaptive_metrics = simulate_controller(counts, adaptive, params)
    fixed_metrics = simulate_controller(counts, fixed, params)
    return {
        "timestamp": timestamp(),
        "project_version": __version__,
        "scenario": scenario,
        "seed": seed,
        "lane_counts": counts,
        "lane_densities": [
            calculate_density(c, config.traffic.density_road_length) for c in counts
        ],
        "controllers": {
            "adaptive": to_dict(adaptive_metrics),
            "fixed_time": to_dict(fixed_metrics),
        },
        "improvements": {
            "wait_time_reduction_pct": calculate_improvement(
                adaptive_metrics.avg_wait_time, fixed_metrics.avg_wait_time
            ),
            "fuel_savings_pct": calculate_improvement(
                adaptive_metrics.fuel_consumption, fixed_metrics.fuel_consumption
            ),
            "co2_reduction_pct": calculate_improvement(
                adaptive_metrics.co2_emissions, fixed_metrics.co2_emissions
            ),
            "throughput_increase_pct": calculate_improvement(
                adaptive_metrics.throughput, fixed_metrics.throughput, higher_is_better=True
            ),
            "queue_reduction_pct": calculate_improvement(
                adaptive_metrics.avg_queue_length, fixed_metrics.avg_queue_length
            ),
        },
        "configuration": asdict(config),
    }


def run_simulate(args: argparse.Namespace, config: AppConfig) -> int:
    seed = args.seed if args.seed is not None else config.simulation.seed
    counts = args.counts or generate_scenario_counts(args.scenario, config.traffic.lane_count, seed)
    if len(counts) != config.traffic.lane_count:
        raise ValueError(
            f"Expected {config.traffic.lane_count} lane counts, received {len(counts)}"
        )
    scenario = args.scenario if args.counts is None else classify_scenario(counts)
    report = _simulation_report(counts, scenario, config, args.duration, seed)
    output = write_json_report(report, args.output)
    print(f"Wrote simulation report: {output}")
    print(json.dumps(report["improvements"], indent=2))
    return 0


def run_benchmark(args: argparse.Namespace, config: AppConfig) -> int:
    reports: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    scenarios = ["off-peak", "mixed", "peak"]
    for scenario in scenarios:
        scenario_reports = []
        for run in range(args.runs):
            seed = args.seed + run
            counts = generate_scenario_counts(scenario, config.traffic.lane_count, seed)
            report = _simulation_report(counts, scenario, config, args.duration, seed)
            scenario_reports.append(report)
            rows.append(
                {
                    "scenario": scenario,
                    "seed": seed,
                    "adaptive_avg_wait_time": report["controllers"]["adaptive"]["avg_wait_time"],
                    "fixed_avg_wait_time": report["controllers"]["fixed_time"]["avg_wait_time"],
                    "wait_time_reduction_pct": report["improvements"]["wait_time_reduction_pct"],
                    "adaptive_throughput": report["controllers"]["adaptive"]["throughput"],
                    "fixed_throughput": report["controllers"]["fixed_time"]["throughput"],
                }
            )
        reports.append(
            {
                "scenario": scenario,
                "runs": scenario_reports,
                "summary": {
                    "runs": args.runs,
                    "mean_wait_time_reduction_pct": mean(
                        r["improvements"]["wait_time_reduction_pct"] for r in scenario_reports
                    ),
                    "median_wait_time_reduction_pct": median(
                        r["improvements"]["wait_time_reduction_pct"] for r in scenario_reports
                    ),
                    "std_wait_time_reduction_pct": stdev(
                        r["improvements"]["wait_time_reduction_pct"] for r in scenario_reports
                    )
                    if args.runs > 1
                    else 0.0,
                },
            }
        )
    write_json_report(
        {"timestamp": timestamp(), "project_version": __version__, "benchmark": reports},
        args.output_json,
    )
    write_benchmark_csv(rows, args.output_csv)
    if args.plot:
        from .reporting import write_benchmark_plot

        write_benchmark_plot(rows, args.plot)
        print(f"Wrote benchmark plot: {args.plot}")
    print(f"Wrote benchmark reports: {args.output_json}, {args.output_csv}")
    return 0


def run_detect(args: argparse.Namespace, config: AppConfig) -> int:
    paths = validate_lane_inputs(args.input)
    rois = load_rois(args.roi) if args.roi else None
    model_path = args.model or config.model.path
    confidence = args.confidence if args.confidence is not None else config.model.confidence
    iou = args.iou if args.iou is not None else config.model.iou
    image_size = args.image_size if args.image_size is not None else config.model.image_size
    tracker = args.tracker or config.model.tracker
    if args.dry_run:
        print(
            f"Validated {len(paths)} input(s); roi={len(rois) if rois else 'full-frame fallback'}; "
            f"model={model_path}; confidence={confidence}; iou={iou}; image_size={image_size}; tracker={tracker}"
        )
        return 0
    from .detection.pipeline import DetectionRunConfig, run_detection

    result = run_detection(
        DetectionRunConfig(
            model_path=model_path,
            input_paths=[str(path) for path in paths],
            output_dir=args.output,
            roi_path=args.roi,
            confidence=confidence,
            iou=iou,
            image_size=image_size,
            device=args.device or config.model.device,
            tracker=tracker,
            vehicle_classes=config.traffic.vehicle_classes,
            density_road_length=config.traffic.density_road_length,
            save_annotated=args.annotate,
            max_frames=args.max_frames,
        )
    )
    print(f"Wrote detection report: {result.report_path}")
    if result.annotated_paths:
        print("Annotated outputs:")
        for path in result.annotated_paths:
            print(f"- {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s"
    )
    try:
        config = load_config(args.config)
        if args.command == "simulate":
            return run_simulate(args, config)
        if args.command == "benchmark":
            return run_benchmark(args, config)
        if args.command == "detect":
            return run_detect(args, config)
    except Exception as exc:
        LOGGER.error("%s", exc)
        return 2
    return 0
