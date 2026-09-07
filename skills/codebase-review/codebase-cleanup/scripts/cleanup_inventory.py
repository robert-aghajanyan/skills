#!/usr/bin/env python3
"""Read-only cleanup inventory helper for codebase-cleanup skill."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


MANIFESTS = {
    "package.json",
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "setup.py",
    "setup.cfg",
    "poetry.lock",
    "uv.lock",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "Gemfile",
    "Gemfile.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "gradle.lockfile",
    "build.sbt",
    "composer.json",
    "composer.lock",
    "mix.exs",
    "rebar.config",
    "pubspec.yaml",
    "Package.swift",
}

CI_PATTERNS = [
    ".github/workflows/*",
    ".gitlab-ci.yml",
    "Jenkinsfile",
    "azure-pipelines.yml",
    "circle.yml",
    ".circleci/config.yml",
    "buildkite.yml",
    ".buildkite/*",
]

GENERATED_NAMES = [
    "dist",
    "build",
    "coverage",
    ".coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".next",
    ".nuxt",
    ".turbo",
    "node_modules",
    "__pycache__",
    ".DS_Store",
]

ARTIFACT_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".class",
    ".o",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".log",
    ".tmp",
    ".temp",
    ".bak",
    ".orig",
    ".rej",
    ".coverage",
    ".lcov",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
}

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".kts",
    ".rb",
    ".php",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".swift",
    ".scala",
    ".sh",
}

DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}
TEST_MARKERS = ("test", "tests", "spec", "specs", "__tests__")
SCRIPT_DIR_NAMES = {"scripts", "script", "bin", "tools", "tasks"}
ENTRYPOINT_NAMES = {
    "app.py",
    "asgi.py",
    "cli.py",
    "entrypoint.py",
    "main.py",
    "manage.py",
    "server.py",
    "wsgi.py",
}
RUNTIME_PATTERNS = [
    "Dockerfile",
    "Dockerfile.*",
    "docker-compose*.yml",
    "docker-compose*.yaml",
    "compose*.yml",
    "compose*.yaml",
    "Procfile",
    "helm/**",
    "charts/**",
    "chart/**",
    "deploy/**",
    "deployment/**",
    "k8s/**",
    "kubernetes/**",
    ".github/workflows/*",
    ".gitlab-ci.yml",
]


def run_git(repo: Path, args: list[str], timeout: int = 30) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return 124, f"git {' '.join(args)} timed out after {timeout}s"
    output = proc.stdout.strip()
    if proc.returncode != 0 and proc.stderr.strip():
        output = proc.stderr.strip()
    return proc.returncode, output


def rel(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def is_match(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def has_named_part(path: str, names: set[str]) -> bool:
    return any(part.lower() in names for part in Path(path).parts)


def parse_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line.strip()]


def human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def load_git_files(repo: Path) -> tuple[list[str], list[str], list[str]]:
    code, tracked = run_git(repo, ["ls-files"])
    tracked_files = parse_lines(tracked) if code == 0 else []

    code, ignored = run_git(repo, ["ls-files", "--others", "--ignored", "--exclude-standard"])
    ignored_files = parse_lines(ignored) if code == 0 else []

    code, status = run_git(repo, ["status", "--short", "--branch"])
    status_lines = parse_lines(status) if code == 0 else [status]
    return tracked_files, ignored_files, status_lines


def collect_inventory(repo: Path) -> dict[str, object]:
    tracked, ignored, status = load_git_files(repo)
    tracked_set = set(tracked)

    manifests = sorted(path for path in tracked if Path(path).name in MANIFESTS)
    ci_files = sorted(path for path in tracked if is_match(path, CI_PATTERNS))

    source_dirs: set[str] = set()
    tests: list[str] = []
    scripts: list[str] = []
    docs: list[str] = []
    entrypoints: list[str] = []
    runtime_files: list[str] = []
    generated_like: list[str] = []
    large_files: list[tuple[str, int]] = []
    broken_symlinks: list[str] = []

    extension_counts: dict[str, int] = defaultdict(int)
    basename_map: dict[str, list[str]] = defaultdict(list)

    for path_str in tracked:
        path = repo / path_str
        parts = Path(path_str).parts
        suffix = path.suffix.lower()
        if suffix:
            extension_counts[suffix] += 1
        basename_map[Path(path_str).name].append(path_str)

        if suffix in SOURCE_EXTENSIONS and parts:
            source_dirs.add(parts[0] if len(parts) > 1 else ".")
        if any(marker in {part.lower() for part in parts} for marker in TEST_MARKERS):
            tests.append(path_str)
        if has_named_part(path_str, SCRIPT_DIR_NAMES):
            scripts.append(path_str)
        if suffix in DOC_EXTENSIONS and Path(path_str).name not in MANIFESTS:
            docs.append(path_str)
        if Path(path_str).name in ENTRYPOINT_NAMES or path_str in {"package.json", "pyproject.toml"}:
            entrypoints.append(path_str)
        if is_match(path_str, RUNTIME_PATTERNS):
            runtime_files.append(path_str)
        if any(part in GENERATED_NAMES for part in parts) or suffix in ARTIFACT_EXTENSIONS:
            generated_like.append(path_str)

        try:
            if path.is_symlink() and not path.exists():
                broken_symlinks.append(path_str)
            if path.is_file() and not path.is_symlink():
                size = path.stat().st_size
                if size >= 1024 * 1024:
                    large_files.append((path_str, size))
        except OSError:
            continue

    duplicate_basenames = {
        name: paths
        for name, paths in sorted(basename_map.items())
        if len(paths) > 1 and name not in {"__init__.py", "index.ts", "index.tsx", "index.js", "README.md"}
    }

    ignored_names = {Path(path).name for path in ignored}
    tracked_ignored_name_matches = sorted(
        path for path in generated_like if Path(path).name in ignored_names or any(part in ignored_names for part in Path(path).parts)
    )

    return {
        "repo": str(repo),
        "status": status,
        "tracked_file_count": len(tracked),
        "ignored_untracked_count": len(ignored),
        "manifests": manifests,
        "ci_files": ci_files,
        "source_roots": sorted(source_dirs),
        "test_file_count": len(tests),
        "test_examples": tests[:30],
        "script_file_count": len(scripts),
        "script_examples": scripts[:30],
        "doc_file_count": len(docs),
        "doc_examples": docs[:30],
        "entrypoint_like_files": sorted(entrypoints)[:50],
        "runtime_files": sorted(runtime_files)[:80],
        "generated_like_tracked": sorted(generated_like)[:80],
        "tracked_artifact_ignored_name_matches": tracked_ignored_name_matches[:80],
        "large_files": [(path, human_size(size)) for path, size in sorted(large_files, key=lambda item: item[1], reverse=True)[:30]],
        "broken_symlinks": sorted(broken_symlinks),
        "duplicate_basenames": dict(list(duplicate_basenames.items())[:40]),
        "top_extensions": sorted(extension_counts.items(), key=lambda item: item[1], reverse=True)[:30],
        "notes": [
            "This helper is read-only and produces leads, not deletion proof.",
            "Check dynamic/config/external usage before deleting anything.",
            "Run repo-native tests after edits.",
        ],
    }


def print_markdown(data: dict[str, object]) -> None:
    print(f"# Cleanup Inventory: {data['repo']}")
    print()
    print("## Git Status")
    for line in data["status"]:  # type: ignore[index]
        print(f"- `{line}`")
    print()
    print("## Inventory")
    print(f"- Tracked files: {data['tracked_file_count']}")
    print(f"- Ignored/untracked files: {data['ignored_untracked_count']}")
    print(f"- Test files detected: {data['test_file_count']}")
    print(f"- Script files detected: {data['script_file_count']}")
    print(f"- Doc files detected: {data['doc_file_count']}")
    print()

    for title, key in [
        ("Dependency Manifests", "manifests"),
        ("CI Files", "ci_files"),
        ("Source Roots", "source_roots"),
        ("Entrypoint-Like Files", "entrypoint_like_files"),
        ("Runtime / Deployment Files", "runtime_files"),
        ("Generated-Like Tracked Files", "generated_like_tracked"),
        ("Tracked Artifact / Ignored Name Matches", "tracked_artifact_ignored_name_matches"),
        ("Large Files", "large_files"),
        ("Broken Symlinks", "broken_symlinks"),
    ]:
        print(f"## {title}")
        values = data[key]
        if not values:
            print("- None detected")
        elif key == "large_files":
            for path, size in values:  # type: ignore[assignment]
                print(f"- `{path}` ({size})")
        else:
            for value in values:  # type: ignore[assignment]
                print(f"- `{value}`")
        print()

    print("## Duplicate Basenames")
    duplicates = data["duplicate_basenames"]
    if not duplicates:
        print("- None detected")
    else:
        for name, paths in duplicates.items():  # type: ignore[union-attr]
            joined = ", ".join(f"`{path}`" for path in paths[:8])
            suffix = " ..." if len(paths) > 8 else ""
            print(f"- `{name}`: {joined}{suffix}")
    print()

    print("## Top Extensions")
    for ext, count in data["top_extensions"]:  # type: ignore[index]
        print(f"- `{ext}`: {count}")
    print()

    print("## Notes")
    for note in data["notes"]:  # type: ignore[index]
        print(f"- {note}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize cleanup leads for a repository without modifying files.")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root to inspect")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"error: repo path does not exist or is not a directory: {repo}", file=sys.stderr)
        return 2

    code, inside = run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    if code != 0 or inside.strip() != "true":
        print(f"error: not a git worktree: {repo}", file=sys.stderr)
        return 2

    code, root = run_git(repo, ["rev-parse", "--show-toplevel"])
    if code == 0 and root:
        repo = Path(root).resolve()

    data = collect_inventory(repo)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_markdown(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
