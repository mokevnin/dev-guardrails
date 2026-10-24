#!/usr/bin/env python3
"""Compare pinned PHPMD/Mago metrics on generated PHP text, without executing it."""
import argparse
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--phpmd", type=Path, required=True, help="PHPMD 3.0.0 PHAR")
parser.add_argument("--mago", type=Path, required=True, help="Mago 1.58.2 executable")
parser.add_argument("--output", type=Path, required=True, help="Empty directory for inputs and reports")
args = parser.parse_args()
phpmd, mago, output = args.phpmd.resolve(), args.mago.resolve(), args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
if any(output.iterdir()):
    raise SystemExit("Choose an empty output directory")
for command, expected in ((["php", str(phpmd), "--version"], "PHPMD 3.0.0"),
                          ([str(mago), "--version"], "mago 1.58.2")):
    version = subprocess.check_output(command, text=True).strip()
    print(version, flush=True)
    if version != expected:
        raise SystemExit("Unexpected version: " + version)

HEADER = "<?php\ndeclare(strict_types=1);\n\nnamespace Fixture;\n\n"
METRICS = "cyclomatic-complexity,too-many-methods,too-many-properties,excessive-parameter-list"
cases = []


def subject(body):
    return HEADER + "/** Static-analysis example. */\nfinal class Subject\n{\n" + body + "}\n"


def method(body, parameters="array $flags", result="int"):
    return "    /** Compute the example result. */\n    public function evaluate(" + parameters + "): " + result + "\n    {\n" + body + "    }\n"


def methods(count):
    return "".join(f"    /** Return an example value. */\n    public function action{i}(): int {{ return {i}; }}\n" for i in range(count))


def properties(count):
    return "".join(f"    /** Example value. */\n    public int $value{i} = {i};\n" for i in range(count))


def add(metric, variant, rule, maximum, code, expected, mago_rules=None, extra=None, **properties):
    properties = {"maximum": maximum, **properties}
    cases.append(dict(name=metric + "-" + variant, rule=rule, properties=properties,
                      code=code, expected=expected, mago_rules=mago_rules or {}, extra=extra or {}))


for variant, count in (("control", 2), ("over", 3)):
    body = "        $result = 0;\n" + "".join(
        f"        if ($flags[{i}]) {{ $result += 1; }}\n" for i in range(count)) + "        return $result;\n"
    add("cyclomatic", variant, "codesize.xml/CyclomaticComplexity", 3, subject(method(body)),
        (0, 0) if variant == "control" else (2, 1),
        {"cyclomatic-complexity": "threshold=999, method-threshold=3"}, showClassesComplexity=False)

for variant, count in (("control", 7), ("over", 8)):
    body = "        $result = 0;\n" + "".join(
        f"        if ($flags[{i}]) {{ $result += 1; }}\n" for i in range(count)) + "        return $result;\n"
    add("npath", variant, "codesize.xml/NPathComplexity", 200, subject(method(body)),
        (0, 0) if variant == "control" else (2, 0))

for variant, count in (("control", 5), ("over", 6)):
    add("parameters", variant, "codesize.xml/ExcessiveParameterList", 5,
        subject(method("        return " + " + ".join(f"$input{i}" for i in range(count)) + ";\n",
                       ", ".join(f"int $input{i}" for i in range(count)))),
        (0, 0) if variant == "control" else (2, 1),
        {"excessive-parameter-list": "threshold=5"})
    add("methods", variant, "codesize.xml/TooManyMethods", 5, subject(methods(count)),
        (0, 0) if variant == "control" else (2, 1),
        {"too-many-methods": "threshold=5, count-setters-and-getters=true"})
    add("fields", variant, "codesize.xml/TooManyFields", 5, subject(properties(count)),
        (0, 0) if variant == "control" else (2, 1),
        {"too-many-properties": "threshold=5"})
    add("wmc", variant, "codesize.xml/ExcessiveClassComplexity", 5, subject(methods(count)),
        (0, 0) if variant == "control" else (2, 0),
        {"cyclomatic-complexity": "threshold=5, method-threshold=10"})

for variant, count in (("control", 5), ("over", 20)):
    body = "        $result = [];\n" + "".join(
        f"        $result['field{i}'] = $values['input{i}'];\n" for i in range(count)) + "        return $result;\n"
    add("method-loc", variant, "codesize.xml/ExcessiveMethodLength", 15,
        subject(method(body, parameters="array $values", result="array")), (0, 0) if variant == "control" else (2, 0))

body = "        $result = 0;\n" + "        $result += 1;\n" * 20 + "        return $result;\n"
add("method-loc", "halstead-overlap", "codesize.xml/ExcessiveMethodLength", 15,
    subject(method(body, parameters="")), (2, 0))

for variant, count in (("control", 5), ("over", 20)):
    body = "        $result = [];\n" + "".join(
        f"        $result['field{i}'] = $values['input{i}'];\n" for i in range(count)) + "        return $result;\n"
    add("class-loc", variant, "codesize.xml/ExcessiveClassLength", 25,
        subject(method(body, parameters="array $values", result="array")), (0, 0) if variant == "control" else (2, 0))

for variant, count in (("control", 5), ("over", 6)):
    body = "        return [" + ", ".join(f"new Dependency{i}()" for i in range(count)) + "];\n"
    extra = {f"Dependency{i}.php": HEADER + f"/** Example dependency. */\nfinal class Dependency{i} {{}}\n" for i in range(count)}
    add("coupling", variant, "design.xml/CouplingBetweenObjects", 5,
        subject(method(body, parameters="", result="array")),
        (0, 0) if variant == "control" else (2, 0), extra=extra)

for variant, count in (("control", 2), ("over", 3)):
    add("public-surface", variant, "codesize.xml/ExcessivePublicCount", 5,
        subject(properties(count) + methods(count)), (0, 0) if variant == "control" else (2, 0),
        {"too-many-methods": "threshold=5, count-setters-and-getters=true",
         "too-many-properties": "threshold=5"})

catalog = subprocess.check_output([str(mago), "lint", "--pedantic", "--list-rules", "--json"], text=True)
(output / "mago-all-rules.json").write_text(catalog)
all_rules = {rule["code"]: 'enabled=true,level="error"' for rule in json.loads(catalog)}
summary = []
for case in cases:
    directory = output / case["name"]
    directory.mkdir()
    source = directory / "src"
    source.mkdir()
    (source / "Subject.php").write_text(case["code"])
    for filename, code in case["extra"].items():
        (source / filename).write_text(code)
    settings = "".join(f"      {key}: {str(value).lower()}\n" for key, value in case["properties"].items())
    policy = directory / "phpmd.yml"
    policy.write_text("rules:\n  - ref: rulesets/" + case["rule"] + "\n    properties:\n" + settings)
    rules = {"cyclomatic-complexity": "threshold=15, method-threshold=10",
             "too-many-methods": "threshold=25, count-setters-and-getters=true",
             "too-many-properties": "threshold=15", "excessive-parameter-list": "threshold=10"}
    rules.update(case["mago_rules"])
    config = directory / "mago.toml"
    config.write_text('version="1.58.2"\nphp-version="8.2"\n[linter.rules]\n' + "".join(
        f'{key}={{enabled=true,level="error",{value}}}\n' for key, value in rules.items()))
    full_config = directory / "mago-all.toml"
    full_rules = {**all_rules, **{key: 'enabled=true,level="error",' + value for key, value in rules.items()}}
    full_config.write_text('version="1.58.2"\nphp-version="8.2"\n[linter.rules]\n' + "".join(
        f'{key}={{{value}}}\n' for key, value in full_rules.items()))
    commands = {
        "phpmd": ["php", str(phpmd), "analyze", "--ruleset", str(policy), "--no-progress", "--threads", "1", "--format", "json", str(source)],
        "mago-metrics": [str(mago), "--workspace", str(directory), "--config", str(config), "--threads", "1", "lint", "--only", METRICS, "--reporting-format", "json", str(source)],
        "mago-all": [str(mago), "--workspace", str(directory), "--config", str(full_config), "--threads", "1", "lint", "--minimum-fail-level", "help", "--reporting-format", "json", str(source)],
    }
    row = {"case": case["name"], "commands": commands}
    for name, command in commands.items():
        result = subprocess.run(command, cwd=directory, capture_output=True, text=True)
        (directory / f"{name}.json").write_text(result.stdout)
        (directory / f"{name}.stderr").write_text(result.stderr)
        report = json.loads(result.stdout)
        if name == "phpmd" and report.get("errors"):
            raise SystemExit(f"PHPMD processing errors in {case['name']}: {report['errors']}")
        diagnostics = [v for file in report.get("files", []) for v in file.get("violations", [])] if name == "phpmd" else report["issues"]
        row[name] = {"exit": result.returncode, "codes": sorted({v.get("rule", v.get("code")) for v in diagnostics})}
    expected = case["expected"]
    actual = (row["phpmd"]["exit"], row["mago-metrics"]["exit"])
    print(case["name"], actual, "all-rules:", row["mago-all"], flush=True)
    summary.append(row)
    if actual != expected:
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        raise SystemExit(f"Unexpected result for {case['name']}: {actual} != {expected}; inspect reports")
    expected_phpmd = [case["rule"].split("/")[-1]] if expected[0] else []
    if row["phpmd"]["codes"] != expected_phpmd:
        raise SystemExit(f"Unexpected PHPMD diagnostics: {row}")
    expected_mago = []
    if expected[1]:
        expected_mago = [{"cyclomatic": "cyclomatic-complexity", "parameters": "excessive-parameter-list",
                          "methods": "too-many-methods", "fields": "too-many-properties"}[case["name"].rsplit("-", 1)[0]]]
    if row["mago-metrics"]["codes"] != expected_mago:
        raise SystemExit(f"Unexpected Mago metric diagnostics: {row}")
    expected_all = ["halstead"] if case["name"] == "method-loc-halstead-overlap" else expected_mago
    if row["mago-all"]["codes"] != expected_all or row["mago-all"]["exit"] != bool(expected_all):
        raise SystemExit(f"Unexpected full-rule Mago diagnostics: {row}")

invalid = output / "invalid"
invalid.mkdir()
(invalid / "Invalid.php").write_text("<?php\nfunction broken( {\n")
for name, command, expected in (
    ("phpmd", ["php", str(phpmd), "analyze", "--ruleset", "codesize", "--no-progress", "--threads", "1", "--format", "json", str(invalid / "Invalid.php")], 3),
    ("mago", [str(mago), "--workspace", str(invalid), "--php-version", "8.2", "--threads", "1", "lint", "--only", "cyclomatic-complexity", "--reporting-format", "json", str(invalid / "Invalid.php")], 1),
):
    result = subprocess.run(command, cwd=invalid, capture_output=True, text=True)
    (invalid / f"{name}.json").write_text(result.stdout)
    (invalid / f"{name}.stderr").write_text(result.stderr)
    report = json.loads(result.stdout)
    has_error = bool(report.get("errors")) if name == "phpmd" else any(i["code"] == "parse" for i in report["issues"])
    if result.returncode != expected or not has_error:
        raise SystemExit(f"Expected parse failure from {name}; inspect {invalid}")
    print("invalid", name, result.returncode, flush=True)
    summary.append({"case": "invalid", "tool": name, "command": command, "exit": result.returncode})
(output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
