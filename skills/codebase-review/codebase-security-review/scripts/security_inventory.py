#!/usr/bin/env python3
"""Deterministic local security inventory for a repository.

The script does not call the network and does not print raw secret values. It is
intended to reduce review blind spots, not to replace manual code review.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

SKIP_DIRS = {
    ".cache",
    ".git",
    ".hg",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}

TEXT_SUFFIXES = {
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".lock",
    ".mjs",
    ".php",
    ".properties",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".sql",
    ".swift",
    ".tf",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

MANIFEST_NAMES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-test.txt",
    "poetry.lock",
    "uv.lock",
    "Pipfile",
    "Pipfile.lock",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Gemfile",
    "Gemfile.lock",
    "composer.json",
    "composer.lock",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
}

CONFIG_HINTS = (
    ".github",
    ".env",
    "secret",
    "secrets",
    "config",
    "values",
    "terraform",
    "helm",
    "kustomization",
    "deployment",
    "workflow",
    "workflows",
    "ingress",
    "serviceaccount",
)

SENSITIVE_NAME = r"[A-Za-z0-9_.-]*(?:secret|token|password|passwd|api[_-]?key|client[_-]?secret|private[_-]?key)[A-Za-z0-9_.-]*"

SECRET_PATTERNS = [
    ("aws-access-key-id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("generic-secret-assignment", re.compile(rf"(?i)\b{SENSITIVE_NAME}\b\s*[:=]\s*['\"]?[^'\"\s]{{8,}}")),
    ("secret-name-reference", re.compile(rf"(?i)\b{SENSITIVE_NAME}\b")),
]

RISKY_PATTERNS = [
    ("shell-exec", re.compile(r"\b(shell=True|os\.system|subprocess\.(Popen|run|call)|execFile|child_process\.(exec|spawn)|childProcess\.(exec|spawn)|Runtime\.getRuntime\(\)\.exec)\b")),
    ("dynamic-code", re.compile(r"\b(eval|exec|Function|setTimeout|setInterval)\s*\(")),
    ("unsafe-yaml", re.compile(r"\byaml\.load\s*\(")),
    ("python-pickle", re.compile(r"\b(pickle|cPickle|dill)\.loads?\s*\(")),
    ("template-render", re.compile(r"\b(render_template_string|dangerouslySetInnerHTML|innerHTML\s*=)\b")),
    ("http-client", re.compile(r"\b(requests\.(get|post|put|delete)|fetch\s*\(|axios\.|http\.Get|http\.Post|urllib\.request|curl\b)\b")),
    ("file-write", re.compile(r"\b(open\s*\(|writeFile|createWriteStream|FileOutputStream|fs\.write|Path\.write_text|Path\.write_bytes)\b")),
    ("path-join", re.compile(r"\b(path\.join|filepath\.Join|os\.path\.join|Path\s*\(|resolve\s*\()\b")),
    ("sql-construction", re.compile(r"(?i)\b(select|insert|update|delete)\b.+(%s|\+|\$\{|format\(|f['\"])")),
]

ROUTE_PATTERNS = [
    ("express-route", re.compile(r"\b(app|router)\.(get|post|put|patch|delete|all)\s*\(")),
    ("fastapi-route", re.compile(r"@\w+\.(get|post|put|patch|delete|api_route)\s*\(")),
    ("flask-route", re.compile(r"@\w+\.route\s*\(")),
    ("django-url", re.compile(r"\b(path|re_path|url)\s*\(")),
    ("rails-route", re.compile(r"\b(get|post|put|patch|delete|resources)\s+['\":]")),
    ("go-handler", re.compile(r"\b(HandleFunc|Handle)\s*\(")),
    ("spring-route", re.compile(r"@(Get|Post|Put|Patch|Delete|Request)Mapping\b")),
]

AUTH_PATTERNS = [
    ("auth-check", re.compile(r"(?i)\b(authenticate|authorize|authorization|permission|hasPermission|requireAuth|login_required|current_user|principal|is_admin|role)\b")),
    ("tenant-scope", re.compile(r"(?i)\b(tenant|workspace|project|organization|organisation|account_id|org_id|workspace_id|project_id)\b")),
]


@dataclass
class Match:
    kind: str
    label: str
    path: str
    line: int
    preview: str


@dataclass
class Inventory:
    root: str
    manifests: list[str]
    config_files: list[str]
    routes: list[Match]
    auth_and_tenant_signals: list[Match]
    risky_sinks: list[Match]
    possible_secrets: list[Match]


def is_text_candidate(path: Path) -> bool:
    if path.name in MANIFEST_NAMES:
        return True
    if path.name.startswith(".env"):
        return True
    return path.suffix in TEXT_SUFFIXES


def iter_files(root: Path, max_bytes: int):
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            path = Path(current_root) / filename
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            if is_text_candidate(path):
                yield path


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def scrub_preview(line: str) -> str:
    text = line.strip()
    text = re.sub(rf"(?i)({SENSITIVE_NAME})(\s*[:=]\s*['\"]?)([^'\"\s]+)", r"\1\2<redacted>", text)
    text = re.sub(r"\bAKIA[0-9A-Z]{16}\b", "AKIA<redacted>", text)
    text = re.sub(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b", "gh_<redacted>", text)
    text = re.sub(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b", "xox<redacted>", text)
    if len(text) > 180:
        text = text[:177] + "..."
    return text


def add_matches(matches: list[Match], patterns, kind: str, root: Path, path: Path, line_no: int, line: str, limit: int) -> None:
    if len(matches) >= limit:
        return
    for label, pattern in patterns:
        if pattern.search(line):
            matches.append(Match(kind=kind, label=label, path=rel(path, root), line=line_no, preview=scrub_preview(line)))
            return


def collect(root: Path, max_bytes: int, max_matches: int) -> Inventory:
    manifests: list[str] = []
    config_files: list[str] = []
    routes: list[Match] = []
    auth_and_tenant: list[Match] = []
    risky_sinks: list[Match] = []
    possible_secrets: list[Match] = []

    for path in iter_files(root, max_bytes):
        path_rel = rel(path, root)
        lower_rel = path_rel.lower()
        if path.name in MANIFEST_NAMES or path.name.startswith("requirements"):
            manifests.append(path_rel)
        if path.name.startswith(".env") or any(hint in lower_rel for hint in CONFIG_HINTS):
            config_files.append(path_rel)

        try:
            lines = path.read_text(errors="ignore").splitlines()
        except OSError:
            continue

        for line_no, line in enumerate(lines, start=1):
            add_matches(routes, ROUTE_PATTERNS, "route", root, path, line_no, line, max_matches)
            add_matches(auth_and_tenant, AUTH_PATTERNS, "auth-or-tenant", root, path, line_no, line, max_matches)
            add_matches(risky_sinks, RISKY_PATTERNS, "risky-sink", root, path, line_no, line, max_matches)
            add_matches(possible_secrets, SECRET_PATTERNS, "possible-secret", root, path, line_no, line, max_matches)

    return Inventory(
        root=str(root),
        manifests=sorted(set(manifests)),
        config_files=sorted(set(config_files)),
        routes=routes,
        auth_and_tenant_signals=auth_and_tenant,
        risky_sinks=risky_sinks,
        possible_secrets=possible_secrets,
    )


def print_section(title: str, values: list[str]) -> None:
    print(f"\n## {title}")
    if not values:
        print("- none found")
        return
    for value in values:
        print(f"- {value}")


def print_matches(title: str, matches: list[Match]) -> None:
    print(f"\n## {title}")
    if not matches:
        print("- none found")
        return
    for match in matches:
        print(f"- {match.path}:{match.line} [{match.label}] {match.preview}")


def print_markdown(inventory: Inventory) -> None:
    print(f"# Security Inventory\n\nRoot: `{inventory.root}`")
    print_section("Dependency Manifests", inventory.manifests)
    print_section("Config And Deployment Files", inventory.config_files)
    print_matches("Route Signals", inventory.routes)
    print_matches("Auth And Tenant Signals", inventory.auth_and_tenant_signals)
    print_matches("Risky Sink Signals", inventory.risky_sinks)
    print_matches("Possible Secret Signals", inventory.possible_secrets)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect a deterministic local security inventory for a repository.")
    parser.add_argument("repo_root", help="Repository root to scan")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--max-bytes", type=int, default=1_000_000, help="Skip files larger than this many bytes")
    parser.add_argument("--max-matches", type=int, default=200, help="Maximum matches per category")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"repo root is not a directory: {root}")

    inventory = collect(root, args.max_bytes, args.max_matches)
    if args.format == "json":
        print(json.dumps(asdict(inventory), indent=2, sort_keys=True))
    else:
        print_markdown(inventory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
