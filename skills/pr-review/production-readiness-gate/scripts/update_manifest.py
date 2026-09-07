#!/usr/bin/env python3
"""Regenerate the production-readiness-gate manifest checksums."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


IGNORED_DIRS = {".git", "__pycache__"}
IGNORED_FILES = {"manifest.json", ".DS_Store"}


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def discover_files(skill_dir: Path) -> list[str]:
    paths: list[str] = []
    for path in skill_dir.rglob("*"):
        rel = path.relative_to(skill_dir)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if not path.is_file() or path.name in IGNORED_FILES or path.suffix == ".pyc":
            continue
        paths.append(rel.as_posix())
    return sorted(paths)


def combined_digest(skill_dir: Path, relative_paths: list[str]) -> str:
    combined = hashlib.sha256()
    for rel_path in relative_paths:
        combined.update(rel_path.encode("utf-8"))
        combined.update(b"\0")
        combined.update(file_digest(skill_dir / rel_path).encode("ascii"))
        combined.update(b"\n")
    return combined.hexdigest()


def git_value(skill_dir: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(skill_dir), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def source_block(
    skill_dir: Path,
    existing: dict,
    source_repo: str | None,
    source_commit: str | None,
    source_tag: str | None,
) -> dict:
    git_root = git_value(skill_dir, "rev-parse", "--show-toplevel")
    git_commit = git_value(skill_dir, "rev-parse", "HEAD") if git_root else None
    source = dict(existing.get("source") or {})

    source["type"] = "git-working-copy" if git_root or source_repo or source_commit else "local-installed-skill"
    source["installed_path"] = str(skill_dir)
    if source_repo or git_root:
        source["source_repo"] = source_repo or git_root
    elif "source_repo" in source:
        del source["source_repo"]
    source["git_commit"] = source_commit or git_commit
    inferred_tag = git_value(skill_dir, "describe", "--tags", "--exact-match", "HEAD") if git_root else None
    if source_tag or inferred_tag:
        source["source_tag"] = source_tag or inferred_tag
    elif "source_tag" in source:
        del source["source_tag"]

    if source["git_commit"] and source.get("source_tag"):
        source["provenance_note"] = "Installed copy is validated by file checksums and stamped with source commit and tag provenance."
    elif source["git_commit"]:
        source["provenance_note"] = "Installed copy is validated by file checksums and stamped with source commit provenance."
    else:
        source["provenance_note"] = "Installed copy is validated by file checksums. No source Git commit is available from this directory."
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-repo", help="Optional source repository path or URL to stamp into manifest.")
    parser.add_argument("--source-commit", help="Optional source commit SHA to stamp into manifest.")
    parser.add_argument("--source-tag", help="Optional source tag to stamp into manifest.")
    parser.add_argument("--version", help="Optional manifest version override.")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    manifest_path = skill_dir / "manifest.json"
    existing = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    relative_paths = discover_files(skill_dir)
    tracked_files = [{"path": rel_path, "sha256": file_digest(skill_dir / rel_path)} for rel_path in relative_paths]
    manifest = {
        "schema_version": 1,
        "name": "production-readiness-gate",
        "version": args.version or existing.get("version", "1.1.0"),
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": source_block(skill_dir, existing, args.source_repo, args.source_commit, args.source_tag),
        "content_sha256": combined_digest(skill_dir, relative_paths),
        "tracked_files": tracked_files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"updated {manifest_path}")
    print(f"content_sha256 {manifest['content_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
