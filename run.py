#!/usr/bin/env python3
"""Backward-compatible wrapper for the TrafficPilot CLI."""

from trafficpilot.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
