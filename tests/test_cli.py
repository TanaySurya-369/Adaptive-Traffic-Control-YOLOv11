import json
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str):
    return subprocess.run(
        [sys.executable, "-m", "trafficpilot", *args], text=True, capture_output=True, check=False
    )


def test_help():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "TrafficPilot AI CLI" in result.stdout


def test_simulate_writes_report(tmp_path: Path):
    output = tmp_path / "simulation.json"
    result = run_cli(
        "simulate", "--counts", "5", "4", "3", "2", "--duration", "30", "--output", str(output)
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(output.read_text())
    assert data["lane_counts"] == [5, 4, 3, 2]
    assert "controllers" in data


def test_benchmark_writes_reports(tmp_path: Path):
    output_json = tmp_path / "benchmark.json"
    output_csv = tmp_path / "benchmark.csv"
    result = run_cli(
        "benchmark",
        "--runs",
        "1",
        "--duration",
        "20",
        "--output-json",
        str(output_json),
        "--output-csv",
        str(output_csv),
    )
    assert result.returncode == 0, result.stderr
    assert output_json.exists()
    assert output_csv.exists()
