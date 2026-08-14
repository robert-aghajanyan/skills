#!/usr/bin/env python3
"""Read-only documentation inventory for codebase documentation reviews."""

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

DOC_EXTS = {".adoc", ".md", ".mdx", ".rst", ".txt"}
TEXT_EXTS = DOC_EXTS | {
    ".bash",
    ".cfg",
    ".conf",
    ".css",
    ".env",
    ".go",
    ".graphql",
    ".html",
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
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".xml",
    ".yaml",
    ".yml",
}

DOC_NAME_RE = re.compile(
    r"(readme|runbook|incident|troubleshoot|troubleshooting|setup|install|quickstart|"
    r"architecture|design|api|openapi|swagger|graphql|example|tutorial|how-?to|"
    r"deploy|deployment|release|changelog|migration|\boperations?\b|operational[-_ ]docs?|oncall|support|"
    r"environment|configuration|config|diagram)",
    re.IGNORECASE,
)
RUNBOOK_RE = re.compile(r"(runbook|incident|troubleshoot|rollback|recovery|oncall|\bops\b|\boperations?\b)", re.IGNORECASE)
DIAGRAM_RE = re.compile(r"```(?:mermaid|plantuml|puml)|!\[[^\]]*]\(([^)]+)\)|\.(?:mmd|mermaid|drawio|puml|plantuml|svg|png|jpg|jpeg)\b", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+]\(([^)]+)\)|https?://[^\s)>\"]+")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
ENV_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
PATH_RE = re.compile(
    r"(?:(?:\.{1,2}/|[A-Za-z0-9_.-]+/)[A-Za-z0-9_./@+=:-]+|"
    r"[A-Za-z0-9_.-]+\.(?:graphql|proto|json|yaml|toml|java|mdx|jsx|tsx|rst|txt|yml|sql|php|md|py|js|ts|sh|go|rs|rb))"
)
API_RE = re.compile(
    r"\b(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/[A-Za-z0-9_./{}:?-]*)|"
    r"\bcurl\b|https?://[^\s)>\"]+|"
    r"\b(?:query|mutation|subscription)\s+[A-Za-z0-9_]+",
    re.IGNORECASE,
)
FENCE_RE = re.compile(r"^```([A-Za-z0-9_-]*)\s*$")
PROMPT_RE = re.compile(r"^\s*(?:[$>]|\w+@\S+[:$])\s+(.+)$")
COMMENT_RE = re.compile(r"^\s*(#|//|/\*|\*|<!--|--)\s?")
MAKE_TARGET_RE = re.compile(r"^([A-Za-z0-9_.-]+):(?:\s|$)")
SPECIAL_TEXT_NAMES = {"Dockerfile", "Makefile", "Procfile"}
COMMON_ENV_NAMES = {
    "CI",
    "DEBUG",
    "ENV",
    "HOME",
    "HOST",
    "PATH",
    "PORT",
    "PWD",
    "SHELL",
    "TERM",
    "TZ",
    "USER",
}
ENV_PREFIXES = (
    "ANTHROPIC_",
    "AWS_",
    "AZURE_",
    "CODEX_",
    "DATADOG_",
    "DD_",
    "GCP_",
    "GITHUB_",
    "GOOGLE_",
    "KAFKA_",
    "MYSQL_",
    "NODE_",
    "OPENAI_",
    "POSTGRES_",
    "PYTHON_",
    "REDIS_",
    "S3_",
)
ENV_SUFFIXES = (
    "_DEBUG",
    "_DIR",
    "_ENV",
    "_FILE",
    "_HOST",
    "_ID",
    "_KEY",
    "_MODE",
    "_NAME",
    "_PASSWORD",
    "_PATH",
    "_PORT",
    "_PROFILE",
    "_REGION",
    "_SECRET",
    "_TIMEOUT",
    "_TOKEN",
    "_URI",
    "_URL",
    "_USER",
    "_USERNAME",
)
PATH_PREFIXES = (
    "./",
    "../",
    "/",
    "~",
    ".github/",
    "app/",
    "bin/",
    "charts/",
    "cmd/",
    "config/",
    "configs/",
    "database/",
    "db/",
    "deploy/",
    "deployment/",
    "deployments/",
    "doc/",
    "docs/",
    "docker/",
    "example/",
    "examples/",
    "helm/",
    "infra/",
    "infrastructure/",
    "internal/",
    "k8s/",
    "lib/",
    "migrations/",
    "packages/",
    "pkg/",
    "scripts/",
    "services/",
    "src/",
    "terraform/",
    "test/",
    "tests/",
)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            if any(part in IGNORE_DIRS for part in path.relative_to(root).parts):
                continue
            files.append(path)
    return sorted(files)


def is_special_text_file(path: Path) -> bool:
    if path.name in SPECIAL_TEXT_NAMES:
        return True
    if is_env_template(path):
        return True
    return not path.suffix and bool(DOC_NAME_RE.search(path.name))


def is_env_template(path: Path) -> bool:
    return bool(re.match(r"^\.env(?:[._-][A-Za-z0-9_-]+)*[._-](?:example|sample|template|dist)$", path.name))


def read_text(path: Path, max_bytes: int = 1_000_000) -> str | None:
    if path.suffix.lower() not in TEXT_EXTS and not is_special_text_file(path):
        return None
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data[:max_bytes].decode("utf-8", errors="replace")


def is_doc_file(path: Path, root: Path) -> bool:
    relative = rel(path, root)
    lowered = relative.lower()
    if path.suffix.lower() in DOC_EXTS:
        return True
    if is_env_template(path):
        return True
    if lowered.startswith(("docs/", "doc/", ".github/")) and DOC_NAME_RE.search(path.name):
        return True
    if path.suffix.lower() in TEXT_EXTS or is_special_text_file(path):
        return bool(DOC_NAME_RE.search(relative))
    return False


def classify_doc(path: Path, root: Path, text: str) -> list[str]:
    relative = rel(path, root).lower()
    name = path.name.lower()
    title_text = "\n".join(text.splitlines()[:20]).lower()
    joined = " ".join([relative, name, title_text])
    labels: list[str] = []
    patterns = [
        ("readme", r"readme"),
        ("setup", r"setup|install|quickstart|getting started|development"),
        ("api", r"\bapi\b|openapi|swagger|graphql|protobuf|sdk|webhook"),
        ("runbook", r"runbook|incident|troubleshoot|rollback|recovery|oncall"),
        ("architecture", r"architecture|design|diagram|adr|decision"),
        ("examples", r"example|tutorial|sample|how-?to"),
        ("ci-deploy", r"ci|workflow|deploy|deployment|release"),
        ("config", r"config|configuration|environment|env"),
        ("changelog", r"changelog|release notes|migration"),
    ]
    for label, pattern in patterns:
        if re.search(pattern, joined, re.IGNORECASE):
            labels.append(label)
    return labels or ["docs"]


def line_item(path: Path, root: Path, line_no: int, value: str) -> dict[str, Any]:
    return {"file": rel(path, root), "line": line_no, "value": value.strip()}


def dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[Any, Any, Any]] = set()
    for item in items:
        key = (item.get("file"), item.get("line"), item.get("value"))
        if key in seen:
            continue
        deduped.append(item)
        seen.add(key)
    return deduped


def is_probable_env_var(value: str) -> bool:
    if value in COMMON_ENV_NAMES:
        return True
    if "_" in value:
        return True
    return value.startswith(ENV_PREFIXES) or value.endswith(ENV_SUFFIXES)


def is_probable_path(value: str) -> bool:
    lowered = value.lower()
    if lowered.startswith(PATH_PREFIXES):
        return True
    return bool(re.search(r"\.[a-z0-9]{1,10}(?:$|[?#:/])", lowered))


def extract_commands(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    in_fence = False
    fence_lang = ""
    command_langs = {"bash", "console", "shell", "sh", "terminal", "zsh"}
    for idx, line in enumerate(text.splitlines(), start=1):
        fence = FENCE_RE.match(line.strip())
        if fence:
            if in_fence:
                in_fence = False
                fence_lang = ""
            else:
                in_fence = True
                fence_lang = fence.group(1).lower()
            continue
        if in_fence and fence_lang in command_langs and line.strip() and not line.lstrip().startswith("#"):
            value = PROMPT_RE.sub(r"\1", line).strip()
            if value and not value.startswith(("output", "...")):
                commands.append(line_item(path, root, idx, value))
            continue
        match = PROMPT_RE.match(line)
        if match:
            commands.append(line_item(path, root, idx, match.group(1)))
    return commands


def extract_inline_values(path: Path, root: Path, text: str, pattern: re.Pattern[str]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for idx, line in enumerate(text.splitlines(), start=1):
        for match in pattern.finditer(line):
            value = match.group(0)
            key = (idx, value)
            if key not in seen:
                values.append(line_item(path, root, idx, value))
                seen.add(key)
    return values


def extract_env_values(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for idx, line in enumerate(text.splitlines(), start=1):
        for match in ENV_RE.finditer(line):
            value = match.group(0)
            if not is_probable_env_var(value):
                continue
            key = (idx, value)
            if key not in seen:
                values.append(line_item(path, root, idx, value))
                seen.add(key)
    return values


def extract_path_values(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for idx, line in enumerate(text.splitlines(), start=1):
        for match in PATH_RE.finditer(line):
            value = match.group(0)
            if not is_probable_path(value):
                continue
            key = (idx, value)
            if key not in seen:
                values.append(line_item(path, root, idx, value))
                seen.add(key)
    return values


def extract_links(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for idx, line in enumerate(text.splitlines(), start=1):
        for match in LINK_RE.finditer(line):
            value = match.group(1) if match.group(1) is not None else match.group(0)
            key = (idx, value)
            if key not in seen:
                links.append(line_item(path, root, idx, value))
                seen.add(key)
    return links


def extract_inline_code(path: Path, root: Path, text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    env_vars: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for code in INLINE_CODE_RE.findall(line):
            for env in ENV_RE.findall(code):
                if is_probable_env_var(env):
                    env_vars.append(line_item(path, root, idx, env))
            for found in PATH_RE.findall(code):
                if is_probable_path(found):
                    paths.append(line_item(path, root, idx, found))
    return env_vars, paths


def discover_repo_scripts(root: Path, files: list[Path]) -> dict[str, Any]:
    scripts: dict[str, Any] = {"package_json": [], "make_targets": [], "script_files": []}
    for path in files:
        relative = rel(path, root)
        if path.name == "package.json":
            text = read_text(path)
            if text:
                try:
                    data = json.loads(text)
                    for name, command in sorted(data.get("scripts", {}).items()):
                        scripts["package_json"].append({"file": relative, "name": name, "command": command})
                except json.JSONDecodeError:
                    scripts["package_json"].append({"file": relative, "error": "invalid json"})
        elif path.name == "Makefile":
            text = read_text(path)
            if text:
                for idx, line in enumerate(text.splitlines(), start=1):
                    match = MAKE_TARGET_RE.match(line)
                    if match and not match.group(1).startswith("."):
                        scripts["make_targets"].append({"file": relative, "line": idx, "target": match.group(1)})
        elif "scripts/" in relative or relative.startswith(("bin/", "scripts/")):
            if path.suffix.lower() in {".bash", ".js", ".mjs", ".py", ".rb", ".sh", ".ts"} or os.access(path, os.X_OK):
                scripts["script_files"].append(relative)
    return scripts


def discover_doc_comments(root: Path, files: list[Path], limit: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for path in files:
        if path.suffix.lower() not in TEXT_EXTS - DOC_EXTS:
            continue
        text = read_text(path, max_bytes=120_000)
        if not text:
            continue
        lines = text.splitlines()[:120]
        comment_lines = [idx for idx, line in enumerate(lines, start=1) if COMMENT_RE.match(line)]
        if len(comment_lines) >= 8:
            candidates.append(
                {
                    "file": rel(path, root),
                    "comment_lines_in_first_120": len(comment_lines),
                    "first_comment_line": comment_lines[0],
                }
            )
    return sorted(candidates, key=lambda item: (-item["comment_lines_in_first_120"], item["file"]))[:limit]


def cap(items: list[Any], limit: int) -> list[Any]:
    return items[:limit]


def inventory(root: Path, limit: int) -> dict[str, Any]:
    root = root.resolve()
    files = iter_files(root)
    docs: list[dict[str, Any]] = []
    commands: list[dict[str, Any]] = []
    referenced_paths: list[dict[str, Any]] = []
    env_vars: list[dict[str, Any]] = []
    api_examples: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    diagrams: list[dict[str, Any]] = []
    runbooks: list[str] = []

    for path in files:
        text = read_text(path)
        if text is None:
            continue
        if not is_doc_file(path, root):
            continue

        relative = rel(path, root)
        labels = classify_doc(path, root, text)
        docs.append({"file": relative, "labels": labels, "lines": text.count("\n") + (0 if text.endswith("\n") else 1)})
        if RUNBOOK_RE.search(relative) or "runbook" in labels:
            runbooks.append(relative)

        commands.extend(extract_commands(path, root, text))
        inline_env, inline_paths = extract_inline_code(path, root, text)
        env_vars.extend(inline_env)
        referenced_paths.extend(inline_paths)
        referenced_paths.extend(extract_path_values(path, root, text))
        env_vars.extend(extract_env_values(path, root, text))
        api_examples.extend(extract_inline_values(path, root, text, API_RE))
        links.extend(extract_links(path, root, text))
        diagrams.extend(extract_inline_values(path, root, text, DIAGRAM_RE))

    label_counts = Counter(label for doc in docs for label in doc["labels"])
    return {
        "root": str(root),
        "doc_count": len(docs),
        "doc_labels": dict(sorted(label_counts.items())),
        "docs": cap(docs, limit),
        "commands_in_docs": cap(dedupe_items(commands), limit),
        "referenced_paths": cap(dedupe_items(referenced_paths), limit),
        "env_vars": cap(dedupe_items(env_vars), limit),
        "api_examples": cap(dedupe_items(api_examples), limit),
        "repo_scripts": discover_repo_scripts(root, files),
        "runbooks": cap(sorted(set(runbooks)), limit),
        "diagrams": cap(dedupe_items(diagrams), limit),
        "links": cap(dedupe_items(links), limit),
        "doc_comment_candidates": discover_doc_comments(root, files, min(limit, 50)),
    }


def print_section(title: str, items: Any, limit: int) -> None:
    print(f"\n## {title}")
    if not items:
        print("(none found)")
        return
    if isinstance(items, dict):
        for key, value in items.items():
            print(f"- {key}: {value}")
        return
    for item in items[:limit]:
        if isinstance(item, dict) and {"file", "line", "value"} <= set(item):
            print(f"- {item['file']}:{item['line']} {item['value']}")
        else:
            print(f"- {item}")


def print_text_report(data: dict[str, Any], limit: int) -> None:
    print(f"# Documentation Inventory: {data['root']}")
    print(f"Docs found: {data['doc_count']}")
    print_section("Doc Labels", data["doc_labels"], limit)
    print_section("Docs", data["docs"], limit)
    print_section("Commands In Docs", data["commands_in_docs"], limit)
    print_section("Referenced Paths", data["referenced_paths"], limit)
    print_section("Environment Variables", data["env_vars"], limit)
    print_section("API Examples", data["api_examples"], limit)
    print_section("Repo Scripts", data["repo_scripts"], limit)
    print_section("Runbooks", data["runbooks"], limit)
    print_section("Diagrams", data["diagrams"], limit)
    print_section("Links", data["links"], limit)
    print_section("Doc Comment Candidates", data["doc_comment_candidates"], limit)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize documentation signals in a repository.")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root to inventory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a text report.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum items per section.")
    args = parser.parse_args()

    root = Path(args.repo)
    if not root.exists() or not root.is_dir():
        parser.error(f"repo does not exist or is not a directory: {root}")

    data = inventory(root, max(args.limit, 1))
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_text_report(data, max(args.limit, 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
