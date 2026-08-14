#!/usr/bin/env python3
"""Deterministic first-pass inventory for reliability review signals."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    "target",
    "coverage",
    ".terraform",
    "vendor",
}

TEXT_SUFFIXES = {
    ".bash",
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
    ".kts",
    ".md",
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
    ".yaml",
    ".yml",
}

SAFE_TEXT_FILENAMES = {
    ".env.example",
    ".env.sample",
    ".env.template",
    "Dockerfile",
    "Makefile",
    "Procfile",
}

SENSITIVE_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.prod",
    ".env.staging",
    ".env.development",
    ".npmrc",
    ".pypirc",
}

SECRET_NAME_RE = re.compile(
    r"(?i)(secret|token|password|passwd|credential|api[_-]?key|access[_-]?key|private[_-]?key)"
)
ASSIGNMENT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_.-]*\s*[:=]\s*)([^,\s#]+|['\"][^'\"]*['\"])")


PATTERNS = {
    "external_calls": [
        r"\brequests\.",
        r"\bhttpx\.",
        r"\baiohttp\b",
        r"\burllib\b",
        r"\bfetch\s*\(",
        r"\baxios\b",
        r"\bgot\s*\(",
        r"\bgrpc\b",
        r"\bboto3\b",
        r"\bS3Client\b",
        r"\bSQS\b",
        r"\bSNS\b",
        r"\bDynamoDB\b",
        r"\bredis\b",
        r"\bkafka\b",
        r"\bKafka\b",
    ],
    "timeouts": [
        r"\btimeout\s*[=:]",
        r"\bTimeout\b",
        r"\bWithTimeout\b",
        r"\bdeadline\b",
        r"\bDeadline\b",
        r"\bsetTimeout\s*\(",
        r"\bread_timeout\b",
        r"\bconnect_timeout\b",
    ],
    "retries": [
        r"\bretry\b",
        r"\bretries\b",
        r"\bRetry\b",
        r"\bmax_retries\b",
        r"\battempts?\b",
        r"\bbackoff\b",
        r"\btenacity\b",
        r"\bexponential\b",
    ],
    "background_jobs": [
        r"\bworker\b",
        r"\bWorker\b",
        r"\bqueue\b",
        r"\bQueue\b",
        r"\bcron\b",
        r"\bCronJob\b",
        r"\bschedule\b",
        r"\bcelery\b",
        r"\bSidekiq\b",
        r"\bBullMQ\b",
        r"\bAPScheduler\b",
    ],
    "concurrency": [
        r"\bThreadPool\b",
        r"\bProcessPool\b",
        r"\basyncio\.gather\b",
        r"\bPromise\.all\b",
        r"\bgoroutine\b",
        r"^\s*go\s+\w",
        r"\bMutex\b",
        r"\bLock\b",
        r"\bSemaphore\b",
        r"\bsynchronized\b",
    ],
    "data_writes": [
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bDELETE\b",
        r"\bUPSERT\b",
        r"\btransaction\b",
        r"\bcommit\s*\(",
        r"\bsave!\b",
        r"\bcreate!\b",
        r"\bupdate!\b",
        r"\.save\s*\(",
        r"\.insert\s*\(",
        r"\.update\s*\(",
        r"\bput_item\b",
        r"\bupdate_item\b",
    ],
    "logging_observability": [
        r"\blogger\.",
        r"\blogging\.",
        r"\blog\.",
        r"\bconsole\.",
        r"\bslog\.",
        r"\bzap\.",
        r"\bpino\b",
        r"\bwinston\b",
        r"\bmetrics?\.",
        r"\btrace\b",
        r"\bspan\b",
    ],
    "config_defaults": [
        r"\bos\.getenv\b",
        r"\benviron\.get\b",
        r"\bprocess\.env\b",
        r"\bDEFAULT_",
        r"\bdefault=",
        r"\bgetenv\s*\(",
        r"\bConfig\b",
        r"\bvalues\.yaml\b",
    ],
    "health_shutdown": [
        r"\bhealthz\b",
        r"\breadyz\b",
        r"\blivenessProbe\b",
        r"\breadinessProbe\b",
        r"\bSIGTERM\b",
        r"\bSIGINT\b",
        r"\bshutdown\b",
        r"\bgraceful\b",
        r"\bpreStop\b",
        r"\bterminationGracePeriodSeconds\b",
    ],
}


@dataclass(frozen=True)
class Match:
    category: str
    path: str
    line: int
    text: str


def is_text_candidate(path: Path) -> bool:
    if path.name in SENSITIVE_FILENAMES:
        return False
    if path.name in SAFE_TEXT_FILENAMES:
        return True
    if path.suffix in TEXT_SUFFIXES:
        return True
    return False


def iter_files(root: Path, max_file_bytes: int) -> Iterable[Path]:
    for current_root, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for filename in sorted(files):
            path = Path(current_root) / filename
            if not is_text_candidate(path):
                continue
            try:
                if max_file_bytes >= 0 and path.stat().st_size > max_file_bytes:
                    continue
            except OSError:
                continue
            yield path


def redact_line(line: str) -> str:
    def replace(match: re.Match[str]) -> str:
        prefix = match.group(1)
        if SECRET_NAME_RE.search(prefix):
            return f"{prefix}<redacted>"
        return match.group(0)

    return ASSIGNMENT_RE.sub(replace, line)


def scan(root: Path, max_file_bytes: int) -> list[Match]:
    compiled = {
        category: [re.compile(pattern) for pattern in patterns]
        for category, patterns in PATTERNS.items()
    }
    matches: list[Match] = []
    for path in iter_files(root, max_file_bytes=max_file_bytes):
        try:
            rel_path = path.relative_to(root).as_posix()
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            for category, patterns in compiled.items():
                if any(pattern.search(line) for pattern in patterns):
                    matches.append(Match(category, rel_path, line_no, redact_line(stripped)[:220]))
    return matches


def summarize(matches: list[Match], max_lines: int) -> str:
    by_category: dict[str, list[Match]] = {category: [] for category in PATTERNS}
    for match in matches:
        by_category[match.category].append(match)

    output = ["# Reliability Inventory", ""]
    output.append("| Category | Matches |")
    output.append("| --- | ---: |")
    for category in sorted(by_category):
        output.append(f"| {category} | {len(by_category[category])} |")

    for category in sorted(by_category):
        category_matches = by_category[category]
        if not category_matches:
            continue
        output.extend(["", f"## {category}", ""])
        for match in category_matches[:max_lines]:
            output.append(f"- `{match.path}:{match.line}` {match.text}")
        remaining = len(category_matches) - max_lines
        if remaining > 0:
            output.append(f"- ... {remaining} more")

    return "\n".join(output) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan a repository for reliability-review inventory signals."
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository or directory to scan.")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=25,
        help="Maximum example matches to print per category.",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=1_000_000,
        help="Skip candidate files larger than this many bytes; use -1 for no size limit.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    matches = scan(root, max_file_bytes=args.max_file_bytes)
    matches.sort(key=lambda item: (item.category, item.path, item.line, item.text))

    if args.json:
        print(json.dumps([match.__dict__ for match in matches], indent=2, sort_keys=True))
    else:
        print(summarize(matches, max(args.max_lines, 0)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
