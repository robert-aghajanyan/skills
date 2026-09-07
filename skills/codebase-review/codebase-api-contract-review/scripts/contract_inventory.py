#!/usr/bin/env python3
"""Inventory likely public contracts in a repository.

The script is dependency-free and read-only. It is a triage aid for API
contract review, not a substitute for reading the code behind each signal.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


IGNORE_DIRS = {
    ".cache",
    ".codex-worktrees",
    ".git",
    ".hg",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".terraform",
    ".venv",
    ".worktrees",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}

TEXT_EXTS = {
    ".avdl",
    ".avsc",
    ".cfg",
    ".conf",
    ".cs",
    ".env",
    ".go",
    ".graphql",
    ".hcl",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".proto",
    ".py",
    ".rb",
    ".rs",
    ".rst",
    ".scala",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
    ".md",
    ".mdx",
}

TEXT_NAMES = {
    ".env",
    "Dockerfile",
    "Makefile",
    "Procfile",
}

SPEC_NAME_RE = re.compile(
    r"(openapi|swagger|asyncapi|graphql|schema|schemas|proto|avro|jsonschema)",
    re.IGNORECASE,
)
MIGRATION_RE = re.compile(r"(^|/)(migrations?|schema_migrations?|alembic|db/migrate)(/|$)", re.IGNORECASE)
GENERATED_RE = re.compile(r"(^|/)(generated|gen|api-client|client|openapi|swagger)(/|$)", re.IGNORECASE)
CONFIG_RE = re.compile(
    r"(^|/)(config|configs|settings|helm|charts|terraform|deploy|deployment|k8s|kubernetes|\.github/workflows)(/|$)|"
    r"(^|/)(\.env(\..*)?|docker-compose\.ya?ml|values\.ya?ml|config\.(json|ya?ml|toml)|settings\.(py|json|ya?ml|toml))$",
    re.IGNORECASE,
)
EVENT_FILE_RE = re.compile(r"(event|events|message|messages|topic|topics|queue|queues|kafka|pubsub|consumer|producer)", re.IGNORECASE)


@dataclass(frozen=True)
class Signal:
    category: str
    path: str
    line: int | None
    kind: str
    value: str


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if any(part in IGNORE_DIRS for part in path.relative_to(root).parts):
                continue
            yield path


def read_text(path: Path, max_bytes: int = 1_000_000) -> str | None:
    if path.name not in TEXT_NAMES and path.suffix not in TEXT_EXTS and not SPEC_NAME_RE.search(path.name):
        return None
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data[:max_bytes].decode("utf-8", errors="replace")


def add(signals: list[Signal], category: str, path: str, line: int | None, kind: str, value: str) -> None:
    compact = " ".join(value.strip().split())
    if compact:
        signals.append(Signal(category, path, line, kind, compact[:240]))


def line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def kind_applies(kind: str, path: Path) -> bool:
    suffix = path.suffix.lower()
    if kind in {"python_route", "argparse_flag", "click_option", "python_all", "python_entry_point"}:
        return suffix == ".py"
    if kind in {"js_route", "commander_option", "ts_export", "env_var_bracket"}:
        return suffix in {".js", ".jsx", ".mjs", ".ts", ".tsx"}
    if kind == "go_export":
        return suffix == ".go"
    if kind == "spring_route":
        return suffix in {".java", ".kt", ".scala"}
    return True


def scan_file(path: Path, root: Path) -> list[Signal]:
    relative = rel(path, root)
    text = read_text(path)
    signals: list[Signal] = []
    lower = relative.lower()

    if SPEC_NAME_RE.search(path.name) or path.suffix in {".graphql", ".proto", ".avsc", ".avdl"}:
        add(signals, "schemas_and_specs", relative, None, "file", relative)
    if MIGRATION_RE.search(relative):
        add(signals, "migrations", relative, None, "file", relative)
    if GENERATED_RE.search(relative):
        add(signals, "generated_clients", relative, None, "file", relative)
    if CONFIG_RE.search(relative):
        add(signals, "config", relative, None, "file", relative)
    if EVENT_FILE_RE.search(relative):
        add(signals, "events_and_messages", relative, None, "file", relative)
    if path.name in {"package.json", "pyproject.toml", "setup.cfg", "setup.py", "Cargo.toml", "go.mod"}:
        add(signals, "manifests", relative, None, "file", relative)

    if text is None:
        return signals

    patterns: list[tuple[str, str, re.Pattern[str]]] = [
        (
            "routes",
            "python_route",
            re.compile(r"@\w+\.(?:route|get|post|put|patch|delete|options|head)\(\s*['\"]([^'\"]+)['\"]"),
        ),
        (
            "routes",
            "js_route",
            re.compile(r"\b(?:app|router|server)\.(?:get|post|put|patch|delete|options|head)\(\s*['`]([^'`]+)['`]"),
        ),
        (
            "routes",
            "spring_route",
            re.compile(r"@(Get|Post|Put|Patch|Delete|Request)Mapping\(\s*(?:value\s*=\s*)?['\"]([^'\"]+)['\"]"),
        ),
        (
            "cli",
            "argparse_flag",
            re.compile(r"\.add_argument\(\s*['\"](--?[A-Za-z0-9][^'\"]*)['\"]"),
        ),
        (
            "cli",
            "click_option",
            re.compile(r"@(?:click|typer)\.(?:option|argument)\(\s*['\"]([^'\"]+)['\"]"),
        ),
        (
            "cli",
            "commander_option",
            re.compile(r"\.(?:option|requiredOption)\(\s*['\"]([^'\"]+)['\"]"),
        ),
        (
            "cli",
            "cobra_command",
            re.compile(r"\bUse:\s*['\"]([^'\"]+)['\"]"),
        ),
        (
            "config",
            "env_var",
            re.compile(r"\b(?:process\.env\.|os\.getenv\(\s*['\"]?|getenv\(\s*['\"]?|env\(\s*['\"]?)([A-Z][A-Z0-9_]{2,})"),
        ),
        (
            "config",
            "env_var_bracket",
            re.compile(r"\bprocess\.env\[\s*['\"]([A-Z][A-Z0-9_]{2,})['\"]\s*\]"),
        ),
        (
            "events_and_messages",
            "topic_or_queue",
            re.compile(r"\b(?:topic|queue|subject|routing[_-]?key|event[_-]?name)\b\s*[:=]\s*['\"]([^'\"]+)['\"]", re.IGNORECASE),
        ),
        (
            "exports",
            "python_all",
            re.compile(r"__all__\s*=\s*\[([^\]]+)\]", re.DOTALL),
        ),
        (
            "exports",
            "ts_export",
            re.compile(r"^\s*export\s+(?:default\s+)?(?:class|function|const|interface|type|enum)\s+([A-Za-z_$][\w$]*)", re.MULTILINE),
        ),
        (
            "exports",
            "go_export",
            re.compile(r"^\s*(?:func|type|const|var)\s+([A-Z][A-Za-z0-9_]*)", re.MULTILINE),
        ),
        (
            "plugin_hooks",
            "python_entry_point",
            re.compile(r"\bentry_points\b|\bpluggy\b|@hookimpl|@hookspec"),
        ),
        (
            "plugin_hooks",
            "plugin_manifest",
            re.compile(r"\b(plugin|extension|hook|capability|activationEvents)\b", re.IGNORECASE),
        ),
    ]

    for category, kind, pattern in patterns:
        if not kind_applies(kind, path):
            continue
        for match in pattern.finditer(text):
            value = match.group(2) if kind == "spring_route" and match.lastindex and match.lastindex >= 2 else match.group(1) if match.lastindex else match.group(0)
            add(signals, category, relative, line_no(text, match.start()), kind, value)

    if path.name == "package.json":
        for key in ("main", "module", "types", "bin", "exports"):
            if re.search(rf'"{key}"\s*:', text):
                add(signals, "exports", relative, None, f"package_{key}", key)

    if lower.endswith((".md", ".mdx", ".rst")):
        for marker in ("curl ", "http://", "https://", "--", ".env", "OPENAPI", "GraphQL"):
            if marker in text:
                add(signals, "documented_examples", relative, None, "doc_marker", marker)

    return signals


def inventory(root: Path, limit: int) -> dict[str, list[dict[str, object]]]:
    root = root.resolve()
    by_category: dict[str, list[Signal]] = defaultdict(list)
    for path in sorted(iter_files(root)):
        for signal in scan_file(path, root):
            by_category[signal.category].append(signal)

    result: dict[str, list[dict[str, object]]] = {}
    for category, signals in sorted(by_category.items()):
        seen: set[tuple[str, int | None, str, str]] = set()
        unique: list[Signal] = []
        for signal in signals:
            key = (signal.path, signal.line, signal.kind, signal.value)
            if key in seen:
                continue
            seen.add(key)
            unique.append(signal)
        result[category] = [asdict(signal) for signal in unique[:limit]]
    return result


def print_markdown(data: dict[str, list[dict[str, object]]]) -> None:
    print("# Contract Inventory")
    if not data:
        print("\nNo likely contract surfaces found.")
        return
    for category, signals in data.items():
        print(f"\n## {category.replace('_', ' ').title()}")
        for signal in signals:
            location = signal["path"]
            if signal["line"]:
                location = f"{location}:{signal['line']}"
            print(f"- `{location}` [{signal['kind']}] {signal['value']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", help="Repository root to scan")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--limit", type=int, default=80, help="Maximum signals per category")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root)
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"repo_root is not a directory: {root}")
    data = inventory(root, args.limit)
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_markdown(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
