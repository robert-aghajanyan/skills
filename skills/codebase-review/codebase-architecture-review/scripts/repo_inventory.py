#!/usr/bin/env python3
"""Summarize repository structure for architecture review.

The script is intentionally dependency-free and read-only. It is a triage aid,
not a substitute for reading the code behind each reported signal.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


IGNORE_DIRS = {
    ".cache",
    ".git",
    ".hg",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".terraform",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}

MANIFEST_NAMES = {
    ".github/workflows",
    ".gitlab-ci.yml",
    "Cargo.toml",
    "Dockerfile",
    "Gemfile",
    "Makefile",
    "Pipfile",
    "Procfile",
    "README.md",
    "build.gradle",
    "composer.json",
    "docker-compose.yml",
    "docker-compose.yaml",
    "go.mod",
    "gradle.properties",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
    "tsconfig.json",
    "uv.lock",
}

TEXT_EXTS = {
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".graphql",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".md",
    ".mjs",
    ".php",
    ".proto",
    ".py",
    ".rb",
    ".rs",
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
}

ENTRYPOINT_NAMES = {
    "app.py",
    "cli.py",
    "index.js",
    "index.ts",
    "main.go",
    "main.py",
    "server.py",
    "wsgi.py",
}

TEST_RE = re.compile(
    r"(^|[/\\])(tests?|spec)([/\\])|(^|[/\\])test_[^/\\]*|(_test|\.test|\.spec)\.",
    re.IGNORECASE,
)
IMPORT_RES = [
    re.compile(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", re.MULTILINE),
    re.compile(r"^\s*import\s+(?:type\s+)?(?:[^'\"]+\s+from\s+)?['\"]([^'\"]+)['\"]", re.MULTILINE),
    re.compile(r"require\(['\"]([^'\"]+)['\"]\)"),
    re.compile(r"^\s*use\s+([A-Za-z_][\w:]*)", re.MULTILINE),
]
CONDITIONAL_RE = re.compile(r"\b(if|elif|else if|switch|case|match|when|guard)\b")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]+")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_ignored(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return any(part in IGNORE_DIRS for part in parts)


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        if is_ignored(current, root):
            continue
        for filename in filenames:
            path = current / filename
            if not is_ignored(path, root):
                files.append(path)
    return sorted(files)


def read_text(path: Path, max_bytes: int = 1_000_000) -> str | None:
    if path.suffix not in TEXT_EXTS and path.name not in MANIFEST_NAMES:
        return None
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data[:max_bytes].decode("utf-8", errors="replace")


def line_count(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def classify_entrypoint(path: Path, text: str | None) -> str | None:
    name = path.name
    if name in ENTRYPOINT_NAMES:
        return "name"
    if text is None:
        return None
    markers = [
        'if __name__ == "__main__"',
        "if __name__ == '__main__'",
        "FastAPI(",
        "Flask(",
        "express()",
        "createServer(",
        "argparse.",
        "click.",
        "typer.",
        "uvicorn.run(",
    ]
    if any(marker in text for marker in markers):
        return "marker"
    return None


def extract_imports(text: str | None) -> list[str]:
    if text is None:
        return []
    imports: list[str] = []
    for pattern in IMPORT_RES:
        imports.extend(match.group(1).split(".")[0].split("::")[0] for match in pattern.finditer(text))
    return [item for item in imports if item and not item.startswith(".")]


def repeated_tokens(files: list[Path], root: Path) -> list[tuple[str, int, list[str]]]:
    token_paths: dict[str, list[str]] = defaultdict(list)
    for path in files:
        relative = rel(path, root)
        for token in set(TOKEN_RE.findall(relative.replace("-", "_"))):
            lowered = token.lower()
            if len(lowered) < 4 or lowered.isdigit():
                continue
            token_paths[lowered].append(relative)

    ranked = sorted(
        ((token, len(paths), paths[:5]) for token, paths in token_paths.items() if len(paths) >= 4),
        key=lambda item: (-item[1], item[0]),
    )
    return ranked[:20]


def inventory(root: Path, top: int) -> dict[str, Any]:
    root = root.resolve()
    files = iter_files(root)
    ext_counts = Counter(path.suffix or "[none]" for path in files)
    by_dir = Counter(path.relative_to(root).parts[0] if len(path.relative_to(root).parts) > 1 else "." for path in files)

    manifest_paths: list[str] = []
    large_files: list[dict[str, Any]] = []
    condition_hotspots: list[dict[str, Any]] = []
    entrypoints: list[dict[str, str]] = []
    tests: list[str] = []
    generated: list[str] = []
    import_counts: Counter[str] = Counter()

    for path in files:
        relative = rel(path, root)
        if path.name in MANIFEST_NAMES or relative.startswith(".github/workflows/"):
            manifest_paths.append(relative)
        if TEST_RE.search(relative):
            tests.append(relative)
        if any(marker in relative.lower() for marker in ("generated", "pb2", "openapi", "swagger", "vendor")):
            generated.append(relative)

        text = read_text(path)
        if text is None:
            continue

        lines = line_count(text)
        if lines:
            large_files.append({"path": relative, "lines": lines, "bytes": path.stat().st_size})
        condition_count = len(CONDITIONAL_RE.findall(text))
        if condition_count:
            condition_hotspots.append({"path": relative, "conditionals": condition_count, "lines": lines})
        entrypoint_reason = classify_entrypoint(path, text)
        if entrypoint_reason:
            entrypoints.append({"path": relative, "reason": entrypoint_reason})
        import_counts.update(extract_imports(text))

    large_files.sort(key=lambda item: (-item["lines"], item["path"]))
    condition_hotspots.sort(key=lambda item: (-item["conditionals"], item["path"]))

    return {
        "root": str(root),
        "file_count": len(files),
        "top_level_dirs": by_dir.most_common(30),
        "extensions": ext_counts.most_common(30),
        "manifests_and_ci": sorted(manifest_paths)[:80],
        "likely_entrypoints": entrypoints[:top],
        "largest_files": large_files[:top],
        "conditional_hotspots": condition_hotspots[:top],
        "test_files": sorted(tests)[:top],
        "generated_or_vendor_hints": sorted(generated)[:top],
        "dependency_hints": import_counts.most_common(top),
        "repeated_naming_patterns": repeated_tokens(files, root),
    }


def print_markdown(data: dict[str, Any]) -> None:
    print(f"# Repository Inventory\n\nRoot: `{data['root']}`\n")
    print(f"- Files scanned: {data['file_count']}")
    print(f"- Top-level areas: {', '.join(f'{name} ({count})' for name, count in data['top_level_dirs'][:12]) or 'none'}")
    print(f"- File types: {', '.join(f'{name} ({count})' for name, count in data['extensions'][:12]) or 'none'}")

    sections = [
        ("Manifests And CI", data["manifests_and_ci"], lambda item: f"- `{item}`"),
        ("Likely Entrypoints", data["likely_entrypoints"], lambda item: f"- `{item['path']}` ({item['reason']})"),
        ("Largest Files", data["largest_files"], lambda item: f"- `{item['path']}`: {item['lines']} lines"),
        (
            "Conditional Hotspots",
            data["conditional_hotspots"],
            lambda item: f"- `{item['path']}`: {item['conditionals']} conditionals across {item['lines']} lines",
        ),
        ("Test Files", data["test_files"], lambda item: f"- `{item}`"),
        ("Generated Or Vendor Hints", data["generated_or_vendor_hints"], lambda item: f"- `{item}`"),
        ("Dependency Hints", data["dependency_hints"], lambda item: f"- `{item[0]}`: {item[1]} references"),
        (
            "Repeated Naming Patterns",
            data["repeated_naming_patterns"],
            lambda item: f"- `{item[0]}`: {item[1]} paths, examples: {', '.join(f'`{path}`' for path in item[2])}",
        ),
    ]

    for title, values, formatter in sections:
        print(f"\n## {title}\n")
        if not values:
            print("_None detected._")
            continue
        for value in values:
            print(formatter(value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize repository structure for architecture review.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root to inspect.")
    parser.add_argument("--top", type=int, default=25, help="Number of rows to show per section.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        parser.error(f"root does not exist or is not a directory: {root}")

    data = inventory(root, args.top)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_markdown(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
