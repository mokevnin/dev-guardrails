#!/usr/bin/env python3
"""Reproduce the ast-grep claims in research/custom-rules.md.

Requires ast-grep 0.51.0 on PATH. Copies project/ to a temp directory first.
Run from any directory: python3 research/fixtures/ast-grep/run.py
"""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile

SOURCE = Path(__file__).resolve().parent / "project"
version = subprocess.run(["ast-grep", "--version"], capture_output=True, text=True, check=True).stdout.strip()
print(version)
if "0.51.0" not in version:
    raise SystemExit(f"Unexpected ast-grep version: {version}")

work = Path(tempfile.mkdtemp(prefix="ast-grep-fixture-")) / "project"
shutil.copytree(SOURCE, work)


def run(*args):
    return subprocess.run(["ast-grep", *args], cwd=work, capture_output=True, text=True)


def expect(label, result, code):
    print(f"{label}: exit={result.returncode}", flush=True)
    if result.returncode != code:
        raise SystemExit(f"Unexpected exit for {label}: {result.returncode}, wanted {code}\n{result.stderr}")


expect("test, committed snapshot", run("test"), 0)
expect("scan, warning rule only", run("scan", "src"), 0)

(work / "src" / "domain").mkdir()
(work / "src" / "domain" / "order.ts").write_text('import { a } from "../ui/button";\n')
expect("scan, error rule matches", run("scan"), 1)

sarif = run("scan", "--format", "sarif")
results = json.loads(sarif.stdout)["runs"][0]["results"]
print("sarif levels:", sorted({item["level"] for item in results}))
if {item["level"] for item in results} != {"error", "warning"}:
    raise SystemExit("SARIF should carry both levels")

(work / "src" / "domain" / "order.ts").unlink()
rule = work / "rules" / "no-console-log.yml"
rule.write_text(rule.read_text().replace("logger.info(", "logger.debug("))
expect("test, stale snapshot", run("test"), 4)
