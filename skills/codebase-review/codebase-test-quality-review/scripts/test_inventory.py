#!/usr/bin/env python3
"""Read-only test inventory helper for test-quality-review."""

from __future__ import annotations

import argparse
import configparser
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback.
    tomllib = None  # type: ignore[assignment]


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".codex-worktrees",
    ".worktrees",
    ".claude",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    ".cache",
    "__pycache__",
    "coverage",
    "htmlcov",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".gradle",
}

SOURCE_EXTS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".go",
    ".java",
    ".kt",
    ".kts",
    ".rb",
    ".rs",
    ".cs",
    ".php",
    ".swift",
    ".scala",
}

TEST_DIR_NAMES = {"test", "tests", "__tests__", "spec", "specs", "e2e", "integration"}
FIXTURE_DIR_NAMES = {"fixture", "fixtures", "testdata", "data", "__fixtures__"}
SNAPSHOT_DIR_NAMES = {"__snapshots__", "snapshots"}
MOCK_DIR_NAMES = {"mock", "mocks", "__mocks__", "fakes", "stubs"}


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_hidden_or_skipped(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return any(part in SKIP_DIRS for part in parts)


def is_test_file(path: Path, root: Path) -> bool:
    name = path.name
    parts = set(path.relative_to(root).parts[:-1])
    if parts & TEST_DIR_NAMES:
        return path.suffix in SOURCE_EXTS
    patterns = [
        r"^test_.*\.py$",
        r".*_test\.py$",
        r".*(_test|\.test|\.spec)\.(js|jsx|ts|tsx|mjs|cjs)$",
        r".*(_test)\.go$",
        r".*(Test|Tests|IT)\.(java|kt|kts)$",
        r".*(_spec|_test)\.rb$",
        r".*(_test)\.rs$",
        r".*(Tests|Test)\.cs$",
        r".*(Test|Spec)\.php$",
        r".*(Tests|Test)\.swift$",
        r".*(Spec|Suite)\.scala$",
    ]
    return any(re.match(pattern, name) for pattern in patterns)


def normalized_stem(path: Path) -> str:
    stem = path.stem
    for suffix in (
        ".test",
        ".spec",
        "_test",
        "_spec",
        "Test",
        "Tests",
        "IT",
    ):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    if stem.startswith("test_"):
        stem = stem[5:]
    return stem.lower().replace("-", "_")


def classify_language(ext: str) -> str:
    return {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".mjs": "JavaScript",
        ".cjs": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".go": "Go",
        ".java": "Java",
        ".kt": "Kotlin",
        ".kts": "Kotlin",
        ".rb": "Ruby",
        ".rs": "Rust",
        ".cs": "C#",
        ".php": "PHP",
        ".swift": "Swift",
        ".scala": "Scala",
    }.get(ext, ext or "unknown")


def collect_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in SKIP_DIRS and not dirname.startswith(".cache")
        ]
        if is_hidden_or_skipped(current, root):
            continue
        for filename in filenames:
            path = current / filename
            if not is_hidden_or_skipped(path, root):
                files.append(path)
    return files


def read_text(path: Path, max_bytes: int = 256_000) -> str:
    try:
        return path.read_bytes()[:max_bytes].decode("utf-8", errors="replace")
    except OSError:
        return ""


def package_json_commands(path: Path) -> dict[str, str]:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return {}
    scripts = data.get("scripts") if isinstance(data, dict) else None
    if not isinstance(scripts, dict):
        return {}
    return {
        f"npm run {name}": str(command)
        for name, command in scripts.items()
        if "test" in name.lower()
        or any(token in str(command).lower() for token in ("jest", "vitest", "playwright", "cypress", "mocha"))
    }


def parse_pyproject(path: Path) -> dict[str, Any]:
    if tomllib is None:
        return {}
    try:
        data = tomllib.loads(read_text(path))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def discover_commands(root: Path, files_by_name: dict[str, list[Path]]) -> list[dict[str, str]]:
    commands: list[dict[str, str]] = []

    for path in files_by_name.get("package.json", []):
        for command, detail in package_json_commands(path).items():
            commands.append({"source": rel(path, root), "command": command, "detail": detail})

    for path in files_by_name.get("pyproject.toml", []):
        data = parse_pyproject(path)
        tool = data.get("tool", {}) if isinstance(data, dict) else {}
        if isinstance(tool, dict):
            if "pytest" in tool or "coverage" in tool:
                commands.append({"source": rel(path, root), "command": "pytest", "detail": "pyproject.toml contains pytest/coverage config"})
            poetry = tool.get("poetry")
            if isinstance(poetry, dict) and "pytest" in json.dumps(poetry).lower():
                commands.append({"source": rel(path, root), "command": "poetry run pytest", "detail": "poetry config references pytest"})

    for filename, command in {
        "pytest.ini": "pytest",
        "tox.ini": "tox",
        "noxfile.py": "nox",
        "go.mod": "go test ./...",
        "Cargo.toml": "cargo test",
        "pom.xml": "mvn test",
        "build.gradle": "./gradlew test",
        "build.gradle.kts": "./gradlew test",
        "Gemfile": "bundle exec rspec",
        "composer.json": "composer test",
    }.items():
        for path in files_by_name.get(filename, []):
            commands.append({"source": rel(path, root), "command": command, "detail": f"detected {filename}"})

    for path in files_by_name.get("Makefile", []):
        text = read_text(path)
        targets = sorted(set(re.findall(r"^([A-Za-z0-9_.-]*test[A-Za-z0-9_.-]*):", text, re.MULTILINE)))
        for target in targets:
            commands.append({"source": rel(path, root), "command": f"make {target}", "detail": "Makefile test target"})

    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, str]] = []
    for item in commands:
        key = (item["source"], item["command"], item["detail"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def discover_coverage(root: Path, files_by_name: dict[str, list[Path]]) -> list[str]:
    names = [
        ".coveragerc",
        "coverage.xml",
        "codecov.yml",
        ".codecov.yml",
        "jest.config.js",
        "jest.config.ts",
        "vitest.config.js",
        "vitest.config.ts",
        ".nycrc",
        "nyc.config.js",
        "pytest.ini",
        "pyproject.toml",
        "tox.ini",
    ]
    hits: list[str] = []
    for name in names:
        for path in files_by_name.get(name, []):
            text = read_text(path, 64_000).lower()
            if name in {".coveragerc", "coverage.xml", "codecov.yml", ".codecov.yml", ".nycrc", "nyc.config.js"}:
                hits.append(rel(path, root))
            elif any(token in text for token in ("coverage", "cov", "collectcoverage", "coverageprovider")):
                hits.append(rel(path, root))
    return sorted(set(hits))


def discover_ci(root: Path, files: list[Path]) -> list[dict[str, str]]:
    ci_files = [
        path
        for path in files
        if path.match(".github/workflows/*")
        or path.match(".gitlab-ci.yml")
        or path.match("azure-pipelines.yml")
        or path.match("Jenkinsfile")
        or path.match(".circleci/config.yml")
        or path.match("bitbucket-pipelines.yml")
    ]
    jobs: list[dict[str, str]] = []
    for path in ci_files:
        text = read_text(path, 256_000)
        lines = [
            line.strip()
            for line in text.splitlines()
            if re.search(r"\b(test|pytest|jest|vitest|playwright|cypress|go test|cargo test|mvn test|gradlew test|rspec)\b", line, re.I)
        ]
        if lines:
            jobs.append({"file": rel(path, root), "test_related_lines": lines[:20]})
        else:
            jobs.append({"file": rel(path, root), "test_related_lines": []})
    return jobs


def count_keyword_usage(paths: list[Path], root: Path) -> dict[str, list[str]]:
    patterns = {
        "mock": r"\b(mock|patch|stub|spy|monkeypatch|MagicMock|jest\.fn|vi\.fn|sinon|Mockito)\b",
        "fixture": r"\b(fixture|fixtures|factory|FactoryBot|faker|hypothesis|testdata)\b",
        "snapshot": r"\b(snapshot|toMatchSnapshot|snapshots?)\b",
        "sleep_or_time": r"\b(sleep|setTimeout|setInterval|Date\.now|datetime\.now|time\.time|freezegun|clock|fakeTimers)\b",
        "network_or_fs": r"\b(requests\.|fetch\(|axios|httpx|urllib|fs\.|readFile|writeFile|open\(|Path\()\b",
    }
    hits: dict[str, list[str]] = {key: [] for key in patterns}
    for path in paths:
        text = read_text(path, 128_000)
        for key, pattern in patterns.items():
            if re.search(pattern, text, re.I):
                hits[key].append(rel(path, root))
    return {key: value[:50] for key, value in hits.items() if value}


def summarize(root: Path) -> dict[str, Any]:
    files = collect_files(root)
    files_by_name: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        files_by_name[path.name].append(path)

    source_files = [
        path
        for path in files
        if path.suffix in SOURCE_EXTS and not is_test_file(path, root)
    ]
    test_files = [
        path
        for path in files
        if path.suffix in SOURCE_EXTS and is_test_file(path, root)
    ]

    language_counts = Counter(classify_language(path.suffix) for path in source_files + test_files)
    test_dir_counts = Counter(
        rel(path.parent, root).split("/")[0] if "/" in rel(path.parent, root) else rel(path.parent, root)
        for path in test_files
    )
    source_dir_counts = Counter(
        rel(path.parent, root).split("/")[0] if "/" in rel(path.parent, root) else rel(path.parent, root)
        for path in source_files
    )

    test_stems = {normalized_stem(path) for path in test_files}
    likely_untested = [
        path
        for path in source_files
        if normalized_stem(path) not in test_stems
        and path.name not in {"__init__.py", "index.ts", "index.js", "main.py"}
    ]

    fixture_dirs = sorted(
        {
            rel(path, root)
            for path in files
            if any(part in FIXTURE_DIR_NAMES for part in path.relative_to(root).parts[:-1])
        }
    )
    snapshot_files = sorted(
        {
            rel(path, root)
            for path in files
            if any(part in SNAPSHOT_DIR_NAMES for part in path.relative_to(root).parts)
            or path.suffix in {".snap"}
        }
    )
    mock_dirs = sorted(
        {
            rel(path, root)
            for path in files
            if any(part in MOCK_DIR_NAMES for part in path.relative_to(root).parts[:-1])
        }
    )

    return {
        "root": str(root),
        "languages": dict(language_counts.most_common()),
        "counts": {
            "source_files": len(source_files),
            "test_files": len(test_files),
            "fixture_or_testdata_files": len(fixture_dirs),
            "snapshot_files": len(snapshot_files),
            "mock_or_fake_files": len(mock_dirs),
        },
        "source_directories": dict(source_dir_counts.most_common(20)),
        "test_directories": dict(test_dir_counts.most_common(20)),
        "test_commands": discover_commands(root, files_by_name),
        "coverage_config": discover_coverage(root, files_by_name),
        "ci_test_jobs": discover_ci(root, files),
        "likely_untested_modules": [rel(path, root) for path in likely_untested[:100]],
        "fixture_files_sample": fixture_dirs[:50],
        "snapshot_files_sample": snapshot_files[:50],
        "mock_or_fake_files_sample": mock_dirs[:50],
        "test_keyword_usage": count_keyword_usage(test_files, root),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [f"# Test Inventory: {summary['root']}", ""]
    lines.append("## Counts")
    for key, value in summary["counts"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    for title, key in (
        ("Languages", "languages"),
        ("Source Directories", "source_directories"),
        ("Test Directories", "test_directories"),
    ):
        lines.append(f"## {title}")
        data = summary.get(key) or {}
        if data:
            for name, count in data.items():
                lines.append(f"- {name}: {count}")
        else:
            lines.append("- none detected")
        lines.append("")

    lines.append("## Test Commands")
    commands = summary.get("test_commands") or []
    if commands:
        for command in commands:
            lines.append(f"- `{command['command']}` from `{command['source']}` - {command['detail']}")
    else:
        lines.append("- none detected")
    lines.append("")

    lines.append("## Coverage Config")
    coverage = summary.get("coverage_config") or []
    if coverage:
        for path in coverage:
            lines.append(f"- `{path}`")
    else:
        lines.append("- none detected")
    lines.append("")

    lines.append("## CI Test Jobs")
    ci_jobs = summary.get("ci_test_jobs") or []
    if ci_jobs:
        for job in ci_jobs:
            lines.append(f"- `{job['file']}`")
            for item in job.get("test_related_lines", [])[:5]:
                lines.append(f"  - {item}")
    else:
        lines.append("- none detected")
    lines.append("")

    for title, key in (
        ("Likely Untested Modules", "likely_untested_modules"),
        ("Fixture Files Sample", "fixture_files_sample"),
        ("Snapshot Files Sample", "snapshot_files_sample"),
        ("Mock Or Fake Files Sample", "mock_or_fake_files_sample"),
    ):
        lines.append(f"## {title}")
        data = summary.get(key) or []
        if data:
            for path in data[:30]:
                lines.append(f"- `{path}`")
        else:
            lines.append("- none detected")
        lines.append("")

    lines.append("## Test Keyword Usage")
    usage = summary.get("test_keyword_usage") or {}
    if usage:
        for key, paths in usage.items():
            lines.append(f"- {key}: {len(paths)} files, sample: {', '.join(f'`{path}`' for path in paths[:8])}")
    else:
        lines.append("- none detected")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a repository's test inventory without modifying files.")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args()

    root = Path(args.repo).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"repo must be an existing directory: {root}")

    summary = summarize(root)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_markdown(summary), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
