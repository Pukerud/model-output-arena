#!/usr/bin/env python3
"""Record future arena runs; Python standard library only. See PLAN.md."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TESTS = ("01-car-parallax", "02-plants-vs-zombies", "03-threejs-thriller")
TOKEN_KEYS = ("input_tokens", "output_tokens", "total_tokens")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, data, exclusive=False):
    text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if exclusive:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
    else:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(text, encoding="utf-8", newline="\n")
        temporary.replace(path)


def model_dir(root, model):
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*/[a-z0-9][a-z0-9.-]*", model):
        raise ValueError("model must be provider-slug/model-slug (no traversal or absolute paths)")
    path = root / "providers" / model
    if not path.resolve().is_relative_to((root / "providers").resolve()):
        raise ValueError("model path escapes providers")
    return path


def timestamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("timestamps must be UTC ISO-8601 strings ending in Z")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def validate_usage(usage):
    if not isinstance(usage, dict):
        raise ValueError("usage must be an object")
    if set(usage) != {"coverage", "source", "reason", *TOKEN_KEYS}:
        raise ValueError("usage requires coverage, source, reason, input_tokens, output_tokens, total_tokens")
    coverage = usage["coverage"]
    if coverage not in ("complete", "partial", "unavailable"):
        raise ValueError("usage coverage must be complete, partial, or unavailable")
    for key in ("source", "reason"):
        if not isinstance(usage[key], str):
            raise ValueError(f"usage {key} must be a string")
    for key in TOKEN_KEYS:
        value = usage[key]
        if value is not None and (type(value) is not int or not 0 <= value <= 9007199254740991):
            raise ValueError(f"{key} must be a nonnegative JavaScript-safe integer or null")
    if coverage == "unavailable":
        if any(usage[key] is not None for key in TOKEN_KEYS):
            raise ValueError("unavailable usage must use null counts, not zero")
    elif not usage["source"].strip() or all(usage[key] is None for key in TOKEN_KEYS):
        raise ValueError("measured usage needs a source and at least one count")
    if coverage == "complete" and usage["total_tokens"] is None:
        raise ValueError("complete coverage requires a total_tokens count")
    if coverage != "complete" and not usage["reason"].strip():
        raise ValueError("partial/unavailable usage requires a reason")
    inp, out, total = (usage[key] for key in TOKEN_KEYS)
    if total is not None and inp is not None and out is not None and total != inp + out:
        raise ValueError("normalized total_tokens must equal input_tokens + output_tokens")
    if total is not None and any(value is not None and value > total for value in (inp, out)):
        raise ValueError("token components cannot exceed total_tokens")


def validate_artifacts(root, directory):
    for test in TESTS:
        folder = directory / test
        output = folder / "output.html"
        if not output.is_file() or not output.stat().st_size:
            raise ValueError(f"missing or empty output: {output}")
        prompt = (root / "PROMPTS" / (test + ".md")).read_bytes()
        if (folder / "prompt.md").read_bytes() != prompt:
            raise ValueError(f"prompt differs from canonical bytes: {test}")
        meta = read_json(folder / "meta.json")
        if not isinstance(meta, dict):
            raise ValueError(f"metadata must be a JSON object: {test}")
        expected = "sha256:" + hashlib.sha256(prompt).hexdigest()
        if meta.get("test_id") != test or meta.get("prompt_hash") != expected:
            raise ValueError(f"incorrect test_id or prompt_hash: {test}")
        if meta.get("provider") != directory.parent.name or meta.get("model") != directory.name:
            raise ValueError(f"metadata provider/model mismatch: {test}")


def validate_run(run, directory):
    if not isinstance(run, dict):
        raise ValueError("run metadata must be a JSON object")
    if run.get("schema_version") != 1 or run.get("scope") != "three-prompt-run":
        raise ValueError("unsupported run schema or scope")
    if run.get("provider") != directory.parent.name or run.get("model") != directory.name:
        raise ValueError("run provider/model does not match its folder")
    if run.get("test_ids") != list(TESTS) or run.get("status") != "completed":
        raise ValueError("run must be completed and cover all three tests")
    elapsed = round((timestamp(run["completed_at"]) - timestamp(run["started_at"])).total_seconds() * 1000)
    if type(run.get("duration_ms")) is not int or elapsed < 0 or run["duration_ms"] != elapsed:
        raise ValueError("duration_ms must match the nonnegative whole-run UTC interval")
    validate_usage(run["usage"])


def start(root, model):
    directory = model_dir(root, model)
    # Refuse historical folders, even if they have no run.json. No retrospective estimates.
    directory.mkdir(parents=True, exist_ok=False)
    run = {
        "schema_version": 1, "provider": directory.parent.name, "model": directory.name,
        "scope": "three-prompt-run", "test_ids": list(TESTS), "status": "running",
        "started_at": now(), "completed_at": None, "duration_ms": None, "usage": None,
    }
    write_json(directory / "run.json", run, exclusive=True)
    return directory / "run.json"


def finish(root, model, usage):
    directory = model_dir(root, model)
    path = directory / "run.json"
    run = read_json(path)
    if run.get("status") != "running":
        raise ValueError("only a started, unfinished run can be finished; no overwrites")
    validate_usage(usage)
    validate_artifacts(root, directory)
    run["completed_at"] = now()
    run["duration_ms"] = round((timestamp(run["completed_at"]) - timestamp(run["started_at"])).total_seconds() * 1000)
    run["status"] = "completed"
    run["usage"] = usage
    validate_run(run, directory)
    write_json(path, run)
    return path


def index_text(root):
    runs = {}
    for path in sorted((root / "providers").glob("*/*/run.json")):
        run = read_json(path)
        validate_run(run, path.parent)
        validate_artifacts(root, path.parent)
        runs[path.parent.relative_to(root).as_posix()] = run
    return "// Generated by scripts/run_metrics.py build; do not edit.\nwindow.ARENA_RUN_METRICS = " + json.dumps(runs, indent=2, ensure_ascii=True, allow_nan=False) + ";\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("start", help="start a NEW model's whole run").add_argument("model")
    end = sub.add_parser("finish", help="validate artifacts and finalize metrics before committing")
    end.add_argument("model")
    source = end.add_mutually_exclusive_group(required=True)
    source.add_argument("--usage", type=Path, help="normalized usage JSON; see PLAN.md")
    source.add_argument("--unavailable", help="why this harness cannot expose whole-run usage")
    sub.add_parser("build", help="regenerate the file:// compatible metrics index")
    sub.add_parser("check", help="validate future runs and detect a stale metrics index")
    args = parser.parse_args()
    try:
        if args.command == "start":
            print(start(ROOT, args.model))
        elif args.command == "finish":
            usage = read_json(args.usage) if args.usage else {
                "coverage": "unavailable", "source": "", "reason": args.unavailable,
                "input_tokens": None, "output_tokens": None, "total_tokens": None,
            }
            print(finish(ROOT, args.model, usage))
            print("Next: python scripts/run_metrics.py build")
        else:
            expected = index_text(ROOT)
            path = ROOT / "run-metrics.js"
            if args.command == "build":
                path.write_text(expected, encoding="utf-8", newline="\n")
                print(path)
            elif not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise ValueError("run-metrics.js is stale; run build and include it in your commit")
            else:
                print("Run metadata, artifacts, and metrics index verified (historical runs unchanged).")
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
