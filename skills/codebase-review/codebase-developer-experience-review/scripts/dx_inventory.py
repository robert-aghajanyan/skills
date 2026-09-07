#!/usr/bin/env python3
"""Read-only developer-experience inventory for repository reviews."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
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
    ".tox",
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

TEXT_EXTS = {
    ".cfg",
    ".conf",
    ".ini",
    ".json",
    ".md",
    ".mdx",
    ".py",
    ".rst",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
    ".example",
    ".sample",
    ".template",
}

MANIFEST_NAMES = {
    "package.json",
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
    "bun.lockb",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-test.txt",
    "uv.lock",
    "poetry.lock",
    "Pipfile",
    "Pipfile.lock",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "Gemfile",
    "Gemfile.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "gradlew",
    "composer.json",
    "pubspec.yaml",
    "deno.json",
    "deno.jsonc",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "devcontainer.json",
    ".tool-versions",
    ".nvmrc",
    ".node-version",
    ".python-version",
    ".ruby-version",
    ".java-version",
    "mise.toml",
}

SCRIPT_DIRS = {"scripts", "bin", "tools", "dev"}
SCRIPT_EXTS = {".sh", ".bash", ".py", ".js", ".mjs", ".ts", ".rb", ".go"}
DOC_EXTS = {".md", ".mdx", ".rst", ".txt"}
ENV_EXAMPLE_RE = re.compile(r"(^|/)(\.env(?:\.[A-Za-z0-9_-]+)?\.(?:example|sample|template)|env\.example|env\.sample|.*\.env\.example)$")
ENV_ASSIGN_RE = re.compile(r"^\s*(?:export\s+)?([A-Z][A-Z0-9_]{1,})\s*=")
MAKE_TARGET_RE = re.compile(r"^([A-Za-z0-9_.-]+):(?:\s|$)")
DOC_COMMAND_RE = re.compile(
    r"\b("
    r"npm|yarn|pnpm|bun|node|npx|python|python3|pip|pipx|poetry|uv|pytest|tox|nox|"
    r"go|cargo|make|just|task|docker|docker-compose|kubectl|helm|terraform|"
    r"mvn|gradle|ruff|mypy|eslint|prettier"
    r")\b"
)
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
TEST_COMMAND_RE = re.compile(
    r"\b("
    r"test|pytest|jest|vitest|mocha|playwright|cypress|go test|cargo test|mvn test|"
    r"gradle test|tox|nox|rspec|phpunit"
    r")\b",
    re.IGNORECASE,
)
SETUP_COMMAND_RE = re.compile(
    r"\b("
    r"install|setup|bootstrap|init|quickstart|dev|start|serve|compose up|docker compose up"
    r")\b",
    re.IGNORECASE,
)
SETUP_SCRIPT_NAME_RE = re.compile(r"^(dev|start|serve|setup|bootstrap|install|init|quickstart)(:[A-Za-z0-9_.-]+)?$", re.IGNORECASE)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            try:
                relative_parts = path.relative_to(root).parts
            except ValueError:
                continue
            if any(part in IGNORE_DIRS for part in relative_parts):
                continue
            files.append(path)
    return sorted(files)


def read_text(path: Path, max_bytes: int = 1_000_000) -> str | None:
    if path.suffix.lower() not in TEXT_EXTS and path.name not in {"Makefile", "Justfile", "Taskfile"}:
        return None
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data[:max_bytes].decode("utf-8", errors="replace")


def is_manifest(path: Path) -> bool:
    if path.name in MANIFEST_NAMES:
        return True
    if path.name.startswith("requirements") and path.suffix == ".txt":
        return True
    return False


def is_ci_file(path: Path, root: Path) -> bool:
    relative = rel(path, root)
    return (
        relative.startswith(".github/workflows/")
        or relative in {".gitlab-ci.yml", ".gitlab-ci.yaml", "azure-pipelines.yml", "Jenkinsfile"}
        or relative.startswith(".circleci/")
        or relative.startswith(".buildkite/")
    )


def is_env_example(path: Path, root: Path) -> bool:
    return bool(ENV_EXAMPLE_RE.search(rel(path, root)))


def is_script_file(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return bool(parts and parts[0] in SCRIPT_DIRS and (path.suffix in SCRIPT_EXTS or os.access(path, os.X_OK)))


def parse_package_json(path: Path) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    scripts = payload.get("scripts")
    if isinstance(scripts, dict):
        return {str(key): str(value) for key, value in sorted(scripts.items())}
    return {}


def parse_make_targets(path: Path) -> list[str]:
    text = read_text(path) or ""
    targets: list[str] = []
    for line in text.splitlines():
        if line.startswith(("\t", " ", "#", ".")):
            continue
        match = MAKE_TARGET_RE.match(line)
        if not match:
            continue
        target = match.group(1)
        if "%" not in target and "/" not in target:
            targets.append(target)
    return sorted(dict.fromkeys(targets))


def parse_ci_commands(path: Path) -> list[dict[str, Any]]:
    text = read_text(path) or ""
    commands: list[dict[str, Any]] = []
    lines = text.splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        line_number = idx + 1
        stripped = line.strip()
        command = ""
        if stripped.startswith("- run:"):
            command = stripped.removeprefix("- run:").strip().strip("'\"")
        elif stripped.startswith("run:"):
            command = stripped.removeprefix("run:").strip().strip("'\"")

        if command:
            if command in {"|", ">", "|-", ">-"}:
                base_indent = len(line) - len(line.lstrip())
                idx += 1
                while idx < len(lines):
                    block_line = lines[idx]
                    block_stripped = block_line.strip()
                    block_indent = len(block_line) - len(block_line.lstrip())
                    if block_stripped and block_indent <= base_indent:
                        idx -= 1
                        break
                    if block_stripped and not block_stripped.startswith("#"):
                        commands.append({"line": idx + 1, "command": block_stripped})
                    idx += 1
            else:
                commands.append({"line": line_number, "command": command})
        idx += 1
    return commands


def parse_doc_commands(path: Path) -> list[dict[str, Any]]:
    text = read_text(path) or ""
    commands: list[dict[str, Any]] = []
    in_fence = False
    fence_lang = ""
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            fence_lang = stripped.strip("`").lower() if in_fence else ""
            continue
        candidate = stripped
        if in_fence:
            if fence_lang and fence_lang not in {"", "bash", "sh", "shell", "zsh", "console", "text"}:
                continue
            candidate = candidate.removeprefix("$ ").removeprefix("> ")
        elif candidate.startswith(("$ ", "> ")):
            candidate = candidate[2:].strip()
        else:
            for inline in INLINE_CODE_RE.findall(stripped):
                if DOC_COMMAND_RE.search(inline):
                    commands.append({"line": idx, "command": inline.strip()})
            continue
        if DOC_COMMAND_RE.search(candidate):
            commands.append({"line": idx, "command": candidate})
    return commands


def parse_env_vars(path: Path) -> list[str]:
    text = read_text(path) or ""
    names: list[str] = []
    for line in text.splitlines():
        match = ENV_ASSIGN_RE.match(line)
        if match:
            names.append(match.group(1))
    return sorted(dict.fromkeys(names))


def summarize(root: Path) -> dict[str, Any]:
    files = iter_files(root)
    manifests = [rel(path, root) for path in files if is_manifest(path)]
    script_files = [rel(path, root) for path in files if is_script_file(path, root)]
    ci_files = [path for path in files if is_ci_file(path, root)]
    docs = [path for path in files if path.suffix.lower() in DOC_EXTS]
    env_examples = [path for path in files if is_env_example(path, root)]

    package_scripts: dict[str, dict[str, str]] = {}
    for path in files:
        if path.name == "package.json":
            scripts = parse_package_json(path)
            if scripts:
                package_scripts[rel(path, root)] = scripts

    make_targets: dict[str, list[str]] = {}
    for path in files:
        if path.name in {"Makefile", "makefile", "GNUmakefile", "Justfile", "justfile", "Taskfile"} or path.name.startswith("Taskfile."):
            targets = parse_make_targets(path)
            if targets:
                make_targets[rel(path, root)] = targets

    ci_commands = {
        rel(path, root): parse_ci_commands(path)
        for path in ci_files
    }
    ci_commands = {key: value for key, value in ci_commands.items() if value}

    doc_commands: dict[str, list[dict[str, Any]]] = {}
    for path in docs:
        commands = parse_doc_commands(path)
        if commands:
            doc_commands[rel(path, root)] = commands

    env_vars = {rel(path, root): parse_env_vars(path) for path in env_examples}
    env_vars = {key: value for key, value in env_vars.items() if value}

    command_sources: list[dict[str, str]] = []
    for path, scripts in package_scripts.items():
        command_sources.extend(
            {
                "source": path,
                "name": name,
                "command": command,
                "search_text": f"{name} {command}",
                "kind": "package_script",
            }
            for name, command in scripts.items()
        )
    for path, commands in ci_commands.items():
        command_sources.extend(
            {
                "source": path,
                "name": "",
                "command": item["command"],
                "search_text": item["command"],
                "kind": "ci",
            }
            for item in commands
        )
    for path, commands in doc_commands.items():
        command_sources.extend(
            {
                "source": path,
                "name": "",
                "command": item["command"],
                "search_text": item["command"],
                "kind": "docs",
            }
            for item in commands
        )

    test_commands = [
        {"source": item["source"], "command": item["command"]}
        for item in command_sources
        if TEST_COMMAND_RE.search(item["search_text"])
    ]

    setup_commands = [
        {"source": item["source"], "command": item["command"]}
        for item in command_sources
        if (
            SETUP_SCRIPT_NAME_RE.search(item["name"])
            if item["kind"] == "package_script"
            else SETUP_COMMAND_RE.search(item["command"])
        )
    ]

    contradictions = find_possible_contradictions(manifests, doc_commands, package_scripts, make_targets, ci_commands)

    return {
        "root": root.as_posix(),
        "manifests": manifests,
        "script_files": script_files,
        "package_scripts": package_scripts,
        "make_targets": make_targets,
        "ci_files": [rel(path, root) for path in ci_files],
        "ci_commands": ci_commands,
        "doc_command_files": doc_commands,
        "env_examples": env_vars,
        "test_commands": test_commands,
        "setup_commands": setup_commands,
        "possible_contradictions": contradictions,
    }


def find_possible_contradictions(
    manifests: list[str],
    doc_commands: dict[str, list[dict[str, Any]]],
    package_scripts: dict[str, dict[str, str]],
    make_targets: dict[str, list[str]],
    ci_commands: dict[str, list[dict[str, Any]]],
) -> list[str]:
    notes: list[str] = []
    manifest_names = {Path(path).name for path in manifests}

    js_locks = sorted(name for name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb"} if name in manifest_names)
    if len(js_locks) > 1:
        notes.append(f"Multiple JavaScript lockfiles found: {', '.join(js_locks)}.")

    py_locks = sorted(name for name in {"requirements.txt", "uv.lock", "poetry.lock", "Pipfile.lock"} if name in manifest_names)
    if len(py_locks) > 1:
        notes.append(f"Multiple Python dependency entrypoints found: {', '.join(py_locks)}.")

    doc_command_text = "\n".join(item["command"] for items in doc_commands.values() for item in items)
    doc_package_managers = sorted(set(re.findall(r"\b(npm|yarn|pnpm|bun|pip|poetry|uv)\b", doc_command_text)))
    if len(doc_package_managers) > 1:
        notes.append(f"Docs mention multiple package managers: {', '.join(doc_package_managers)}.")

    if "pnpm-lock.yaml" in manifest_names and re.search(r"\bnpm install\b", doc_command_text):
        notes.append("Docs mention `npm install` while `pnpm-lock.yaml` is present.")
    if "yarn.lock" in manifest_names and re.search(r"\bnpm install\b", doc_command_text):
        notes.append("Docs mention `npm install` while `yarn.lock` is present.")
    if "uv.lock" in manifest_names and re.search(r"\bpip install\b", doc_command_text):
        notes.append("Docs mention `pip install` while `uv.lock` is present.")

    script_names = Counter(
        name
        for scripts in package_scripts.values()
        for name in scripts
        if name.lower() in {"test", "lint", "typecheck", "build", "dev", "start"}
    )
    target_names = Counter(
        target
        for targets in make_targets.values()
        for target in targets
        if target.lower() in {"test", "lint", "typecheck", "build", "dev", "start"}
    )
    overlaps = sorted(set(script_names) & set(target_names))
    if overlaps:
        notes.append(f"Package scripts and task targets overlap for: {', '.join(overlaps)}. Verify they use the same flags.")

    ci_text = "\n".join(item["command"] for items in ci_commands.values() for item in items)
    if ci_text and doc_command_text:
        for command_name in ["test", "lint", "typecheck", "build"]:
            doc_has = re.search(rf"\b{re.escape(command_name)}\b", doc_command_text, re.IGNORECASE)
            ci_has = re.search(rf"\b{re.escape(command_name)}\b", ci_text, re.IGNORECASE)
            if ci_has and not doc_has:
                notes.append(f"CI appears to run `{command_name}` but docs do not mention a matching local command.")

    return notes


def limited(items: list[Any], limit: int) -> tuple[list[Any], int]:
    return items[:limit], max(0, len(items) - limit)


def print_list(title: str, items: list[str], limit: int = 40) -> None:
    print(f"\n## {title}")
    if not items:
        print("- None found.")
        return
    shown, remaining = limited(items, limit)
    for item in shown:
        print(f"- {item}")
    if remaining:
        print(f"- ... {remaining} more")


def print_markdown(data: dict[str, Any]) -> None:
    print("# DX Inventory")
    print(f"\nRoot: `{data['root']}`")

    print_list("Manifest And Tool Files", data["manifests"])
    print_list("Script Files", data["script_files"])

    print("\n## Package Scripts")
    if not data["package_scripts"]:
        print("- None found.")
    else:
        for path, scripts in data["package_scripts"].items():
            names = ", ".join(scripts.keys())
            print(f"- `{path}`: {names}")

    print("\n## Task Targets")
    if not data["make_targets"]:
        print("- None found.")
    else:
        for path, targets in data["make_targets"].items():
            print(f"- `{path}`: {', '.join(targets)}")

    print_list("CI Workflow Files", data["ci_files"])

    print("\n## CI Commands")
    if not data["ci_commands"]:
        print("- None found.")
    else:
        for path, commands in data["ci_commands"].items():
            shown, remaining = limited(commands, 12)
            print(f"- `{path}`")
            for item in shown:
                print(f"  - line {item['line']}: `{item['command']}`")
            if remaining:
                print(f"  - ... {remaining} more")

    print("\n## Docs Commands")
    if not data["doc_command_files"]:
        print("- None found.")
    else:
        for path, commands in sorted(data["doc_command_files"].items()):
            shown, remaining = limited(commands, 8)
            print(f"- `{path}`")
            for item in shown:
                print(f"  - line {item['line']}: `{item['command']}`")
            if remaining:
                print(f"  - ... {remaining} more")

    print("\n## Env Example Variables")
    if not data["env_examples"]:
        print("- None found.")
    else:
        for path, names in data["env_examples"].items():
            print(f"- `{path}`: {', '.join(names)}")

    print("\n## Likely Test Commands")
    if not data["test_commands"]:
        print("- None found.")
    else:
        shown, remaining = limited(data["test_commands"], 30)
        for item in shown:
            print(f"- `{item['command']}` from `{item['source']}`")
        if remaining:
            print(f"- ... {remaining} more")

    print("\n## Likely Setup Or Run Commands")
    if not data["setup_commands"]:
        print("- None found.")
    else:
        shown, remaining = limited(data["setup_commands"], 30)
        for item in shown:
            print(f"- `{item['command']}` from `{item['source']}`")
        if remaining:
            print(f"- ... {remaining} more")

    print("\n## Possible Duplicate Or Contradictory Setup Paths")
    if not data["possible_contradictions"]:
        print("- None detected by heuristic checks.")
    else:
        for note in data["possible_contradictions"]:
            print(f"- {note}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".", help="Repository root to inventory.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repo root does not exist or is not a directory: {root}")

    data = summarize(root)
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_markdown(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
