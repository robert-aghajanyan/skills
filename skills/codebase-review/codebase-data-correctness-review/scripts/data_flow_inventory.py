#!/usr/bin/env python3
"""Summarize likely data-correctness review surfaces in a repository.

This helper is read-only. It uses filename and content heuristics to build a
first-pass map of inputs, outputs, transformations, SQL, migrations, reports,
aggregations, date/window logic, and fixture datasets.
"""

from __future__ import annotations

import argparse
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


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
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "coverage",
    ".next",
    ".turbo",
    ".worktrees",
    ".codex-worktrees",
    ".claude",
    ".claude-plugin",
    ".codex-plugin",
    ".cache",
    "target",
}

SKIP_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "Pipfile.lock",
}

TEXT_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".kt",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".cs",
    ".scala",
    ".sql",
    ".sh",
    ".bash",
    ".zsh",
    ".yaml",
    ".yml",
    ".json",
    ".jsonl",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".r",
    ".R",
    ".ipynb",
}

DATA_SUFFIXES = {
    ".csv",
    ".tsv",
    ".xlsx",
    ".xls",
    ".parquet",
    ".avro",
    ".orc",
    ".feather",
    ".arrow",
    ".sqlite",
    ".db",
    ".duckdb",
}

JSON_DATA_SUFFIXES = {".json", ".jsonl"}

DATA_PATH_HINT = re.compile(
    r"(^|/)(data|datasets?|fixtures?|examples?|samples?|testdata|test_data|inputs?|outputs?|exports?|reports?|actuals?|forecasts?|billing|cost|invoices?|metrics)(/|_|-|\.|$)",
    re.IGNORECASE,
)

PATTERNS = {
    "input readers": re.compile(
        r"\b(read_csv|read_excel|read_json|read_parquet|read_sql|load_table|load_dataset|from_csv|COPY\s+.*FROM|SELECT\s+.+\s+FROM|open\s*\(|fs\.readFile|createReadStream)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    "output writers": re.compile(
        r"\b(to_csv|to_excel|to_json|to_parquet|write_csv|write_excel|write_json|write_parquet|saveAsTable|insertInto|COPY\s+.+\s+TO|render|export|writeFile|createWriteStream)\b",
        re.IGNORECASE,
    ),
    "joins": re.compile(
        r"\b(join|merge|concat|LEFT\s+JOIN|RIGHT\s+JOIN|INNER\s+JOIN|FULL\s+OUTER\s+JOIN|CROSS\s+JOIN|UNION\s+ALL|lookup|foreign_key)\b",
        re.IGNORECASE,
    ),
    "aggregation": re.compile(
        r"\b(groupby|group_by|GROUP\s+BY|HAVING|agg|aggregate|pivot|rollup|cube|sum\s*\(|avg\s*\(|mean\s*\(|count\s*\(|nunique|distinct|window|PARTITION\s+BY|resample)\b",
        re.IGNORECASE,
    ),
    "date/window logic": re.compile(
        r"\b(datetime|date|timestamp|timezone|tz|utc|fiscal|calendar|month|quarter|week|day|between|start_date|end_date|from_date|to_date|now\s*\(|today\s*\(|CURRENT_DATE|CURRENT_TIMESTAMP|date_trunc|rolling|window)\b",
        re.IGNORECASE,
    ),
    "rounding/precision": re.compile(
        r"\b(round|ceil|floor|decimal|precision|scale|BigDecimal|quantize|toFixed|Math\.round|ROUND\s*\()\b",
        re.IGNORECASE,
    ),
    "currency/units": re.compile(
        r"\b(currency|exchange_rate|fx|usd|eur|gbp|jpy|cost|billing|price|amount|unit|bytes|gib|gb|mib|mb|cpu|millicore|seconds|milliseconds|rate|percent|percentage|bps)\b",
        re.IGNORECASE,
    ),
    "null/default handling": re.compile(
        r"\b(null|none|nan|na|missing|coalesce|fillna|ifnull|isnull|nvl|default|empty|blank|dropna|notna)\b",
        re.IGNORECASE,
    ),
    "forecast/report metrics": re.compile(
        r"\b(forecast|actual|variance|reconcile|metric|kpi|dashboard|report|billing|invoice|cost|revenue|margin|usage|utilization)\b",
        re.IGNORECASE,
    ),
}

CATEGORY_HINTS = {
    "migrations": re.compile(r"(^|/)(migrations?|alembic|db/migrate|schema|backfill)(/|$)|migration|backfill", re.IGNORECASE),
    "report writers": re.compile(r"report|dashboard|export|writer|renderer|template|html|pdf|xlsx|spreadsheet|chart", re.IGNORECASE),
    "fixtures/examples": re.compile(r"fixture|fixtures|example|examples|sample|samples|testdata|test_data|golden|snapshot", re.IGNORECASE),
    "transformations": re.compile(r"transform|etl|pipeline|prepare|normalize|enrich|reconcile|forecast|billing|aggregate|rollup", re.IGNORECASE),
}


@dataclass
class Hit:
    path: str
    reason: str


def iter_files(root: Path, max_files: int) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            if len(files) >= max_files:
                return files
            if filename.startswith(".env") or filename in SKIP_FILES:
                continue
            files.append(Path(dirpath) / filename)
    return files


def read_text(path: Path, max_bytes: int) -> str:
    if path.suffix not in TEXT_SUFFIXES:
        return ""
    try:
        raw = path.read_bytes()[:max_bytes]
    except OSError:
        return ""
    if b"\x00" in raw:
        return ""
    return raw.decode("utf-8", errors="replace")


def add_hit(bucket: dict[str, list[Hit]], category: str, path: Path, root: Path, reason: str) -> None:
    rel = str(path.relative_to(root))
    bucket[category].append(Hit(rel, reason))


def classify_file(path: Path, root: Path, text: str, bucket: dict[str, list[Hit]]) -> None:
    rel = str(path.relative_to(root))
    rel_lower = rel.lower()
    suffix = path.suffix.lower()

    if suffix in DATA_SUFFIXES or (suffix in JSON_DATA_SUFFIXES and DATA_PATH_HINT.search(rel_lower)):
        reason = f"data-like suffix {suffix}"
        if CATEGORY_HINTS["fixtures/examples"].search(rel_lower):
            add_hit(bucket, "fixture/example datasets", path, root, reason)
        else:
            add_hit(bucket, "data inputs or outputs", path, root, reason)

    if suffix == ".sql":
        add_hit(bucket, "SQL files", path, root, "SQL file")

    for category, regex in CATEGORY_HINTS.items():
        if regex.search(rel_lower):
            add_hit(bucket, category, path, root, "path/name hint")

    if not text or suffix == ".md":
        return

    for category, regex in PATTERNS.items():
        match = regex.search(text)
        if match:
            snippet = " ".join(match.group(0).split())[:80]
            add_hit(bucket, category, path, root, f"content match: {snippet}")


def dedupe_hits(hits: list[Hit]) -> list[Hit]:
    seen: set[tuple[str, str]] = set()
    deduped: list[Hit] = []
    for hit in hits:
        key = (hit.path, hit.reason)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(hit)
    return sorted(deduped, key=lambda item: item.path)


def print_section(title: str, hits: list[Hit], limit: int) -> None:
    print(f"\n## {title}")
    if not hits:
        print("- none found")
        return
    deduped = dedupe_hits(hits)
    for hit in deduped[:limit]:
        print(f"- `{hit.path}` - {hit.reason}")
    remaining = len(deduped) - limit
    if remaining > 0:
        print(f"- ... {remaining} more")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="Repository root to inspect")
    parser.add_argument("--max-files", type=int, default=2500, help="Maximum files to inspect")
    parser.add_argument("--max-bytes", type=int, default=200_000, help="Maximum bytes to read per text file")
    parser.add_argument("--limit", type=int, default=40, help="Maximum entries per section")
    args = parser.parse_args()

    root = Path(args.repo).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    bucket: dict[str, list[Hit]] = defaultdict(list)
    files = iter_files(root, args.max_files)
    for path in files:
        text = read_text(path, args.max_bytes)
        classify_file(path, root, text, bucket)

    print(f"# Data Flow Inventory: {root}")
    print(f"\nScanned {len(files)} files. Heuristics are a map for review, not proof.")

    ordered_sections = [
        "data inputs or outputs",
        "input readers",
        "output writers",
        "transformations",
        "SQL files",
        "migrations",
        "report writers",
        "joins",
        "aggregation",
        "date/window logic",
        "rounding/precision",
        "currency/units",
        "null/default handling",
        "forecast/report metrics",
        "fixture/example datasets",
    ]

    for section in ordered_sections:
        print_section(section, bucket.get(section, []), args.limit)

    print("\n## Suggested Next Checks")
    print("- Reconcile row counts before and after joins and filters.")
    print("- Recompute high-risk totals from raw inputs with a minimal fixture.")
    print("- Verify time windows with boundary rows and explicit timezone assumptions.")
    print("- Compare report totals against the authoritative source at the same grain.")
    print("- Check migrations for idempotence, partial-run recovery, and schema drift.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
