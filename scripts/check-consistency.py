#!/usr/bin/env python3
"""Fail the build when the repo's manifests, READMEs, and skills drift apart.

Checks, for a repo laid out as skills/<bucket>/<skill>/SKILL.md:

  1. every promoted skill has an entry in .claude-plugin/plugin.json
  2. plugin.json lists nothing that is not a promoted skill on disk
  3. plugin.json and marketplace.json agree on the version
  4. every skill has LICENSE.txt and agents/openai.yaml
  5. SKILL.md frontmatter and agents/openai.yaml are both valid YAML, and
     disable-model-invocation agrees with policy.allow_implicit_invocation
  6. every promoted skill appears in its bucket README, the top-level README,
     and the which-skill router map
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs it
    yaml = None

REPO = Path(__file__).resolve().parent.parent
PROMOTED = {"codebase-review", "pr-review", "engineering", "planning", "productivity", "meta"}
ROUTER = REPO / "skills" / "meta" / "which-skill" / "SKILL.md"

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def frontmatter(skill_md: Path) -> str:
    text = skill_md.read_text()
    parts = text.split("---\n")
    return parts[1] if len(parts) > 2 else ""


def main() -> int:
    plugin = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())

    if plugin["version"] != market["metadata"]["version"]:
        err(
            f"version mismatch: plugin.json {plugin['version']}, "
            f"marketplace.json {market['metadata']['version']}"
        )

    on_disk = {}
    for skill_md in sorted((REPO / "skills").glob("*/*/SKILL.md")):
        d = skill_md.parent
        on_disk[f"./skills/{d.parent.name}/{d.name}"] = d

    listed = set(plugin["skills"])
    promoted = {p: d for p, d in on_disk.items() if d.parent.name in PROMOTED}

    for p in sorted(promoted.keys() - listed):
        err(f"promoted skill missing from plugin.json: {p}")
    for p in sorted(listed - set(on_disk)):
        err(f"plugin.json lists a path that does not exist: {p}")
    for p in sorted(listed & set(on_disk) - promoted.keys()):
        err(f"plugin.json ships a non-promoted skill: {p}")

    root_readme = (REPO / "README.md").read_text()
    router = ROUTER.read_text()

    for path, d in sorted(on_disk.items()):
        name, bucket = d.name, d.parent.name

        if not (d / "LICENSE.txt").is_file():
            err(f"{name}: missing LICENSE.txt")

        yaml_path = d / "agents" / "openai.yaml"
        if not yaml_path.is_file():
            err(f"{name}: missing agents/openai.yaml")
            continue

        fm = frontmatter(d / "SKILL.md")
        claude_user = bool(re.search(r"^disable-model-invocation:\s*true", fm, re.M))
        codex_user = "allow_implicit_invocation: false" in yaml_path.read_text()
        if claude_user != codex_user:
            err(
                f"{name}: invocation axis disagrees between harnesses "
                f"(SKILL.md user={claude_user}, openai.yaml user={codex_user})"
            )

        if yaml is not None:
            # An unquoted ": " in a description silently produces frontmatter no
            # harness can parse. validate-skill.py reads it with a regex and
            # does not notice, so check it here.
            for label, raw in (("SKILL.md frontmatter", fm),
                               ("agents/openai.yaml", yaml_path.read_text())):
                try:
                    parsed = yaml.safe_load(raw)
                except yaml.YAMLError as exc:
                    first = str(exc).split("\n")[0]
                    err(f"{name}: {label} is not valid YAML: {first}")
                    continue
                if label.startswith("SKILL.md") and parsed.get("name") != name:
                    err(f"{name}: frontmatter name is {parsed.get('name')!r}")
                if label.startswith("agents") and not (
                    parsed.get("interface", {}) or {}
                ).get("display_name"):
                    err(f"{name}: agents/openai.yaml has no interface.display_name")

        if bucket not in PROMOTED:
            continue

        bucket_readme = REPO / "skills" / bucket / "README.md"
        if not bucket_readme.is_file():
            err(f"{bucket}: missing README.md")
        elif f"/{name}/SKILL.md)" not in bucket_readme.read_text():
            err(f"{name}: missing from skills/{bucket}/README.md")

        if f"skills/{bucket}/{name}" not in root_readme:
            err(f"{name}: missing from the top-level README.md")
        if name != "which-skill" and f"`{name}`" not in router:
            err(f"{name}: missing from the which-skill router map")

    if errors:
        print(f"✘ {len(errors)} consistency error(s):\n", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"✔ {len(on_disk)} skills consistent ({len(promoted)} promoted, v{plugin['version']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
