#!/usr/bin/env python3
"""Scan fixture text only; never build images or start fixture services.

Requires Docker, Trivy 0.76.1 and Checkov 3.3.30 on PATH.
Run from any directory: python3 research/fixtures/kics/run.py /tmp/kics-results
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

FIXTURES = Path(__file__).resolve().parent
OUTPUT = Path(sys.argv[1]).resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)
IMAGE = "checkmarx/kics@sha256:ef29dbac14b046b1ef65f3280646112e927a61781c5f01bca1aeb723e0b96003"
KICS_CHECKS = "67fd0c4a-68cf-46d7-8c41-bc9fba7e40ae,ae5b6871-7f45-42e0-bb4c-ab300c4d2026,65905cec-d691-4320-b320-2000436cb696"
if any(OUTPUT.iterdir()):
    raise SystemExit("Use an empty output directory to guarantee isolated embedded Trivy checks")
for command, expected in ((["trivy", "--cache-dir", str(OUTPUT / "trivy-cache"), "--version"], "Version: 0.76.1"), (["checkov", "--version"], "3.3.30"), (["docker", "run", "--rm", "--network", "none", IMAGE, "version"], "2.2.0")):
    version = subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip()
    print(version, flush=True)
    if expected not in version:
        raise SystemExit(f"Unexpected scanner version: {version}")
summary = []
expected_codes = {"hardened": {"kics": 30, "trivy": 0, "checkov": 1, "kics-targeted": 0, "checkov-targeted": 0}, "misconfigured": {"kics": 50, "trivy": 1, "checkov": 1, "kics-targeted": 50, "checkov-targeted": 1, "trivy-default-exit": 0}}
expected_counts = {"hardened": {"kics": 4, "trivy": 0, "checkov": 1, "kics-targeted": 0, "checkov-targeted": 0}, "misconfigured": {"kics": 18, "trivy": 6, "checkov": 6, "kics-targeted": 3, "checkov-targeted": 2, "trivy-default-exit": 6}}
for state in ("hardened", "misconfigured"):
    commands = {
        "kics": ["docker", "run", "--rm", "--network", "none", "-v", f"{FIXTURES}:/fixtures:ro", "-v", f"{OUTPUT}:/reports", IMAGE, "scan", "-p", f"/fixtures/{state}", "-o", "/reports", "--output-name", f"kics-{state}", "--report-formats", "json,sarif", "--no-progress", "--disable-secrets"],
        "trivy": ["trivy", "config", "--cache-dir", str(OUTPUT / "trivy-cache"), "--skip-check-update", "--skip-version-check", "--format", "json", "--exit-code", "1", "--output", str(OUTPUT / f"trivy-{state}.json"), str(FIXTURES / state)],
        "checkov": ["checkov", "--directory", str(FIXTURES / state), "--framework", "dockerfile", "terraform", "--output", "json", "--skip-download", "--quiet"],
    }
    commands["kics-targeted"] = commands["kics"] + ["--include-queries", KICS_CHECKS, "--output-name", f"kics-targeted-{state}"]
    commands["checkov-targeted"] = commands["checkov"] + ["--check", "CKV_DOCKER_8,CKV_AWS_24"]
    if state == "misconfigured":
        commands["trivy-default-exit"] = commands["trivy"].copy()
        commands["trivy-default-exit"].remove("--exit-code")
        commands["trivy-default-exit"].remove("1")
    for scanner, command in commands.items():
        started = time.monotonic()
        result = subprocess.run(command, capture_output=True, text=True, env={**os.environ, "CHECKOV_ENABLE_VERSION_CHECK": "false"})
        (OUTPUT / f"{scanner}-{state}.stdout").write_text(result.stdout)
        (OUTPUT / f"{scanner}-{state}.stderr").write_text(result.stderr)
        summary.append({"scanner": scanner, "fixture": state, "exit": result.returncode, "seconds": round(time.monotonic() - started, 2), "command": command})
        print(scanner, state, result.returncode, flush=True)
        if scanner.startswith("kics"):
            report = json.loads((OUTPUT / f"{scanner}-{state}.json").read_text())
            count = sum(len(query["files"]) for query in report["queries"])
        elif scanner.startswith("trivy"):
            report = json.loads((OUTPUT / f"trivy-{state}.json").read_text())
            count = sum(len(item.get("Misconfigurations", [])) for item in report.get("Results", []))
        else:
            report = json.loads(result.stdout)
            reports = report if isinstance(report, list) else [report]
            count = sum(len(item.get("results", {}).get("failed_checks", [])) for item in reports)
        if result.returncode != expected_codes[state][scanner] or count != expected_counts[state][scanner]:
            raise SystemExit(f"Unexpected result: {scanner} {state}: exit={result.returncode}, findings={count}; inspect reports before updating expectations")
(OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
