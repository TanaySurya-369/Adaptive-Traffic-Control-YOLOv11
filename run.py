#!/usr/bin/env python3
"""Small CLI wrapper for Merges.py

This wrapper parses a small set of args and invokes `Merges.main()`.
Use `--mode detect` or `--mode simulate` and optionally `--input` and `--weights`.
"""
import argparse
import sys

def build_argv(args):
    argv = []
    if args.input:
        argv += ["--input", args.input]
    if args.mode:
        argv += ["--mode", args.mode]
    if args.weights:
        argv += ["--weights", args.weights]
    return argv

def main():
    parser = argparse.ArgumentParser(prog="run.py")
    parser.add_argument("--input", help="Input file or comma-separated list")
    parser.add_argument("--mode", choices=["detect", "simulate"], required=True)
    parser.add_argument("--weights", help="Path to YOLO weights file")
    args = parser.parse_args()

    # Import Merges locally to avoid heavy imports when run.py is inspected
    import Merges

    argv = build_argv(args)
    try:
        Merges.main(argv)
    except Exception as e:
        print(f"Error running Merges: {e}")
        raise

if __name__ == "__main__":
    main()
