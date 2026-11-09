"""Record local validation without substituting mocks for a real broker run."""
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "project"
ARTIFACTS = ROOT / "artifacts"


def run(name, arguments):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run([sys.executable, *arguments], cwd=PROJECT,
                            capture_output=True, text=True, encoding="utf-8", env=env)
    (ARTIFACTS / f"{name}.log").write_text(result.stdout+result.stderr, encoding="utf-8")
    return {"name": name, "status": "PASS" if result.returncode == 0 else "FAIL",
            "exit_code": result.returncode, "command": [sys.executable, *arguments],
            "log": f"artifacts/{name}.log"}


def static_checks():
    compose = yaml.safe_load((PROJECT / "compose.yaml").read_text(encoding="utf-8"))
    assert set(compose["services"]) == {"broker", "provider", "advisor"}
    manifest = yaml.safe_load((PROJECT / "config/ankaios.yaml").read_text(encoding="utf-8"))
    assert manifest["apiVersion"] == "v1"
    for workload in manifest["workloads"].values():
        config = yaml.safe_load(workload["runtimeConfig"])
        assert "image" in config and isinstance(config["commandArgs"], list)
    schema = json.loads((PROJECT / "config/vss.json").read_text(encoding="utf-8"))
    with (PROJECT / "config/signals.csv").open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            entry = schema
            for part in row["path"].split("."):
                entry = entry.get("children", entry)[part]
            assert entry["type"] == row["type"] and entry["datatype"] == row["datatype"]
            assert entry.get("unit", "") == row["unit"]
    expected = {"val.proto": "5d78098dd3a7469f5dc15634a5c47557bf26faa4d01afd9714a0ad1cd5e0f94e",
                "types.proto": "301f7cd69646506367e449585db51c0351dbbd8ef5f0bfb8ffc781bb3dbe8808"}
    for name, digest in expected.items():
        assert hashlib.sha256((PROJECT / "proto/kuksa/val/v2" / name).read_bytes()).hexdigest() == digest
    return {"name": "static-schema-and-yaml", "status": "PASS",
            "note": "YAML parsed, nested runtimeConfig parsed, signal CSV matches JSON; proto hashes match. Does not replace docker compose config or runtime validation."}


class ReaderLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs = [], []

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if "id" in fields:
            self.ids.append(fields["id"])
        if tag == "a" and "href" in fields:
            self.hrefs.append(fields["href"])


def document_checks():
    failures = []
    files = [ROOT / "README.md", ROOT / "VALIDATION.md", *sorted((ROOT / "docs").glob("*.md")),
             PROJECT / "README.md", PROJECT / "THIRD_PARTY_NOTICES.md"]
    for path in files:
        raw = path.read_text(encoding="utf-8")
        for href in re.findall(r'\]\(([^)]+)\)', raw):
            parts = urlsplit(href)
            if not parts.scheme and parts.path and not (path.parent / unquote(parts.path)).exists():
                failures.append(f"{path.name}: {href}")
    reader = ReaderLinks()
    reader.feed((ROOT / "START_HERE.html").read_text(encoding="utf-8"))
    assert len(reader.ids) == len(set(reader.ids)), "Duplicate HTML IDs"
    for href in reader.hrefs:
        parts = urlsplit(href)
        if parts.scheme or parts.netloc:
            continue
        if not parts.path and parts.fragment and unquote(parts.fragment) not in reader.ids:
            failures.append("HTML missing anchor: "+href)
        if parts.path and not (ROOT / unquote(parts.path)).exists():
            failures.append("HTML missing local file: "+href)
    assert not failures, failures
    return {"name": "document-links", "status": "PASS", "markdown_files": len(files),
            "html_links": len(reader.hrefs), "html_ids": len(reader.ids)}


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    report = {"prepared_date": "2026-11-09", "executed_at_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "platform": platform.platform(),
              "packages": {name: importlib.metadata.version(name)
                           for name in ["grpcio", "grpcio-tools", "protobuf", "PyYAML", "Markdown"]},
              "checks": []}
    checks = report["checks"]
    # The report itself is linked by VALIDATION.md; make it exist before link checks,
    # including on a clean checkout with no earlier artifacts.
    (ARTIFACTS / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for name, args in [("generate-proto", ["scripts/generate_proto.py"]),
                       ("unit-tests", ["-m", "unittest", "discover", "-s", "tests", "-v"]),
                       ("offline-demo", ["-m", "sdv_lab", "offline"]),
                       ("pip-check", ["-m", "pip", "check"])]:
        checks.append(run(name, args))
    for callback in [static_checks, document_checks]:
        try:
            checks.append(callback())
        except Exception as exc:
            checks.append({"name": callback.__name__, "status": "FAIL", "error": str(exc)})
    checks.append({"name": "real-broker-compose-ankaios-vcan-target", "status": "NOT RUN",
                   "docker_in_path": shutil.which("docker"),
                   "note": "Local Windows validation only. No working Linux/container environment was available for this preparation. Run documented real-broker smoke and Linux labs separately."})
    (ARTIFACTS / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for item in checks:
        print(item["status"], item["name"], item.get("error", ""))
    return 1 if any(item["status"] == "FAIL" for item in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
