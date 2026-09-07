#!/usr/bin/env python3
"""Report how far the mp-* skills have drifted from mattpocock/skills.

The mp-* skills are ports, not forks: content matches upstream byte for byte
once the deliberate renames are undone. This script clones upstream into a temp
directory, reverses those renames, and diffs. Anything it prints is either
upstream moving ahead or a local edit that should not exist.

  python3 scripts/check-upstream-sync.py            # summary
  python3 scripts/check-upstream-sync.py --diff     # full unified diffs
  python3 scripts/check-upstream-sync.py --ref REF  # pin an upstream commit
"""
import argparse
import difflib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UPSTREAM = "https://github.com/mattpocock/skills.git"

# upstream skill name -> (our skill name, our bucket)
PORTED = {
    "grill-me": ("mp-grill-me", "planning"),
    "grill-with-docs": ("mp-grill-with-docs", "planning"),
    "grilling": ("mp-grilling", "planning"),
    "domain-modeling": ("mp-domain-modeling", "planning"),
    "improve-codebase-architecture": ("mp-improve-codebase-architecture", "planning"),
    "to-spec": ("mp-to-spec", "planning"),
    "to-tickets": ("mp-to-tickets", "planning"),
    "wayfinder": ("mp-wayfinder", "planning"),
    "triage": ("mp-triage", "planning"),
    "setup-matt-pocock-skills": ("mp-setup", "planning"),
    "tdd": ("mp-tdd", "engineering"),
    "codebase-design": ("mp-codebase-design", "engineering"),
    "diagnosing-bugs": ("mp-diagnosing-bugs", "engineering"),
    "implement": ("mp-implement", "engineering"),
    "resolving-merge-conflicts": ("mp-resolving-merge-conflicts", "engineering"),
    "prototype": ("mp-prototype", "engineering"),
    "wizard": ("mp-wizard", "engineering"),
    "handoff": ("mp-handoff", "productivity"),
    "teach": ("mp-teach", "productivity"),
    "wait-what": ("mp-wait-what", "productivity"),
    "to-questionnaire": ("mp-to-questionnaire", "productivity"),
    "writing-for-agents": ("mp-writing-for-agents", "meta"),
}
# upstream skills we answer with our own equivalent instead of porting
ALIASES = {"code-review": "team-review", "research": "team-research", "ask-matt": "which-skill"}

RENAMES = {u: o for u, (o, _) in PORTED.items()}
RENAMES.update(ALIASES)

# Deliberate local edits, applied after the rename reversal so an expected
# difference does not read as drift. Keep this list short: every entry is a
# place where re-syncing upstream needs a human decision.
DEBRAND = [
    ("# Setup Engineering Skills", "# Setup Matt Pocock's Skills"),
    ('display_name: "Setup Engineering Skills"', 'display_name: "Setup Matt Pocock Skills"'),
    ("| Label in robert-aghajanyan/skills | Label in our tracker |",
     "| Label in mattpocock/skills | Label in our tracker |"),
    ("| --------------------------------- | -------------------- |",
     "| -------------------------- | -------------------- |"),
]

# Ours -> upstream, so a local file can be compared against the upstream original.
def to_upstream(text: str) -> str:
    for up in sorted(RENAMES, key=len, reverse=True):
        ours = RENAMES[up]
        text = text.replace(f'"{ours}"', f'"{up}"')
        text = re.sub(rf"`/{re.escape(ours)}`", f"`/{up}`", text)
        text = re.sub(rf"`{re.escape(ours)}`", f"`{up}`", text)
        text = re.sub(rf"(?<![\w/-])/{re.escape(ours)}\b", f"/{up}", text)
    for ours_text, upstream_text in DEBRAND:
        text = text.replace(ours_text, upstream_text)
    return text


def strip_name(text: str) -> str:
    return re.sub(r"^name: .*$", "name: <name>", text, count=1, flags=re.M)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff", action="store_true", help="print full diffs")
    ap.add_argument("--ref", help="upstream ref to compare against (default: default branch)")
    args = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="upstream-skills-"))
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
        for up_name, (our_name, bucket) in sorted(PORTED.items()):
            src = next(
                (up / "skills" / b / up_name for b in ("engineering", "productivity", "misc", "in-progress")
                 if (up / "skills" / b / up_name).is_dir()),
                None,
            )
            if src is None:
                print(f"  GONE UPSTREAM  {up_name} -> {our_name} (deprecated or renamed upstream?)")
                missing += 1
                continue
            dst = REPO / "skills" / bucket / our_name
            for f in sorted(p for p in src.rglob("*") if p.is_file()):
                rel = f.relative_to(src)
                # LICENSE.txt is ours: upstream licenses at the repo root.
                if rel.name == "LICENSE.txt":
                    continue
                target = dst / rel
                if not target.exists():
                    print(f"  NEW UPSTREAM   {our_name}/{rel}")
                    missing += 1
                    continue
                compared += 1
                a, b = f.read_text(), to_upstream(target.read_text())
                if rel.name == "SKILL.md":
                    a, b = strip_name(a), strip_name(b)
                if a == b:
                    continue
                drifted += 1
                if args.diff:
                    print(f"\n  --- {our_name}/{rel}")
                    for line in difflib.unified_diff(
                        a.splitlines(), b.splitlines(),
                        fromfile=f"upstream/{up_name}/{rel}", tofile=f"ours/{our_name}/{rel}",
                        lineterm="", n=2,
                    ):
                        print("  " + line)
                else:
                    n = sum(
                        1 for line in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0)
                        if line[:1] in "+-" and not line.startswith(("---", "+++"))
                    )
                    print(f"  DRIFT          {our_name}/{rel} ({n} changed lines)")

        print(f"\n{compared} files compared, {drifted} drifted, {missing} missing or new upstream")
        if drifted or missing:
            print("Re-run with --diff to see what changed.")
            return 1
        print("mp-* skills are in sync with upstream.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
