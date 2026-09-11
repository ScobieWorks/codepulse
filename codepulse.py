#!/usr/bin/env python3
"""Entry point for the CodePulse CLI.

Usage:
    codepulse analyze <path> [-o OUTPUT]
"""
import argparse
import json
import sys
from pathlib import Path

from metrics import analyze


def main() -> None:
    parser = argparse.ArgumentParser(description="CodePulse – lightweight code maintainability metrics")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze_cmd = sub.add_parser("analyze", help="Analyze a codebase")
    analyze_cmd.add_argument("path", type=Path, help="Path to the codebase (directory or file)")
    analyze_cmd.add_argument("-o", "--output", type=Path, help="Write JSON report to file (default: stdout)")

    args = parser.parse_args()

    if args.command == "analyze":
        report = analyze(args.path)
        output = json.dumps(report, indent=2)
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
