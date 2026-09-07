#!/usr/bin/env python3
"""Report how far skills/productivity/humanizer has drifted from blader/humanizer.

Like the mp-* skills, humanizer is a port, not a fork: SKILL.md and
agents/openai.yaml match upstream byte for byte once the two deliberate local
edits below are undone. Upstream keeps them at the repo root; we keep them in a
bucket. Anything this script prints is either upstream moving ahead or a local
edit that should not exist.

  python3 scripts/check-humanizer-sync.py            # summary
  python3 scripts/check-humanizer-sync.py --diff     # full unified diffs
  python3 scripts/check-humanizer-sync.py --ref REF  # pin an upstream commit
"""
import argparse
import difflib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UPSTREAM = "https://github.com/blader/humanizer.git"
OURS = REPO / "skills" / "productivity" / "humanizer"

# upstream path (relative to upstream repo root) -> our path (relative to OURS)
PORTED = {
    "SKILL.md": "SKILL.md",
    "agents/openai.yaml": "agents/openai.yaml",
}

# Deliberate local edits, stripped before comparing so an expected difference
# does not read as drift. Both make the skill user-invoked in this repo, which
# upstream does not do. Keep this list short: every entry is a place where
# re-syncing upstream needs a human decision.
LOCAL_EDITS = {
    "SKILL.md": ["disable-model-invocation: true\n"],
    "agents/openai.yaml": ["policy:\n  allow_implicit_invocation: false\n"],
}


def to_upstream(rel: str, text: str) -> str:
    """Undo our deliberate edits so the file can be compared with the original."""
    for edit in LOCAL_EDITS.get(rel, []):
        if edit not in text:
            print(f"  LOCAL EDIT GONE  humanizer/{rel}: expected to strip {edit.splitlines()[0]!r}")
        text = text.replace(edit, "", 1)
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff", action="store_true", help="print full diffs")
    ap.add_argument("--ref", help="upstream ref to compare against (default: default branch)")
    args = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="upstream-humanizer-"))
    try:
        subprocess.run(
            ["git", "clone", "--quiet", "--depth", "50", UPSTREAM, str(tmp / "up")],
            check=True,
        )
        up = tmp / "up"
        if args.ref:
            subprocess.run(["git", "-C", str(up), "checkout", "--quiet", args.ref], check=True)
        head = subprocess.run(
            ["git", "-C", str(up), "log", "-1", "--format=%h %ad %s", "--date=short"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        print(f"upstream {UPSTREAM}\n  at {head}\n")

        drifted = missing = compared = 0
        for up_rel, our_rel in sorted(PORTED.items()):
            src, dst = up / up_rel, OURS / our_rel
            if not src.is_file():
                print(f"  GONE UPSTREAM  {up_rel} (moved or renamed upstream?)")
                missing += 1
                continue
            if not dst.is_file():
                print(f"  MISSING HERE   humanizer/{our_rel}")
                missing += 1
                continue
            compared += 1
            a, b = src.read_text(), to_upstream(our_rel, dst.read_text())
            if a == b:
                continue
            drifted += 1
            if args.diff:
                print(f"\n  --- humanizer/{our_rel}")
                for line in difflib.unified_diff(
                    a.splitlines(), b.splitlines(),
                    fromfile=f"upstream/{up_rel}", tofile=f"ours/{our_rel}",
                    lineterm="", n=2,
                ):
                    print("  " + line)
            else:
                n = sum(
                    1 for line in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0)
                    if line[:1] in "+-" and not line.startswith(("---", "+++"))
                )
                print(f"  DRIFT          humanizer/{our_rel} ({n} changed lines)")

        print(f"\n{compared} files compared, {drifted} drifted, {missing} missing or gone upstream")
        if drifted or missing:
            print("Re-run with --diff to see what changed.")
            return 1
        print("humanizer is in sync with upstream.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
