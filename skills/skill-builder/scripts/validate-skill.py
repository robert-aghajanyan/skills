#!/usr/bin/env python3
"""
Validate a Claude Code skill for common issues.

Usage:
    python validate-skill.py <skill-directory>

Checks:
1. SKILL.md exists and has valid frontmatter
2. Name is kebab-case, max 64 chars, no reserved words
3. Description exists, max 1024 chars, no XML tags
4. SKILL.md is under 500 lines
5. No README.md in the skill directory
6. Referenced files exist
7. Gotchas section present
"""

import sys
import re
from pathlib import Path

RESERVED = {"claude", "anthropic"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
XML_TAG = re.compile(r"<[^>]+>")


def validate(skill_dir: str) -> list[str]:
    errors = []
    warnings = []
    path = Path(skill_dir)

    print(f"\nValidating: {skill_dir}")
    print(f"{'=' * 50}")

    # 1. SKILL.md exists
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        print(f"\nERRORS (1):\n  [x] SKILL.md not found")
        return errors

    content = skill_md.read_text()
    lines = content.splitlines()

    # 2. Frontmatter exists
    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter (must start with ---)")
        print(f"\nERRORS (1):\n  [x] Missing YAML frontmatter (must start with ---)")
        return errors

    end = content.find("---", 3)
    if end == -1:
        errors.append("Frontmatter not closed (missing second ---)")
        print(f"\nERRORS (1):\n  [x] Frontmatter not closed (missing second ---)")
        return errors

    frontmatter = content[3:end].strip()

    # 3. Name field
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if len(name) > 64:
            errors.append(f"Name too long ({len(name)} chars, max 64)")
        if not KEBAB.match(name):
            errors.append(f"Name '{name}' must be kebab-case (lowercase, hyphens only)")
        if any(r in name.lower() for r in RESERVED):
            errors.append(f"Name '{name}' contains reserved word (claude/anthropic)")
        if XML_TAG.search(name):
            errors.append("Name contains XML tags")
    else:
        warnings.append("No 'name' field — will use directory name")

    # 4. Description field
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) > 1024:
            errors.append(f"Description too long ({len(desc)} chars, max 1024)")
        if XML_TAG.search(desc):
            errors.append("Description contains XML tags")
        if "use when" not in desc.lower() and "trigger" not in desc.lower():
            warnings.append("Description missing trigger phrases (e.g., 'Use when...')")
    else:
        warnings.append("No 'description' field — Claude won't know when to trigger")

    # 5. Line count
    body_start = end + 3
    body_lines = content[body_start:].splitlines()
    if len(body_lines) > 500:
        warnings.append(f"SKILL.md body is {len(body_lines)} lines (recommended: under 500). Move detail to references/")

    # 6. No README.md
    if (path / "README.md").exists():
        warnings.append("README.md found — documentation should go in SKILL.md or references/")

    # 7. Referenced files exist
    for match in re.finditer(r"\[.*?\]\(((?!http)[^)]+)\)", content):
        ref = match.group(1)
        ref_path = path / ref
        if not ref_path.exists():
            errors.append(f"Referenced file not found: {ref}")

    # 8. Gotchas section
    if "gotcha" not in content.lower():
        warnings.append("No Gotchas section — this is the highest-signal content in a skill")

    # Print results
    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  [x] {e}")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  [!] {w}")

    if not errors and not warnings:
        print("\n  PASS — no issues found")

    stats = {
        "name": name_match.group(1).strip() if name_match else "(none)",
        "body_lines": len(body_lines),
        "files": len(list(path.rglob("*")) ) - 1,  # exclude SKILL.md
        "has_scripts": (path / "scripts").is_dir(),
        "has_references": (path / "references").is_dir(),
    }
    print(f"\nStats:")
    print(f"  Name: {stats['name']}")
    print(f"  Body lines: {stats['body_lines']}")
    print(f"  Supporting files: {stats['files']}")
    print(f"  Has scripts/: {stats['has_scripts']}")
    print(f"  Has references/: {stats['has_references']}")

    return errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate-skill.py <skill-directory>")
        sys.exit(1)

    errors = validate(sys.argv[1])
    sys.exit(1 if errors else 0)
