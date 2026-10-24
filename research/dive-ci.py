"""Reproduce Dive 0.13.1 CI exit codes using generated, trusted Docker archives.

Run with Python 3 and Dive 0.13.1 on PATH. No Docker daemon or downloads needed.
The JSON case deliberately asserts a known bypass, not desirable behavior.
"""

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile


def archive(files):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as stream:
        for name, data in files.items():
            header = tarfile.TarInfo(name)
            header.size = len(data)
            header.mode = 0o644
            stream.addfile(header, io.BytesIO(data))
    return output.getvalue()


def image(path, layers):
    blobs = [archive(files) for files in layers]
    ids = [hashlib.sha256(blob).hexdigest() for blob in blobs]
    config = json.dumps({
        "architecture": "arm64",
        "os": "linux",
        "config": {},
        "rootfs": {"type": "layers", "diff_ids": ["sha256:" + i for i in ids]},
        "history": [{"created_by": "fixture layer " + str(i)} for i in range(len(blobs))],
    }).encode()
    config_name = hashlib.sha256(config).hexdigest() + ".json"
    names = [i + "/layer.tar" for i in ids]
    manifest = [{"Config": config_name, "RepoTags": ["dive-fixture:local"], "Layers": names}]
    path.write_bytes(archive({
        config_name: config,
        "manifest.json": json.dumps(manifest).encode(),
        **dict(zip(names, blobs)),
    }))


version = subprocess.check_output(["dive", "--version"], text=True).strip()
if version != "dive 0.13.1":
    raise SystemExit("This reproduction expects dive 0.13.1; found " + version)
print(version)

with tempfile.TemporaryDirectory(prefix="dive-ci-review-") as temporary:
    root = Path(temporary)
    clean = root / "clean.tar"
    wasted = root / "wasted.tar"
    image(clean, [{"keep": b"x" * 4096}])
    image(wasted, [{"keep": b"x" * 4096, "waste": b"y" * 65536}, {".wh.waste": b""}])

    def run(name, source, flags, expected):
        result = subprocess.run(
            ["dive", "--source", "docker-archive", "--ci", *flags, str(source)],
            cwd=root,
            env={**os.environ, "CI": "true"},
            capture_output=True,
            text=True,
        )
        print(f"{name}: expected={expected} actual={result.returncode}")
        if result.returncode != expected:
            raise SystemExit(result.stdout + result.stderr)

    policy = [
        "--lowestEfficiency", "0.95",
        "--highestWastedBytes", "20KB",
        "--highestUserWastedPercent", "disabled",
    ]
    run("clean image passes", clean, policy, 0)
    run("waste fails", wasted, policy, 1)
    run("relaxed policy passes", wasted, [
        "--lowestEfficiency", "0", "--highestWastedBytes", "100KB",
        "--highestUserWastedPercent", "disabled",
    ], 0)
    run("equal byte boundary passes", wasted, [
        "--lowestEfficiency", "disabled", "--highestWastedBytes", "65536",
        "--highestUserWastedPercent", "disabled",
    ], 0)
    run("user waste ratio fails", wasted, [
        "--lowestEfficiency", "disabled", "--highestWastedBytes", "disabled",
        "--highestUserWastedPercent", "0.1",
    ], 1)
    run("JSON bypasses CI (known limitation)", wasted, [
        *policy, "--json", str(root / "report.json"),
    ], 0)
    report = json.loads((root / "report.json").read_text())
    assert report["image"]["inefficientBytes"] == 65536, report
    run("missing archive fails", root / "missing.tar", policy, 1)
