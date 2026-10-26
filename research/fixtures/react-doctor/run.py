#!/usr/bin/env python3
"""Print react-doctor 0.9.18 exit codes on a fixture with warnings and no errors.

Requires Node and network access for npx. Telemetry and the score API are off.
Run from any directory: python3 research/fixtures/react-doctor/run.py
Expected: exit=0 by default, 1 with --blocking warning, 0 with --blocking none, 3 with --warning-exit-code 3.
"""
from pathlib import Path
import subprocess

APP = Path(__file__).resolve().parent / "app"
for flags in ([], ["--blocking", "warning"], ["--blocking", "none"], ["--warning-exit-code", "3"]):
    result = subprocess.run(["npx", "-y", "react-doctor@0.9.18", ".", "--no-telemetry", *flags], cwd=APP, capture_output=True, text=True)
    print(f"{' '.join(flags) or '(default)'}: exit={result.returncode}")
