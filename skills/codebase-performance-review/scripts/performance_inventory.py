#!/usr/bin/env python3
"""Read-only first-pass inventory for performance review signals."""

from __future__ import annotations

import argparse
import json
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
    ".next",
    ".turbo",
    "coverage",
    "dist",
    "build",
    "target",
    "vendor",
    ".terraform",
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

PATTERNS: dict[str, list[str]] = {
    "entrypoints": [
        r"@\w*route\b",
        r"\bapp\.(get|post|put|patch|delete)\s*\(",
        r"\brouter\.(get|post|put|patch|delete)\s*\(",
        r"\bFastAPI\s*\(",
        r"\bAPIRouter\s*\(",
        r"\bdef\s+main\s*\(",
        r"\bif\s+__name__\s*==\s*['\"]__main__['\"]",
        r"\bclick\.command\b",
        r"\btyper\.Typer\b",
        r"\bargparse\.ArgumentParser\b",
        r"\bcommander\.",
        r"\bprogram\.command\s*\(",
        r"\bfunc\s+main\s*\(",
        r"\bCronJob\b",
        r"\bworker\b",
        r"\bqueue\b",
        r"\bconsumer\b",
        r"\bschedule\b",
    ],
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
        r"\bDynamoDB\b",
        r"\bredis\b",
        r"\bkafka\b",
        r"\bOpenAI\b",
        r"\bAnthropic\b",
    ],
    "database_access": [
        r"\bSELECT\b",
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bDELETE\b",
        r"\bJOIN\b",
        r"\bfind_many\b",
        r"\bfindMany\b",
        r"\bfindAll\b",
        r"\bfind_one\b",
        r"\bquery\s*\(",
        r"\bexecute\s*\(",
        r"\bsession\.",
        r"\bobjects\.",
        r"\bprisma\.",
        r"\bsequelize\.",
        r"\bmongoose\.",
        r"\bdb\.",
    ],
    "loops": [
        r"^\s*for\s+",
        r"^\s*while\s+",
        r"\.forEach\s*\(",
        r"\.map\s*\(",
        r"\.filter\s*\(",
        r"\.reduce\s*\(",
        r"\bfor\s*\(",
    ],
    "pagination": [
        r"\bpage\b",
        r"\bper_page\b",
        r"\blimit\b",
        r"\boffset\b",
        r"\bcursor\b",
        r"\bnext[_-]?token\b",
        r"\bcontinuation\b",
        r"\bpaginate\b",
        r"\bpaginator\b",
        r"\bLink\b",
    ],
    "large_data_processing": [
        r"\bread_csv\b",
        r"\bread_json\b",
        r"\bread_parquet\b",
        r"\bDataFrame\b",
        r"\bjson\.loads?\b",
        r"\bJSON\.parse\b",
        r"\bread\(\)",
        r"\bread_text\(",
        r"\bread_bytes\(",
        r"\bglob\b",
        r"\brglob\b",
        r"\bos\.walk\b",
        r"\bsort(ed)?\s*\(",
        r"\bgroupby\b",
        r"\bto_json\b",
        r"\bjson\.dumps\b",
        r"\bJSON\.stringify\b",
    ],
    "cache_usage": [
        r"\b[a-z0-9_]*cache[a-z0-9_]*\b",
        r"\blru_cache\b",
        r"\bmemo",
        r"\bTTL\b",
        r"\bredis\b",
        r"\bmemcached\b",
        r"\bMap<",
        r"\bnew Map\s*\(",
    ],
    "sleep_retry": [
        r"\bsleep\s*\(",
        r"\btime\.sleep\b",
        r"\bsetTimeout\s*\(",
        r"\bretry\b",
        r"\bretries\b",
        r"\bbackoff\b",
        r"\btenacity\b",
        r"\battempts?\b",
    ],
    "heavy_startup": [
        r"^\s*import\s+(pandas|numpy|torch|tensorflow|sklearn|spacy|transformers|selenium|playwright)\b",
        r"^\s*from\s+(pandas|numpy|torch|tensorflow|sklearn|spacy|transformers|selenium|playwright)\b",
        r"^\s*const\s+.*=\s*require\(['\"](playwright|puppeteer|sharp|canvas|tensorflow|onnxruntime)",
        r"\bcreate_engine\s*\(",
        r"\bconnect\s*\(",
        r"\bload_model\b",
        r"\bfrom_pretrained\b",
        r"\bchromium\.launch\b",
        r"\bnew\s+(S3Client|DynamoDBClient|OpenAI|Anthropic)\b",
    ],
    "logging": [
        r"\blogger\.",
        r"\blogging\.",
        r"\bconsole\.",
        r"\blog\.",
        r"\bslog\.",
        r"\bzap\.",
        r"\bpino\b",
        r"\bwinston\b",
    ],
}

COMPILED_PATTERNS = {
    name: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for name, patterns in PATTERNS.items()
}


@dataclass(frozen=True)
class Hit:
    file: str
    line: int
    text: str


def is_text_candidate(path: Path) -> bool:
    if path.name in SENSITIVE_FILENAMES:
        return False
    if path.name in SAFE_TEXT_FILENAMES:
        return True
    return path.suffix in TEXT_SUFFIXES


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if is_text_candidate(path):
            yield path


def read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def trim(text: str, limit: int = 180) -> str:
    normalized = " ".join(text.strip().split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def add_hit(bucket: list[Hit], root: Path, path: Path, line_no: int, text: str, max_hits: int) -> None:
    if len(bucket) >= max_hits:
        return
    bucket.append(Hit(str(path.relative_to(root)), line_no, trim(text)))


def scan_file(root: Path, path: Path, max_hits: int) -> dict[str, list[Hit]]:
    lines = read_lines(path)
    results: dict[str, list[Hit]] = {name: [] for name in PATTERNS}

    for line_no, line in enumerate(lines, start=1):
        for name, patterns in COMPILED_PATTERNS.items():
            if len(results[name]) >= max_hits:
                continue
            if any(pattern.search(line) for pattern in patterns):
                add_hit(results[name], root, path, line_no, line, max_hits)

    loop_lines = [hit.line for hit in results["loops"]]
    if loop_lines and (results["external_calls"] or results["database_access"]):
        call_lines = [
            hit.line for hit in results["external_calls"] + results["database_access"]
        ]
        near_external_loop = [
            loop_line
            for loop_line in loop_lines
            if any(abs(call_line - loop_line) <= 8 for call_line in call_lines)
        ]
        if near_external_loop:
            bucket = results.setdefault("possible_loops_over_external_calls", [])
            for loop_line in near_external_loop[:max_hits]:
                add_hit(bucket, root, path, loop_line, lines[loop_line - 1], max_hits)

    return {name: hits for name, hits in results.items() if hits}


def summarize(root: Path, max_hits_per_category: int) -> dict[str, object]:
    category_hits: dict[str, list[Hit]] = {}
    files_scanned = 0

    for path in iter_files(root):
        files_scanned += 1
        file_results = scan_file(root, path, max_hits_per_category)
        for name, hits in file_results.items():
            bucket = category_hits.setdefault(name, [])
            remaining = max_hits_per_category - len(bucket)
            if remaining > 0:
                bucket.extend(hits[:remaining])

    return {
        "repo": str(root),
        "files_scanned": files_scanned,
        "categories": {
            name: [hit.__dict__ for hit in hits]
            for name, hits in sorted(category_hits.items())
        },
        "notes": [
            "Inventory is pattern-based and read-only; validate every important hit by reading code paths.",
            "possible_loops_over_external_calls is a proximity signal, not proof of an N+1 issue.",
            "Sensitive dotenv and package-auth files are skipped.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="Repository root to scan")
    parser.add_argument(
        "--max-hits-per-category",
        type=int,
        default=50,
        help="Maximum example hits retained for each category",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")
    summary = summarize(root, max(1, args.max_hits_per_category))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
